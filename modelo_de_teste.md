# 🧪 Modelo de Teste — ChatBot GoodWe

> Documento de referência para avaliação do comportamento esperado do chatbot na Sprint 2.
> Persona-alvo: **Síndico / Gestor Condominial**

---

## Pergunta 1

**Input do usuário:**
> "Como funciona o rateio de energia elétrica entre os moradores que usam o carregador?"

**Resposta esperada:**
O sistema GoodWe registra cada sessão de carregamento individualmente, identificando qual unidade utilizou o eletroposto, por quanto tempo e qual a energia consumida (kWh). Ao final do mês, é possível gerar um relatório por unidade, que pode ser utilizado pelo síndico para cobrar cada morador proporcionalmente ao seu consumo — separando o custo de carregamento da conta de energia comum do condomínio.

**Critério de avaliação:** Resposta deve citar registro individual por unidade, medição em kWh e possibilidade de cobrança proporcional.

---

## Pergunta 2

**Input do usuário:**
> "Quantos carros podem carregar ao mesmo tempo sem sobrecarregar a rede elétrica do prédio?"

**Resposta esperada:**
Isso depende da capacidade do quadro elétrico do condomínio e da configuração do sistema de gerenciamento de carga. O GoodWe oferece a funcionalidade de **load balancing** (balanceamento de carga), que distribui automaticamente a potência disponível entre os carregadores ativos, evitando sobrecarga. Para saber o número exato de carros simultâneos, é necessário verificar a potência total disponível na entrada do condomínio com o síndico ou o engenheiro responsável.

**Critério de avaliação:** Deve citar load balancing, distribuição automática de potência e necessidade de verificação técnica.

---

## Pergunta 3

**Input do usuário:**
> "Um morador está reclamando que o carregador ficou ocupado por horas sem o carro estar carregando. O que posso fazer?"

**Resposta esperada:**
Essa situação é conhecida como "ocupação indevida" do eletroposto. Recomenda-se: (1) verificar no painel do sistema se a sessão de carregamento foi finalizada corretamente; (2) implementar uma política condominial de tempo máximo de uso, com multa por permanência após o fim da carga; (3) configurar notificações automáticas via app para alertar o usuário quando a carga estiver completa. O GoodWe permite configurar alertas e relatórios de sessões finalizadas.

**Critério de avaliação:** Deve sugerir política de uso, verificação de sessão e uso de notificações/alertas do sistema.

---

## Pergunta 4

**Input do usuário:**
> "Como faço para ver um relatório de uso dos carregadores do mês passado?"

**Resposta esperada:**
Para acessar o relatório de uso, acesse o painel de gestão GoodWe com suas credenciais de administrador. Na seção "Relatórios" ou "Histórico de Sessões", selecione o período desejado (mês anterior) e exporte os dados em formato CSV ou PDF. O relatório mostrará data, horário, duração, energia consumida (kWh) e unidade usuária de cada sessão registrada.

**Critério de avaliação:** Deve indicar o caminho no sistema, mencionar o período selecionável e os dados disponíveis no relatório.

---

## Pergunta 5

**Input do usuário:**
> "Um morador quer instalar um carregador particular na vaga dele. Isso é permitido?"

**Resposta esperada:**
Depende da convenção do condomínio e da legislação local. Em geral, o morador pode instalar um carregador em vaga privativa desde que: (1) obtenha aprovação em assembleia condominial; (2) arque com os custos de instalação e adequação elétrica; (3) o sistema seja individualizado, medindo e cobrando somente o consumo daquela unidade. É recomendado exigir que a instalação seja feita por profissional habilitado e que o equipamento seja homologado. Como síndico, você pode solicitar a apresentação do projeto elétrico antes de autorizar.

**Critério de avaliação:** Deve mencionar aprovação em assembleia, individualização do medidor e responsabilidade do morador pelos custos.

---

## Observações Gerais

- Todas as respostas devem ser em **português claro e acessível**, sem jargão excessivamente técnico
- O chatbot não deve inventar dados ou especificações técnicas que não constem no contexto fornecido
- Caso a pergunta esteja fora do escopo GoodWe/EV, o chatbot deve redirecionar educadamente
- As respostas acima servirão como **gabarito de avaliação qualitativa** na Sprint 2
