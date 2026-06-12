import pandas as pd
import numpy as np

CARGA_PART = 'microdados_enem_2024/DADOS/PARTICIPANTES_2024.csv'
CARGA_RES  = 'microdados_enem_2024/DADOS/RESULTADOS_2024.csv'
SAIDA      = 'enem_2024_limpo.csv'

PART_COLS = [
    'NU_INSCRICAO', 'TP_FAIXA_ETARIA', 'TP_SEXO', 'TP_COR_RACA',
    'IN_TREINEIRO', 'SG_UF_PROVA', 'Q001', 'Q002', 'Q006'
]

RES_COLS = [
    'TP_DEPENDENCIA_ADM_ESC',
    'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
    'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO'
]

NOTAS = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

print("Carregando PARTICIPANTES...")
part_chunks = []
for chunk in pd.read_csv(
    CARGA_PART,
    sep=';', encoding='ISO-8859-1',
    usecols=PART_COLS,
    chunksize=500_000,
    low_memory=False
):
    part_chunks.append(chunk)
df_part = pd.concat(part_chunks, ignore_index=True)
del part_chunks
print(f"  PARTICIPANTES: {len(df_part):,} linhas")

print("Carregando RESULTADOS...")
res_chunks = []
for chunk in pd.read_csv(
    CARGA_RES,
    sep=';', encoding='ISO-8859-1',
    usecols=RES_COLS,
    chunksize=500_000,
    low_memory=False
):
    res_chunks.append(chunk)
df_res = pd.concat(res_chunks, ignore_index=True)
del res_chunks
print(f"  RESULTADOS: {len(df_res):,} linhas")

print("Merge por índice...")
df = pd.concat([df_part, df_res], axis=1)

antes = len(df)
print(f"Antes dos filtros: {len(df):,}")

df = df[df['IN_TREINEIRO'] == 0]
print(f"  Após remover treineiros: {len(df):,} ({len(df)/antes*100:.1f}%)")

df = df[
    (df['TP_PRESENCA_CN'] == 1) &
    (df['TP_PRESENCA_CH'] == 1) &
    (df['TP_PRESENCA_LC'] == 1) &
    (df['TP_PRESENCA_MT'] == 1)
]
print(f"  Após manter presentes em todas: {len(df):,}")

df['TP_ESCOLA'] = df['TP_DEPENDENCIA_ADM_ESC'].map({1: 2, 2: 2, 3: 2, 4: 3})
df = df[df['TP_ESCOLA'].isin([2, 3])]
print(f"  Após filtro tipo escola: {len(df):,}")

df = df.dropna(subset=NOTAS)
print(f"  Após remover notas ausentes: {len(df):,}")

df['Tipo de Escola'] = df['TP_ESCOLA'].map({2: 'Pública', 3: 'Privada'})

df['Sexo'] = df['TP_SEXO'].map({'M': 'Masculino', 'F': 'Feminino'})

df['Raça/Cor'] = df['TP_COR_RACA'].map({
    0: 'Não declarado', 1: 'Branca', 2: 'Preta',
    3: 'Parda', 4: 'Amarela', 5: 'Indígena'
})

df['Faixa Etária'] = df['TP_FAIXA_ETARIA'].map({
    1: '<17', 2: '17', 3: '18', 4: '19', 5: '20',
    6: '21', 7: '22', 8: '23', 9: '24', 10: '25',
    11: '26–30', 12: '31–35', 13: '36–40', 14: '41–45',
    15: '46–50', 16: '51–55', 17: '56–60', 18: '61–65',
    19: '66–70', 20: '>70'
})

df['Renda Familiar'] = df['Q006'].map({
    'A': 'Nenhuma renda',
    'B': 'Até R$1.320'
})
ORDEM_RENDA = ['Nenhuma renda', 'Até R$1.320']
df['Renda Familiar'] = pd.Categorical(df['Renda Familiar'], categories=ORDEM_RENDA, ordered=True)


REGIOES = {
    'AC':'Norte','AM':'Norte','AP':'Norte','PA':'Norte','RO':'Norte','RR':'Norte','TO':'Norte',
    'AL':'Nordeste','BA':'Nordeste','CE':'Nordeste','MA':'Nordeste','PB':'Nordeste',
    'PE':'Nordeste','PI':'Nordeste','RN':'Nordeste','SE':'Nordeste',
    'DF':'Centro-Oeste','GO':'Centro-Oeste','MS':'Centro-Oeste','MT':'Centro-Oeste',
    'ES':'Sudeste','MG':'Sudeste','RJ':'Sudeste','SP':'Sudeste',
    'PR':'Sul','RS':'Sul','SC':'Sul'
}
df['Região'] = df['SG_UF_PROVA'].map(REGIOES)

df['Nota Média'] = df[NOTAS].mean(axis=1).round(1)
df['Acima de 600'] = (df[NOTAS] > 600).any(axis=1)

df = df.rename(columns={
    'NU_NOTA_CN': 'Ciências da Natureza',
    'NU_NOTA_CH': 'Ciências Humanas',
    'NU_NOTA_LC': 'Linguagens',
    'NU_NOTA_MT': 'Matemática',
    'NU_NOTA_REDACAO': 'Redação'
})

import gzip, shutil, os
df.to_csv(SAIDA, index=False, encoding='utf-8')
with open(SAIDA, 'rb') as f_in:
    with gzip.open(SAIDA + '.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
os.remove(SAIDA)
print(f"\nDataset limpo exportado: {len(df):,} candidatos, {len(df.columns)} colunas")
print(f"Arquivo: {SAIDA}.gz")
