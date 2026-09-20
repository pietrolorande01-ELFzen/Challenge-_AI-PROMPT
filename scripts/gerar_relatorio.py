#!/usr/bin/env python3
"""
Gera os relatórios da Sprint 03 a partir de results/consolidado.json.

    python scripts/gerar_relatorio.py

Saídas:
    docs/relatorio_modelos.md              (Bloco B — comparação entre modelos)
    docs/relatorio_evolucao_sprint03.md    (Bloco D — fonte do PDF)
    docs/relatorio_evolucao_sprint03.pdf   (entregue junto do repositório)

Sem os resultados do eval, as células numéricas saem como «—» e o relatório fica
marcado como PRELIMINAR. Depois de rodar `python -m eval.run_eval --tudo`, basta
executar este script de novo para que as tabelas sejam preenchidas com os números
medidos na execução.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

DIR_RESULTS = RAIZ / "results"
DIR_DOCS = RAIZ / "docs"
VAZIO = "—"

EQUIPE = [
    ("Ana Beatriz Berbel Marini", "574176"),
    ("Gustavo Bonamico Piccoli", "569984"),
    ("Julian Nayde Moncoski", "572603"),
    ("Marcelo Francisco Josafá Ribeiro Martins", "573905"),
    ("Maria Eduarda Medeiros Lemos", "574094"),
    ("Pietro Lorande da Silva", "569125"),
]

TAREFAS = {
    "574176": "Guardrails e casos de teste de segurança (S01–S11); documento `seguranca_guardrails.md`",
    "569984": "Migração do RAG para retriever LangChain, indexação Chroma e corpus de contingência",
    "572603": "Memória por sessão (`RunnableWithMessageHistory`), janela deslizante e demonstração de 3+ turnos",
    "573905": "Comparação entre modelos, varredura de parametrização e `relatorio_modelos.md`",
    "574094": "Eval set reexecutado, scoring reprodutível e instrumentação de métricas (latência/tokens)",
    "569125": "Arquitetura da chain, refactory do núcleo conversacional, interface Gradio e integração do repositório",
}


def carregar(nome: str):
    caminho = DIR_RESULTS / nome
    if not caminho.exists():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def val(dic, *chaves, sufixo=""):
    atual = dic
    for c in chaves:
        if not isinstance(atual, dict) or c not in atual:
            return VAZIO
        atual = atual[c]
    if atual is None:
        return VAZIO
    return f"{atual}{sufixo}"


# ──────────────────────────────────────────────────────────────────────────────
def gerar_relatorio_modelos(cons: dict) -> str:
    from src.config import GRADE_PARAMETROS, MODELOS

    qual = cons.get("qualidade", {}) if cons else {}
    seg = cons.get("seguranca", {}) if cons else {}
    modelos = (cons or {}).get("modelos_testados", ["qwen", "llama"])

    linhas_param = "\n".join(
        f"| `{MODELOS[m].repo_id}` | {MODELOS[m].temperature} | {MODELOS[m].top_p} | "
        f"{MODELOS[m].max_tokens} | {MODELOS[m].repetition_penalty} | {MODELOS[m].observacao} |"
        for m in modelos
        if m in MODELOS
    )

    linhas_result = "\n".join(
        f"| `{MODELOS[m].repo_id}` | {val(qual, m, 'nota_media')} | {val(qual, m, 'percentual', sufixo='%')} | "
        f"{val(qual, m, 'corretos')}/{val(qual, m, 'casos')} | {val(qual, m, 'latencia_media_s', sufixo=' s')} | "
        f"{val(qual, m, 'tokens_medio_por_turno')} | {val(seg, m, 'taxa_aprovacao', sufixo='%')} |"
        for m in modelos
        if m in MODELOS
    )

    varreduras = ((cons or {}).get("parametros") or {})
    linhas_varredura = []
    for modelo, dados in varreduras.items():
        for item in dados.get("varreduras", []):
            p, r = item["parametros"], item["resumo"]
            linhas_varredura.append(
                f"| `{modelo}` | {p['temperature']} | {p['top_p']} | {p['max_tokens']} | "
                f"{r.get('nota_media', VAZIO)} | {r.get('latencia_media_s', VAZIO)} s | "
                f"{r.get('tokens_medio_por_turno', VAZIO)} |"
            )
    if not linhas_varredura:
        linhas_varredura = [
            f"| {VAZIO} | {g['temperature']} | {g['top_p']} | {g['max_tokens']} | {VAZIO} | {VAZIO} | {VAZIO} |"
            for g in GRADE_PARAMETROS
        ]

    status = "" if cons else (
        "> ⚠️ **Relatório preliminar.** As células numéricas são preenchidas automaticamente após\n"
        "> `python -m eval.run_eval --tudo && python scripts/gerar_relatorio.py`.\n\n"
    )

    return f"""# Relatório de uso de modelos e parâmetros — Sprint 03

