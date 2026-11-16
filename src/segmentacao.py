# -*- coding: utf-8 -*-
"""Segmentação: quebra texto limpo em trechos/parágrafos analisáveis."""
import re

def segmentar(texto: str, min_chars: int = 40, max_chars: int = 1000) -> list[str]:
    """Divide um texto longo em blocos com sentido semântico completo.
    
    Regras:
    1. Divide primeiro por parágrafos duplos (linhas em branco).
    2. Se o parágrafo for muito longo (> max_chars), quebra respeitando as pontuações (. ! ?).
    3. Descarta trechos curtos demais (< min_chars) que não contêm informação útil.
    """
    brutos = re.split(r"\n\s*\n", texto)
    trechos: list[str] = []
    
    for bloco in brutos:
        bloco = bloco.strip()
        if not bloco:
            continue
            
        # Caso 1: Parágrafo tem um tamanho ideal
        if len(bloco) <= max_chars:
            if len(bloco) >= min_chars:
                trechos.append(bloco)
            continue
            
        # Caso 2: Parágrafo gigante -> quebra respeitando frases
        frases = re.split(r"(?<=[.!?])\s+", bloco)
        atual = ""
        for frase in frases:
            if len(atual) + len(frase) < max_chars:
                atual += " " + frase
            else:
                if len(atual.strip()) >= min_chars:
                    trechos.append(atual.strip())
                atual = frase
                
        if len(atual.strip()) >= min_chars:
            trechos.append(atual.strip())
            
    return trechos
