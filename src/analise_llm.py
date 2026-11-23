# -*- coding: utf-8 -*-
"""Análise completa da política via LLM local (trilha MVP).

Uma chamada ao Ollama devolve, para cada uma das 12 categorias:
presente (bool), nível (verde/amarelo/vermelho), trecho citado e justificativa.
"""
import json
import re
import ollama
from src.taxonomia import CATEGORIAS, POR_ID
from src.regras import artigos_da_categoria, ajustar_nivel

MODELO = "qwen2.5:3b"

def _montar_prompt(texto: str) -> str:
    """Monta o prompt com as 12 categorias da taxonomia e instrução estrita de JSON."""
    cats = "\n".join(
        f'- id="{c["id"]}" ({c["nome"]}): {c["descricao"]} '
        f'Alerta vermelho = {c["alerta_vermelho"]}'
        for c in CATEGORIAS
    )
    # Limita a 12.000 caracteres para não sobrecarregar a janela de contexto da LLM local
    trecho_texto = texto[:12000]
    
    return (
        "Você é um analista especialista em privacidade e LGPD. Analise a política de privacidade "
        "abaixo contra as 12 categorias listadas a seguir. Para CADA categoria encontrada, "
        "diga se ela está presente no texto, o nível de risco e cite um trecho curto literal.\n\n"
        "Critérios de nível:\n"
        "- 'verde': claro, transparente e adequado à LGPD.\n"
        "- 'amarelo': vago, genérico ou incompleto.\n"
        "- 'vermelho': risco direto ao titular dos dados.\n\n"
        f"CATEGORIAS OBRIGATÓRIAS:\n{cats}\n\n"
        "Responda ESTRITAMENTE com um JSON no seguinte formato, sem explicações adicionais:\n"
        '{\n'
        '  "categorias": [\n'
        '    {\n'
        '      "id": "id_da_categoria",\n'
        '      "presente": true,\n'
        '      "nivel": "verde|amarelo|vermelho",\n'
        '      "trecho": "citação curta literal do texto",\n'
        '      "justificativa": "frase curta explicando o motivo da classificação"\n'
        '    }\n'
        '  ]\n'
        '}\n\n'
        f"POLÍTICA A SER ANALISADA:\n{trecho_texto}"
    )

def analisar(texto: str) -> list[dict]:
    """Envia o texto para a LLM via Ollama e enriquece os resultados com a LGPD e regras."""
    resp = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": _montar_prompt(texto)}],
        format="json",
        options={"temperature": 0},
    )
    
    conteudo = resp["message"]["content"].strip()
    
    # Tratamento defensivo caso o modelo inclua blocos de markdown ```json ... ```
    if "```" in conteudo:
        conteudo = re.sub(r"^```json\s*", "", conteudo)
        conteudo = re.sub(r"```$", "", conteudo).strip()
        
    try:
        dados = json.loads(conteudo)
        itens = dados.get("categorias", [])
    except (json.JSONDecodeError, KeyError):
        itens = []

    # Normaliza, valida contra a taxonomia e aplica o motor de regras
    resultado = []
    for item in itens:
        cat_id = item.get("id")
        if cat_id not in POR_ID:
            continue
            
        nivel = item.get("nivel", "amarelo")
        trecho = item.get("trecho", "")
        
        resultado.append({
            "id": cat_id,
            "categoria": POR_ID[cat_id]["nome"],
            "presente": item.get("presente", True),
            # Se a IA achou que é verde mas o texto tem termos vagos, o motor rebaixa:
            "nivel": ajustar_nivel(trecho, nivel),
            "trecho": trecho,
            "justificativa": item.get("justificativa", ""),
            # Vincula os artigos oficiais da LGPD:
            "artigos": artigos_da_categoria(cat_id),
        })
        
    return resultado
