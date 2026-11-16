# -*- coding: utf-8 -*-
"""Motor de regras: categoria + sinais do texto -> artigo LGPD + nível de alerta."""
from src.taxonomia import POR_ID

# Lista de termos vagos ou ambíguos comuns em políticas abusivas
TERMOS_VAGOS = [
    "podemos", "poderemos", "entre outros", "como por exemplo", "tais como",
    "parceiros", "terceiros", "de tempos em tempos", "a nosso critério",
    "quando necessário", "por tempo indeterminado", "a qualquer momento",
    "sem aviso", "etc",
]

def artigos_da_categoria(cat_id: str) -> list[str]:
    """Retorna a lista de artigos da LGPD aplicáveis àquela categoria."""
    cat = POR_ID.get(cat_id)
    return cat["artigos"] if cat else []

def ajustar_nivel(trecho: str, nivel_sugerido: str) -> str:
    """Ajusta o nível de risco.
    
    Se a IA marcou como 'verde' (adequado), mas o texto tem 2 ou mais termos vagos,
    o sistema rebaixa para 'amarelo' (vago ou incompleto).
    """
    texto = trecho.lower()
    vagos_encontrados = sum(1 for t in TERMOS_VAGOS if t in texto)
    
    if nivel_sugerido == "verde" and vagos_encontrados >= 2:
        return "amarelo"
        
    return nivel_sugerido
