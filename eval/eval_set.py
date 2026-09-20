"""
Eval set — MESMO conjunto definido na Sprint 1 e executado na Sprint 2.

Reexecutado sem alteração sobre a versão refatorada: é isso que torna a tabela
antes/depois comparável. Cada caso traz os termos que a resposta correta precisa
conter (`obrigatorios`) e os que não pode conter (`proibidos`), o que permite uma
nota reprodutível e auditável, sem depender de julgamento humano a cada rodada.
"""

CASOS = [
    {
        "id": "T01",
        "categoria": "operacao_basica",
        "pergunta": "Como eu inicio uma sessão de carga manualmente para um cliente que não tem o aplicativo?",
        "resposta_ideal": "Iniciar sessão manual pelo portal GoodWe Cloud (Gerenciamento de Carregadores → Sessões) ou com cartão RFID master.",
        "obrigatorios": [["cloud", "portal"], ["sessão", "sessao"], ["rfid", "manual"]],
        "proibidos": [],
    },
    {
        "id": "T02",
        "categoria": "diagnostico_erro",
        "pergunta": "O carregador está travado com o display piscando 'E07'. O que significa e como resolvo?",
        "resposta_ideal": "E07 = falha no módulo de medição. Desligar disjuntor 30s, religar, aguardar reinício; persistindo, abrir chamado sem abrir o equipamento.",
        "obrigatorios": [["e07", "medição", "medicao"], ["disjuntor", "reinici"], ["support.goodwe", "suporte", "chamado"]],
        "proibidos": ["abra o equipamento", "desmonte"],
    },
    {
        "id": "T03",
        "categoria": "faturamento",
        "pergunta": "Quero cobrar R$ 1,80 por kWh. Como configuro o preço no sistema?",
        "resposta_ideal": "Configurações → Tarifas e Faturamento, modelo 'por kWh', valor 1.80, moeda BRL; vale para as próximas sessões.",
        "obrigatorios": [["tarifa", "faturamento"], ["kwh"], ["1,80", "1.80"]],
        "proibidos": [],
    },
    {
        "id": "T04",
        "categoria": "relatorios",
        "pergunta": "Preciso gerar um relatório do mês passado com todas as sessões e o valor faturado. Como faço?",
        "resposta_ideal": "Relatórios → Sessões de Carga, filtrar período, gerar e exportar em CSV ou PDF.",
        "obrigatorios": [["relatóri", "relatori"], ["período", "periodo", "filtr"], ["csv", "pdf", "export"]],
        "proibidos": [],
    },
    {
        "id": "T05",
        "categoria": "balanceamento",
        "pergunta": "Tenho 4 carregadores ligados no mesmo quadro de 80A. Às vezes o disjuntor cai. Como configuro o balanceamento?",
        "resposta_ideal": "Criar grupo de carregadores, definir corrente máxima do grupo com margem e ativar o balanceamento dinâmico.",
        "obrigatorios": [["balanceamento", "load balancing"], ["grupo"], ["corrente", "a)", "ampè", "ampere"]],
        "proibidos": [],
    },
    {
        "id": "T06",
        "categoria": "conectividade",
        "pergunta": "O carregador parou de aparecer no meu painel do GoodWe Cloud. Como revinculo ele ao sistema?",
        "resposta_ideal": "Conferir rede, adicionar dispositivo pelo número de série e confirmar pareamento; reset de fábrica como último recurso.",
        "obrigatorios": [["número de série", "numero de serie", "s/n"], ["adicionar", "parear", "vincul"], ["rede", "wi-fi", "wifi", "ethernet"]],
        "proibidos": [],
    },
    {
        "id": "T07",
        "categoria": "fora_de_escopo_comercial",
        "pergunta": "Quanto custa instalar um novo carregador GoodWe de 22kW no meu posto?",
        "resposta_ideal": "Não informa preço; encaminha ao canal comercial GoodWe e se oferece para ajudar na operação.",
        "obrigatorios": [["comercial", "revendedor", "orçamento", "orcamento"], ["goodwe"]],
        "proibidos": ["r$ 1", "r$ 2", "r$ 3", "custa aproximadamente", "o preço é"],
    },
    {
        "id": "T08",
        "categoria": "gestao_usuarios",
        "pergunta": "Como cadastro um cartão RFID para um cliente frequente que usa o posto toda semana?",
        "resposta_ideal": "Usuários → Cartões RFID → Adicionar Cartão, informar número do cartão, vincular cliente e ativar.",
        "obrigatorios": [["rfid"], ["cadastr", "adicionar"], ["cartão", "cartao"]],
        "proibidos": [],
    },
]

# Conversa usada para demonstrar a memória por sessão (3+ turnos, com referência anafórica).
CONVERSA_MEMORIA = [
    "Tenho 4 carregadores EV-AC22 no estacionamento do shopping e o quadro é de 80A.",
    "Com essa configuração que te falei, como eu evito que o disjuntor caia?",
    "E se só um carro estiver carregando, ele usa toda a corrente que sobra?",
    "Beleza. Agora me lembra: quantos carregadores eu disse que tenho e em que tipo de local?",
]

# Critério do 4º turno: o agente precisa recuperar os fatos do 1º turno.
MEMORIA_OBRIGATORIOS = [["4", "quatro"], ["shopping", "estacionamento"]]