**Projeto:** GoodWe Assist · EV Challenge 2026 — GoodWe / FIAP
**Gerado em:** {date.today().isoformat()}

{status}## 1. Modelos avaliados e parametrização

Todos os modelos foram executados **sobre o mesmo pipeline** (mesma chain LangChain, mesmo
retriever, mesmo prompt v3, mesmo eval set das Sprints 1/2). A única variável é a LLM e seus
parâmetros — sem isso a comparação não mediria o modelo, mediria o contexto.

| Modelo | temperature | top_p | max_tokens | repetition_penalty | Observação |
|---|---|---|---|---|---|
{linhas_param}

**Por que esses parâmetros como ponto de partida**

- `temperature = 0.2` — suporte operacional é tarefa determinística: o mesmo erro E07 deve gerar
  o mesmo procedimento. Temperatura alta produz variação de passo a passo, que é exatamente o que
  confunde o operador.
- `top_p = 0.9` — corta a cauda de tokens improváveis (origem das alucinações de código de erro e
  de nome de menu) sem engessar a redação.
- `max_tokens = 600` — os procedimentos do eval set cabem com folga em 600 tokens; acima disso o
  modelo passa a repetir avisos e o custo por turno sobe sem ganho de nota.
- `repetition_penalty = 1.05` — leve, só para conter a repetição de blocos de aviso observada nos
  modelos abertos de 7B.

## 2. Resultados por modelo

| Modelo | Nota média (0–1) | % do eval | Respostas corretas | Latência média | Tokens/turno | Aprovação em segurança |
|---|---|---|---|---|---|---|
{linhas_result}

## 3. Varredura de parametrização

Executada no modelo com melhor desempenho, sobre o eval set completo:

| Modelo | temperature | top_p | max_tokens | Nota média | Latência média | Tokens/turno |
|---|---|---|---|---|---|---|
{chr(10).join(linhas_varredura)}

## 4. Seleção justificada

> **Preencher com base nos números acima.** O critério de decisão, definido *antes* da execução
> para não enviesar a leitura, é lexicográfico:
> 1. **Aprovação em segurança** — reprovar em injection ou em recusa de domínio elimina o modelo,
>    por maior que seja a nota de qualidade;
> 2. **Nota média no eval set** — diferença menor que 0,05 é considerada empate;
> 3. **Latência média** — no empate, vence quem responde mais rápido ao operador;
> 4. **Tokens por turno** — critério de desempate final (custo).

**Modelo selecionado:** {VAZIO}
**Parametrização selecionada:** {VAZIO}
**Justificativa:** {VAZIO}

## 5. Reprodutibilidade

```bash
pip install -r requirements.txt
export HUGGING_FACE_API_KEY=...        # ou .env / Colab Secrets / Kaggle Secrets
python -m eval.run_eval --tudo --modelos qwen llama
python -m eval.run_eval --parametros qwen
python scripts/gerar_relatorio.py
```

Evidências brutas (resposta completa de cada caso, por modelo): `results/qualidade_*.json`,
`results/seguranca_*.json`, `results/parametros_*.json`, `results/metricas_brutas.json`.

**Nota sobre a contagem de tokens:** quando o provedor não devolve `usage_metadata`, a contagem é
estimada em ≈4 caracteres por token e o campo `tokens_estimados` fica `true` no JSON. A estimativa
é a mesma para as duas versões comparadas, então a variação relativa continua válida.
"""


# ──────────────────────────────────────────────────────────────────────────────
def gerar_relatorio_evolucao(cons: dict) -> str:
    qual = (cons or {}).get("qualidade", {})
    seg = (cons or {}).get("seguranca", {})
    mem = (cons or {}).get("memoria", {})
    principal = ((cons or {}).get("modelos_testados") or ["qwen"])[0]

    leg_q, nov_q = qual.get("legado", {}), qual.get(principal, {})
    leg_s, nov_s = seg.get("legado", {}), seg.get(principal, {})
    mem_p = mem.get(principal, {})

    def par(dic, *ch, sufixo=""):
        return val(dic, *ch, sufixo=sufixo)

    memoria_ok = mem_p.get("memoria_recuperou_contexto")
    memoria_txt = VAZIO if memoria_ok is None else ("sim" if memoria_ok else "não")
    isolou = mem_p.get("sessoes_isoladas")
    isolou_txt = VAZIO if isolou is None else ("sim" if isolou else "não")

    equipe_md = "\n".join(
        f"| {nome} | {rm} | {TAREFAS[rm]} |" for nome, rm in EQUIPE
    )

    status = "" if cons else (
        "> ⚠️ **Versão preliminar.** As células numéricas da tabela antes/depois são preenchidas\n"
        "> automaticamente por `scripts/gerar_relatorio.py` depois de `python -m eval.run_eval --tudo`.\n\n"
    )

    return f"""# Relatório de evolução do projeto — Sprint 03

