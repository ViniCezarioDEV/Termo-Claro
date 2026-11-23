# 📄 Termo Claro

> **Leitor inteligente de políticas de privacidade e termos de uso à luz da LGPD, com IA local e open source.**

O **Termo Claro** é uma solução de auditoria e tradução de políticas de privacidade para a linguagem do cidadão comum. Utilizando Inteligência Artificial executada **100% localmente na máquina do usuário** (via Ollama e modelos compactos de 3B/4B na GPU), a ferramenta varre contratos e termos de serviço, identifica cláusulas abusivas, alerta para riscos à privacidade e associa cada ponto aos artigos da **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)**.

---

## 🎯 Por que o projeto existe?

1. **Ninguém lê os termos que aceita:** Pesquisas indicam que ler todas as políticas de serviços que um usuário aceita em um ano levaria mais de 200 horas (~76 dias úteis).
2. **A lei exige clareza, mas a prática entrega burocracia:** A LGPD garante o princípio da transparência (art. 6º, VI), mas a maioria dos termos é redigida em "juridiquês" genérico e ambíguo.
3. **Privacidade por Projeto (*Privacy by Design*):** A análise é executada **localmente na GPU**. Nenhum dado, documento ou termo enviado pelo usuário sai da máquina.

---

## 🚦 Semáforo de Risco

| Alerta | Significado | Exemplo Prático |
|:---:|---|---|
| 🟢 | **Adequado** | Finalidade clara, base legal informada e canal de contato explícito. |
| 🟡 | **Vago ou Incompleto** | Uso de termos ambíguos (*"podemos coletar"*, *"parceiros comerciais"*, *"de tempos em tempos"*). |
| 🔴 | **Risco ao Titular** | Coleta excessiva sem finalidade, retenção "por tempo indeterminado" ou alteração de termos sem aviso. |

---

## 🏛️ As 12 Categorias da Taxonomia LGPD

O coração do sistema é uma taxonomia que adapta o dataset acadêmico mundial **OPP-115** para os artigos da lei brasileira:

1. **Coleta e uso pelo app** *(art. 6º I-III, art. 7º)*
2. **Compartilhamento com terceiros** *(art. 7º §5º, art. 9º V)*
3. **Localização geográfica** *(art. 6º III, art. 9º)*
4. **Dados sensíveis** *(art. 5º II, art. 11)*
5. **Escolhas e consentimento** *(art. 8º, art. 18 IX)*
6. **Direitos do titular** *(art. 18)*
7. **Retenção de dados** *(art. 15, art. 16)*
8. **Segurança e incidentes** *(art. 46, art. 48)*
9. **Crianças e adolescentes** *(art. 14)*
10. **Transferência internacional** *(art. 33)*
11. **Mudanças na política** *(art. 8º §6º, art. 9º §2º)*
12. **Encarregado de dados (DPO)** *(art. 41)*

---

## 🛠️ Recursos e Funcionalidades

- **Extração Multiformato Unificada:** Suporta upload direto de arquivos em **PDF, HTML, HTM, Markdown (.md), Texto (.txt)** ou inserção de **URLs diretas**.
- **Detecção Automática do Nome do App:** Se o usuário não preencher o nome, o sistema infere automaticamente a partir do nome do arquivo, domínio da URL ou cabeçalhos.
- **Filtro Inteligente de Visualização:** Práticas não citadas não poluem o relatório principal e são agrupadas em uma gaveta informativa secundária.
- **Exportação de Relatórios:** Botão integrado para baixar o relatório completo da auditoria em formato **Markdown (.md)** com carimbo de data/hora.
- **Pipeline Híbrido (LLM + Regras):** LLM local para classificação semântica e motor determinístico que rebaixa para amarelo textos cheios de termos vagos.
- **Trilha Científica Automatizada:** Script `avaliar_opp115.py` para medir F1-Score contra o gabarito humano da Carnegie Mellon University.

---

## 📂 Estrutura do Repositório

