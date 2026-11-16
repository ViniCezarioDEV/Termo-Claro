# Termo Claro — Guia passo a passo (do zero à entrega)

> Leitor de políticas de privacidade à luz da LGPD, com IA local e open source.
> Este guia é **config por config**. Siga de cima para baixo. Cada bloco de código tem onde salvar e como testar.

**Convenção:** tudo que estiver em `powershell` você roda no PowerShell. Tudo que for arquivo tem o caminho completo no título (ex.: `C:\dev\termo-claro\src\taxonomia.py`).

**Caminhos oficiais do projeto:**
- Código: `C:\dev\termo-claro` (local, versionado em git)
- Documentos (pptx, docx, este guia): `D:\Meu Drive\AI\termo-claro` (Drive, backup)

> ⚠️ **Nunca** coloque a `.venv` nem os modelos dentro do Google Drive — o sync corrompe. Código no `C:\dev`, docs no Drive.

---

## Sumário

- [Parte 0 — Entender o que vamos construir](#parte-0--entender-o-que-vamos-construir)
- [Parte 1 — Preparar a máquina (do zero)](#parte-1--preparar-a-máquina-do-zero)
- [Parte 2 — Criar o projeto](#parte-2--criar-o-projeto)
- [Parte 3 — Arquivos de configuração](#parte-3--arquivos-de-configuração)
- [Parte 4 — A taxonomia (coração do projeto)](#parte-4--a-taxonomia-coração-do-projeto)
- [Parte 5 — Módulos do núcleo](#parte-5--módulos-do-núcleo)
- [Parte 6 — MVP que funciona hoje (análise via LLM)](#parte-6--mvp-que-funciona-hoje-análise-via-llm)
- [Parte 7 — Interface Streamlit](#parte-7--interface-streamlit)
- [Parte 8 — Dados: OPP-115, LGPD e corpus BR](#parte-8--dados-opp-115-lgpd-e-corpus-br)
- [Parte 9 — Classificação rigorosa (baseline + transformer)](#parte-9--classificação-rigorosa-baseline--transformer)
- [Parte 10 — Avaliação e métricas](#parte-10--avaliação-e-métricas)
- [Parte 11 — Git e GitHub](#parte-11--git-e-github)
- [Parte 12 — Cronograma de 16 semanas](#parte-12--cronograma-de-16-semanas)
- [Parte 13 — Troubleshooting](#parte-13--troubleshooting)

---

## Parte 0 — Entender o que vamos construir

**Fluxo do sistema:**

```
Texto / URL / PDF
      │
      ▼
[1] Extração      → texto limpo
      │
      ▼
[2] Segmentação   → lista de trechos
      │
      ▼
[3] Classificação → cada trecho recebe 1+ das 12 categorias
      │
      ▼
[4] Motor de regras → categoria + sinais → artigo LGPD + 🟢/🟡/🔴
      │
      ▼
[5] Resumo (LLM)  → linguagem simples
      │
      ▼
[6] Relatório (Streamlit) → painel por categoria, com trecho + artigo
```

**Duas trilhas de classificação** (não se confunda):
1. **Trilha MVP (Parte 6):** análise da política inteira numa chamada ao LLM local (Ollama). Funciona **no primeiro dia**, sem dados de treino. É o que você demonstra.
2. **Trilha rigorosa (Parte 9):** TF-IDF + Regressão Logística (baseline) e BERTimbau (transformer), treinados no OPP-115. É o que gera as **métricas** da comparação acadêmica.

Faça a trilha MVP primeiro (demo andando), depois a rigorosa (ciência).

---

## Parte 1 — Preparar a máquina (do zero)

Máquina Windows recém-instalada. Abra o **PowerShell**.

### 1.1 Instalar as ferramentas
```powershell
winget install Python.Python.3.12
winget install Git.Git
winget install Ollama.Ollama
winget install Microsoft.VisualStudioCode
```

> **Por que Python 3.12 e não a mais nova?** PyTorch, Transformers e várias libs de ML ainda não publicam versões ("wheels") para o Python 3.14. Na 3.12 tudo instala liso.

**Feche e reabra o PowerShell** (pra atualizar o PATH).

### 1.2 Conferir que instalou
```powershell
py -3.12 --version     # Python 3.12.x
git --version          # git version 2.x
ollama --version       # ollama version ...
```
Se algum falhar, reinicie o computador e tente de novo.

### 1.3 Baixar o modelo de LLM local
```powershell
ollama pull qwen3:4b
ollama run qwen3:4b "responda em uma linha: tudo certo?"
```
Baixa ~3 GB e responde em CPU. Se quiser testar alternativa: `ollama pull gemma3:4b`.

> **RAM:** 8 GB é o mínimo pra rodar o modelo 4B quantizado. Se travar, feche o navegador e outros apps antes de rodar.

### 1.4 Configurar o Git (uma vez por máquina)
```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

---

## Parte 2 — Criar o projeto

### 2.1 Criar a pasta e a venv
```powershell
mkdir C:\dev\termo-claro
cd C:\dev\termo-claro
git init
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Depois de ativar, o prompt vira `(.venv) PS C:\dev\termo-claro>`.

> **Erro de permissão ao ativar?** Rode uma vez:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> e ative de novo.

### 2.2 Criar a estrutura de pastas
```powershell
mkdir src, data, data\opp115, data\corpus_br, modelos, resultados, tests
New-Item src\__init__.py -ItemType File
```

Estrutura final:
```
C:\dev\termo-claro\
├─ .venv\                   (ambiente Python — não vai pro git)
├─ data\
│  ├─ opp115\               (dataset de treino)
│  ├─ corpus_br\            (suas políticas BR anotadas)
│  └─ lgpd.txt             (texto da Lei 13.709/2018)
├─ modelos\                 (modelos treinados .joblib — não vai pro git)
├─ resultados\             (relatórios de métricas)
├─ src\
│  ├─ __init__.py
│  ├─ taxonomia.py
│  ├─ extracao.py
│  ├─ segmentacao.py
│  ├─ regras.py
│  ├─ analise_llm.py
│  ├─ resumo.py
│  └─ classificador.py
├─ tests\
├─ app.py
├─ avaliacao.py
├─ requirements.txt
├─ requirements-train.txt
├─ .gitignore
└─ README.md
```

---

## Parte 3 — Arquivos de configuração

### 3.1 `C:\dev\termo-claro\requirements.txt`
Dependências do dia a dia (MVP + interface):
```
scikit-learn
pandas
numpy
trafilatura
beautifulsoup4
lxml
pypdf
ollama
streamlit
joblib
```

### 3.2 `C:\dev\termo-claro\requirements-train.txt`
Dependências pesadas, só para a fase de fine-tune do transformer (instale depois, ou use o Colab):
```
torch
transformers
datasets
evaluate
scikit-learn
accelerate
```

### 3.3 Instalar as do dia a dia
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 `C:\dev\termo-claro\.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Modelos e artefatos pesados
modelos/
*.joblib
*.bin
*.safetensors

# Dados que não devem ir pro repo público (rever licença antes!)
data/opp115/
# O corpus BR anotado VAI pro repo (é a contribuição). Não ignore data/corpus_br/

# Sistema
.DS_Store
Thumbs.db
.vscode/
resultados/*.tmp
```

### 3.5 `C:\dev\termo-claro\README.md`
```markdown
# Termo Claro

Leitor de políticas de privacidade à luz da LGPD, com IA local e open source.
Classifica trechos por prática de dados, aponta o artigo da LGPD correspondente
e sinaliza risco (🟢 adequado / 🟡 vago / 🔴 risco) — tudo rodando localmente.

## Requisitos
- Python 3.12
- Ollama com o modelo `qwen3:4b`

## Instalação
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ollama pull qwen3:4b

## Uso
    streamlit run app.py

## Aviso
Ferramenta educacional. Orienta, não substitui parecer jurídico.

## Licença
MIT
```

---

## Parte 4 — A taxonomia (coração do projeto)

As **12 categorias**, cada uma mapeada para os artigos da LGPD e com o exemplo de alerta vermelho. Este arquivo é a **fonte única da verdade** — todos os outros módulos importam dele.

### Tabela de referência

| # | Categoria | Artigos LGPD | Exemplo de alerta 🔴 |
|---|---|---|---|
| 1 | Coleta e uso pelo app | art. 6º I-III · 7º | Coleta ampla sem finalidade definida |
| 2 | Compartilhamento com terceiros | art. 7º §5º · 9º V | "Parceiros" não identificados |
| 3 | Localização | art. 6º III · 9º | Localização contínua em 2º plano |
| 4 | Dados sensíveis | art. 5º II · 11 | Saúde/biometria sem consentimento |
| 5 | Escolhas e consentimento | art. 8º · 18 IX | Sem como revogar o consentimento |
| 6 | Direitos do titular | art. 18 | Não diz como acessar/excluir dados |
| 7 | Retenção | arts. 15 e 16 | Guarda "por tempo indeterminado" |
| 8 | Segurança e incidentes | art. 46 · 48 | Nenhuma medida de segurança citada |
| 9 | Crianças e adolescentes | art. 14 | Coleta de menores sem consentimento dos pais |
| 10 | Transferência internacional | art. 33 | Envia a outro país sem dizer qual |
| 11 | Mudanças na política | art. 8º §6º · 9º §2º | Pode mudar os termos sem avisar |
| 12 | Encarregado (DPO) | art. 41 | Não identifica o encarregado |

### `C:\dev\termo-claro\src\taxonomia.py`
```python
# -*- coding: utf-8 -*-
"""Fonte única da verdade do Termo Claro.

As 12 categorias de prática de dados, o mapeamento para a LGPD (Lei 13.709/2018)
e as palavras-chave que alimentam o motor de regras e os prompts do LLM.
"""

CATEGORIAS = [
    {
        "id": "coleta_uso",
        "nome": "Coleta e uso pelo app",
        "artigos": ["art. 6º I-III", "art. 7º"],
        "descricao": "Quais dados o app coleta e para qual finalidade.",
        "alerta_vermelho": "Coleta ampla sem finalidade definida.",
        "keywords": ["coleta", "coletamos", "informações que você fornece",
                     "dados que obtemos", "finalidade", "uso dos dados"],
    },
    {
        "id": "compartilhamento",
        "nome": "Compartilhamento com terceiros",
        "artigos": ["art. 7º §5º", "art. 9º V"],
        "descricao": "Com quem os dados são compartilhados.",
        "alerta_vermelho": "'Parceiros' ou 'terceiros' não identificados.",
        "keywords": ["compartilh", "terceiros", "parceiros", "afiliadas",
                     "fornecedores", "divulgar a"],
    },
    {
        "id": "localizacao",
        "nome": "Localização",
        "artigos": ["art. 6º III", "art. 9º"],
        "descricao": "Coleta e uso de dados de localização.",
        "alerta_vermelho": "Localização contínua em segundo plano.",
        "keywords": ["localização", "geolocalização", "GPS", "sua posição",
                     "segundo plano"],
    },
    {
        "id": "dados_sensiveis",
        "nome": "Dados sensíveis",
        "artigos": ["art. 5º II", "art. 11"],
        "descricao": "Dados de saúde, biometria, origem racial, opinião, etc.",
        "alerta_vermelho": "Saúde/biometria sem consentimento específico.",
        "keywords": ["dados sensíveis", "saúde", "biometria", "biométric",
                     "origem racial", "religião", "orientação sexual"],
    },
    {
        "id": "consentimento",
        "nome": "Escolhas e consentimento",
        "artigos": ["art. 8º", "art. 18 IX"],
        "descricao": "Como o usuário consente e como revoga.",
        "alerta_vermelho": "Não diz como revogar o consentimento.",
        "keywords": ["consentimento", "consente", "autoriza", "revogar",
                     "opt-out", "descadastr"],
    },
    {
        "id": "direitos_titular",
        "nome": "Direitos do titular",
        "artigos": ["art. 18"],
        "descricao": "Direitos de acesso, correção e exclusão.",
        "alerta_vermelho": "Não explica como acessar/excluir os dados.",
        "keywords": ["seus direitos", "acessar seus dados", "excluir",
                     "corrigir", "portabilidade", "titular"],
    },
    {
        "id": "retencao",
        "nome": "Retenção",
        "artigos": ["art. 15", "art. 16"],
        "descricao": "Por quanto tempo os dados são guardados.",
        "alerta_vermelho": "Guarda 'por tempo indeterminado'.",
        "keywords": ["retenção", "armazenamos", "guardamos", "período",
                     "pelo tempo", "indeterminado"],
    },
    {
        "id": "seguranca",
        "nome": "Segurança e incidentes",
        "artigos": ["art. 46", "art. 48"],
        "descricao": "Medidas de segurança e comunicação de incidentes.",
        "alerta_vermelho": "Nenhuma medida de segurança citada.",
        "keywords": ["segurança", "criptografia", "medidas técnicas",
                     "incidente", "vazamento", "proteção dos dados"],
    },
    {
        "id": "criancas",
        "nome": "Crianças e adolescentes",
        "artigos": ["art. 14"],
        "descricao": "Tratamento de dados de menores.",
        "alerta_vermelho": "Coleta de menores sem consentimento dos pais.",
        "keywords": ["crianças", "menores", "adolescentes", "responsáveis",
                     "18 anos", "consentimento dos pais"],
    },
    {
        "id": "transferencia_intl",
        "nome": "Transferência internacional",
        "artigos": ["art. 33"],
        "descricao": "Envio de dados para fora do país.",
        "alerta_vermelho": "Envia a outro país sem dizer qual.",
        "keywords": ["transferência internacional", "outro país", "exterior",
                     "servidores nos Estados Unidos", "fora do Brasil"],
    },
    {
        "id": "mudancas",
        "nome": "Mudanças na política",
        "artigos": ["art. 8º §6º", "art. 9º §2º"],
        "descricao": "Como mudanças na política são comunicadas.",
        "alerta_vermelho": "Pode mudar os termos sem avisar.",
        "keywords": ["alterar esta política", "mudanças", "atualizar",
                     "a qualquer momento", "sem aviso prévio"],
    },
    {
        "id": "encarregado",
        "nome": "Encarregado (DPO)",
        "artigos": ["art. 41"],
        "descricao": "Identificação do encarregado pelos dados.",
        "alerta_vermelho": "Não identifica o encarregado.",
        "keywords": ["encarregado", "DPO", "data protection officer",
                     "contato para privacidade"],
    },
]

# Índices auxiliares
POR_ID = {c["id"]: c for c in CATEGORIAS}
IDS = [c["id"] for c in CATEGORIAS]

NIVEIS = {
    "verde": {"emoji": "🟢", "label": "Adequado"},
    "amarelo": {"emoji": "🟡", "label": "Vago ou incompleto"},
    "vermelho": {"emoji": "🔴", "label": "Risco ao titular"},
}
```

**Teste rápido** (com a venv ativa):
```powershell
python -c "from src.taxonomia import CATEGORIAS; print(len(CATEGORIAS), 'categorias')"
```
Deve imprimir `12 categorias`.

---

## Parte 5 — Módulos do núcleo

### 5.1 `C:\dev\termo-claro\src\extracao.py`
Recebe texto cru, caminho de arquivo (`.pdf`/`.html`/`.txt`) ou URL e devolve texto limpo.
```python
# -*- coding: utf-8 -*-
"""Extração: transforma qualquer fonte (texto, URL, arquivo) em texto limpo."""
import os
import re

def _limpar(texto: str) -> str:
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()

def de_url(url: str) -> str:
    import trafilatura
    baixado = trafilatura.fetch_url(url)
    if not baixado:
        raise ValueError(f"Não consegui baixar: {url}")
    texto = trafilatura.extract(baixado, include_comments=False, include_tables=False)
    return _limpar(texto or "")

def de_pdf(caminho: str) -> str:
    from pypdf import PdfReader
    leitor = PdfReader(caminho)
    partes = [pagina.extract_text() or "" for pagina in leitor.pages]
    return _limpar("\n".join(partes))

def de_html(caminho: str) -> str:
    from bs4 import BeautifulSoup
    with open(caminho, encoding="utf-8", errors="ignore") as f:
        sopa = BeautifulSoup(f.read(), "lxml")
    for tag in sopa(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return _limpar(sopa.get_text(separator="\n"))

def extrair(fonte: str) -> str:
    """Detecta automaticamente o tipo da fonte."""
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
    # senão, trata como texto cru colado
    return _limpar(fonte)
```

### 5.2 `C:\dev\termo-claro\src\segmentacao.py`
Quebra o texto em trechos de tamanho de sentido.
```python
# -*- coding: utf-8 -*-
"""Segmentação: texto limpo -> lista de trechos analisáveis."""
import re

def segmentar(texto: str, min_chars: int = 40, max_chars: int = 1000) -> list[str]:
    # quebra por parágrafos (linhas em branco)
    brutos = re.split(r"\n\s*\n", texto)
    trechos: list[str] = []
    for bloco in brutos:
        bloco = bloco.strip()
        if not bloco:
            continue
        if len(bloco) <= max_chars:
            if len(bloco) >= min_chars:
                trechos.append(bloco)
            continue
        # parágrafo gigante: quebra por frases
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
```

### 5.3 `C:\dev\termo-claro\src\regras.py`
Dado um trecho e sua(s) categoria(s), anexa o artigo da LGPD e ajusta o nível com base em termos vagos.
```python
# -*- coding: utf-8 -*-
"""Motor de regras: categoria + sinais do texto -> artigo LGPD + nível de alerta."""
from src.taxonomia import POR_ID

TERMOS_VAGOS = [
    "podemos", "poderemos", "entre outros", "como por exemplo", "tais como",
    "parceiros", "terceiros", "de tempos em tempos", "a nosso critério",
    "quando necessário", "por tempo indeterminado", "a qualquer momento",
    "sem aviso", "etc",
]

def artigos_da_categoria(cat_id: str) -> list[str]:
    cat = POR_ID.get(cat_id)
    return cat["artigos"] if cat else []

def ajustar_nivel(trecho: str, nivel_sugerido: str) -> str:
    """Se o LLM disse 'verde' mas o texto está cheio de termos vagos, rebaixa p/ amarelo."""
    texto = trecho.lower()
    vagos = sum(1 for t in TERMOS_VAGOS if t in texto)
    if nivel_sugerido == "verde" and vagos >= 2:
        return "amarelo"
    return nivel_sugerido
```

### 5.4 `C:\dev\termo-claro\src\resumo.py`
Resumo em linguagem simples via Ollama (usado como camada de apresentação).
```python
# -*- coding: utf-8 -*-
"""Resumo em linguagem simples a partir dos trechos já classificados."""
import ollama

MODELO = "qwen3:4b"

def resumir(nome_app: str, achados: list[dict]) -> str:
    """achados: lista de {categoria, nivel, trecho}."""
    linhas = [f"- [{a['nivel']}] {a['categoria']}: {a['trecho'][:200]}" for a in achados]
    prompt = (
        "Você explica políticas de privacidade para leigos, em português claro.\n"
        f"App analisado: {nome_app}\n"
        "Com base nos pontos abaixo, escreva um resumo de 4 a 6 frases dizendo "
        "o que acontece com os dados do usuário e o que merece atenção. "
        "Não invente nada além dos pontos. Não use juridiquês.\n\n"
        + "\n".join(linhas)
    )
    resp = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.2},
    )
    return resp["message"]["content"].strip()
```

---

## Parte 6 — MVP que funciona hoje (análise via LLM)

Esta é a peça que faz o sistema andar **sem dados de treino**. Uma chamada ao LLM analisa a política inteira contra as 12 categorias e devolve JSON estruturado.

### `C:\dev\termo-claro\src\analise_llm.py`
```python
# -*- coding: utf-8 -*-
"""Análise completa da política via LLM local (trilha MVP).

Uma chamada ao Ollama devolve, para cada uma das 12 categorias:
presente (bool), nível (verde/amarelo/vermelho), trecho citado e resumo.
"""
import json
import ollama
from src.taxonomia import CATEGORIAS, POR_ID
from src.regras import artigos_da_categoria, ajustar_nivel

MODELO = "qwen3:4b"

def _montar_prompt(texto: str) -> str:
    cats = "\n".join(
        f'- id="{c["id"]}" ({c["nome"]}): {c["descricao"]} '
        f'Alerta vermelho = {c["alerta_vermelho"]}'
        for c in CATEGORIAS
    )
    # limita o tamanho para caber no contexto do modelo 4B
    trecho_texto = texto[:12000]
    return (
        "Você é um analista de privacidade. Analise a política de privacidade "
        "abaixo contra as 12 categorias listadas. Para CADA categoria, diga se "
        "ela aparece no texto (presente), o nível de risco e cite um trecho curto.\n\n"
        "Níveis: 'verde' = claro e adequado; 'amarelo' = vago ou incompleto; "
        "'vermelho' = risco ao titular.\n\n"
        f"CATEGORIAS:\n{cats}\n\n"
        "Responda APENAS com um JSON no formato:\n"
        '{"categorias": [{"id": "...", "presente": true, "nivel": "verde|amarelo|vermelho", '
        '"trecho": "citação curta do texto", "justificativa": "1 frase"}]}\n\n'
        f"POLÍTICA:\n{trecho_texto}"
    )

def analisar(texto: str) -> list[dict]:
    resp = ollama.chat(
        model=MODELO,
        messages=[{"role": "user", "content": _montar_prompt(texto)}],
        format="json",
        options={"temperature": 0},
    )
    try:
        dados = json.loads(resp["message"]["content"])
        itens = dados.get("categorias", [])
    except (json.JSONDecodeError, KeyError):
        itens = []

    # normaliza e enriquece com os artigos da LGPD
    resultado = []
    for item in itens:
        cat_id = item.get("id")
        if cat_id not in POR_ID:
            continue
        nivel = item.get("nivel", "amarelo")
        trecho = item.get("trecho", "")
        resultado.append({
            "id": cat_id,
            "categoria": POR_ID[cat_id]["nome"],
            "presente": item.get("presente", True),
            "nivel": ajustar_nivel(trecho, nivel),
            "trecho": trecho,
            "justificativa": item.get("justificativa", ""),
            "artigos": artigos_da_categoria(cat_id),
        })
    return resultado
```

**Teste de ponta a ponta** no terminal:
```powershell
python -c "from src.extracao import extrair; from src.analise_llm import analisar; import json; t=extrair('Coletamos seu nome, CPF e localização. Compartilhamos com parceiros. Guardamos por tempo indeterminado.'); print(json.dumps(analisar(t), ensure_ascii=False, indent=2))"
```
Demora alguns segundos (CPU) e imprime o JSON com categorias, níveis e artigos. **Se isso funcionar, o núcleo está pronto.**

---

## Parte 7 — Interface Streamlit

### `C:\dev\termo-claro\app.py`
```python
# -*- coding: utf-8 -*-
"""Termo Claro — interface Streamlit."""
import streamlit as st
from src.extracao import extrair
from src.analise_llm import analisar
from src.resumo import resumir
from src.taxonomia import NIVEIS

st.set_page_config(page_title="Termo Claro", page_icon="📄", layout="wide")

CORES = {"verde": "#2f7d4f", "amarelo": "#b8860b", "vermelho": "#b3362c"}

st.title("📄 Termo Claro")
st.caption("Leitor de políticas de privacidade à luz da LGPD · IA local e open source")

with st.sidebar:
    st.header("Entrada")
    nome_app = st.text_input("Nome do app", "App de exemplo")
    fonte = st.text_area(
        "Cole o texto, uma URL ou o caminho de um PDF/HTML",
        height=200,
        placeholder="https://exemplo.com/privacidade  ou  cole o texto aqui...",
    )
    analisar_btn = st.button("Analisar", type="primary", use_container_width=True)

st.info("⚠️ Ferramenta educacional. Orienta, não substitui parecer jurídico.", icon="⚠️")

if analisar_btn and fonte.strip():
    with st.spinner("Extraindo texto..."):
        texto = extrair(fonte.strip())
    if len(texto) < 50:
        st.error("Texto muito curto ou não consegui extrair. Tente colar o texto direto.")
        st.stop()

    with st.spinner("Analisando com o modelo local (pode levar alguns segundos)..."):
        achados = analisar(texto)

    if not achados:
        st.warning("O modelo não retornou resultados. Tente novamente.")
        st.stop()

    # Resumo geral
    with st.spinner("Gerando resumo em linguagem simples..."):
        texto_resumo = resumir(nome_app, achados)
    st.subheader("Resumo")
    st.write(texto_resumo)

    # Contadores
    c1, c2, c3 = st.columns(3)
    for col, nivel in zip((c1, c2, c3), ("vermelho", "amarelo", "verde")):
        n = sum(1 for a in achados if a["nivel"] == nivel)
        col.metric(f"{NIVEIS[nivel]['emoji']} {NIVEIS[nivel]['label']}", n)

    # Relatório por categoria
    st.subheader("Análise por categoria")
    ordem = {"vermelho": 0, "amarelo": 1, "verde": 2}
    for a in sorted(achados, key=lambda x: ordem.get(x["nivel"], 3)):
        cor = CORES.get(a["nivel"], "#555")
        emoji = NIVEIS.get(a["nivel"], {}).get("emoji", "⚪")
        with st.expander(f"{emoji} {a['categoria']}  ·  {' · '.join(a['artigos'])}"):
            st.markdown(f"**Avaliação:** :{'' }{a['justificativa']}")
            if a["trecho"]:
                st.markdown("**Trecho da política:**")
                st.markdown(f"> {a['trecho']}")
            st.caption(f"Base legal: {' · '.join(a['artigos'])} (LGPD, Lei 13.709/2018)")

elif analisar_btn:
    st.warning("Cole um texto, URL ou caminho de arquivo primeiro.")
```

**Rodar:**
```powershell
streamlit run app.py
```
Abre no navegador em `http://localhost:8501`. Cole um texto e clique em **Analisar**.

🎉 **Neste ponto você tem o MVP funcionando.** O resto é rigor acadêmico (dados + métricas).

---

## Parte 8 — Dados: OPP-115, LGPD e corpus BR

### 8.1 Texto da LGPD
Baixe o texto da **Lei nº 13.709/2018** do Planalto (`planalto.gov.br`) e salve como `C:\dev\termo-claro\data\lgpd.txt`. Serve de base para as citações e para conferência manual.

### 8.2 OPP-115 (dataset de treino)
- Fonte: **usableprivacy.org/data** → "OPP-115 Corpus".
- São 115 políticas em inglês com ~23 mil anotações feitas por especialistas em direito, em 10 categorias.
- Baixe e descompacte em `C:\dev\termo-claro\data\opp115\`.
- **Confira a licença** antes de redistribuir — por isso ele está no `.gitignore`.

### 8.3 Tradução do OPP-115 para PT
Como o OPP-115 é em inglês, traduza os trechos para português com modelo open source (Opus-MT ou NLLB via `transformers`), e revise uma **amostra** manualmente. Guarde o resultado em `data/opp115/traduzido/`.

> Dica: a tradução é tarefa de lote. Faça um script `traduzir.py` que percorre os trechos e salva um CSV `trecho_pt, categorias`.

### 8.4 Corpus BR (a contribuição do projeto)
Este é o **diferencial** e **vai para o repositório público**.

1. Escolha **30 a 40 apps** populares no Brasil: bancos digitais, delivery, transporte, redes sociais, varejo, saúde.
2. Baixe a política de privacidade de cada um (salve o texto em `data/corpus_br/brutos/`).
3. **Anote por trecho** seguindo o guia abaixo.
4. Use o corpus **só como teste** — nunca em treino.

### 8.5 Guia de anotação (resumo do protocolo)
Crie `data/corpus_br/GUIA_ANOTACAO.md` com:
- **Unidade:** o trecho (parágrafo). Cada trecho pode ter **várias** categorias (multirrótulo).
- **Rótulos:** os 12 `id`s da taxonomia + o `nivel` (verde/amarelo/vermelho).
- **Processo:** cada política é anotada por **2 membros** de forma independente.
- **Concordância:** medida pelo **kappa de Cohen** (meta ≥ 0,70).
- **Divergências:** resolvidas por um **3º membro**.
- **Formato de saída:** um CSV por política em `data/corpus_br/anotado/`, colunas: `trecho, categorias (lista), nivel, anotador`.

---

## Parte 9 — Classificação rigorosa (baseline + transformer)

Esta trilha gera as **3 abordagens comparadas** dos OKRs.

### 9.1 Baseline — TF-IDF + Regressão Logística
`C:\dev\termo-claro\src\classificador.py`
```python
# -*- coding: utf-8 -*-
"""Baseline multirrótulo: TF-IDF + Regressão Logística (um-contra-todos)."""
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from src.taxonomia import IDS

CAMINHO_MODELO = "modelos/baseline.joblib"

def treinar(trechos: list[str], rotulos: list[list[str]]):
    mlb = MultiLabelBinarizer(classes=IDS)
    Y = mlb.fit_transform(rotulos)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=20000)),
        ("clf", OneVsRestClassifier(LogisticRegression(max_iter=1000, class_weight="balanced"))),
    ])
    pipe.fit(trechos, Y)
    joblib.dump({"pipe": pipe, "mlb": mlb}, CAMINHO_MODELO)
    return pipe, mlb

def carregar():
    dados = joblib.load(CAMINHO_MODELO)
    return dados["pipe"], dados["mlb"]

def prever(trechos: list[str]) -> list[list[str]]:
    pipe, mlb = carregar()
    Y = pipe.predict(trechos)
    return [list(labels) for labels in mlb.inverse_transform(Y)]
```

**Treinar** (depois de ter o OPP-115 traduzido em CSV):
```python
# treinar_baseline.py (exemplo)
import pandas as pd
from src.classificador import treinar
df = pd.read_csv("data/opp115/traduzido/treino.csv")  # colunas: trecho, categorias
rotulos = [c.split("|") for c in df["categorias"].fillna("")]
treinar(df["trecho"].tolist(), rotulos)
```

### 9.2 Transformer — BERTimbau (no Colab)
- Modelo: `neuralmind/bert-base-portuguese-cased` (BERTimbau) ou `xlm-roberta-base`.
- Tarefa: classificação multirrótulo (`problem_type="multi_label_classification"`).
- **Faça o fine-tune no Google Colab grátis** (tem GPU), baixe o modelo treinado e rode a inferência localmente.
- Instale as deps pesadas só aqui: `pip install -r requirements-train.txt`.

### 9.3 LLM — zero/few-shot
Já está pronto na Parte 6 (`analise_llm.py`). Para a comparação, meça o F1 dele no mesmo corpus BR.

---

## Parte 10 — Avaliação e métricas

### `C:\dev\termo-claro\avaliacao.py`
```python
# -*- coding: utf-8 -*-
"""Avaliação das abordagens no corpus BR (nunca usado em treino)."""
from sklearn.metrics import f1_score, classification_report
from sklearn.preprocessing import MultiLabelBinarizer
from src.taxonomia import IDS

def avaliar(y_true: list[list[str]], y_pred: list[list[str]]) -> dict:
    mlb = MultiLabelBinarizer(classes=IDS)
    Yt = mlb.fit_transform(y_true)
    Yp = mlb.transform(y_pred)
    return {
        "f1_macro": round(f1_score(Yt, Yp, average="macro", zero_division=0), 3),
        "f1_micro": round(f1_score(Yt, Yp, average="micro", zero_division=0), 3),
        "relatorio": classification_report(Yt, Yp, target_names=IDS, zero_division=0),
    }

if __name__ == "__main__":
    # exemplo de uso: carregue y_true do corpus anotado e y_pred de cada abordagem
    exemplo_true = [["coleta_uso"], ["compartilhamento", "retencao"]]
    exemplo_pred = [["coleta_uso"], ["compartilhamento"]]
    r = avaliar(exemplo_true, exemplo_pred)
    print("F1 macro:", r["f1_macro"], "| F1 micro:", r["f1_micro"])
    print(r["relatorio"])
```

**Métricas que entram no relatório final (dos OKRs):**

| Métrica | O que mede | Meta |
|---|---|---|
| F1 macro (12 categorias) | Qualidade da classificação | ≥ 0,75 |
| Falsos negativos nos alertas 🔴 | Deixar de avisar algo crítico | ≤ 5% |
| Falsos positivos | Alarme falso | monitorar |
| Kappa de Cohen (anotadores) | Confiabilidade do corpus | ≥ 0,70 |
| Tempo por política (8 GB, sem GPU) | Viabilidade | ≤ 30 s |

Salve os resultados em `resultados/` como CSV/MD reprodutível por script.

---

## Parte 11 — Git e GitHub

### 11.1 Primeiro commit
```powershell
cd C:\dev\termo-claro
git add .
git commit -m "Estrutura inicial do Termo Claro (MVP + taxonomia)"
```

### 11.2 Criar o repositório no GitHub
```powershell
winget install GitHub.cli    # se ainda não tiver
gh auth login
gh repo create termo-claro --public --source=. --remote=origin --push
```
Ou crie pela web em github.com e depois:
```powershell
git remote add origin https://github.com/SEU_USUARIO/termo-claro.git
git branch -M main
git push -u origin main
```

### 11.3 Licença MIT
Crie o arquivo `LICENSE` (o GitHub oferece o template MIT na criação do repo). É exigência dos entregáveis.

---

## Parte 12 — Cronograma de 16 semanas

| Sem. | Etapa | O que fazer |
|---|---|---|
| 01-02 | Setup | Partes 1-7 deste guia: máquina, projeto, MVP andando, repo no GitHub |
| 03-04 | Dados e taxonomia | OPP-115, texto LGPD, taxonomia final, guia de anotação, EDA |
| 05-07 | Núcleo | Extração/segmentação/regras refinados; tradução do OPP-115; anotar corpus BR |
| 08-10 | Treino | Baseline TF-IDF; fine-tune BERTimbau (Colab); ajustar prompts e limiares |
| 11-12 | Integração | Streamlit completo; resumo pelo LLM; CLI de lote |
| 13-14 | Testes | Avaliar no corpus BR; comparar as 3 abordagens; tempo e recursos |
| 15-16 | Entrega | README; relatório final; publicar corpus; demo ao vivo |

---

## Parte 13 — Troubleshooting

| Problema | Causa / Solução |
|---|---|
| `Activate.ps1` dá erro de permissão | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e ative de novo |
| `ollama: command not found` | Feche e reabra o PowerShell; se persistir, reinicie o PC |
| Erro ao instalar PyTorch/Transformers | Você está na Python 3.14. Use `py -3.12` para criar a venv |
| Ollama muito lento / trava | Modelo 4B em CPU é lento; feche outros apps; garanta 8 GB livres |
| `analise_llm` retorna `[]` | O modelo não gerou JSON válido. Rode de novo; confira `format="json"` |
| `ModuleNotFoundError: src` | Rode sempre da raiz `C:\dev\termo-claro` e mantenha `src\__init__.py` |
| Texto de URL vem vazio | Alguns sites bloqueiam robôs; copie e cole o texto direto |
| venv "sumiu" / erros estranhos | Verifique que o projeto está em `C:\dev`, **não** no Google Drive |

---

*Documento gerado para o projeto acadêmico Termo Claro. Atualize conforme o projeto evolui.*
