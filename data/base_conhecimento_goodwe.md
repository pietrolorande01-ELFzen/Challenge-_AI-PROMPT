# Base de conhecimento operacional — GoodWe Assist

> **Origem:** notas operacionais consolidadas pelo grupo nas Sprints 1 e 2 a partir da documentação
> técnica GoodWe (datasheet HCA-G2, manual do usuário e mapa MODBUS) e do enunciado do desafio
> ChargeGrid Intelligence. Serve como corpus de contingência do RAG quando os PDFs não estão
> montados no ambiente, garantindo que o pipeline e o eval rodem de ponta a ponta.
> Não substitui a documentação oficial: em caso de divergência, vale o PDF do fabricante.

## Portal GoodWe Cloud — navegação

O portal GoodWe Cloud (cloud.goodwe.com) é o console do operador. Menus principais:

- **Gerenciamento de Carregadores → Sessões** — iniciar, pausar, encerrar e monitorar sessões.
- **Configurações → Tarifas e Faturamento** — modelos de cobrança e preços.
- **Configurações → Grupos de Carregadores** — agrupamento e balanceamento de carga.
- **Relatórios → Sessões de Carga** — histórico, exportação CSV e PDF.
- **Usuários → Cartões RFID** — cadastro e permissões de cartões.
- **Carregadores → Adicionar Dispositivo** — vinculação por número de série.

## Iniciar uma sessão de carga manualmente

Para um cliente sem o aplicativo GoodWe Charge:

1. Acessar o portal GoodWe Cloud com login de operador.
2. Ir em Gerenciamento de Carregadores → Sessões.
3. Selecionar o carregador e clicar em "Iniciar Sessão Manual".
4. Informar o conector a liberar (Conector A ou B).
5. Confirmar — a sessão inicia em até 10 segundos.

Alternativa: passar o **cartão RFID master** (de administrador) no leitor do equipamento libera a
sessão imediatamente, sem passar pelo portal.

## Configuração de tarifas e faturamento

Modelos de cobrança suportados: por kWh consumido, por tempo de sessão, taxa fixa por sessão e
planos de assinatura. Formas de pagamento integradas: Pix, cartão de crédito/débito e carteiras
digitais.

Para definir preço por kWh:

1. Portal GoodWe Cloud como administrador.
2. Configurações → Tarifas e Faturamento.
3. Selecionar o carregador ou o grupo.
4. Em "Modelo de cobrança", escolher "Por kWh consumido".
5. Preencher o valor (ex.: 1.80) no campo "Preço por kWh (R$)".
6. Definir a moeda (BRL) e salvar.

A tarifa vale para a próxima sessão iniciada. Sessões em andamento mantêm o preço anterior.

## Relatórios operacionais

Para gerar o relatório mensal de sessões e faturamento:

1. Relatórios → Sessões de Carga.
2. Filtrar por período (data inicial e final).
3. Selecionar todos os carregadores ou um específico.
4. Clicar em "Gerar Relatório".
5. O relatório traz data/hora, energia consumida (kWh), duração e valor faturado por sessão.
6. Exportar em CSV ou PDF; o arquivo também é enviado ao e-mail cadastrado do operador.

## Balanceamento de carga (load balancing)

O ChargeGrid Intelligence faz balanceamento dinâmico: a cada ciclo de monitoramento, quando a
demanda se aproxima do limite contratado, o sistema reduz proporcionalmente a potência dos
carregadores ativos, evitando o desarme do disjuntor geral e a ultrapassagem de demanda.

Configuração de um grupo:

1. Configurações → Grupos de Carregadores.
2. Criar um grupo e adicionar os carregadores que compartilham o mesmo quadro.
3. Preencher "Corrente máxima do grupo (A)" abaixo da capacidade do quadro, deixando margem de
   segurança (ex.: 75 A em um quadro de 80 A).
4. Ativar "Balanceamento dinâmico ativo".
5. Salvar.

Com o grupo ativo, a corrente disponível é dividida entre os veículos em carga; quando apenas um
veículo carrega, ele pode usar até o limite configurado do grupo. O dimensionamento do quadro,
disjuntores e cabos é responsabilidade de eletricista habilitado (NR-10, com ART/RRT).

## Cartões RFID e gestão de usuários

1. Usuários → Cartões RFID.
2. "Adicionar Cartão".
3. Informar o número impresso no cartão ou passá-lo no leitor USB de administração.
4. Preencher o nome do cliente e, opcionalmente, limite de crédito ou plano de cobrança.
5. Ativar o cartão e salvar.

Feito isso, o cliente inicia sessões aproximando o cartão do leitor, sem o aplicativo.

## Conectividade e revinculação ao Cloud

Se o carregador sumiu do painel:

1. No equipamento, abrir o menu de configurações (botão lateral por 5 segundos).
2. Rede → Wi-Fi ou Ethernet: confirmar que há conexão ativa.
3. No portal: Carregadores → Adicionar Dispositivo.
4. Informar o número de série (S/N) da etiqueta lateral.
5. Confirmar o código de pareamento exibido no display.

Se não aparecer em 5 minutos, o reset de fábrica (botão de reset por 10 segundos até o display
piscar 3 vezes) apaga as configurações locais e permite refazer a vinculação.

## Códigos de erro observados em operação

- **E03 — temperatura elevada.** Garantir 20 cm livres ao redor do equipamento e ventilação
  adequada; verificar exposição direta ao sol. Persistindo, acionar o suporte GoodWe.
- **E04 — falha de comunicação com o GoodWe Cloud.** Verificar Wi-Fi ou cabo de rede, reiniciar o
  roteador, aguardar 2 minutos e reiniciar o carregador. Persistindo após 10 minutos, abrir chamado
  em support.goodwe.com com o número de série.
- **E07 — falha no módulo de medição de energia.** Causas típicas: surto de tensão, cabo interno
  frouxo, defeito no medidor. Desligar o disjuntor dedicado por 30 segundos e religar; aguardar
  cerca de 2 minutos pelo reinício completo. Persistindo, **não abrir o equipamento**: abrir chamado
  em support.goodwe.com informando o código e o número de série.

## Limites de atendimento do assistente

Fora do escopo do GoodWe Assist, sempre com encaminhamento:

- Preço de equipamento, orçamento de instalação, garantia e contratos → canal comercial GoodWe
  (www.goodwe.com/br) ou revendedor autorizado.
- Questões jurídicas, tributárias e regulatórias → advogado ou contador da empresa.
- Análise financeira (payback, financiamento, precificação estratégica) → consultoria financeira
  ou time comercial GoodWe.
- Intervenção elétrica ou física no equipamento e no quadro → eletricista qualificado com NR-10 e
  ART/RRT; suporte GoodWe para defeito de hardware.
