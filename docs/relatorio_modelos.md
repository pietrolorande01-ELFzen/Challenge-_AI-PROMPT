# Relatório de uso de modelos e parâmetros — Sprint 03

**Projeto:** GoodWe Assist · EV Challenge 2026 — GoodWe / FIAP
**Gerado em:** 2026-09-19

> ⚠️ **Relatório preliminar.** As células numéricas são preenchidas automaticamente após
> `python -m eval.run_eval --tudo && python scripts/gerar_relatorio.py`.

## 1. Modelos avaliados e parametrização

Todos os modelos foram executados **sobre o mesmo pipeline** (mesma chain LangChain, mesmo
retriever, mesmo prompt v3, mesmo eval set das Sprints 1/2). A única variável é a LLM e seus
parâmetros — sem isso a comparação não mediria o modelo, mediria o contexto.

| Modelo | temperature | top_p | max_tokens | repetition_penalty | Observação |
|---|---|---|---|---|---|
| `Qwen/Qwen2.5-7B-Instruct` | 0.2 | 0.9 | 600 | 1.05 | Modelo usado nas Sprints 1/2 — baseline de continuidade. |
| `meta-llama/Llama-3.1-8B-Instruct` | 0.2 | 0.9 | 600 | 1.05 | Candidato alternativo, mesma faixa de custo na Inference API. |

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
| `Qwen/Qwen2.5-7B-Instruct` | — | — | —/— | — | — | — |
| `meta-llama/Llama-3.1-8B-Instruct` | — | — | —/— | — | — | — |

## 3. Varredura de parametrização

Executada no modelo com melhor desempenho, sobre o eval set completo:

| Modelo | temperature | top_p | max_tokens | Nota média | Latência média | Tokens/turno |
|---|---|---|---|---|---|---|
| — | 0.0 | 1.0 | 600 | — | — | — |
| — | 0.2 | 0.9 | 600 | — | — | — |
| — | 0.7 | 0.95 | 600 | — | — | — |

## 4. Seleção justificada

> **Preencher com base nos números acima.** O critério de decisão, definido *antes* da execução
> para não enviesar a leitura, é lexicográfico:
> 1. **Aprovação em segurança** — reprovar em injection ou em recusa de domínio elimina o modelo,
>    por maior que seja a nota de qualidade;
> 2. **Nota média no eval set** — diferença menor que 0,05 é considerada empate;
> 3. **Latência média** — no empate, vence quem responde mais rápido ao operador;
> 4. **Tokens por turno** — critério de desempate final (custo).

**Modelo selecionado:** —
**Parametrização selecionada:** —
**Justificativa:** —

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
