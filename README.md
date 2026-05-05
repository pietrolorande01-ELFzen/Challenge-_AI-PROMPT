#  ChatBot GoodWe — EV Challenge 2026

> Chatbot com IA para suporte operacional em eletropostos e gestão condominial de carregamento veicular.

---

##  Integrantes



##  Problema Abordado

A GoodWe identificou a ausência de mecanismos integrados nos eletropostos para:

- **Orquestrar potência** entre múltiplos veículos conectados simultaneamente
- **Registrar ciclos** de carregamento de forma rastreável
- **Faturar automaticamente** sessões de recarga
- **Comunicar status** do eletroposto em tempo real

Esse conjunto de lacunas se manifesta em dois cenários principais do desafio:

- **ChargeGrid Intelligence**: falta de inteligência para gerenciar eletropostos comerciais
- **EV ChargeOps**: ausência de ferramentas para gestão de carregamento em condomínios residenciais

---

##  Proposta do Chatbot

O chatbot atua como **ferramenta operacional** de suporte para síndicos e moradores em condomínios com infraestrutura de recarga elétrica (contexto EV ChargeOps).

### Persona Atendida: **Síndico / Gestor Condominial**

**Justificativa da escolha:** O síndico é o ponto central de decisão em um condomínio. É quem precisa entender o consumo de energia, aprovar instalações, resolver conflitos de uso entre moradores e prestar contas à administração. Um chatbot que responda dúvidas técnicas e operacionais em linguagem acessível agrega valor direto ao dia a dia dessa persona — sem exigir conhecimento técnico aprofundado.

### O que o chatbot responde:

- Dúvidas sobre consumo e rateio de energia entre moradores
- Orientações sobre regras de uso compartilhado dos carregadores
- Informações sobre status e disponibilidade de eletropostos
- Alertas e relatórios simplificados de uso
- Esclarecimentos sobre o sistema GoodWe e normas aplicáveis

---

##  Tecnologias Selecionadas

| Tecnologia | Função | Justificativa |
|---|---|---|
| **OpenAI API (GPT-4o)** | Modelo de linguagem principal | Alta capacidade de compreensão contextual, boa performance em português, ampla documentação |
| **LangChain** | Orquestração do fluxo conversacional | Facilita injeção de contexto, gerenciamento de histórico e encadeamento de prompts |
| **Python + FastAPI** | Backend da aplicação | Leveza, velocidade de desenvolvimento e fácil integração com a API OpenAI |
| **Streamlit** | Interface de prototipagem | Permite construir e testar o chatbot rapidamente sem frontend complexo |
| **GitHub** | Controle de versão e documentação | Centraliza código, documentação e histórico do projeto |

### Alternativas Consideradas

- **LLaMA 3 (Meta)**: considerado para uso local sem custo de API, mas exige mais infraestrutura
- **Gemini (Google)**: boa performance, mas menor suporte nativo a português técnico
- **Rasa**: mais adequado para fluxos rígidos; descartado pela necessidade de respostas abertas e contextuais

---

##  Fluxograma de Funcionamento

O fluxograma está disponível na pasta `/docs/fluxograma_chatbot_goodwe.png` do repositório.

**Resumo do fluxo:**

1. Usuário envia uma pergunta via interface
2. Sistema verifica se a pergunta é relevante ao contexto GoodWe/EV
3. System prompt com contexto GoodWe é injetado no modelo
4. Persona do usuário é identificada (síndico, morador, técnico)
5. LLM processa a pergunta com o contexto completo
6. Resposta contextualizada é gerada e exibida

---

##  Modelo de Teste

O modelo de teste com 5 perguntas e respostas esperadas está disponível em `/docs/modelo_de_teste.md`.

---

##  Estrutura do Repositório

```
/
├── README.md
├── docs/
│   ├── fluxograma_chatbot_goodwe.png
│   ├── modelo_de_teste.md
│   └── system_prompt.md
└── sprint1/
    └── (código e protótipos virão na Sprint 2)
```

---

##  Sprint Atual

**Sprint 1 — Exploração e Planejamento**

- [x] Definição do problema e escopo
- [x] Escolha da persona (síndico)
- [x] Seleção e justificativa das tecnologias
- [x] Elaboração do fluxograma
- [x] Modelo de teste com 5 perguntas/respostas
- [x] System prompt base

---

##  Contexto Acadêmico

Projeto desenvolvido para o **EV Challenge 2026** em parceria com a **GoodWe** e a **FIAP**.
