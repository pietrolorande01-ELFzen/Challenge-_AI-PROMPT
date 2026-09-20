"""
Memória por sessão — recurso NATIVO do framework (LangChain).

Sprint 2: lista Python `historico` passada manualmente para a função do chatbot e
remontada a cada chamada. Sprint 03: `InMemoryChatMessageHistory` + `RunnableWithMessageHistory`,
com isolamento por `session_id` e janela deslizante via `trim_messages`.
"""

from __future__ import annotations

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, trim_messages

from src.config import MAX_TURNOS_MEMORIA

# Registro de sessões: um histórico isolado por session_id.
_SESSOES: dict[str, InMemoryChatMessageHistory] = {}


def obter_historico(session_id: str) -> BaseChatMessageHistory:
    """Factory exigida por RunnableWithMessageHistory."""
    if session_id not in _SESSOES:
        _SESSOES[session_id] = InMemoryChatMessageHistory()
    return _SESSOES[session_id]


def limpar_sessao(session_id: str) -> None:
    _SESSOES.pop(session_id, None)


def limpar_todas() -> None:
    _SESSOES.clear()


def sessoes_ativas() -> list[str]:
    return list(_SESSOES)


def snapshot(session_id: str) -> list[dict]:
    """Dump legível da memória — usado na demonstração de 3+ turnos."""
    hist = _SESSOES.get(session_id)
    if not hist:
        return []
    return [{"papel": m.type, "conteudo": m.content} for m in hist.messages]


def janela(mensagens: list[BaseMessage], max_turnos: int = MAX_TURNOS_MEMORIA) -> list[BaseMessage]:
    """
    Janela deslizante: mantém apenas os N pares mais recentes.
    Controla o crescimento de tokens por turno sem perder a coerência da conversa.
    """
    return trim_messages(
        mensagens,
        max_tokens=max_turnos * 2,          # contagem por mensagem
        token_counter=len,                  # len(lista) = nº de mensagens
        strategy="last",
        start_on="human",
        include_system=False,
        allow_partial=False,
    )
