# 📊 Relatório de Avaliação Científica — OPP-115

- **Modelo Avaliado:** `qwen2.5:3b` (rodando localmente na GPU)
- **Base de Comparação (Ground Truth):** OPP-115 Corpus (anotações de especialistas da Carnegie Mellon)
- **Tamanho da Amostra:** 21 trechos multirrótulo balanceados

### 🎯 Índices Globais
- **F1-Score Macro:** **0.361** (36.1%)
- **F1-Score Micro:** **0.347** (34.7%)

### 📋 Tabela de Classificação por Categoria
```
                  precision    recall  f1-score   support

   consentimento       0.12      0.33      0.18         3
        mudancas       0.75      1.00      0.86         3
      coleta_uso       0.18      1.00      0.30         3
compartilhamento       0.00      0.00      0.00         3
        criancas       1.00      1.00      1.00         3
        retencao       0.00      0.00      0.00         3
       seguranca       0.38      1.00      0.55         3
direitos_titular       0.00      0.00      0.00         0

       micro avg       0.24      0.62      0.35        21
       macro avg       0.30      0.54      0.36        21
    weighted avg       0.35      0.62      0.41        21
     samples avg       0.32      0.62      0.39        21
```
