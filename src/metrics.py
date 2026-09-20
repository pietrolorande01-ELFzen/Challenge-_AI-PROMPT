"""
Instrumentação de métricas — insumo da tabela antes/depois do relatório.

Mede, por turno: latência (s), tokens de entrada, tokens de saída, tokens totais.
Os tokens vêm de `usage_metadata` quando o provedor reporta; caso contrário é usada
uma estimativa declarada (≈4 caracteres por token), sempre sinalizada em `estimado`.
"""

from __future__ import annotations

import json
import statistics
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class MetricaTurno:
    versao: str                 # "legado" | "sprint3"
    modelo: str
    turno: int
    latencia_s: float
    tokens_entrada: int
    tokens_saida: int
    estimado: bool
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_total(self) -> int:
        return self.tokens_entrada + self.tokens_saida

    def como_dict(self) -> dict:
        d = asdict(self)
        d["tokens_total"] = self.tokens_total
        return d


def estimar_tokens(texto: str) -> int:
    return max(1, round(len(texto or "") / 4))


def extrair_uso(resposta: Any, prompt_texto: str, resposta_texto: str) -> tuple[int, int, bool]:
    """Lê usage_metadata do LangChain; cai para estimativa quando indisponível."""
    uso = getattr(resposta, "usage_metadata", None) or {}
    if not uso:
        meta = getattr(resposta, "response_metadata", {}) or {}
        uso = meta.get("token_usage") or meta.get("usage") or {}

    entrada = uso.get("input_tokens") or uso.get("prompt_tokens")
    saida = uso.get("output_tokens") or uso.get("completion_tokens")

    if entrada and saida:
        return int(entrada), int(saida), False
    return estimar_tokens(prompt_texto), estimar_tokens(resposta_texto), True


@contextmanager
def cronometro():
    inicio = time.perf_counter()
    marcador = {"segundos": 0.0}
    try:
        yield marcador
    finally:
        marcador["segundos"] = round(time.perf_counter() - inicio, 3)


class ColetorMetricas:
    """Acumula métricas de uma execução de eval e consolida os agregados."""

    def __init__(self) -> None:
        self.registros: list[MetricaTurno] = []

    def registrar(self, metrica: MetricaTurno) -> None:
        self.registros.append(metrica)

    def filtrar(self, versao: str | None = None, modelo: str | None = None) -> list[MetricaTurno]:
        return [
            r
            for r in self.registros
            if (versao is None or r.versao == versao) and (modelo is None or r.modelo == modelo)
        ]

    def agregar(self, versao: str | None = None, modelo: str | None = None) -> dict:
        subset = self.filtrar(versao, modelo)
        if not subset:
            return {}
        lat = [r.latencia_s for r in subset]
        tok = [r.tokens_total for r in subset]
        return {
            "versao": versao,
            "modelo": modelo,
            "turnos": len(subset),
            "latencia_media_s": round(statistics.mean(lat), 2),
            "latencia_p95_s": round(sorted(lat)[max(0, int(len(lat) * 0.95) - 1)], 2),
            "tokens_medio_por_turno": round(statistics.mean(tok), 1),
            "tokens_entrada_medio": round(statistics.mean([r.tokens_entrada for r in subset]), 1),
            "tokens_saida_medio": round(statistics.mean([r.tokens_saida for r in subset]), 1),
            "tokens_estimados": any(r.estimado for r in subset),
        }

    def salvar(self, caminho: str | Path) -> Path:
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(
            json.dumps([r.como_dict() for r in self.registros], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return caminho
