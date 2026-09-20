# Escolha do framework de agentes — LangChain

## Decisão

O núcleo conversacional do GoodWe Assist foi reconstruído em **LangChain** (LCEL +
`RunnableWithMessageHistory`), com `InMemoryChatMessageHistory` como memória por sessão e
`Chroma` como retriever.

## Alternativas consideradas

| Framework | A favor | Contra, no nosso caso | Veredito |
|---|---|---|---|
| **LangChain** | Memória por sessão nativa (`RunnableWithMessageHistory`); integração pronta com Chroma e Hugging Face Inference API; troca de provedor sem tocar no núcleo; LCEL permite inserir guardrails como etapas da chain | Curva de aprendizado da API LCEL; mudanças frequentes entre versões menores | **Escolhido** |
| **CrewAI** | Excelente para orquestrar vários agentes com papéis distintos e delegação | Nosso problema é de **um** agente de suporte com RAG e memória; multiagente adicionaria chamadas de LLM (custo e latência) sem ganho de qualidade para o operador | Descartado |
| **Google ADK** | Integração forte com Gemini e com o ecossistema Google Cloud | Amarra o projeto a um provedor; as Sprints 1/2 rodam em Hugging Face Inference API no plano gratuito, e a comparação entre modelos exigida no Bloco B ficaria mais difícil | Descartado |
| **LlamaIndex** | Ótimo em indexação e recuperação | O gargalo da Sprint 2 não era retrieval, e sim memória, escopo e segurança | Descartado |

## Por que LangChain resolve exatamente as dores da Sprint 2

1. **Memória** — na Sprint 2 o histórico era uma lista Python remontada à mão dentro da função do
   chatbot, global para todos os usuários. `RunnableWithMessageHistory` dá isolamento por
   `session_id` e janela deslizante (`trim_messages`) de graça, que é o que a rubrica cobra em
   "memória gerenciada pelo framework".
2. **Composição** — guardrail de entrada, recuperação, higienização de contexto, prompt, LLM e
   guardrail de saída viram etapas explícitas de um pipeline, em vez de um bloco de `if` dentro de
   uma função de 60 linhas.
3. **Comparação entre modelos** — `ChatHuggingFace`, `ChatOpenAI` e afins expõem a mesma interface.
   Trocar de LLM na nossa base é mudar uma entrada do dicionário `MODELOS` em `src/config.py`.
4. **Observabilidade** — `usage_metadata` padronizado nas respostas permitiu instrumentar tokens
   por turno e latência sem gambiarra, que é o insumo da tabela antes/depois.
5. **Continuidade** — LangChain já constava como orquestrador planejado no README da Sprint 1; a
   Sprint 03 cumpre esse plano em vez de trocar de rumo.

## Trade-offs assumidos

- **Peso de dependências.** LangChain + Chroma + sentence-transformers pesam mais que o
  `InferenceClient` puro da Sprint 2. Aceito: o ganho em memória e segurança compensa, e o tempo
  de import não afeta a latência por turno.
- **Acoplamento à API do framework.** `RunnableWithMessageHistory` teve mudanças entre versões
  0.2 e 0.3. Mitigado com versões mínimas fixadas em `requirements.txt` e com a memória isolada em
  `src/memory.py`, um único arquivo a ajustar caso a API mude.
- **Abstração extra no debug.** Um erro dentro da chain gera stack trace mais longo. Mitigado com
  as métricas por turno e o dump de memória (`agente.memoria(session_id)`).
- **Agente sem tool calling.** Optamos por chain determinística em vez de `AgentExecutor` com
  ferramentas: os modelos abertos de 7–8B usados na comparação têm suporte irregular a function
  calling, e um loop de ferramentas aumentaria latência e chance de alucinação sem trazer ganho
  para o caso de uso do operador.
