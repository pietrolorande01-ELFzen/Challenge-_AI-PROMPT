"""
Configuração central do GoodWe Assist — Sprint 03.

Toda credencial vem de variável de ambiente (.env / Colab Secrets / Kaggle Secrets).
NENHUMA chave é escrita em código ou commitada no repositório.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
RAIZ = Path(__file__).resolve().parent.parent
DIR_DATA = RAIZ / "data"
DIR_RESULTS = RAIZ / "results"
DIR_DOCS = RAIZ / "docs"
DIR_CHROMA = RAIZ / ".chroma"

DIR_RESULTS.mkdir(exist_ok=True)

# Pasta com os PDFs técnicos GoodWe (datasheet, manual, mapa MODBUS).
# Kaggle: /kaggle/input/<dataset>   ·   Colab: /content
PASTA_PDFS = os.environ.get("GOODWE_PDF_DIR", str(DIR_DATA / "pdfs"))


# ──────────────────────────────────────────────────────────────────────────────
# Credenciais — carregadas de forma compatível com .env, Kaggle e Colab
# ──────────────────────────────────────────────────────────────────────────────
def carregar_token(nome: str = "HUGGING_FACE_API_KEY", obrigatorio: bool = True) -> str:
    """Busca o token em: variável de ambiente → .env → Kaggle Secrets → Colab Secrets."""
    token = os.environ.get(nome, "")
    if token:
        return token

    # .env local (não versionado)
    env_file = RAIZ / ".env"
    if env_file.exists():
        for linha in env_file.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, _, valor = linha.partition("=")
            if chave.strip() == nome:
                valor = valor.strip().strip("'\"")
                os.environ[nome] = valor
                return valor

    try:  # Kaggle
        from kaggle_secrets import UserSecretsClient  # type: ignore

        valor = UserSecretsClient().get_secret(nome)
        if valor:
            os.environ[nome] = valor
            return valor
    except Exception:
        pass

    try:  # Colab
        from google.colab import userdata  # type: ignore

        valor = userdata.get(nome)
        if valor:
            os.environ[nome] = valor
            return valor
    except Exception:
        pass

    if obrigatorio:
        raise EnvironmentError(
            f"Credencial '{nome}' não encontrada.\n"
            "Configure via .env (gitignored), Kaggle Secrets ou Colab Secrets. "
            "Nunca escreva a chave no código."
        )
    return ""


# ──────────────────────────────────────────────────────────────────────────────
# Parametrização dos modelos comparados (Bloco B da rubrica)
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class ConfigModelo:
    """Parametrização explícita de cada LLM avaliada."""

    apelido: str
    repo_id: str
    provedor: str = "huggingface"          # huggingface | openai
    temperature: float = 0.2
    top_p: float = 0.9
    max_tokens: int = 600
    repetition_penalty: float = 1.05
    observacao: str = ""

    def como_dict(self) -> dict:
        return asdict(self)


# Grade de modelos usada na comparação. Mínimo exigido: 2 modelos.
MODELOS: dict[str, ConfigModelo] = {
    "qwen": ConfigModelo(
        apelido="qwen",
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        temperature=0.2,
        top_p=0.9,
        max_tokens=600,
        observacao="Modelo usado nas Sprints 1/2 — baseline de continuidade.",
    ),
    "llama": ConfigModelo(
        apelido="llama",
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0.2,
        top_p=0.9,
        max_tokens=600,
        observacao="Candidato alternativo, mesma faixa de custo na Inference API.",
    ),
    "mistral": ConfigModelo(
        apelido="mistral",
        repo_id="mistralai/Mistral-7B-Instruct-v0.3",
        temperature=0.2,
        top_p=0.9,
        max_tokens=600,
        observacao="Terceiro modelo opcional (controle).",
    ),
}

# Varredura de parametrização aplicada ao modelo vencedor (justificar temperature/top_p).
GRADE_PARAMETROS = [
    {"temperature": 0.0, "top_p": 1.0, "max_tokens": 600},
    {"temperature": 0.2, "top_p": 0.9, "max_tokens": 600},
    {"temperature": 0.7, "top_p": 0.95, "max_tokens": 600},
]

MODELO_PADRAO = os.environ.get("GOODWE_MODELO", "qwen")

# RAG
N_RESULTADOS_RAG = 3
TAMANHO_CHUNK = 1000
OVERLAP_CHUNK = 150

# Memória por sessão
MAX_TURNOS_MEMORIA = 6  # pares (user, assistant) mantidos na janela
