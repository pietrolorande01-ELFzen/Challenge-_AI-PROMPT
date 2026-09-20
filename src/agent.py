"""
Núcleo conversacional refatorado — LangChain (LCEL + RunnableWithMessageHistory).

Pipeline end-to-end:

    pergunta
       │
       ├─► [Guardrail de entrada]  ── bloqueio? ─► resposta canônica (LLM não é chamada)
       │
       ├─► [Retriever Chroma] ──► higienização do contexto
       │
       ├─► [Prompt v3] + [Memória da sessão (framework)]
       │
       ├─► [LLM parametrizada]  ──► métricas (latência, tokens)
       │
       └─► [Guardrail de saída] ──► resposta final + gravação na memória
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.config import ConfigModelo, MODELOS, MODELO_PADRAO, carregar_token
from src.guardrails import Veredito, higienizar_contexto, validar_entrada, validar_saida
from src.knowledge import construir_retriever, formatar_contexto
from src.memory import janela, obter_historico, snapshot
from src.metrics import ColetorMetricas, MetricaTurno, cronometro, extrair_uso
from src.prompts import VERSAO_PROMPT, montar_prompt


# ──────────────────────────────────────────────────────────────────────────────
# Fábrica de LLMs — provedor trocável sem alterar o núcleo
# ──────────────────────────────────────────────────────────────────────────────
def criar_llm(cfg: ConfigModelo):
    if cfg.provedor == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=cfg.repo_id,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
            max_tokens=cfg.max_tokens,
            api_key=carregar_token("OPENAI_API_KEY"),
        )

    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

    endpoint = HuggingFaceEndpoint(
        repo_id=cfg.repo_id,
        task="text-generation",
        temperature=max(cfg.temperature, 0.01),   # a API rejeita temperature=0
        top_p=cfg.top_p,
        max_new_tokens=cfg.max_tokens,
        repetition_penalty=cfg.repetition_penalty,
        huggingfacehub_api_token=carregar_token("HUGGING_FACE_API_KEY"),
        timeout=120,
    )
    return ChatHuggingFace(llm=endpoint)


@dataclass
class RespostaAgente:
    texto: str
    modelo: str
    session_id: str
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    tokens_estimados: bool
    guardrail_entrada: dict
    guardrail_saida: dict
    bloqueado: bool
    trechos_recuperados: list[str] = field(default_factory=list)

    @property
    def tokens_total(self) -> int:
        return self.tokens_entrada + self.tokens_saida


class GoodWeAgent:
    """Agente conversacional GoodWe Assist (Sprint 03)."""

    def __init__(
        self,
        modelo: str | ConfigModelo = MODELO_PADRAO,
        retriever: Any | None = None,
        coletor: ColetorMetricas | None = None,
        versao_metrica: str = "sprint3",
        parametros: dict | None = None,
    ) -> None:
        cfg = MODELOS[modelo] if isinstance(modelo, str) else modelo
        if parametros:  # override pontual para a varredura de parametrização
            cfg = ConfigModelo(**{**cfg.como_dict(), **parametros})

        self.cfg = cfg
        self.versao_prompt = VERSAO_PROMPT
        self.versao_metrica = versao_metrica
        self.coletor = coletor or ColetorMetricas()
        self.retriever = retriever if retriever is not None else construir_retriever()
        self.llm = criar_llm(cfg)
        self.prompt = montar_prompt()
        self._contador_turnos: dict[str, int] = {}
        self._ultimo_guardrail = None
        self._chain_com_memoria = self._montar_chain()

    # ── construção da chain ──────────────────────────────────────────────────
    def _recuperar(self, entrada: dict) -> dict:
        docs = self.retriever.invoke(entrada["pergunta"])
        self._ultimos_docs = docs
        contexto = higienizar_contexto(formatar_contexto(docs))
        aviso = entrada.get("aviso_guardrail") or ""
        if aviso:
            contexto = f"{contexto}\n\n[ORIENTAÇÃO INTERNA DE SEGURANÇA]\n{aviso}"
        return {**entrada, "contexto": contexto}

    def _aplicar_janela(self, entrada: dict) -> dict:
        return {**entrada, "historico": janela(entrada.get("historico", []))}

    def _montar_chain(self):
        chain = (
            RunnablePassthrough()
            | RunnableLambda(self._aplicar_janela)
            | RunnableLambda(self._recuperar)
            | self.prompt
            | self.llm
        )
        return RunnableWithMessageHistory(
            chain,
            obter_historico,                     # memória gerenciada pelo framework
            input_messages_key="pergunta",
            history_messages_key="historico",
        )

    # ── API pública ──────────────────────────────────────────────────────────
    def responder(self, pergunta: str, session_id: str = "demo") -> RespostaAgente:
        turno = self._contador_turnos.get(session_id, 0) + 1
        self._contador_turnos[session_id] = turno
        self._ultimos_docs = []

        g_entrada = validar_entrada(pergunta)

        # Bloqueio duro: economiza tokens e latência, e não expõe a LLM ao ataque.
        if g_entrada.veredito == Veredito.BLOQUEAR:
            historico = obter_historico(session_id)
            historico.add_user_message(pergunta)
            historico.add_ai_message(g_entrada.mensagem)
            resposta = RespostaAgente(
                texto=g_entrada.mensagem,
                modelo=self.cfg.apelido,
                session_id=session_id,
                latencia_s=0.0,
                tokens_entrada=0,
                tokens_saida=0,
                tokens_estimados=False,
                guardrail_entrada=g_entrada.como_dict(),
                guardrail_saida={"veredito": "permitir", "categoria": "nao_aplicavel"},
                bloqueado=True,
            )
            self._registrar_metrica(resposta, turno)
            return resposta

        entrada = {"pergunta": pergunta, "aviso_guardrail": g_entrada.mensagem}
        config = {"configurable": {"session_id": session_id}}

        with cronometro() as t:
            bruto = self._chain_com_memoria.invoke(entrada, config=config)

        texto = bruto.content if hasattr(bruto, "content") else str(bruto)
        tok_in, tok_out, estimado = extrair_uso(bruto, pergunta, texto)

        g_saida = validar_saida(texto, g_entrada)
        bloqueado = g_saida.veredito == Veredito.BLOQUEAR
        if bloqueado:
            texto = g_saida.mensagem
            hist = obter_historico(session_id)
            if hist.messages:                     # substitui a resposta insegura na memória
                hist.messages[-1] = AIMessage(content=texto)

        resposta = RespostaAgente(
            texto=texto,
            modelo=self.cfg.apelido,
            session_id=session_id,
            latencia_s=t["segundos"],
            tokens_entrada=tok_in,
            tokens_saida=tok_out,
            tokens_estimados=estimado,
            guardrail_entrada=g_entrada.como_dict(),
            guardrail_saida=g_saida.como_dict(),
            bloqueado=bloqueado,
            trechos_recuperados=[d.metadata.get("chunk_id", "?") for d in self._ultimos_docs],
        )
        self._registrar_metrica(resposta, turno)
        return resposta

    def _registrar_metrica(self, r: RespostaAgente, turno: int) -> None:
        self.coletor.registrar(
            MetricaTurno(
                versao=self.versao_metrica,
                modelo=r.modelo,
                turno=turno,
                latencia_s=r.latencia_s,
                tokens_entrada=r.tokens_entrada,
                tokens_saida=r.tokens_saida,
                estimado=r.tokens_estimados,
                extras={
                    "session_id": r.session_id,
                    "bloqueado": r.bloqueado,
                    "guardrail": r.guardrail_entrada.get("categoria"),
                    "temperature": self.cfg.temperature,
                    "top_p": self.cfg.top_p,
                    "max_tokens": self.cfg.max_tokens,
                },
            )
        )

    def memoria(self, session_id: str = "demo") -> list[dict]:
        return snapshot(session_id)
