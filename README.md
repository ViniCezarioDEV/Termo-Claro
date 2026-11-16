# 📄 Termo Claro

> **Leitor inteligente de políticas de privacidade e termos de uso à luz da LGPD, com IA local e open source.**

O **Termo Claro** é uma ferramenta de IA que lê a política de privacidade ou os termos de uso de um aplicativo e traduz, em português simples e direto, o que acontece com os dados do usuário: o que é coletado, com quem é compartilhado, uso de localização ou dados sensíveis, tempo de retenção e direitos do titular.

Cada cláusula analisada recebe um nível de risco visual e é vinculada diretamente aos artigos correspondentes da **Lei Geral de Proteção de Dados (Lei nº 13.709/2018)**.

---

## 🎯 Por que o projeto existe?

1. **Ninguém lê os termos que aceita:** Pesquisas indicam que ler todas as políticas de serviços que um usuário aceita em um ano levaria mais de 200 horas (~76 dias úteis).
2. **A lei exige clareza, mas a prática entrega burocracia:** A LGPD garante o princípio da transparência (art. 6º, VI), mas a maioria dos termos é redigida em "juridiquês" genérico e ambíguo.
3. **Privacidade por Projeto (*Privacy by Design*):** A análise é executada **100% localmente no computador do usuário** (via Ollama e modelos compactos de 4B). Nenhum texto do usuário é enviado para APIs externas na nuvem.

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

## 🛠️ Arquitetura e Tecnologias

```
Entrada (URL / PDF / HTML / Texto)
                │
                ▼
      [ 1. src/extracao.py ]       --> Limpeza e raspagem com Trafilatura / BeautifulSoup / PyPDF
                │
                ▼
     [ 2. src/segmentacao.py ]     --> Fatiamento em trechos semânticos com pontuação
                │
                ▼
     [ 3. src/analise_llm.py ]     --> LLM Local (Ollama + Qwen 4B) com saída estrita em JSON
                │
                ▼
       [ 4. src/regras.py ]        --> Motor de regras determinístico para mitigar termos vagos
                │
                ▼
       [ 5. src/resumo.py ]        --> Resumo leigo em linguagem simples
                │
                ▼
          [ 6. app.py ]            --> Painel visual interativo em Streamlit
```

- **Linguagem:** Python 3.12
- **IA Local:** [Ollama](https://ollama.com/) com `qwen3:4b` ou `qwen2.5:3b`
- **Interface Web:** Streamlit
- **Processamento de Texto:** Trafilatura, BeautifulSoup4, PyPDF
- **Machine Learning & Ciência de Dados:** Scikit-Learn, Pandas, NumPy, Joblib

---

## 📂 Estrutura de Pastas

```text
D:\Vinas\IA\
├── docs/                      # Proposta em HTML, slides e guia de implementação
├── src/                       # Código-fonte da inteligência do sistema
│   ├── __init__.py
│   ├── taxonomia.py          # As 12 categorias e artigos da LGPD (Fonte da verdade)
│   ├── extracao.py           # Leitor de URLs, PDFs, HTML e texto puro
│   ├── segmentacao.py        # Divisão inteligente do texto em trechos analisáveis
│   ├── regras.py             # Motor de regras determinísticas e termos vagos
│   ├── analise_llm.py        # Integração com Ollama para classificação
│   ├── resumo.py             # Geração do resumo leigo
│   └── classificador.py      # Baseline TF-IDF + Regressão Logística
├── data/
│   ├── opp115/               # Dataset internacional de treino
│   └── corpus_br/            # Políticas de apps brasileiros anotadas
├── modelos/                   # Modelos treinados (.joblib)
├── resultados/                # Relatórios de métricas e avaliação
├── tests/                     # Testes unitários
├── app.py                     # Interface gráfica (Streamlit)
├── requirements.txt           # Dependências do projeto
├── .gitignore                 # Arquivos ignorados pelo Git
└── README.md                  # Este documento
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- **Python 3.12+**
- **Git**
- **Ollama** instalado e rodando

### 1. Clonar e preparar o ambiente virtual
```powershell
# Ativar o ambiente virtual
.\.venv\Scripts\Activate.ps1

# Instalar as dependências
pip install -r requirements.txt
```

### 2. Baixar o modelo de IA no Ollama
```powershell
ollama pull qwen3:4b
```

### 3. Rodar a aplicação Web
```powershell
streamlit run app.py
```
O painel abrirá automaticamente no seu navegador em `http://localhost:8501`.

---

## ⚖️ Aviso Legal
O **Termo Claro** é um projeto educacional e acadêmico de auxílio à conscientização de privacidade e segurança. As análises emitidas pela IA têm caráter exclusivamente informativo e orientador, **não substituindo parecer ou consultoria jurídica formal**.

---

## 📝 Licença
Distribuído sob a licença **MIT**. Consulte `LICENSE` para mais informações.