```text
D:\Vinas\IA\
├── docs/                      # Documentação formal e guias do projeto
│   ├── GUIA_ANOTACAO_CLAUDE.md # Prompt oficial para anotação assistida com Claude
│   ├── GUIA_PASSO_A_PASSO_Termo_Claro.md
│   └── termo-claro.html
├── src/                       # Núcleo da inteligência do sistema
│   ├── __init__.py
│   ├── taxonomia.py          # As 12 categorias e artigos da LGPD (Fonte da verdade)
│   ├── extracao.py           # Parser universal (.pdf, .html, .md, .txt, URLs)
│   ├── segmentacao.py        # Divisão inteligente do texto em blocos semânticos
│   ├── regras.py             # Motor determinístico de detecção de termos vagos
│   ├── analise_llm.py        # Integração com Ollama (Qwen 2.5 3B na GPU)
│   └── resumo.py             # Geração do resumo leigo em linguagem simples
├── data/
│   ├── opp115/               # Dataset internacional oficial anotado por advogados
│   └── corpus_br/            # Corpus brasileiro
│       ├── brutos/           # Políticas reais brasileiras (Nubank, iFood, Google, etc.)
│       └── anotado/          # Gabarito oficial em CSV (gerado via Claude / Especialistas)
├── resultados/                # Relatórios de métricas e F1-Score
│   └── f1_score_opp115.md
├── app.py                     # Aplicação Web (Streamlit)
├── avaliar_opp115.py          # Script de cálculo de métricas científicas (F1 Macro/Micro)
├── requirements.txt           # Dependências do projeto
├── .gitignore                 # Arquivos ignorados pelo Git
└── README.md                  # Este documento
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- **Python 3.12+**
- **Ollama** com o modelo `qwen2.5:3b` baixado (`ollama pull qwen2.5:3b`)

### 1. Ativar o ambiente virtual e instalar dependências
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Rodar a aplicação Web (Streamlit)
```powershell
streamlit run app.py
```
O painel abrirá automaticamente no seu navegador em `http://localhost:8501`.

### 3. Rodar a Avaliação Científica de F1-Score (OPP-115)
```powershell
python avaliar_opp115.py
```

---

## 📊 Avaliação Científica e Métricas (F1-Score)

Para garantir rigor acadêmico, o classificador do **Termo Claro** é avaliado matematicamente contra anotações humanas especializadas.

### O que mede o F1-Score?
O **F1-Score** é a média harmônica entre a **Precisão** (quando a IA aponta um risco, quão certa ela está?) e a **Revocação / Recall** (de todos os riscos reais existentes no contrato, quantos a IA conseguiu capturar?).

### Resultados do Benchmark (Baseline no OPP-115)
Abaixo estão os resultados empíricos obtidos na execução local contra o gabarito humano oficial da Universidade Carnegie Mellon:

- **Modelo:** `qwen2.5:3b`
- **Revocação Global (*Recall*):** **62.0%** (a IA capturou mais da metade de todas as cláusulas reais)
- **F1-Score Macro:** **36.1%** (0.361)
- **F1-Score Micro:** **34.7%** (0.347)

#### Desempenho por Categoria de Prática de Dados:
| Categoria | Precisão | Revocação (*Recall*) | F1-Score | Destaque |
|---|:---:|:---:|:---:|---|
| **Crianças e Adolescentes** | 1.00 | 1.00 | **1.00 (100%)** | 🎯 Acerto perfeito em todas as cláusulas |
| **Mudanças na Política** | 0.75 | 1.00 | **0.86 (86%)** | 🚀 Alta capacidade de identificar alterações de termos |
| **Segurança e Incidentes** | 0.38 | 1.00 | **0.55 (55%)** | 🛡️ Captura 100% dos trechos de segurança |
| **Coleta e Uso** | 0.18 | 1.00 | **0.30 (30%)** | 📋 Ampla captura de cláusulas de coleta |
| **Escolhas e Consentimento**| 0.12 | 0.33 | **0.18 (18%)** | ⚖️ Detecção de regras de consentimento |

> *Os relatórios detalhados gerados por execução são armazenados de forma reprodutível em `resultados/f1_score_opp115.md`.*

---

## 📦 Download do Dataset OPP-115

O projeto utiliza o dataset **OPP-115** (*Online Privacy Policies 115*) da Universidade Carnegie Mellon:
- **Link Direto para Download:** [OPP-115_v1_0.zip](https://usableprivacy.org/static/data/OPP-115_v1_0.zip)
- **Instruções:** Baixe o arquivo `.zip` e descompacte o conteúdo diretamente dentro da pasta `data/opp115/`.

---

## ⚖️ Aviso Legal
O **Termo Claro** é um projeto educacional e acadêmico de auxílio à conscientização de privacidade e segurança. As análises emitidas pela IA têm caráter exclusivamente informativo e orientador, **não substituindo parecer ou consultoria jurídica formal**.

---

## 📝 Licença
Distribuído sob a licença **MIT**.
