# ENEM 2024 — Visualização de Dados usando BI

Dashboard interativo e relatório analítico sobre o ENEM 2024, desenvolvido com **Streamlit**, **Plotly**, **Pandas** e **LaTeX**.

## Dataset

Os dados são dos microdados do INEP — ENEM 2024. O processamento cruza dois CSVs:

| Arquivo | Origem | Conteúdo |
|---------|--------|----------|
| `PARTICIPANTES_2024.csv` | INEP | Perfil do candidato (idade, sexo, raça, renda, etc.) |
| `RESULTADOS_2024.csv` | INEP | Notas por área de conhecimento e presença |

**Filtros aplicados no pré-processamento:**
- Remoção de treineiros (`IN_TREINEIRO = 0`)
- Apenas presentes em **todas as 4 provas** (CN, CH, LC, MT)
- Nota válida em todas as áreas
- Apenas escolas públicas e privadas (excluindo não informado)

**Redução:** ~3,9M participantes → ~960 mil candidatos analisados.

## Estrutura

```
data/
├── app.py                  # Dashboard Streamlit
├── preprocessing.py        # Script de limpeza e merge dos CSVs
├── requirements.txt        # Dependências Python
├── enem_2024_limpo.csv.gz  # Dataset limpo (25MB)
├── relatorio_enem2024.tex  # Relatório LaTeX
├── relatorio_enem2024.pdf  # Relatório compilado
└── README.md
```

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dashboard

Três abas principais:

1. **Caracterização do Dataset** — perfil dos candidatos (escola, sexo, raça, idade, distribuição geográfica, notas)
2. **RQ1 — Tipo de Escola vs. Desempenho** — escolas públicas vs. privadas e impacto nas notas
3. **RQ2 — Renda Familiar vs. Desempenho** — relação entre faixa de renda e nota média

### Filtros
- Região (multiseleção)
- Tipo de Escola (pública/privada)
- Sexo

## Relatório

O relatório `relatorio_enem2024.pdf` foi gerado via LaTeX (XeLaTeX) e contém análise textual aprofundada, tabelas de mediana e distribuição de notas.

```bash
xelatex relatorio_enem2024.tex
```

## Tecnologias

- **Streamlit** — frontend interativo
- **Plotly Express** — gráficos (bar, pie, box, histogram, line, imshow)
- **Pandas + PyArrow** — manipulação e carregamento eficiente de dados
- **LaTeX (XeLaTeX)** — relatório estático
