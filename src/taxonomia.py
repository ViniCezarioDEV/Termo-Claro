# -*- coding: utf-8 -*-
"""Fonte única da verdade do Termo Claro.

As 12 categorias de práticas de dados, o mapeamento para a LGPD (Lei 13.709/2018)
e as palavras-chave que alimentam o motor de regras e os prompts da IA.
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
        "descricao": "Coleta e uso de dados de localização geográfica.",
        "alerta_vermelho": "Localização contínua em segundo plano.",
        "keywords": ["localização", "geolocalização", "GPS", "sua posição",
                     "segundo plano"],
    },
    {
        "id": "dados_sensiveis",
        "nome": "Dados sensíveis",
        "artigos": ["art. 5º II", "art. 11"],
        "descricao": "Dados de saúde, biometria, origem racial, opinião política, etc.",
        "alerta_vermelho": "Saúde/biometria sem consentimento específico.",
        "keywords": ["dados sensíveis", "saúde", "biometria", "biométric",
                     "origem racial", "religião", "orientação sexual"],
    },
    {
        "id": "consentimento",
        "nome": "Escolhas e consentimento",
        "artigos": ["art. 8º", "art. 18 IX"],
        "descricao": "Como o usuário consente e como pode revogar a autorização.",
        "alerta_vermelho": "Não diz como revogar o consentimento.",
        "keywords": ["consentimento", "consente", "autoriza", "revogar",
                     "opt-out", "descadastr"],
    },
    {
        "id": "direitos_titular",
        "nome": "Direitos do titular",
        "artigos": ["art. 18"],
        "descricao": "Direitos de acesso, correção, eliminação e portabilidade.",
        "alerta_vermelho": "Não explica como acessar/excluir os dados.",
        "keywords": ["seus direitos", "acessar seus dados", "excluir",
                     "corrigir", "portabilidade", "titular"],
    },
    {
        "id": "retencao",
        "nome": "Retenção",
        "artigos": ["art. 15", "art. 16"],
        "descricao": "Por quanto tempo os dados são armazenados.",
        "alerta_vermelho": "Guarda 'por tempo indeterminado'.",
        "keywords": ["retenção", "armazenamos", "guardamos", "período",
                     "pelo tempo", "indeterminado"],
    },
    {
        "id": "seguranca",
        "nome": "Segurança e incidentes",
        "artigos": ["art. 46", "art. 48"],
        "descricao": "Medidas de segurança e procedimentos em caso de vazamento.",
        "alerta_vermelho": "Nenhuma medida de segurança citada.",
        "keywords": ["segurança", "criptografia", "medidas técnicas",
                     "incidente", "vazamento", "proteção dos dados"],
    },
    {
        "id": "criancas",
        "nome": "Crianças e adolescentes",
        "artigos": ["art. 14"],
        "descricao": "Tratamento de dados de menores de idade.",
        "alerta_vermelho": "Coleta de menores sem consentimento dos responsáveis.",
        "keywords": ["crianças", "menores", "adolescentes", "responsáveis",
                     "18 anos", "consentimento dos pais"],
    },
    {
        "id": "transferencia_intl",
        "nome": "Transferência internacional",
        "artigos": ["art. 33"],
        "descricao": "Envio de dados para servidores fora do Brasil.",
        "alerta_vermelho": "Envia a outro país sem dizer qual.",
        "keywords": ["transferência internacional", "outro país", "exterior",
                     "servidores nos Estados Unidos", "fora do Brasil"],
    },
    {
        "id": "mudancas",
        "nome": "Mudanças na política",
        "artigos": ["art. 8º §6º", "art. 9º §2º"],
        "descricao": "Como mudanças nos termos são comunicadas ao usuário.",
        "alerta_vermelho": "Pode mudar os termos sem aviso prévio.",
        "keywords": ["alterar esta política", "mudanças", "atualizar",
                     "a qualquer momento", "sem aviso prévio"],
    },
    {
        "id": "encarregado",
        "nome": "Encarregado (DPO)",
        "artigos": ["art. 41"],
        "descricao": "Identificação e canal de contato do encarregado de dados.",
        "alerta_vermelho": "Não identifica o encarregado ou canal de contato.",
        "keywords": ["encarregado", "DPO", "data protection officer",
                     "contato para privacidade"],
    },
]

# Dicionários auxiliares para busca rápida (O(1)) pelo código
POR_ID = {c["id"]: c for c in CATEGORIAS}
IDS = [c["id"] for c in CATEGORIAS]

# Definição dos semáforos visuais de risco
NIVEIS = {
    "verde": {"emoji": "🟢", "label": "Adequado"},
    "amarelo": {"emoji": "🟡", "label": "Vago ou incompleto"},
    "vermelho": {"emoji": "🔴", "label": "Risco ao titular"},
}
