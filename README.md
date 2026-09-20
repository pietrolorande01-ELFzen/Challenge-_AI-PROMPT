# GoodWe Assist — Sprint 03

Chatbot de operação de eletropostos comerciais GoodWe, com núcleo conversacional reconstruído em
**framework de agentes (LangChain)**, memória por sessão nativa, guardrails de segurança e
avaliação reprodutível.

| Campo | Informação |
|---|---|
| Projeto | GoodWe Assist |
| Desafio | EV Challenge 2026 — GoodWe / FIAP |
| Contexto | Operação Comercial — ChargeGrid Intelligence |
| Persona | Operador comercial de eletroposto |
| Disciplina | Prompt and Artificial Intelligence — 1º ano Ciência da Computação — 2026.2 |
| Sprint | 03 — Refactory conversacional com framework de agentes |
| Framework | LangChain (LCEL + `RunnableWithMessageHistory`) |
| Modelos avaliados | `Qwen/Qwen2.5-7B-Instruct` · `meta-llama/Llama-3.1-8B-Instruct` |

## Integrantes

| Nome | RM |
|---|---|
| Ana Beatriz Berbel Marini | 574176 |
| Gustavo Bonamico Piccoli | 569984 |
| Julian Nayde Moncoski | 572603 |
| Marcelo Francisco Josafá Ribeiro Martins | 573905 |
| Maria Eduarda Medeiros Lemos | 574094 |
| Pietro Lorande da Silva | 569125 |

---

## O que mudou em relação às Sprints 1 e 2

| | Sprints 1/2 | Sprint 03 |
|---|---|---|
| Núcleo conversacional | `InferenceClient` chamado direto, sem framework | Chain LangChain (LCEL) |
| Memória | Lista Python global remontada a cada chamada | `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` por `session_id`, com janela deslizante |
| RAG | `colecao.query` dentro da função do chatbot | `Chroma` exposto como retriever injetável |
| Segurança | Nenhuma camada dedicada | 3 camadas de guardrail + 11 casos de teste |
| Avaliação | Tabela markdown preenchida à mão | `eval/run_eval.py` — nota determinística, latência e tokens por turno |
| Modelos | Um modelo fixo | Grade de modelos e varredura de parametrização |

O comparativo com os números medidos está em
[`docs/relatorio_evolucao_sprint03.pdf`](docs/relatorio_evolucao_sprint03.pdf).

## Arquitetura

```
pergunta do operador
   │
   ├─► Guardrail de entrada ──(injection conhecida)──► resposta canônica  ✋ LLM nem é chamada
   │        separa instrução × conteúdo colado
   │
   ├─► Retriever Chroma (k=3) ──► higienização do contexto
   │
   ├─► Prompt v3  +  Memória da sessão (LangChain)
   │
   ├─► LLM parametrizada (temperature · top_p · max_tokens)
   │        instrumentação: latência e tokens
   │
   └─► Guardrail de saída ──► resposta + gravação na memória da sessão
```

## Estrutura do repositório

```
├── src/
│   ├── agent.py        núcleo conversacional (chain + memória + guardrails + métricas)
│   ├── memory.py       memória por sessão gerenciada pelo framework
│   ├── guardrails.py   validação determinística de entrada e saída
│   ├── knowledge.py    RAG: indexação Chroma e retriever
│   ├── prompts.py      system prompt v3 (escopo, recusas, segurança)
│   ├── metrics.py      latência e tokens por turno
│   ├── config.py       modelos, parâmetros e carregamento seguro de credenciais
│   └── app.py          interface Gradio
├── legacy/chat_manual.py     baseline das Sprints 1/2, para o comparativo antes/depois
├── eval/
│   ├── eval_set.py     os mesmos 8 casos da Sprint 1 + roteiro de memória
│   ├── security_set.py 11 casos de segurança (injection, recusas, escopo)
│   ├── scoring.py      nota determinística 0 / 0,5 / 1
│   └── run_eval.py     runner que gera todas as evidências
├── scripts/gerar_relatorio.py   preenche os relatórios com os números medidos
├── docs/               relatórios e justificativas
├── data/               corpus de contingência do RAG
├── results/            saídas do eval (JSON)
└── notebooks/GoodWe_Sprint03.ipynb   demonstração executável ponta a ponta
```

## Como executar

### 1. Instalar

```bash
pip install -r requirements.txt
cp .env.example .env     # preencha HUGGING_FACE_API_KEY
```

No Colab ou Kaggle, use Secrets em vez do `.env` — o carregamento é automático
(`src/config.py::carregar_token`). **Nunca escreva a chave no código.**

### 2. Base de conhecimento (opcional)

```bash
export GOODWE_PDF_DIR=/caminho/para/os/pdfs   # Kaggle: /kaggle/input/<dataset> · Colab: /content
```

Sem os PDFs, o pipeline usa `data/base_conhecimento_goodwe.md`, o corpus consolidado das
Sprints 1/2, e segue rodando.

### 3. Conversar

```bash
python -m src.app          # interface Gradio
```

### 4. Rodar o eval completo

```bash
python -m eval.run_eval --tudo --modelos qwen llama
python -m eval.run_eval --parametros qwen
python scripts/gerar_relatorio.py
```

O primeiro comando gera `results/*.json`; o último preenche
`docs/relatorio_modelos.md` e `docs/relatorio_evolucao_sprint03.pdf` com os números medidos.

> A Inference API gratuita tem rate-limit. O runner já pausa 5 s entre casos e faz retry com
> back-off, mas o eval completo leva alguns minutos. Se cair no meio, os blocos já concluídos
> continuam salvos em `results/` e podem ser reexecutados individualmente
> (`--seguranca`, `--memoria`, `--parametros`).

## Documentação

- [`docs/justificativa_framework.md`](docs/justificativa_framework.md) — por que LangChain, e o que foi descartado
- [`docs/seguranca_guardrails.md`](docs/seguranca_guardrails.md) — arquitetura de guardrails e os 11 casos de teste
- [`docs/relatorio_modelos.md`](docs/relatorio_modelos.md) — comparação entre modelos e parametrização
- [`docs/relatorio_evolucao_sprint03.pdf`](docs/relatorio_evolucao_sprint03.pdf) — relatório de evolução (entrega obrigatória)

## Segurança de credenciais

`.env` está no `.gitignore`; o repositório traz apenas `.env.example`. Antes de cada push:

```bash
git grep -nE "hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}" && echo "⚠️ CREDENCIAL EXPOSTA"
```
