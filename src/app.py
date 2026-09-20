"""
Interface Gradio — GoodWe Assist Sprint 03.

Diferença para a Sprint 2: a interface não carrega mais o histórico. Cada aba do
navegador recebe um `session_id` e a memória é do framework, não do componente de UI.
"""

from __future__ import annotations

import uuid

import gradio as gr

from src.agent import GoodWeAgent
from src.config import MODELO_PADRAO, MODELOS
from src.knowledge import construir_retriever

EXEMPLOS = [
    "Como inicio uma sessão de carga manualmente para um cliente sem o aplicativo?",
    "O display está piscando E07. O que faço?",
    "Quero cobrar R$ 1,80 por kWh. Como configuro?",
    "Tenho 4 carregadores num quadro de 80A e o disjuntor cai. Como balanceio?",
    "Como gero o relatório de faturamento do mês passado?",
    "Vale a pena financiar mais dois carregadores?",
]


def construir_interface(modelo: str = MODELO_PADRAO):
    retriever = construir_retriever()
    agente = GoodWeAgent(modelo=modelo, retriever=retriever)

    def conversar(mensagem, historico, estado_sessao):
        # O histórico visual vem do Gradio; a memória real é do LangChain.
        resposta = agente.responder(mensagem, session_id=estado_sessao)
        rodape = (
            f"\n\n<sub>⏱ {resposta.latencia_s}s · {resposta.tokens_total} tokens · "
            f"modelo `{resposta.modelo}`"
            + (" · 🛡️ guardrail acionado" if resposta.bloqueado else "")
            + "</sub>"
        )
        return resposta.texto + rodape

    with gr.Blocks(theme=gr.themes.Soft(primary_hue="green", secondary_hue="emerald")) as demo:
        estado_sessao = gr.State(lambda: f"ui_{uuid.uuid4().hex[:8]}")
        gr.Markdown(
            "## 🔌 GoodWe Assist — EV Challenge 2026 · Sprint 03\n"
            "Núcleo conversacional em **LangChain** · memória por sessão nativa · "
            "RAG sobre a documentação GoodWe · guardrails de segurança."
        )
        gr.ChatInterface(
            fn=conversar,
            additional_inputs=[estado_sessao],
            examples=EXEMPLOS,
            cache_examples=False,
        )
        with gr.Accordion("🔎 Memória desta sessão", open=False):
            saida = gr.JSON()
            gr.Button("Inspecionar memória").click(
                lambda s: agente.memoria(s), inputs=[estado_sessao], outputs=[saida]
            )

    return demo


if __name__ == "__main__":
    construir_interface().launch(share=True)