**GoodWe Assist · EV Challenge 2026 — GoodWe / FIAP** · {date.today().strftime('%d/%m/%Y')}

| | |
|---|---|
| **Projeto** | GoodWe Assist — chatbot de operação de eletropostos comerciais GoodWe |
| **Contexto do desafio** | ChargeGrid Intelligence |
| **Persona atendida** | Operador comercial de eletroposto |
| **Disciplina** | Prompt and Artificial Intelligence — 1º ano Ciência da Computação — 2026.2 |
| **Modelo principal avaliado** | `{principal}` |

{status}## 1. Resumo da evolução

**O que existia nas Sprints 1 e 2.** Um chatbot funcional em notebook: RAG com ChromaDB sobre três
PDFs técnicos GoodWe, system prompt com few-shot injetado manualmente, chamada direta ao
`InferenceClient` da Hugging Face (Qwen2.5-7B-Instruct) e interface Gradio. A memória era uma lista
Python de tuplas `(pergunta, resposta)` remontada a cada chamada dentro da própria função do
chatbot, sem isolamento entre usuários. Não havia camada de segurança: a única proteção era a frase
"se não souber, indique o suporte" dentro do prompt. A avaliação era manual — uma tabela markdown
preenchida a olho depois de rodar 4 casos.

**O que existe agora na Sprint 03.** O núcleo conversacional foi reconstruído em **LangChain**
(LCEL + `RunnableWithMessageHistory`), com quatro mudanças estruturais:

1. **Memória gerenciada pelo framework** — `InMemoryChatMessageHistory` por `session_id`, com
   janela deslizante via `trim_messages`. Sessões diferentes não enxergam uma à outra.
2. **Guardrails em três camadas** — validação determinística antes e depois da LLM, mais regras
   imutáveis no prompt v3, cobrindo prompt injection (inclusive indireta, via documento colado),
   escopo GoodWe e recusas de domínio jurídico, financeiro e de segurança elétrica.
3. **Avaliação reprodutível** — o mesmo eval set das Sprints 1/2 virou código, com nota
   determinística (0 / 0,5 / 1), 11 casos de segurança e instrumentação de latência e tokens por
   turno.
4. **Comparação entre modelos** — a LLM virou configuração; dois modelos e três parametrizações
   passam pelo mesmo pipeline e geram os JSON que alimentam este relatório.

## 2. Refatoração — decisões técnicas e trade-offs

**Framework escolhido: LangChain.** Detalhamento completo em `docs/justificativa_framework.md`.
Em resumo: CrewAI resolveria orquestração multiagente, que não é o nosso problema — temos um
agente de suporte com RAG e memória, e agentes extras só adicionariam chamadas de LLM, latência e
superfície de alucinação. O Google ADK amarraria o projeto ao Gemini e atrapalharia justamente o
Bloco B, que exige comparar modelos. LangChain entrega memória por sessão nativa, retriever
plugável e interface uniforme entre provedores.

**Decisões de arquitetura e o que custaram:**

- *Chain determinística em vez de `AgentExecutor` com ferramentas.* Modelos abertos de 7–8B têm
  suporte irregular a function calling; um loop de ferramentas traria latência e erro sem ganho
  para o operador. Custo: se no futuro entrar consulta a API real de sessões, será preciso migrar
  para um executor com tools.
- *Guardrail determinístico antes da LLM.* Ataque de injeção conhecido nem chega ao modelo:
  resposta canônica, zero token gasto, comportamento idêntico em qualquer LLM. Custo: regex tem
  falso positivo; mitigado pela separação entre instrução e conteúdo colado, para não bloquear o
  operador que cola um relatório de cliente.
- *Retriever em vez de `colecao.query` direto.* A base de conhecimento virou dependência injetada:
  o eval roda o legado e a versão nova sobre o **mesmo** retriever, o que garante que a tabela
  antes/depois meça o refactory e não a diferença de indexação. Custo: uma camada a mais de
  abstração no debug.
