"""
Baseline das Sprints 1/2 — versão MANUAL, preservada para o comparativo antes/depois.

Características do legado (intencionalmente mantidas):
  · chamada direta ao InferenceClient da Hugging Face (sem framework);
  · histórico como lista Python remontada a cada chamada, sem isolamento por sessão;
  · sem camada de guardrails — a única defesa era a frase "se não souber, indique o suporte";
  · RAG chamado dentro da própria função do chatbot (acoplamento).

O código roda com o MESMO retriever e o MESMO conjunto de avaliação da versão nova,
para que a comparação meça o refactory e não a base de conhecimento.
"""

from __future__ import annotations

from src.config import ConfigModelo, MODELOS, carregar_token
from src.knowledge import formatar_contexto
from src.metrics import ColetorMetricas, MetricaTurno, cronometro, estimar_tokens
from src.prompts import SYSTEM_PROMPT_LEGADO

MAX_TENTATIVAS = 3
PAUSA_RETRY_S = 8


class ChatbotLegado:
    """Reprodução fiel do núcleo conversacional da Sprint 2."""

    def __init__(
        self,
        modelo: str | ConfigModelo = "qwen",
        retriever=None,
        coletor: ColetorMetricas | None = None,
    ) -> None:
        from huggingface_hub import InferenceClient

        self.cfg = MODELOS[modelo] if isinstance(modelo, str) else modelo
        self.retriever = retriever
        self.coletor = coletor or ColetorMetricas()
        self.client = InferenceClient(
            model=self.cfg.repo_id, token=carregar_token("HUGGING_FACE_API_KEY")
        )
        # Histórico global e manual: exatamente como na Sprint 2.
        self.historico: list[tuple[str, str]] = []
        self._turno = 0

    def responder(self, pergunta: str, historico: list | None = None) -> str:
        import time

        self._turno += 1
        historico = self.historico if historico is None else historico

        # 1. RETRIEVAL acoplado
        docs = self.retriever.invoke(pergunta) if self.retriever else []
        contexto = formatar_contexto(docs)

        # 2. Montagem manual das mensagens
        mensagens = [{"role": "system", "content": SYSTEM_PROMPT_LEGADO.format(contexto=contexto)}]
        for turno in historico:
            if isinstance(turno, (list, tuple)) and len(turno) == 2:
                if turno[0]:
                    mensagens.append({"role": "user", "content": turno[0]})
                if turno[1]:
                    mensagens.append({"role": "assistant", "content": turno[1]})
        mensagens.append({"role": "user", "content": pergunta})

        prompt_texto = "\n".join(m["content"] for m in mensagens)

        # 3. Geração com retry
        texto, ultimo_erro = "", None
        with cronometro() as t:
            for tentativa in range(1, MAX_TENTATIVAS + 1):
                try:
                    resp = self.client.chat_completion(
                        messages=mensagens,
                        max_tokens=self.cfg.max_tokens,
                        temperature=self.cfg.temperature,
                    )
                    texto = resp.choices[0].message.content
                    break
                except Exception as erro:
                    ultimo_erro = erro
                    if tentativa < MAX_TENTATIVAS:
                        time.sleep(PAUSA_RETRY_S)
            else:
                texto = f"❌ Falha após {MAX_TENTATIVAS} tentativas: {ultimo_erro}"

        self.historico.append((pergunta, texto))

        self.coletor.registrar(
            MetricaTurno(
                versao="legado",
                modelo=self.cfg.apelido,
                turno=self._turno,
                latencia_s=t["segundos"],
                tokens_entrada=estimar_tokens(prompt_texto),
                tokens_saida=estimar_tokens(texto),
                estimado=True,
                extras={
                    "temperature": self.cfg.temperature,
                    "max_tokens": self.cfg.max_tokens,
                    "guardrails": False,
                },
            )
        )
        return texto

    def resetar(self) -> None:
        self.historico = []
