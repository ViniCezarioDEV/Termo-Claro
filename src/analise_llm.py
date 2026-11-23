# -*- coding: utf-8 -*-
"""Análise completa da política via LLM local (trilha MVP).

Processamento via Ollama na GPU com tratamento para documentos curtos e longos:
- Se <= 8.000 chars: análise direta em chamada única.
- Se > 8.000 chars: análise de início (coleta/sensíveis) e fim (direitos/retenção/DPO)
  com consolidação inteligente dos achados.
"""
import json
import re
import ollama
from src.taxonomia import CATEGORIAS, POR_ID
from src.regras import artigos_da_categoria, ajustar_nivel

MODELO = "qwen2.5:3b"
LIMITE_BLOCO = 7000

def _montar_prompt(trecho_texto: str) -> str:
    """Monta o prompt com o texto no início e as instruções de JSON no final.
    
    Esta estrutura evita que o modelo perca a atenção nas regras de formatação
    ao processar textos densos e longos.
    """
    cats_desc = "\n".join(
        f'- "{c["id"]}" ({c["nome"]}): {c["descricao"]}'
        for c in CATEGORIAS
    )
    
    return f"""Você é um auditor especialista em privacidade e LGPD.
Abaixo está o texto de uma política de privacidade. Leia com atenção:

=== POLÍTICA A SER ANALISADA ===
{trecho_texto}
=== FIM DA POLÍTICA ===

Com base EXCLUSIVAMENTE no texto acima, identifique quais das 12 categorias abaixo estão presentes:

CATEGORIAS POSSÍVEIS (use EXATAMENTE estes IDs):
{cats_desc}

CRITÉRIOS DE RISCO:
- "verde": claro, transparente e adequado à LGPD.
- "amarelo": vago, genérico ou incompleto.
- "vermelho": risco direto ao titular dos dados.

REGRAS OBRIGATÓRIAS:
1. Retorne APENAS as categorias que forem expressamente mencionadas no texto acima. NUNCA invente itens que não existam no texto.
2. O campo "trecho" DEVE ser uma citação LITERAL copiada palavra por palavra do texto.
3. Se fornecedores e operadores forem nomeados (ex: parceiros com finalidade explícita), classifique como verde ou amarelo, NUNCA vermelho.
4. Menção a produtos para menores ou Under-18 conta como "criancas" (verde).
5. E-mail de privacidade ou DPO conta como "encarregado" (verde).
6. Se houver cláusula de retenção ou guarda de dados, classifique em "retencao".

Responda ESTRITAMENTE em formato JSON com esta estrutura exata:
{{
  "categorias": [
    {{
      "id": "id_da_categoria_da_lista",
      "presente": true,
      "nivel": "verde|amarelo|vermelho",
      "trecho": "citação curta literal do texto",
      "justificativa": "explicação curta da classificação"
    }}
  ]
}}"""

def _executar_chamada_llm(trecho: str) -> list[dict]:
    """Chama a LLM local no Ollama e faz o parse defensivo do JSON retornado."""
    if not trecho or len(trecho.strip()) < 40:
        return []
        
    try:
        resp = ollama.chat(
            model=MODELO,
            messages=[{"role": "user", "content": _montar_prompt(trecho)}],
            format="json",
            options={"temperature": 0, "num_ctx": 4096},
        )
    except Exception as e:
        print(f"[Termo Claro] Erro na comunicação com Ollama: {e}")
        return []
        
    conteudo = resp.get("message", {}).get("content", "").strip()
    if not conteudo:
        return []
        
    # Limpeza de markdown caso o modelo insira ```json ... ```
    if "```" in conteudo:
        conteudo = re.sub(r"^```(?:json)?\s*", "", conteudo)
        conteudo = re.sub(r"```$", "", conteudo).strip()
        
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError:
        return []
        
    # Tratamento flexível: dict com 'categorias', ou lista direta, ou chaves alternativas
    itens = []
    if isinstance(dados, dict):
        itens = dados.get("categorias") or dados.get("categories") or dados.get("itens") or []
    elif isinstance(dados, list):
        itens = dados
        
    return itens if isinstance(itens, list) else []

def analisar(texto: str) -> list[dict]:
    """Envia o texto para a LLM via Ollama, trata documentos curtos e longos e enriquece com LGPD."""
    texto_limpo = texto.strip()
    if not texto_limpo:
        return []
        
    # Estratégia de documentos curtos vs longos
    if len(texto_limpo) <= LIMITE_BLOCO:
        itens_brutos = _executar_chamada_llm(texto_limpo)
    else:
        # Documento extenso: processa início (coleta/finalidade/menores) e fim (direitos/retenção/DPO)
        bloco_inicio = texto_limpo[:LIMITE_BLOCO]
        bloco_fim = texto_limpo[-LIMITE_BLOCO:]
        
        itens1 = _executar_chamada_llm(bloco_inicio)
        itens2 = _executar_chamada_llm(bloco_fim)
        
        # Consolidação inteligente sem duplicações
        consolidados = {}
        for it in itens1 + itens2:
            cid = it.get("id")
            if not cid or cid not in POR_ID:
                continue
            
            # Se ainda não vimos essa categoria, adiciona
            if cid not in consolidados:
                consolidados[cid] = it
            else:
                # Se já vimos, prefere o item que tiver citação literal mais longa e informativa
                trecho_existente = consolidados[cid].get("trecho", "")
                trecho_novo = it.get("trecho", "")
                if len(trecho_novo) > len(trecho_existente):
                    consolidados[cid] = it
                    
        itens_brutos = list(consolidados.values())

    # Frases típicas de quando a IA não encontrou evidência real
    frases_nao_mencionado = [
        "não há menção", "não menciona", "não cita", "não foi mencionad",
        "não foram encontrad", "não é mencionad"
    ]

    # Normalização, validação contra a taxonomia e motor de regras LGPD
    resultado = []
    ids_adicionados = set()
    
    for item in itens_brutos:
        cat_id = item.get("id")
        if not cat_id or cat_id not in POR_ID or cat_id in ids_adicionados:
            continue
            
        nivel = item.get("nivel", "amarelo").lower()
        if nivel not in ("verde", "amarelo", "vermelho"):
            nivel = "amarelo"
            
        trecho = item.get("trecho", "").strip()
        justificativa = item.get("justificativa", "").strip()
        
        # Guardrail anti-alucinação: se a justificativa diz explicitamente que não foi mencionado
        # e o trecho não traz evidência real, marcamos como presente=False para não gerar falso risco
        eh_ausente = any(f in justificativa.lower() for f in frases_nao_mencionado)
        if eh_ausente and len(trecho) < 15:
            continue

        ids_adicionados.add(cat_id)
        
        resultado.append({
            "id": cat_id,
            "categoria": POR_ID[cat_id]["nome"],
            "presente": item.get("presente", True) and not eh_ausente,
            # Se a IA achou que é verde mas o trecho possui termos vagos, o motor rebaixa:
            "nivel": ajustar_nivel(trecho, nivel),
            "trecho": trecho,
            "justificativa": justificativa,
            # Vincula os artigos oficiais da LGPD:
            "artigos": artigos_da_categoria(cat_id),
        })
        
    return resultado
