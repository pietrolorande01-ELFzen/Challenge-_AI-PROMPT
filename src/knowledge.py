"""
Base de conhecimento (RAG) — agora exposta como *retriever* do LangChain.

Sprint 2: ChromaDB usado direto (colecao.query), acoplado à função do chatbot.
Sprint 03: `Chroma` do langchain-chroma, devolvido como `Retriever`, plugável em
qualquer chain/agent do framework e substituível sem tocar no núcleo conversacional.
"""

from __future__ import annotations

import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    DIR_DATA,
    N_RESULTADOS_RAG,
    OVERLAP_CHUNK,
    PASTA_PDFS,
    TAMANHO_CHUNK,
)

NOME_COLECAO = "base_goodwe_sprint3"


def _carregar_pdfs() -> list[Document]:
    """Lê os PDFs técnicos GoodWe, se estiverem disponíveis no ambiente."""
    pasta = Path(PASTA_PDFS)
    if not pasta.is_dir():
        return []

    from pypdf import PdfReader

    docs: list[Document] = []
    for caminho in sorted(pasta.glob("*.pdf")):
        try:
            leitor = PdfReader(str(caminho))
            texto = "\n".join(p.extract_text() or "" for p in leitor.pages)
        except Exception as erro:  # PDF corrompido não derruba o pipeline
            print(f"  ⚠️  Falha ao ler {caminho.name}: {erro}")
            continue
        if texto.strip():
            docs.append(Document(page_content=texto, metadata={"fonte": caminho.name}))
            print(f"  📄 {caminho.name}: {len(texto)} caracteres")
    return docs


def _carregar_fallback() -> list[Document]:
    """
    Corpus de contingência: notas operacionais consolidadas pelo grupo nas Sprints 1/2.
    Garante que o pipeline e o eval rodem mesmo sem os PDFs montados no ambiente.
    """
    arquivo = DIR_DATA / "base_conhecimento_goodwe.md"
    if not arquivo.exists():
        return []
    texto = arquivo.read_text(encoding="utf-8")
    return [Document(page_content=texto, metadata={"fonte": arquivo.name})]


def construir_retriever(k: int = N_RESULTADOS_RAG, forcar_rebuild: bool = True):
    """Monta o índice vetorial e devolve um retriever pronto para a chain."""
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    docs = _carregar_pdfs()
    origem = "pdfs_tecnicos"
    if not docs:
        docs = _carregar_fallback()
        origem = "corpus_consolidado"
        print("  ℹ️  PDFs não encontrados — usando o corpus consolidado das Sprints 1/2.")

    if not docs:
        raise FileNotFoundError(
            "Nenhuma fonte de conhecimento encontrada. Defina GOODWE_PDF_DIR ou "
            "mantenha data/base_conhecimento_goodwe.md no repositório."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=TAMANHO_CHUNK,
        chunk_overlap=OVERLAP_CHUNK,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = f"chunk_{i:04d}"
        c.metadata["origem"] = origem

    embeddings = HuggingFaceEmbeddings(
        model_name=os.environ.get("GOODWE_EMBEDDING", "sentence-transformers/all-MiniLM-L6-v2")
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=NOME_COLECAO,
    )
    print(f"  ✅ Índice pronto: {len(chunks)} chunks ({origem}).")
    return vectorstore.as_retriever(search_kwargs={"k": k})


def formatar_contexto(docs: list[Document]) -> str:
    """Serializa os documentos recuperados para injeção no prompt."""
    partes = []
    for d in docs:
        fonte = d.metadata.get("fonte", "documentacao_goodwe")
        partes.append(f"<doc fonte=\"{fonte}\">\n{d.page_content.strip()}\n</doc>")
    return "\n\n".join(partes) if partes else "(nenhum trecho relevante recuperado)"