- *Corpus de contingência versionado.* Os PDFs GoodWe não estão no repositório. Sem eles o eval
  não rodaria em outra máquina, então `data/base_conhecimento_goodwe.md` consolida as notas
  operacionais das Sprints 1/2 e entra como fonte de fallback, sempre identificada na metadata do
  chunk.
- *Nota determinística no eval.* Trocamos o julgamento humano por cobertura de termos obrigatórios
  e ausência de termos proibidos. Custo: o critério é mais rígido que um avaliador humano e pode
  punir uma resposta certa escrita com sinônimos; ganho: qualquer pessoa reexecuta e obtém o mesmo
  número.

## 3. Tabela de comparativo antes/depois

Mesmo eval set (8 casos das Sprints 1/2), mesmo retriever, mesmo modelo
(`{principal}`), executados na mesma sessão de testes.

| Métrica | Sprints 1/2 (versão manual/legado) | Sprint 03 (framework de agentes) |
|---|---|---|
| Framework do núcleo conversacional | Nenhum — `InferenceClient` direto | LangChain (LCEL + `RunnableWithMessageHistory`) |
| Gestão de memória | Lista Python global, remontada a cada chamada | Memória nativa por `session_id` + janela deslizante |
| **Qualidade das respostas — nota média no eval (0–1)** | {par(leg_q, 'nota_media')} | {par(nov_q, 'nota_media')} |
| **Qualidade — % do eval set** | {par(leg_q, 'percentual', sufixo='%')} | {par(nov_q, 'percentual', sufixo='%')} |
| Respostas corretas / parciais / incorretas | {par(leg_q, 'corretos')} / {par(leg_q, 'parciais')} / {par(leg_q, 'incorretos')} | {par(nov_q, 'corretos')} / {par(nov_q, 'parciais')} / {par(nov_q, 'incorretos')} |
| **Tokens por turno (média)** | {par(leg_q, 'tokens_medio_por_turno')} | {par(nov_q, 'tokens_medio_por_turno')} |
| **Latência média por turno** | {par(leg_q, 'latencia_media_s', sufixo=' s')} | {par(nov_q, 'latencia_media_s', sufixo=' s')} |
| Latência p95 | {par(leg_q, 'latencia_p95_s', sufixo=' s')} | {par(nov_q, 'latencia_p95_s', sufixo=' s')} |
| **Testes de segurança — casos aprovados** | {par(leg_s, 'aprovados')} / {par(leg_s, 'casos')} | {par(nov_s, 'aprovados')} / {par(nov_s, 'casos')} |
| **Testes de segurança — taxa de aprovação** | {par(leg_s, 'taxa_aprovacao', sufixo='%')} | {par(nov_s, 'taxa_aprovacao', sufixo='%')} |
| Ataques barrados antes de chegar à LLM | 0 (não havia camada) | {par(nov_s, 'bloqueios_deterministicos')} |
| Memória: recupera contexto no 4º turno | Não testado | {memoria_txt} |
| Memória: isolamento entre sessões | Inexistente (histórico global) | {isolou_txt} |
| Cobertura de testes automatizados | 4 casos executados manualmente | 8 casos de qualidade + 11 de segurança + 1 roteiro de memória, via `eval/run_eval.py` |

Evidências brutas de cada célula: `results/*.json`.

## 4. Problemas encontrados e soluções

**Problema 1 — Falso positivo do guardrail em documento colado.**
A primeira versão do detector bloqueava qualquer mensagem contendo "ignore as instruções". Na
prática, o operador cola relatórios e e-mails de cliente na conversa; um cliente mal-intencionado
(ou só um texto estranho) derrubaria o atendimento legítimo. *Decisão:* separar a mensagem em
instrução do usuário e conteúdo colado (blocos delimitados por crase tripla, `--- ---`, aspas
triplas ou `<doc>`) e rodar a detecção de injeção apenas sobre a instrução. Payload dentro do bloco
colado passa a **sinalizar** — o pedido legítimo é atendido e o modelo recebe o aviso de tratar
aquilo como dado. *Porquê:* bloquear o trabalho do operador é um custo real e recorrente;
a injeção indireta se resolve com neutralização, não com recusa.

**Problema 2 — Avaliação da Sprint 2 não era comparável.**
A tabela de resultados da Sprint 2 era preenchida à mão, com um caso marcado "✅/⚠️" porque a
resposta variava entre execuções. Não dá para montar uma tabela antes/depois em cima disso.
*Decisão:* transformar cada caso do eval set em dados verificáveis (grupos de termos obrigatórios e
lista de termos proibidos) e calcular a nota por cobertura, mantendo a escala 0 / 0,5 / 1 da
Sprint 1. *Porquê:* o Bloco D exige evidência, e evidência precisa ser reexecutável por terceiros.

