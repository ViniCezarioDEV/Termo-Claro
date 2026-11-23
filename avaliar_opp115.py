# -*- coding: utf-8 -*-
"""Avaliação científica do classificador no dataset OPP-115 (Gabarito Humano).

Lê as anotações consolidadas do OPP-115 (anotadas por advogados),
extrai uma amostra de teste balanceada, classifica com o Qwen 2.5 3B local na GPU,
e gera o relatório completo de métricas com F1-Score (Macro e Micro).
"""
import glob
import json
import os
import re
import ollama
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import MultiLabelBinarizer
from src.taxonomia import IDS, POR_ID

MODELO = "qwen2.5:3b"

# Mapeamento oficial entre as categorias do OPP-115 e as nossas 12 categorias
MAPA_OPP_PARA_NOSSO = {
    "First Party Collection/Use": "coleta_uso",
    "Third Party Sharing/Collection": "compartilhamento",
    "User Choice/Control": "consentimento",
    "User Access, Edit and Deletion": "direitos_titular",
    "Data Retention": "retencao",
    "Data Security": "seguranca",
    "Policy Change": "mudancas",
    "International and Specific Audiences": "criancas",
}

def carregar_amostra_opp115(limite_por_categoria: int = 4) -> list[dict]:
    """Carrega trechos e gabarito humano consolidado do OPP-115."""
    pasta_consolidados = "data/opp115/consolidation/threshold-0.5-overlap-similarity"
    pasta_textos = "data/opp115/sanitized_policies"
    
    arquivos_csv = glob.glob(os.path.join(pasta_consolidados, "*.csv"))
    
    amostras_por_cat = {cat: [] for cat in MAPA_OPP_PARA_NOSSO.values()}
    total_carregados = []
    
    for arq_csv in arquivos_csv[:15]: # Analisa as primeiras 15 políticas
        nome_base = os.path.splitext(os.path.basename(arq_csv))[0]
        arq_html = os.path.join(pasta_textos, f"{nome_base}.html")
        
        if not os.path.isfile(arq_html):
            continue
            
        with open(arq_html, "r", encoding="utf-8", errors="ignore") as f:
            conteudo_html = f.read()
            
        # No OPP-115, os segmentos são separados por |||
        segmentos_brutos = conteudo_html.split("|||")
        segmentos = []
        for s in segmentos_brutos:
            limpo = re.sub(r"<[^>]+>", " ", s)
            limpo = re.sub(r"\s+", " ", limpo).strip()
            segmentos.append(limpo)
            
        # Lê as anotações
        with open(arq_csv, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                partes = linha.strip().split(",")
                if len(partes) < 6:
                    continue
                try:
                    seg_id = int(partes[4])
                    categoria_opp = partes[5].strip()
                except ValueError:
                    continue
                    
                if categoria_opp in MAPA_OPP_PARA_NOSSO and seg_id < len(segmentos):
                    cat_nossa = MAPA_OPP_PARA_NOSSO[categoria_opp]
                    trecho = segmentos[seg_id]
                    
                    if len(trecho) >= 50 and len(amostras_por_cat[cat_nossa]) < limite_por_categoria:
                        # Evita duplicatas exatas de trecho
                        if not any(t["trecho"] == trecho for t in total_carregados):
                            item = {
                                "trecho": trecho[:600],
                                "categoria_humana": cat_nossa,
                                "categoria_opp": categoria_opp
                            }
                            amostras_por_cat[cat_nossa].append(item)
                            total_carregados.append(item)
                            
        # Se já preencheu todas as categorias, pode parar
        if all(len(itens) >= limite_por_categoria for itens in amostras_por_cat.values()):
            break
            
    return total_carregados

def classificar_trecho_ia(trecho: str) -> list[str]:
    """Envia o trecho para o Qwen local e extrai as categorias previstas."""
    prompt = (
        "Classifique o parágrafo de política de privacidade abaixo em uma ou mais destas categorias:\n"
        "- coleta_uso (coleta de dados pelo próprio serviço)\n"
        "- compartilhamento (envio de dados a terceiros ou parceiros)\n"
        "- consentimento (escolhas, autorização ou revogação)\n"
        "- direitos_titular (acesso, exclusão, correção dos dados)\n"
        "- retencao (tempo que os dados ficam armazenados)\n"
        "- seguranca (medidas técnicas de proteção contra vazamentos)\n"
        "- mudancas (como alterações nos termos são informadas)\n"
        "- criancas (regras sobre menores de idade)\n\n"
        f"Texto do parágrafo:\n\"{trecho}\"\n\n"
        "Responda estritamente com JSON no formato:\n"
        "{\"categorias\": [\"id_categoria\"]}"
    )
    
    try:
        resp = ollama.chat(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            format="json",
            options={"temperature": 0}
        )
        dados = json.loads(resp["message"]["content"])
        predicoes = dados.get("categorias", [])
        return [p for p in predicoes if p in MAPA_OPP_PARA_NOSSO.values()]
    except Exception:
        return []

def executar_avaliacao():
    print("=" * 60)
    print("🧪 INICIANDO AVALIAÇÃO CIENTÍFICA (F1-SCORE NO OPP-115)")
    print("=" * 60)
    
    amostras = carregar_amostra_opp115(limite_por_categoria=3)
    print(f"-> Amostra extraída do OPP-115: {len(amostras)} trechos balanceados anotados por advogados.\n")
    
    y_true = []
    y_pred = []
    
    for i, item in enumerate(amostras, 1):
        trecho = item["trecho"]
        rotulo_humano = item["categoria_humana"]
        
        print(f"[{i}/{len(amostras)}] Avaliando trecho: {trecho[:65]}...")
        predicoes_ia = classificar_trecho_ia(trecho)
        
        # Garante fallback se a IA não retornou nada
        if not predicoes_ia:
            predicoes_ia = ["outros"]
            
        y_true.append([rotulo_humano])
        y_pred.append(predicoes_ia)
        
        acertou = rotulo_humano in predicoes_ia
        emoji = "✅" if acertou else "❌"
        print(f"      Gabarito Humano: {rotulo_humano} | IA previu: {predicoes_ia} {emoji}\n")

    # Cálculo do F1-Score com Scikit-Learn
    todas_classes = list(set(MAPA_OPP_PARA_NOSSO.values()))
    mlb = MultiLabelBinarizer(classes=todas_classes)
    Yt = mlb.fit_transform(y_true)
    Yp = mlb.fit_transform(y_pred)
    
    f1_mac = f1_score(Yt, Yp, average="macro", zero_division=0)
    f1_mic = f1_score(Yt, Yp, average="micro", zero_division=0)
    relatorio = classification_report(Yt, Yp, target_names=todas_classes, zero_division=0)
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINAIS DAS MÉTRICAS")
    print("=" * 60)
    print(f"🎯 F1-Score Macro: {f1_mac:.3f} ({f1_mac*100:.1f}%)")
    print(f"🎯 F1-Score Micro: {f1_mic:.3f} ({f1_mic*100:.1f}%)")
    print("\nDetalhamento por Categoria:\n")
    print(relatorio)
    
    # Salva o relatório formal em markdown
    os.makedirs("resultados", exist_ok=True)
    caminho_md = "resultados/f1_score_opp115.md"
    with open(caminho_md, "w", encoding="utf-8") as f:
        f.write("# 📊 Relatório de Avaliação Científica — OPP-115\n\n")
        f.write(f"- **Modelo Avaliado:** `{MODELO}` (rodando localmente na GPU)\n")
        f.write(f"- **Base de Comparação (Ground Truth):** OPP-115 Corpus (anotações de especialistas da Carnegie Mellon)\n")
        f.write(f"- **Tamanho da Amostra:** {len(amostras)} trechos multirrótulo balanceados\n\n")
        f.write(f"### 🎯 Índices Globais\n")
        f.write(f"- **F1-Score Macro:** **{f1_mac:.3f}** ({f1_mac*100:.1f}%)\n")
        f.write(f"- **F1-Score Micro:** **{f1_mic:.3f}** ({f1_mic*100:.1f}%)\n\n")
        f.write("### 📋 Tabela de Classificação por Categoria\n```\n")
        f.write(relatorio)
        f.write("```\n")
        
    print(f"\n📄 Relatório salvo com sucesso em: {caminho_md}")

if __name__ == "__main__":
    executar_avaliacao()
