# 🤖 Guia de Anotação com Claude (Opção B - Gabarito Assistido)

Este guia contém o **prompt oficial pronto para copiar e colar no Claude (ou ChatGPT / Gemini)** para gerar o **gabarito de políticas brasileiras** sem que você precise ler páginas inteiras de juridiquês.

---

## 📋 Como Usar:

1. Abra o **Claude** (ou seu LLM preferido).
2. Copie todo o bloco de prompt abaixo.
3. No final do prompt, cole o texto da política de privacidade que você quer anotar (ex: `nubank.txt`, `ifood.txt`, etc.).
4. O Claude vai devolver uma **tabela padronizada com os parágrafos anotados**.
5. Salve a resposta como um arquivo CSV em:
   `data/corpus_br/anotado/[nome_do_app]_anotado.csv`

---

## ✂️ COPIE A PARTIR DAQUI:

```text
Você é um auditor sênior especialista em Direito Digital, Cibersegurança e na Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).

Sua tarefa é analisar a política de privacidade abaixo e gerar o "Gabarito Oficial de Anotação" (Ground Truth) para avaliação científica de um sistema de IA.

Para cada cláusula ou parágrafo relevante da política, classifique-o segundo a TAXONOMIA OFICIAL DE 12 CATEGORIAS:

1. coleta_uso: Coleta e uso pelo app (art. 6º I-III, art. 7º)
   - Alerta Vermelho: Coleta ampla sem finalidade definida.
2. compartilhamento: Compartilhamento com terceiros (art. 7º §5º, art. 9º V)
   - Alerta Vermelho: "Parceiros" ou "terceiros" não identificados nominalmente.
3. localizacao: Dados de geolocalização e GPS (art. 6º III, art. 9º)
   - Alerta Vermelho: Localização contínua em segundo plano sem necessidade.
4. dados_sensiveis: Saúde, biometria, raça, religião, etc. (art. 5º II, art. 11)
   - Alerta Vermelho: Biometria ou saúde sem consentimento específico.
5. consentimento: Escolhas, consentimento e revogação (art. 8º, art. 18 IX)
   - Alerta Vermelho: Não explica como revogar a autorização dada.
6. direitos_titular: Acesso, correção e exclusão de dados (art. 18)
   - Alerta Vermelho: Não disponibiliza canal para o titular exercer direitos.
7. retencao: Período de armazenamento (arts. 15 e 16)
   - Alerta Vermelho: Guarda de dados "por tempo indeterminado".
8. seguranca: Medidas técnicas e incidentes (arts. 46 e 48)
   - Alerta Vermelho: Não cita nenhuma medida de segurança ou criptografia.
9. criancas: Dados de menores de idade (art. 14)
   - Alerta Vermelho: Coleta de menores sem consentimento dos responsáveis.
10. transferencia_intl: Envio para fora do país (art. 33)
    - Alerta Vermelho: Transfere dados para servidores no exterior sem citar país.
11. mudancas: Alterações nos termos (art. 8º §6º, art. 9º §2º)
    - Alerta Vermelho: "Podemos alterar esta política sem aviso prévio".
12. encarregado: DPO / Contato de privacidade (art. 41)
    - Alerta Vermelho: Não informa o contato do encarregado de dados.

CRITÉRIOS DE NÍVEL DE RISCO:
- "verde": Transparente, justificado e em total conformidade.
- "amarelo": Vago, ambíguo ("podemos", "a nosso critério", "parceiros comerciais").
- "vermelho": Risco direto, cláusula abusiva ou ausência de direito garantido.

FORMATO DE RESPOSTA OBRIGATÓRIO (Gere em formato de tabela CSV ou Markdown):
Colunas:
trecho | id_categoria | nivel | artigos_lgpd | justificativa_juridica

INSTRUÇÕES:
- Extraia trechos literais de 1 a 3 frases.
- Não invente informações.
- Liste entre 10 e 25 parágrafos mais representativos da política.

--- TEXTO DA POLÍTICA A SER ANOTADA ---
[COLE O TEXTO DA POLÍTICA DO APP AQUI]
```
