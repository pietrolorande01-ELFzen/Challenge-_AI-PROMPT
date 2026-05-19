# GoodWe Assist — Chatbot de Operação de Eletropostos Comerciais

## Identificação do Projeto

| Campo | Informação |
|---|---|
| **Projeto** | GoodWe Assist |
| **Desafio** | EV Challenge 2026 — GoodWe / FIAP |
| **Contexto escolhido** | Operação Comercial (ChargeGrid Intelligence) |
| **Sprint** | Sprint 1 — Exploração e Planejamento |

---

## Integrantes

> *(Preencher com nome e RM de cada integrante do grupo)*

| Nome | RM |
|---|---|
| Ana Beatriz Berbel Marini | RM574176 |
| Gustavo Bonamico Piccoli | RM569984 |
| Marcelo Francisco Josafá Ribeiro Martins | RM573905 |
| Maria Eduarda Medeiros Lemos | RM574094 |
| Pietro Lorande da Silva | RM569125 |

---

## Problema Abordado

Os eletropostos comerciais GoodWe operam sem mecanismos integrados capazes de:

- **Orquestrar a potência** disponível entre múltiplos carregadores simultaneamente;
- **Registrar ciclos de carga** de forma rastreável e auditável;
- **Faturar sessões** automaticamente por kWh, tempo ou valor fixo;
- **Comunicar status e alertas** ao operador em tempo real.

Essa lacuna — chamada no desafio de **ChargeGrid Intelligence** — cria gargalos operacionais, perda de receita e experiência degradada para o operador e para o usuário final do posto.

---

## Proposta do Chatbot

O **GoodWe Assist** é um assistente conversacional especializado no contexto de **operação comercial de eletropostos GoodWe**. Ele atua como primeira linha de suporte operacional para o **operador comercial** (gestor de posto de gasolina, estacionamento, shopping ou frota), respondendo perguntas sobre:

- Configuração e gestão de carregadores GoodWe;
- Monitoramento e status de sessões de carga;
- Faturamento, relatórios e exportação de dados;
- Diagnóstico de erros e alertas operacionais;
- Boas práticas de operação e manutenção preventiva.

### Persona Atendida

**Operador comercial** — gestor responsável pela operação diária do eletroposto. Tem conhecimento básico de TI, mas não é técnico especialista. Precisa de respostas diretas, práticas e em português.

### Justificativa da Escolha do Contexto Comercial

O contexto comercial foi escolhido por concentrar o maior volume de dúvidas operacionais recorrentes e por ter impacto direto na geração de receita. Operadores comerciais:

1. Gerenciam múltiplos carregadores simultaneamente;
2. Precisam de respostas rápidas para não interromper o atendimento ao cliente;
3. Não têm tempo (nem perfil técnico) para consultar manuais extensos;
4. Dependem de faturamento correto para viabilidade financeira do posto.

Um chatbot bem calibrado nesse contexto **reduz chamados ao suporte técnico GoodWe, aumenta a autonomia do operador e melhora a disponibilidade dos carregadores**.

---

## Tecnologias Selecionadas

| Componente | Tecnologia | Justificativa |
|---|---|---|
| Modelo de linguagem | **OpenAI GPT-4o** (via API) | Alta qualidade de compreensão contextual em português; suporte nativo a system prompts detalhados; latência adequada para uso conversacional |
| Orquestração | **LangChain (Python)** | Facilita a injeção de contexto, gerenciamento de histórico de conversa e futura integração com RAG |
| Interface (MVP) | **Streamlit** | Prototipagem rápida de interfaces web; sem necessidade de frontend dedicado para a Sprint 2 |
| Armazenamento de contexto | **FAISS + LangChain** | Vetorização do manual GoodWe e FAQs para recuperação semântica (RAG) nas próximas sprints |
| Backend futuro | **FastAPI** | API REST leve para integração com sistemas externos (dashboard GoodWe, notificações) |

### Por que não LLaMA local?

O LLaMA exige infraestrutura GPU dedicada e apresenta desempenho inferior ao GPT-4o em português técnico. Para o MVP de demonstração, a API da OpenAI oferece melhor custo-benefício e qualidade imediata.

---

## Fluxograma

O fluxograma de funcionamento do chatbot está disponível no arquivo [`fluxograma_goodwe_assist.svg`](./fluxograma_goodwe_assist.svg) neste repositório.

**Resumo do fluxo:**
1. Operador digita pergunta na interface;
2. LangChain monta o prompt completo (system prompt + histórico + pergunta);
3. GPT-4o processa e gera resposta contextualizada;
4. Resposta é exibida na interface;
5. Caso o modelo não tenha certeza, redireciona ao suporte GoodWe.

---

## Modelo de Teste

O modelo de teste completo está disponível no arquivo [`modelo_de_teste.md`](./modelo_de_teste.md) neste repositório, contendo 8 pares pergunta/resposta ideal que serão usados como base de avaliação na Sprint 2.

---

## System Prompt

O system prompt base está disponível no arquivo [`system_prompt.md`](./system_prompt.md) neste repositório.

---

## Estrutura do Repositório

```
goodwe-assist/
├── README.md                        ← Este arquivo
├── fluxograma_goodwe_assist.svg     ← Fluxograma do chatbot
├── modelo_de_teste.md               ← 8 pares pergunta/resposta ideal
├── system_prompt.md                 ← Prompt base do modelo
└── docs/
    └── justificativa_tecnica.md     ← Detalhamento das escolhas tecnológicas
```

---

## Próximos Passos (Sprint 2)

- Implementar o chatbot com LangChain + GPT-4o;
- Criar interface Streamlit funcional;
- Executar os testes do modelo de teste e medir acurácia;
- Iniciar a ingestão de documentação GoodWe via RAG.
