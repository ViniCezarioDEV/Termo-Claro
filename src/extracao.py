# -*- coding: utf-8 -*-
"""Extração: transforma qualquer fonte (texto, URL, arquivo) em texto limpo."""
import os
import re

def _limpar(texto: str) -> str:
    """Remove espaços em branco excessivos e quebras de linha repetidas."""
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def de_url(url: str) -> str:
    """Baixa o conteúdo de uma URL e extrai apenas o artigo/texto principal."""
    import trafilatura
    baixado = trafilatura.fetch_url(url)
    if not baixado:
        raise ValueError(f"Não consegui baixar a URL: {url}")
    texto = trafilatura.extract(baixado, include_comments=False, include_tables=False)
    return _limpar(texto or "")

def de_pdf(caminho: str) -> str:
    """Extrai o texto de todas as páginas de um arquivo PDF."""
    from pypdf import PdfReader
    leitor = PdfReader(caminho)
    partes = [pagina.extract_text() or "" for pagina in leitor.pages]
    return _limpar("\n".join(partes))

def de_html(caminho: str) -> str:
    """Lê um arquivo HTML local e remove scripts, estilos e cabeçalhos."""
    from bs4 import BeautifulSoup
    with open(caminho, encoding="utf-8", errors="ignore") as f:
        sopa = BeautifulSoup(f.read(), "lxml")
    for tag in sopa(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return _limpar(sopa.get_text(separator="\n"))

def extrair(fonte: str) -> str:
    """Detecta automaticamente o tipo da fonte (URL, arquivo ou texto puro)."""
    if fonte.startswith("http://") or fonte.startswith("https://"):
        return de_url(fonte)
    if os.path.isfile(fonte):
        ext = os.path.splitext(fonte)[1].lower()
        if ext == ".pdf":
            return de_pdf(fonte)
        if ext in (".html", ".htm"):
            return de_html(fonte)
        with open(fonte, encoding="utf-8", errors="ignore") as f:
            return _limpar(f.read())
    # Senão, assume que o usuário colou o próprio texto no formulário
    return _limpar(fonte)
