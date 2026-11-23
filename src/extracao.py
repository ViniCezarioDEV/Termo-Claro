# -*- coding: utf-8 -*-
"""Extração: transforma qualquer fonte (texto, URL, arquivo ou upload) em texto limpo."""
import io
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

def de_pdf(fonte) -> str:
    """Extrai texto de PDF a partir de um caminho (str), bytes ou objeto de arquivo."""
    from pypdf import PdfReader
    if isinstance(fonte, (bytes, bytearray)):
        fonte = io.BytesIO(fonte)
    leitor = PdfReader(fonte)
    partes = [pagina.extract_text() or "" for pagina in leitor.pages]
    return _limpar("\n".join(partes))

def de_html(fonte) -> str:
    """Lê conteúdo HTML (caminho em disco, string ou bytes) e remove tags desnecessárias."""
    from bs4 import BeautifulSoup
    if isinstance(fonte, str) and os.path.isfile(fonte):
        with open(fonte, encoding="utf-8", errors="ignore") as f:
            conteudo = f.read()
    elif isinstance(fonte, bytes):
        conteudo = fonte.decode("utf-8", errors="ignore")
    else:
        conteudo = str(fonte)

    sopa = BeautifulSoup(conteudo, "lxml")
    for tag in sopa(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return _limpar(sopa.get_text(separator="\n"))

def de_markdown(conteudo: str) -> str:
    """Limpa e formata texto vindo de arquivos Markdown (.md)."""
    # Remove marcações de cabeçalhos (#) mantendo o texto legível
    texto = re.sub(r"^#+\s*", "", conteudo, flags=re.MULTILINE)
    return _limpar(texto)

def extrair_arquivo(arquivo_ou_caminho, nome_arquivo: str = None) -> str:
    """Processa arquivos carregados na interface ou caminhos em disco (.pdf, .html, .htm, .md, .txt)."""
    # Caso 1: Upload via Streamlit (objeto com atributo .name e .read)
    if hasattr(arquivo_ou_caminho, "name") and hasattr(arquivo_ou_caminho, "read"):
        nome = nome_arquivo or arquivo_ou_caminho.name
        ext = os.path.splitext(nome)[1].lower()
        conteudo_bytes = arquivo_ou_caminho.read()

        if ext == ".pdf":
            return de_pdf(conteudo_bytes)
        elif ext in (".html", ".htm"):
            return de_html(conteudo_bytes)
        elif ext in (".md", ".markdown"):
            texto = conteudo_bytes.decode("utf-8", errors="ignore")
            return de_markdown(texto)
        else: # .txt ou outros
            return _limpar(conteudo_bytes.decode("utf-8", errors="ignore"))

    # Caso 2: Caminho em disco ou texto puro
    return extrair(str(arquivo_ou_caminho))

def extrair(fonte: str) -> str:
    """Detecta automaticamente o tipo da fonte (URL, arquivo no disco ou texto puro)."""
    if fonte.startswith("http://") or fonte.startswith("https://"):
        return de_url(fonte)
    if os.path.isfile(fonte):
        ext = os.path.splitext(fonte)[1].lower()
        if ext == ".pdf":
            return de_pdf(fonte)
        if ext in (".html", ".htm"):
            return de_html(fonte)
        if ext in (".md", ".markdown"):
            with open(fonte, encoding="utf-8", errors="ignore") as f:
                return de_markdown(f.read())
        with open(fonte, encoding="utf-8", errors="ignore") as f:
            return _limpar(f.read())
    # Senão, assume que o usuário colou o próprio texto no formulário
    return _limpar(fonte)
