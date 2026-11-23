# -*- coding: utf-8 -*-
"""Termo Claro — Interface Web em Streamlit.

Leitor e tradutor de políticas de privacidade e termos de uso à luz da LGPD.
"""
from datetime import datetime
import os
import re
from urllib.parse import urlparse
import streamlit as st
import importlib
import src.taxonomia
import src.regras
import src.extracao
import src.analise_llm
import src.resumo

# Força o recarregamento dos módulos locais para garantir que edições entrem em vigor na hora
importlib.reload(src.taxonomia)
importlib.reload(src.regras)
importlib.reload(src.extracao)
importlib.reload(src.analise_llm)
importlib.reload(src.resumo)

from src.extracao import extrair, extrair_arquivo
from src.analise_llm import analisar
from src.resumo import resumir
from src.taxonomia import NIVEIS

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Termo Claro — Leitor de Privacidade LGPD",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização complementar - Largura customizada da Sidebar e layout
st.markdown("""
<style>
    /* Força a largura mínima da barra lateral para não esmagar os botões e textos */
    section[data-testid="stSidebar"] {
        min-width: 420px !important;
        width: 420px !important;
    }
    
    /* Evita que as opções do seletor pulem de linha */
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        white-space: nowrap !important;
        font-size: 15px !important;
    }

    .metric-card {
        padding: 15px;
        border-radius: 8px;
        background-color: #f8f9fa;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def limpar_nome_sugerido(nome_bruto: str) -> str:
    """Extrai um nome limpo e amigável para o aplicativo a partir de nomes de arquivos ou URLs."""
    if not nome_bruto:
        return ""
    # 1. Remove extensão (.pdf, .txt, etc.)
    nome = os.path.splitext(nome_bruto)[0]
    
    # 2. Converte separadores (hífens, underscores, pontos múltiplos) em espaços
    nome = re.sub(r"[-_.]+", " ", nome).strip()
    
    # 3. Remove prefixos e expressões comuns em arquivos de termos
    padroes = [
        r"^\s*pol[ií]tica\s*(de)?\s*privacidade\s*(de|da|do)?\s*",
        r"^\s*aviso\s*(de)?\s*privacidade\s*(de|da|do)?\s*",
        r"^\s*termos?\s*(de)?\s*uso\s*(de|da|do)?\s*",
        r"\s*privacidade(\s*da)?\s*$",
        r"\s*pol[ií]tica\s*$",
    ]
    for p in padroes:
        nome = re.sub(p, "", nome, flags=re.IGNORECASE).strip()
    
    # 4. Remove preposições órfãs no início (ex: 'de ', 'da ', 'do ')
    nome = re.sub(r"^(de|da|do|dos|das)\s+", "", nome, flags=re.IGNORECASE).strip()
    
    # Mantém caixa alta e camelCase originais se existirem (ex: CotaLayer3D)
    if nome.isupper() or any(c.isupper() for c in nome[1:]):
        return nome.strip()
    return nome.title() if nome else "Serviço Analisado"

def inferir_nome_de_url(url: str) -> str:
    """Extrai o nome do serviço a partir do domínio da URL."""
    try:
        dominio = urlparse(url).netloc
        partes = dominio.replace("www.", "").split(".")
        if partes:
            return partes[0].capitalize()
    except Exception:
        pass
    return "Serviço Web"

def gerar_conteudo_relatorio(nome: str, achados: list[dict], resumo: str, nao_mencionadas: list[dict]) -> str:
    """Gera um arquivo Markdown formatado pronto para download com o relatório completo."""
    data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    qtd_vermelho = sum(1 for a in achados if a["nivel"] == "vermelho")
    qtd_amarelo = sum(1 for a in achados if a["nivel"] == "amarelo")
    qtd_verde = sum(1 for a in achados if a["nivel"] == "verde")
    
    relatorio = f"""# 🛡️ Relatório de Auditoria de Privacidade (LGPD) — Termo Claro

- **Aplicativo / Serviço:** {nome}
- **Data da Auditoria:** {data_hora}
- **Metodologia:** Análise automatizada via IA Local e Motor de Regras da Lei 13.709/2018 (LGPD)

---

## 📋 Resumo Executivo para o Titular
{resumo}

---

## 🚦 Placar Geral de Riscos
- 🔴 **Riscos ao Titular:** {qtd_vermelho}
- 🟡 **Cláusulas Vagas ou Incompletas:** {qtd_amarelo}
- 🟢 **Práticas Adequadas à LGPD:** {qtd_verde}

---

## 🔍 Detalhamento das Práticas Identificadas
"""
    for item in achados:
        emoji = NIVEIS.get(item["nivel"], {}).get("emoji", "⚪")
        label = NIVEIS.get(item["nivel"], {}).get("label", "Desconhecido")
        artigos = " · ".join(item.get("artigos", []))
        
        relatorio += f"\n### {emoji} {item['categoria']} — ({label})\n"
        relatorio += f"- **Avaliação Técnica:** {item['justificativa']}\n"
        relatorio += f"- **Base Legal (LGPD):** `{artigos}`\n"
        if item.get("trecho"):
            relatorio += f"- **Trecho Literal do Documento:**\n> \"{item['trecho']}\"\n"

    if nao_mencionadas:
        relatorio += "\n---\n\n## ℹ️ Práticas Não Mencionadas no Documento\n"
        relatorio += "As seguintes práticas da taxonomia não foram identificadas ou citadas explicitamente no texto analisado:\n"
        for nm in nao_mencionadas:
            relatorio += f"- **{nm['categoria']}** (LGPD: {' · '.join(nm.get('artigos', []))})\n"

    relatorio += """
---
*⚠️ Aviso Legal: Este relatório possui finalidade exclusivamente orientadora e educacional baseada em IA, não substituindo parecer ou consultoria jurídica formal.*
"""
    return relatorio

# Barra lateral (Sidebar) para entrada de dados
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("Termo Claro")
    st.caption("Auditoria de Privacidade & LGPD com IA Local")
    st.divider()

    nome_app_input = st.text_input(
        "Nome do Aplicativo ou Serviço:",
        value="",
        placeholder="Deixe em branco para detecção automática"
    )
    
    tipo_entrada = st.radio(
        "Como deseja fornecer a política?",
        ["📁 Carregar Arquivo", "🔗 Inserir Link (URL)", "✍️ Colar Texto Manual"],
        help="Opção 1 aceita PDF, HTML, HTM, Markdown (.md) e Texto (.txt)"
    )
    
    texto_para_analise = ""
    nome_detectado_auto = ""
    
    if tipo_entrada == "📁 Carregar Arquivo":
        arquivo = st.file_uploader(
            "Selecione um arquivo de política:",
            type=["pdf", "html", "htm", "md", "txt", "markdown"],
            help="Formatos aceitos: PDF, HTML, HTM, Markdown (.md) e Texto (.txt)"
        )
        if arquivo is not None:
            nome_detectado_auto = limpar_nome_sugerido(arquivo.name)
            try:
                with st.spinner("Lendo e extraindo conteúdo do arquivo..."):
                    texto_para_analise = extrair_arquivo(arquivo)
                st.success(f"Arquivo lido com sucesso! ({len(texto_para_analise)} caracteres)")
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
                
    elif tipo_entrada == "🔗 Inserir Link (URL)":
        url_input = st.text_input(
            "Cole o link direto da política de privacidade:",
            placeholder="https://exemplo.com.br/politica-de-privacidade"
        )
        if url_input.strip():
            texto_para_analise = url_input.strip()
            nome_detectado_auto = inferir_nome_de_url(texto_para_analise)
            
    elif tipo_entrada == "✍️ Colar Texto Manual":
        texto_colado = st.text_area(
            "Cole o texto da política aqui:",
            height=250,
            placeholder="Exemplo: Coletamos dados como nome, e-mail e localização em segundo plano...",
        )
        if texto_colado.strip():
            texto_para_analise = texto_colado.strip()
            # Tenta pegar a primeira linha caso seja um título
            primeira_linha = texto_colado.strip().split("\n")[0][:60]
            if "politica" in primeira_linha.lower() or "privacidade" in primeira_linha.lower():
                nome_detectado_auto = limpar_nome_sugerido(primeira_linha)

    # Define o nome final: digitado pelo usuário ou detectado automaticamente
    nome_final_app = nome_app_input.strip() if nome_app_input.strip() else (nome_detectado_auto or "Aplicativo Analisado")

    analisar_btn = st.button("🚀 Analisar Política", type="primary", use_container_width=True)
    
    st.divider()
    st.info("🔒 **Privacidade Total:** Processamento 100% local via Ollama na GPU, sem tráfego de dados para a nuvem.", icon="🔒")

# Cabeçalho Principal
st.title("🛡️ Termo Claro — Auditoria de Termos à Luz da LGPD")
st.markdown(f"Analisando: **{nome_final_app}** · Identifique cláusulas abusivas, dados excessivos e riscos ao titular.")

st.warning("⚠️ **Aviso Educacional:** Esta ferramenta orienta e identifica riscos preliminares com IA, mas **não substitui uma consulta ou parecer jurídico formal**.", icon="⚠️")

# Fluxo de Análise
if analisar_btn:
    if not texto_para_analise.strip():
        st.warning("Por favor, selecione um arquivo, informe uma URL ou cole um texto antes de analisar.")
        st.stop()

    with st.spinner("⏳ Extraindo e normalizando o texto..."):
        try:
            texto_limpo = extrair(texto_para_analise)
        except Exception as e:
            st.error(f"Erro ao extrair texto da fonte: {e}")
            st.stop()

    if len(texto_limpo) < 40:
        st.error("O texto extraído é curto demais para uma política de privacidade válida. Verifique a entrada e tente novamente.")
        st.stop()

    with st.spinner(f"🧠 Analisando cláusulas de '{nome_final_app}' com a IA local na GPU..."):
        todos_achados = analisar(texto_limpo)

    if not todos_achados:
        st.warning("A IA não retornou categorias estruturadas. Tente novamente.")
        st.stop()

    # Separação inteligente: O que foi identificado vs o que não foi mencionado
    achados_relevantes = [
        a for a in todos_achados 
        if a.get("presente") is True and a.get("nivel") in ("vermelho", "amarelo", "verde")
    ]
    
    # As categorias da taxonomia que não foram citadas no texto entram como 'não mencionadas'
    ids_encontrados = {a["id"] for a in achados_relevantes}
    achados_nao_mencionados = [
        {
            "id": c["id"],
            "categoria": c["nome"],
            "artigos": c.get("artigos", []),
        }
        for c in src.taxonomia.CATEGORIAS
        if c["id"] not in ids_encontrados
    ]

    # 1. Resumo em Linguagem Simples
    with st.spinner("✍️ Gerando resumo amigável para leigos..."):
        texto_resumo = resumir(nome_final_app, achados_relevantes if achados_relevantes else todos_achados)

    st.subheader(f"📋 Resumo da Política — {nome_final_app}")
    st.info(texto_resumo, icon="💬")

    # 2. Painel de Métricas (Semáforo de Riscos)
    st.subheader("🚦 Diagnóstico de Riscos Encontrados")
    c1, c2, c3 = st.columns(3)
    
    qtd_vermelho = sum(1 for a in achados_relevantes if a["nivel"] == "vermelho")
    qtd_amarelo = sum(1 for a in achados_relevantes if a["nivel"] == "amarelo")
    qtd_verde = sum(1 for a in achados_relevantes if a["nivel"] == "verde")

    c1.metric(label="🔴 Risco ao Titular", value=qtd_vermelho)
    c2.metric(label="🟡 Vago ou Incompleto", value=qtd_amarelo)
    c3.metric(label="🟢 Adequado à LGPD", value=qtd_verde)

    st.divider()

    # 3. Relatório Detalhado por Categoria (Apenas as identificadas)
    st.subheader(f"🔍 Práticas Identificadas no Texto ({len(achados_relevantes)})")
    
    # Ordena: Vermelhos primeiro, depois amarelos, depois verdes
    ordem_risco = {"vermelho": 0, "amarelo": 1, "verde": 2}
    achados_ordenados = sorted(achados_relevantes, key=lambda x: ordem_risco.get(x["nivel"], 3))

    if achados_ordenados:
        for item in achados_ordenados:
            nivel_info = NIVEIS.get(item["nivel"], {"emoji": "⚪", "label": "Desconhecido"})
            titulo_expander = f"{nivel_info['emoji']} {item['categoria']} — ({nivel_info['label']})"
            
            with st.expander(titulo_expander, expanded=(item["nivel"] == "vermelho")):
                st.markdown(f"**Avaliação da IA:** {item['justificativa']}")
                
                if item.get("trecho"):
                    st.markdown("**Trecho literal extraído do documento:**")
                    st.info(f'"{item["trecho"]}"')
                    
                artigos_str = " · ".join(item.get("artigos", []))
                st.caption(f"⚖️ **Artigos aplicáveis da LGPD:** {artigos_str}")
    else:
        st.write("Nenhuma prática com risco foi identificada com clareza no texto fornecido.")

    # 4. Práticas Não Mencionadas (Discretas no final, para não poluir a tela)
    if achados_nao_mencionados:
        with st.expander(f"ℹ️ Práticas Não Mencionadas ou Omitidas nesta Política ({len(achados_nao_mencionados)})"):
            st.caption("As categorias abaixo não foram detectadas no texto ou não foram citadas pela empresa:")
            cols = st.columns(2)
            for idx, nm in enumerate(achados_nao_mencionados):
                artigos_nm = " · ".join(nm.get("artigos", []))
                with cols[idx % 2]:
                    st.markdown(f"• **{nm['categoria']}** *(LGPD: {artigos_nm})*")

    st.divider()

    # 5. Botão para Download do Mini Relatório
    conteudo_download = gerar_conteudo_relatorio(
        nome=nome_final_app,
        achados=achados_ordenados,
        resumo=texto_resumo,
        nao_mencionadas=achados_nao_mencionados
    )
    
    nome_arquivo_md = f"relatorio_{nome_final_app.lower().replace(' ', '_')}.md"
    
    st.download_button(
        label=f"📥 Baixar Relatório Completo ({nome_final_app}.md)",
        data=conteudo_download.encode("utf-8"),
        file_name=nome_arquivo_md,
        mime="text/markdown",
        type="secondary",
        use_container_width=True
    )
