# Modelo de Teste — GoodWe Assist
## Sprint 1 | Contexto: Operação Comercial de Eletropostos

Este documento define os pares pergunta/resposta ideal que serão utilizados como base de avaliação na Sprint 2. Os critérios de avaliação são: **precisão técnica**, **clareza da resposta**, **tom adequado à persona** e **ausência de alucinações**.

---

## Critérios de Avaliação da Resposta

| Critério | Descrição | Peso |
|---|---|---|
| Precisão | A resposta é tecnicamente correta? | 40% |
| Clareza | A resposta é compreensível para o operador? | 25% |
| Tom | A resposta é direta, em português, sem jargões excessivos? | 20% |
| Segurança | O modelo não inventou informações? | 15% |

**Escala de pontuação por pergunta:** 0 (errado) / 0,5 (parcialmente correto) / 1 (correto)

---

## Perguntas e Respostas Esperadas

---

### Teste 01 — Início de sessão de carga

**Pergunta do operador:**
> "Como eu inicio uma sessão de carga manualmente para um cliente que não tem o aplicativo?"

**Resposta ideal esperada:**

Para iniciar uma sessão manualmente sem o aplicativo GoodWe Charge, siga os passos:

1. Acesse o **portal GoodWe Cloud** (cloud.goodwe.com) com seu login de operador.
2. No menu lateral, vá em **Gerenciamento de Carregadores → Sessões**.
3. Selecione o carregador desejado e clique em **"Iniciar Sessão Manual"**.
4. Informe o conector a ser liberado (ex: Conector A ou B).
5. Confirme — a sessão será iniciada em até 10 segundos.

Alternativamente, se o carregador tiver **cartão RFID master**, passe o cartão de administrador diretamente no leitor do equipamento para liberação imediata.

---

### Teste 02 — Código de erro operacional

**Pergunta do operador:**
> "O carregador está travado com o display piscando 'E07'. O que significa e como resolvo?"

**Resposta ideal esperada:**

O código **E07** indica falha no módulo de medição de energia (energy meter fault). Isso geralmente ocorre por:

- Surto de tensão na rede elétrica;
- Cabo interno frouxo após vibração;
- Defeito no medidor interno.

**Passos para resolução:**

1. Desligue o disjuntor dedicado do carregador por 30 segundos e religue.
2. Aguarde o equipamento reiniciar completamente (aprox. 2 minutos).
3. Verifique se o erro persiste no display.
4. Se persistir, **não tente abrir o equipamento**. Acesse support.goodwe.com, abra um chamado com o número de série (etiqueta na lateral do equipamento) e informe o código E07.

---

### Teste 03 — Configuração de faturamento

**Pergunta do operador:**
> "Quero cobrar R$ 1,80 por kWh. Como configuro o preço no sistema?"

**Resposta ideal esperada:**

Para configurar o preço por kWh:

1. Acesse o **portal GoodWe Cloud** como administrador.
2. Vá em **Configurações → Tarifas e Faturamento**.
3. Selecione o carregador ou grupo de carregadores que deseja configurar.
4. Em **"Modelo de cobrança"**, selecione **"Por kWh consumido"**.
5. Insira o valor **1.80** no campo "Preço por kWh (R$)".
6. Defina a moeda (BRL) e salve.

A nova tarifa entra em vigor na próxima sessão iniciada após salvar. Sessões em andamento mantêm o preço anterior.

---

### Teste 04 — Relatório de faturamento

**Pergunta do operador:**
> "Preciso gerar um relatório do mês passado com todas as sessões e o valor faturado. Como faço?"

**Resposta ideal esperada:**

Para gerar o relatório mensal:

1. No **portal GoodWe Cloud**, acesse **Relatórios → Sessões de Carga**.
2. Filtre por período: selecione o mês anterior (ex: 01/05/2026 a 31/05/2026).
3. Selecione todos os carregadores ou um específico.
4. Clique em **"Gerar Relatório"**.
5. O relatório exibirá: data/hora de cada sessão, energia consumida (kWh), duração e valor faturado.
6. Para exportar, clique em **"Exportar CSV"** ou **"Exportar PDF"**.

O arquivo será enviado para o e-mail cadastrado do operador em até 5 minutos.