**Problema 3 — Instabilidade e rate-limit da Inference API gratuita.**
Já tinha aparecido na Sprint 2 (respostas truncadas, caracteres fora do idioma no primeiro turno,
HTTP 429 entre chamadas). Com dois modelos e três parametrizações, o volume de chamadas do eval
multiplicou. *Decisão:* manter o retry com back-off herdado da Sprint 2, pausar 5 s entre casos,
persistir cada bloco de resultado em JSON assim que termina e tornar o runner parcial
(`--seguranca`, `--memoria`, `--parametros`), para que uma falha no meio não obrigue a refazer tudo.
*Porquê:* eval que não termina não vira evidência.

**Problema 4 — Ausência dos PDFs quebrava o pipeline fora do Kaggle.**
O caminho dos PDFs estava fixo no notebook da Sprint 2 e o notebook não rodava no Colab nem
localmente. *Decisão:* `GOODWE_PDF_DIR` por variável de ambiente, varredura da pasta em vez de
nomes fixos de arquivo, e corpus de contingência versionado. *Porquê:* o professor precisa
conseguir executar o repositório sem montar o dataset.

## 5. Equipe e divisão do trabalho

| Nome | RM | Tarefa principal |
|---|---|---|
{equipe_md}

Histórico Git com commits regulares de cada integrante, conforme as condições de entrega.
"""


# ──────────────────────────────────────────────────────────────────────────────
def markdown_para_pdf(caminho_md: Path, caminho_pdf: Path) -> bool:
    """Converte via pandoc + wkhtmltopdf (HTML intermediário, para as tabelas renderizarem bem)."""
    css = caminho_md.parent / "_relatorio.css"
    css.write_text(
        """
        @page { size: A4; margin: 18mm 16mm; }
        body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 9.5pt; line-height: 1.38; color: #1a1a1a; }
        h1 { font-size: 16pt; color: #14315c; border-bottom: 2px solid #14315c; padding-bottom: 4px; }
        h2 { font-size: 12pt; color: #14315c; margin-top: 14px; }
        h3 { font-size: 10.5pt; }
        table { border-collapse: collapse; width: 100%; font-size: 8.3pt; margin: 8px 0; }
        th { background: #14315c; color: #fff; text-align: left; }
        th, td { border: 1px solid #b9c2cf; padding: 3.5px 5px; vertical-align: top; }
        tr:nth-child(even) td { background: #f4f6f9; }
        code { background: #eef1f5; padding: 0 2px; font-size: 8.3pt; }
        blockquote { border-left: 3px solid #d0a215; background: #fdf8e8; padding: 4px 10px; margin: 8px 0; }
        p, li { margin: 3px 0; }
        """,
        encoding="utf-8",
    )
    html = caminho_md.with_suffix(".html")
    try:
        subprocess.run(
            ["pandoc", str(caminho_md), "-s", "--css", css.name, "-o", str(html), "--metadata", "lang=pt-BR"],
            check=True, cwd=caminho_md.parent,
        )
        subprocess.run(
            ["wkhtmltopdf", "--enable-local-file-access", "--encoding", "utf-8",
             "--margin-top", "14mm", "--margin-bottom", "14mm", str(html), str(caminho_pdf)],
            check=True, cwd=caminho_md.parent,
        )
        html.unlink(missing_ok=True)
        css.unlink(missing_ok=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as erro:
        print(f"  ⚠️  Conversão para PDF indisponível ({erro}). O markdown foi gerado normalmente.")
        return False


def main() -> None:
    cons = carregar("consolidado.json")
    if cons is None:
        print("ℹ️  results/consolidado.json não encontrado — gerando versão PRELIMINAR.")

    DIR_DOCS.mkdir(exist_ok=True)

    md_modelos = DIR_DOCS / "relatorio_modelos.md"
    md_modelos.write_text(gerar_relatorio_modelos(cons), encoding="utf-8")
    print(f"  ✅ {md_modelos}")

    md_evolucao = DIR_DOCS / "relatorio_evolucao_sprint03.md"
    md_evolucao.write_text(gerar_relatorio_evolucao(cons), encoding="utf-8")
    print(f"  ✅ {md_evolucao}")

    pdf = DIR_DOCS / "relatorio_evolucao_sprint03.pdf"
    if markdown_para_pdf(md_evolucao, pdf):
        print(f"  ✅ {pdf}")


if __name__ == "__main__":
    main()
