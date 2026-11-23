# -*- coding: utf-8 -*-
"""Termo Claro — Interface Web em Streamlit.

Leitor e tradutor de políticas de privacidade e termos de uso à luz da LGPD.
"""
import streamlit as st
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

# Estilização complementar - Largura customizada da Sidebar para não quebrar texto
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

# Barra lateral (Sidebar) para entrada de dados
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("Termo Claro")
    st.caption("Auditoria de Privacidade & LGPD com IA")
    st.divider()

    nome_app = st.text_input("Nome do Aplicativo ou Serviço:", placeholder="Meta / Google / Microsoft")
    
    tipo_entrada = st.radio(
        "Como deseja fornecer a política?",
        ["📁 Carregar Arquivo", "🔗 Inserir Link (URL)", "✍️ Colar Texto Manual"]
    )
    
    texto_para_analise = ""
    
    if tipo_entrada == "📁 Carregar Arquivo":
        arquivo = st.file_uploader(
            "Selecione um arquivo de política:",
            type=["pdf", "html", "htm", "md", "txt", "markdown"],
            help="Formatos aceitos: PDF, HTML, HTM, Markdown (.md) e Texto (.txt)"
        )
        if arquivo is not None:
            try:
                with st.spinner("Lendo e extraindo conteúdo do arquivo..."):
                    texto_para_analise = extrair_arquivo(arquivo)
                st.success(f"Arquivo lido com sucesso! ({len(texto_para_analise)} caracteres extraídos)")
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {e}")
                
    elif tipo_entrada == "🔗 Inserir Link (URL)":
        url_input = st.text_input(
            "Cole o link direto da política de privacidade:",
            placeholder="https://exemplo.com.br/politica-de-privacidade"
        )
        if url_input.strip():
            texto_para_analise = url_input.strip()
            
    elif tipo_entrada == "✍️ Colar Texto Manual":
        texto_colado = st.text_area(
            "Cole o texto da política aqui:",
            height=250,
            placeholder="Exemplo: Coletamos dados como nome, e-mail e localização em segundo plano...",
        )
        if texto_colado.strip():
            texto_para_analise = texto_colado.strip()

    analisar_btn = st.button("Analisar Política", type="primary", use_container_width=True)
    
    st.divider()
    st.info("**Privacidade Total:** Os dados são processados 100% na sua máquina via Ollama e GPU, sem envio para servidores externos.", icon="🔒")

# Cabeçalho Principal
st.title("🛡️ Termo Claro — Auditoria de Termos à Luz da LGPD")
st.markdown("Identifique cláusulas abusivas, dados excessivos e riscos ao titular em linguagem acessível.")

st.warning("**Aviso Educacional:** Esta ferramenta orienta e identifica riscos preliminares com IA, mas **não substitui uma consulta ou parecer jurídico formal**.", icon="⚠️")

# Fluxo de Análise
if analisar_btn:
    if not texto_para_analise.strip():
        st.warning("Por favor, selecione um arquivo, informe uma URL ou cole um texto antes de analisar.")
        st.stop()

    with st.spinner("⏳ Extraindo e normalizando o texto..."):
        try:
            # Se for URL, extrai pela rede; se já for texto extraído do arquivo, apenas limpa
            texto_limpo = extrair(texto_para_analise)
        except Exception as e:
            st.error(f"Erro ao extrair texto da fonte: {e}")
            st.stop()

    if len(texto_limpo) < 40:
        st.error("O texto extraído é curto demais para uma política de privacidade válida. Verifique a entrada e tente novamente.")
        st.stop()

    with st.spinner("🧠 Analisando cláusulas com a IA local na GPU (Qwen 2.5 3B)..."):
        achados = analisar(texto_limpo)

    if not achados:
        st.warning("A IA não retornou categorias estruturadas. Tente novamente.")
        st.stop()

    # 1. Resumo em Linguagem Simples
    with st.spinner("✍️ Gerando resumo amigável para leigos..."):
        texto_resumo = resumir(nome_app, achados)

    st.subheader("📋 Resumo para o Usuário")
    st.info(texto_resumo, icon="💬")

    # 2. Painel de Métricas (Semáforo de Riscos)
    st.subheader("🚦 Diagnóstico de Riscos")
    c1, c2, c3 = st.columns(3)
    
    qtd_vermelho = sum(1 for a in achados if a["nivel"] == "vermelho")
    qtd_amarelo = sum(1 for a in achados if a["nivel"] == "amarelo")
    qtd_verde = sum(1 for a in achados if a["nivel"] == "verde")

    c1.metric(label="🔴 Risco ao Titular", value=qtd_vermelho)
    c2.metric(label="🟡 Vago ou Incompleto", value=qtd_amarelo)
    c3.metric(label="🟢 Adequado à LGPD", value=qtd_verde)

    st.divider()

    # 3. Relatório Detalhado por Categoria
    st.subheader("🔍 Detalhamento por Categoria da LGPD")
    
    # Ordena: Vermelhos primeiro, depois amarelos, depois verdes
    ordem_risco = {"vermelho": 0, "amarelo": 1, "verde": 2}
    achados_ordenados = sorted(achados, key=lambda x: ordem_risco.get(x["nivel"], 3))

    for item in achados_ordenados:
        nivel_info = NIVEIS.get(item["nivel"], {"emoji": "⚪", "label": "Desconhecido"})
        titulo_expander = f"{nivel_info['emoji']} {item['categoria']} — ({nivel_info['label']})"
        
        with st.expander(titulo_expander, expanded=(item["nivel"] == "vermelho")):
            st.markdown(f"**Avaliação da IA:** {item['justificativa']}")
            
            if item.get("trecho"):
                st.markdown("**Trecho extraído do documento:**")
                st.info(f'"{item["trecho"]}"')
                
            artigos_str = " · ".join(item.get("artigos", []))
            st.caption(f"⚖️ **Artigos aplicáveis da LGPD:** {artigos_str}")