---

### Teste 05 — Balanceamento de carga

**Pergunta do operador:**
> "Tenho 4 carregadores ligados no mesmo quadro de 80A. Às vezes o disjuntor cai. Como configuro o balanceamento?"

**Resposta ideal esperada:**

Esse problema é resolvido com o **Load Balancing (Balanceamento de Carga Dinâmico)** da GoodWe. Siga os passos:

1. Acesse **Configurações → Grupos de Carregadores** no portal GoodWe Cloud.
2. Crie um **grupo** e adicione os 4 carregadores ao mesmo grupo.
3. No campo **"Corrente máxima do grupo (A)"**, insira **75A** (deixe 5A de margem de segurança).
4. Ative a opção **"Balanceamento dinâmico ativo"**.
5. Salve.

Com isso, o sistema distribuirá automaticamente a corrente disponível entre os carregadores ativos. Se 4 veículos estiverem carregando simultaneamente, cada um receberá ~18,75A. Se apenas 1 estiver carregando, ele pode usar até 75A.

---

### Teste 06 — Reset e reinicialização

**Pergunta do operador:**
> "O carregador parou de aparecer no meu painel do GoodWe Cloud. Como revinculo ele ao sistema?"

**Resposta ideal esperada:**

Para revincular o carregador ao GoodWe Cloud:

1. No próprio carregador, acesse o menu de configurações (botão lateral por 5 segundos).
2. Vá em **Rede → Wi-Fi** (ou Ethernet) e confirme que o equipamento está conectado.
3. No portal GoodWe Cloud, vá em **Carregadores → Adicionar Dispositivo**.
4. Insira o **número de série** (S/N) que está na etiqueta lateral do equipamento.
5. Confirme o código de pareamento exibido no display do carregador.

Se o equipamento não aparecer após 5 minutos, realize um **reset de fábrica** (atenção: apaga as configurações locais):
- Pressione e segure o botão de reset por 10 segundos até o display piscar 3 vezes.
- Refaça o processo de adição acima.

---

### Teste 07 — Pergunta fora do escopo (fallback esperado)

**Pergunta do operador:**
> "Quanto custa instalar um novo carregador GoodWe de 22kW no meu posto?"

**Resposta ideal esperada:**

Valores de instalação e equipamentos dependem de negociação direta com a GoodWe ou revendedores autorizados, pois variam conforme a infraestrutura elétrica do local, frete e condições comerciais.

Para obter um orçamento, entre em contato com:
- **Portal comercial GoodWe Brasil:** www.goodwe.com/br
- **E-mail comercial:** [contato comercial GoodWe]
- **Suporte:** support.goodwe.com

Posso te ajudar com a **operação e configuração** dos equipamentos após a instalação.

---

### Teste 08 — Gestão de usuários e RFID

**Pergunta do operador:**
> "Como cadastro um cartão RFID para um cliente frequente que usa o posto toda semana?"

**Resposta ideal esperada:**

Para cadastrar um cartão RFID de cliente:

1. Acesse **Usuários → Cartões RFID** no portal GoodWe Cloud.
2. Clique em **"Adicionar Cartão"**.
3. Insira o **número do cartão** (impresso na frente do cartão RFID) ou passe o cartão no leitor USB de administração, se disponível.
4. Preencha o nome do cliente e, opcionalmente, um limite de crédito ou plano de cobrança.
5. Ative o cartão e salve.

A partir desse momento, o cliente pode iniciar sessões passando o cartão no leitor do carregador, sem precisar do aplicativo.

---

## Resumo de Cobertura

| # | Categoria | Comportamento esperado |
|---|---|---|
| 01 | Operação básica | Resposta com procedimento passo a passo |
| 02 | Diagnóstico de erro | Identificação do código + resolução + fallback se necessário |
| 03 | Faturamento | Procedimento de configuração de tarifa |
| 04 | Relatórios | Geração e exportação de relatório |
| 05 | Infraestrutura elétrica | Configuração de balanceamento de carga |
| 06 | Conectividade | Revinculação ao portal cloud |
| 07 | Fora do escopo | Fallback correto para suporte comercial |
| 08 | Gestão de usuários | Cadastro de cartão RFID |
