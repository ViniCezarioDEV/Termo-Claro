# -*- coding: utf-8 -*-
"""Resumo em linguagem simples a partir dos trechos classificados."""
import ollama

MODELO = "qwen2.5:3b"

def resumir(nome_app: str, achados: list[dict]) -> str:
    """Gera uma explicação em linguagem simples para leigos a partir dos achados da política."""
    if not achados:
        return "Nenhuma prática de dados relevante foi identificada no texto fornecido."
        
    linhas = [f"- [{a['nivel'].upper()}] {a['categoria']}: {a['trecho'][:200]}" for a in achados]
    
    prompt = (
        "Você é um assistente que explica termos jurídicos e políticas de privacidade para pessoas leigas, "
        "usando um português (Brasileiro) muito claro, direto e acessível.\n"
        f"Aplicativo analisado: {nome_app}\n\n"
        "Com base nos pontos identificados abaixo, escreva um resumo de 4 a 6 frases explicando "
        "o que o aplicativo faz com os dados do usuário e quais pontos merecem atenção ou cuidado.\n"
        "Instruções:\n"
        "- Não use jargões jurídicos.\n"
        "- Seja direto e objetivo.\n"
        "- Baseie-se APENAS nos pontos fornecidos, sem inventar nada.\n\n"
        "PONTOS IDENTIFICADOS:\n"
        + "\n".join(linhas)
    )
    
    resp = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2},
    )
    
    conteudo = resp["message"]["content"].strip()
    # Se o modelo produzir tags de pensamento <think>...</think>, removemos para entregar texto limpo:
    import re
    conteudo = re.sub(r"<think>.*?</think>", "", conteudo, flags=re.DOTALL).strip()
    return conteudo
