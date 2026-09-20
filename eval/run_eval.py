"""
Runner do eval — gera TODAS as evidências numéricas da Sprint 03.

Uso:
    python -m eval.run_eval --tudo                 # legado + refatorado (2 modelos) + segurança + memória
    python -m eval.run_eval --modelos qwen llama   # só a comparação entre modelos
    python -m eval.run_eval --seguranca            # só os testes de segurança
    python -m eval.run_eval --memoria              # só a demonstração de memória (3+ turnos)
    python -m eval.run_eval --parametros qwen      # varredura de temperature/top_p no modelo escolhido

Saídas em results/:
    qualidade_<versao>_<modelo>.json
    seguranca_<modelo>.json
    memoria_<modelo>.json
    parametros_<modelo>.json
    consolidado.json          ← consumido por scripts/gerar_relatorio.py
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from src.config import DIR_RESULTS, GRADE_PARAMETROS, MODELOS
from src.knowledge import construir_retriever
from src.memory import limpar_sessao
from src.metrics import ColetorMetricas

from eval.eval_set import CASOS, CONVERSA_MEMORIA, MEMORIA_OBRIGATORIOS
from eval.scoring import (
    avaliar_qualidade,
    avaliar_seguranca,
    consolidar_qualidade,
    consolidar_seguranca,
)
from eval.security_set import CASOS_SEGURANCA

PAUSA_S = 5  # evita rate-limit da Inference API gratuita


def _salvar(nome: str, dados) -> Path:
    caminho = DIR_RESULTS / nome
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  💾 {caminho}")
    return caminho


# ──────────────────────────────────────────────────────────────────────────────
def rodar_qualidade_refatorado(modelo: str, retriever, coletor: ColetorMetricas) -> dict:
    from src.agent import GoodWeAgent

    print(f"\n▶ Eval de qualidade — versão SPRINT 03 · modelo {modelo}")
    agente = GoodWeAgent(modelo=modelo, retriever=retriever, coletor=coletor)
    avaliacoes = []
    for i, caso in enumerate(CASOS):
        sessao = f"eval_{modelo}_{caso['id']}"      # sessão isolada por caso
        limpar_sessao(sessao)
        r = agente.responder(caso["pergunta"], session_id=sessao)
        av = avaliar_qualidade(r.texto, caso)
        av.update(
            latencia_s=r.latencia_s,
            tokens_total=r.tokens_total,
            tokens_estimados=r.tokens_estimados,
        )
        avaliacoes.append(av)
        print(f"  {caso['id']} nota={av['nota']}  {r.latencia_s}s  {r.tokens_total} tok")
        if i < len(CASOS) - 1:
            time.sleep(PAUSA_S)

    resumo = consolidar_qualidade(avaliacoes)
    resumo |= coletor.agregar(versao="sprint3", modelo=modelo)
    _salvar(f"qualidade_sprint3_{modelo}.json", {"resumo": resumo, "casos": avaliacoes})
    return resumo


def rodar_qualidade_legado(modelo: str, retriever, coletor: ColetorMetricas) -> dict:
    from legacy.chat_manual import ChatbotLegado

    print(f"\n▶ Eval de qualidade — versão LEGADO (Sprints 1/2) · modelo {modelo}")
    bot = ChatbotLegado(modelo=modelo, retriever=retriever, coletor=coletor)
    avaliacoes = []
    for i, caso in enumerate(CASOS):
        bot.resetar()
        texto = bot.responder(caso["pergunta"])
        av = avaliar_qualidade(texto, caso)
        m = coletor.registros[-1]
        av.update(latencia_s=m.latencia_s, tokens_total=m.tokens_total, tokens_estimados=True)
        avaliacoes.append(av)
        print(f"  {caso['id']} nota={av['nota']}  {m.latencia_s}s  {m.tokens_total} tok")
        if i < len(CASOS) - 1:
            time.sleep(PAUSA_S)

    resumo = consolidar_qualidade(avaliacoes)
    resumo |= coletor.agregar(versao="legado", modelo=modelo)
    _salvar(f"qualidade_legado_{modelo}.json", {"resumo": resumo, "casos": avaliacoes})
    return resumo


# ──────────────────────────────────────────────────────────────────────────────
def rodar_seguranca(modelo: str, retriever, coletor: ColetorMetricas, versao: str = "sprint3") -> dict:
    print(f"\n▶ Testes de segurança — versão {versao.upper()} · modelo {modelo}")

    if versao == "sprint3":
        from src.agent import GoodWeAgent

        agente = GoodWeAgent(modelo=modelo, retriever=retriever, coletor=coletor)

        def responder(entrada, idx):
            sessao = f"sec_{modelo}_{idx}"
            limpar_sessao(sessao)
            r = agente.responder(entrada, session_id=sessao)
            return r.texto, r.bloqueado
    else:
        from legacy.chat_manual import ChatbotLegado

        bot = ChatbotLegado(modelo=modelo, retriever=retriever, coletor=coletor)

        def responder(entrada, idx):
            bot.resetar()
            return bot.responder(entrada), False

    avaliacoes = []
    for i, caso in enumerate(CASOS_SEGURANCA):
        texto, bloqueado = responder(caso["entrada"], i)
        av = avaliar_seguranca(texto, caso, bloqueado)
        avaliacoes.append(av)
        status = "PASSOU" if av["passou"] else "FALHOU"
        print(f"  {caso['id']} [{caso['familia']}] {status}" + (" (bloqueio determinístico)" if bloqueado else ""))
        if i < len(CASOS_SEGURANCA) - 1 and not bloqueado:
            time.sleep(PAUSA_S)

    resumo = consolidar_seguranca(avaliacoes)
    _salvar(f"seguranca_{versao}_{modelo}.json", {"resumo": resumo, "casos": avaliacoes})
    return resumo


# ──────────────────────────────────────────────────────────────────────────────
def rodar_memoria(modelo: str, retriever, coletor: ColetorMetricas) -> dict:
    """Demonstra memória por sessão gerenciada pelo framework em 4 turnos."""
    from src.agent import GoodWeAgent
    from eval.scoring import _grupo_atendido, _norm

    print(f"\n▶ Demonstração de memória por sessão — modelo {modelo}")
    agente = GoodWeAgent(modelo=modelo, retriever=retriever, coletor=coletor)
    sessao = f"memoria_{modelo}"
    limpar_sessao(sessao)

    turnos = []
    for i, pergunta in enumerate(CONVERSA_MEMORIA, start=1):
        r = agente.responder(pergunta, session_id=sessao)
        turnos.append(
            {
                "turno": i,
                "pergunta": pergunta,
                "resposta": r.texto,
                "latencia_s": r.latencia_s,
                "tokens_total": r.tokens_total,
                "mensagens_na_memoria": len(agente.memoria(sessao)),
            }
        )
        print(f"  turno {i}: {len(agente.memoria(sessao))} mensagens na memória · {r.latencia_s}s")
        if i < len(CONVERSA_MEMORIA):
            time.sleep(PAUSA_S)

    texto_final = _norm(turnos[-1]["resposta"])
    recuperou = all(_grupo_atendido(g, texto_final) for g in MEMORIA_OBRIGATORIOS)

    # Controle negativo: sessão nova não pode saber o que foi dito na sessão anterior.
    limpar_sessao(f"{sessao}_controle")
    r_ctrl = agente.responder(CONVERSA_MEMORIA[-1], session_id=f"{sessao}_controle")
    isolou = not all(_grupo_atendido(g, _norm(r_ctrl.texto)) for g in MEMORIA_OBRIGATORIOS)

    resultado = {
        "modelo": modelo,
        "turnos": turnos,
        "memoria_recuperou_contexto": recuperou,
        "sessoes_isoladas": isolou,
        "resposta_controle": r_ctrl.texto,
        "dump_memoria": agente.memoria(sessao),
    }
    print(f"  ✔ recuperou contexto: {recuperou} · sessões isoladas: {isolou}")
    _salvar(f"memoria_{modelo}.json", resultado)
    return {"memoria_recuperou_contexto": recuperou, "sessoes_isoladas": isolou, "turnos": len(turnos)}


# ──────────────────────────────────────────────────────────────────────────────
def rodar_parametros(modelo: str, retriever) -> dict:
    """Varredura de temperature/top_p para justificar a parametrização final."""
    from src.agent import GoodWeAgent

    print(f"\n▶ Varredura de parametrização — modelo {modelo}")
    saida = []
    for params in GRADE_PARAMETROS:
        coletor = ColetorMetricas()
        agente = GoodWeAgent(modelo=modelo, retriever=retriever, coletor=coletor, parametros=params)
        avaliacoes = []
        for caso in CASOS:
            sessao = f"param_{modelo}_{params['temperature']}_{caso['id']}"
            limpar_sessao(sessao)
            r = agente.responder(caso["pergunta"], session_id=sessao)
            avaliacoes.append(avaliar_qualidade(r.texto, caso))
            time.sleep(PAUSA_S)
        resumo = consolidar_qualidade(avaliacoes) | coletor.agregar(versao="sprint3", modelo=modelo)
        saida.append({"parametros": params, "resumo": resumo})
        print(f"  temp={params['temperature']} top_p={params['top_p']} → nota média {resumo['nota_media']}")

    _salvar(f"parametros_{modelo}.json", saida)
    return {"varreduras": saida}


# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Eval da Sprint 03 — GoodWe Assist")
    ap.add_argument("--tudo", action="store_true")
    ap.add_argument("--modelos", nargs="*", default=["qwen", "llama"])
    ap.add_argument("--legado", action="store_true")
    ap.add_argument("--seguranca", action="store_true")
    ap.add_argument("--memoria", action="store_true")
    ap.add_argument("--parametros", nargs="?", const="qwen")
    args = ap.parse_args()

    for m in args.modelos:
        if m not in MODELOS:
            raise SystemExit(f"Modelo desconhecido: {m}. Disponíveis: {list(MODELOS)}")

    print("🔧 Construindo índice vetorial...")
    retriever = construir_retriever()

    consolidado = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "modelos_testados": args.modelos,
        "qualidade": {},
        "seguranca": {},
        "memoria": {},
        "parametros": {},
    }

    coletor = ColetorMetricas()

    if args.tudo or args.legado:
        consolidado["qualidade"]["legado"] = rodar_qualidade_legado(args.modelos[0], retriever, coletor)
        consolidado["seguranca"]["legado"] = rodar_seguranca(args.modelos[0], retriever, coletor, versao="legado")

    if args.tudo or not (args.seguranca or args.memoria or args.parametros or args.legado):
        for m in args.modelos:
            consolidado["qualidade"][m] = rodar_qualidade_refatorado(m, retriever, coletor)

    if args.tudo or args.seguranca:
        for m in args.modelos:
            consolidado["seguranca"][m] = rodar_seguranca(m, retriever, coletor)

    if args.tudo or args.memoria:
        consolidado["memoria"][args.modelos[0]] = rodar_memoria(args.modelos[0], retriever, coletor)

    if args.parametros:
        consolidado["parametros"][args.parametros] = rodar_parametros(args.parametros, retriever)

    coletor.salvar(DIR_RESULTS / "metricas_brutas.json")
    _salvar("consolidado.json", consolidado)
    print("\n✅ Eval concluído. Rode: python scripts/gerar_relatorio.py")


if __name__ == "__main__":
    main()
