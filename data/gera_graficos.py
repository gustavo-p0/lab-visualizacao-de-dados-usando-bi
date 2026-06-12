import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

AREAS = ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação']
AREAS_SHORT = ['CN', 'CH', 'LC', 'MT', 'Red']

SAIDA = 'prints'
os.makedirs(SAIDA, exist_ok=True)

df = pd.read_csv('enem_2024_limpo.csv', encoding='utf-8')
ORDEM_RENDA = ['Nenhuma renda', 'Até R$1.320']
df['Renda Familiar'] = pd.Categorical(df['Renda Familiar'], categories=ORDEM_RENDA, ordered=True)

for a in AREAS:
    df[a] = pd.to_numeric(df[a], errors='coerce')

cores_pub_priv = {'Pública': '#1f77b4', 'Privada': '#ff7f0e'}

def salvar(fig, nome):
    fig.savefig(f'{SAIDA}/{nome}.pdf', bbox_inches='tight', dpi=150)
    fig.savefig(f'{SAIDA}/{nome}.png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f'  {nome}')

# -------------------------------------------------------
# G1 — Pizza: Tipo de Escola
# -------------------------------------------------------
def g1():
    contagem = df['Tipo de Escola'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    cores = [cores_pub_priv.get(c, '#999') for c in contagem.index]
    wedges, texts, autotexts = ax.pie(
        contagem.values, labels=contagem.index, autopct='%1.1f%%',
        colors=cores, startangle=90, textprops={'fontsize': 11}
    )
    ax.set_title('Distribuição por Tipo de Escola', fontsize=13, fontweight='bold')
    salvar(fig, 'g1')

# -------------------------------------------------------
# G2 — Barras horizontais: Raça/Cor
# -------------------------------------------------------
def g2():
    dados = df['Raça/Cor'].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(dados.index, dados.values, color='#2c7bb6', edgecolor='white')
    for i, v in enumerate(dados.values):
        ax.text(v + 2000, i, f'{v:,}', va='center', fontsize=9)
    ax.set_title('Candidatos por Raça/Cor', fontsize=13, fontweight='bold')
    ax.set_xlabel('Número de Candidatos')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    salvar(fig, 'g2')

# -------------------------------------------------------
# G3 — Barras verticais: Faixa Etária
# -------------------------------------------------------
def g3():
    age_order = ['<17','17','18','19','20','21','22','23','24','25',
                 '26–30','31–35','36–40','41–45','46–50','51–55','56–60',
                 '61–65','66–70','>70']
    dados = df['Faixa Etária'].value_counts().reindex(age_order).dropna()
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(dados.index, dados.values, color='#2c7bb6', edgecolor='white')
    ax.set_title('Candidatos por Faixa Etária', fontsize=13, fontweight='bold')
    ax.set_ylabel('Número de Candidatos')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    plt.xticks(rotation=45, ha='right')
    salvar(fig, 'g3')

# -------------------------------------------------------
# G4 — Pizza: Sexo
# -------------------------------------------------------
def g4():
    contagem = df['Sexo'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 4))
    cores_sexo = {'Masculino': '#2ca02c', 'Feminino': '#d62728'}
    cores = [cores_sexo.get(c, '#999') for c in contagem.index]
    ax.pie(contagem.values, labels=contagem.index, autopct='%1.1f%%',
           colors=cores, startangle=90, textprops={'fontsize': 11})
    ax.set_title('Distribuição por Sexo', fontsize=13, fontweight='bold')
    salvar(fig, 'g4')

# -------------------------------------------------------
# G5 — Barras agrupadas: Região x Tipo de Escola
# -------------------------------------------------------
def g5():
    dados = df.groupby(['Região', 'Tipo de Escola']).size().unstack(fill_value=0)
    regioes = ['Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
    dados = dados.reindex([r for r in regioes if r in dados.index])
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(dados.index))
    w = 0.35
    b1 = ax.bar(x - w/2, dados['Pública'].values, w, label='Pública', color='#1f77b4')
    b2 = ax.bar(x + w/2, dados['Privada'].values, w, label='Privada', color='#ff7f0e')
    ax.set_xticks(x)
    ax.set_xticklabels(dados.index)
    ax.legend()
    ax.set_title('Candidatos por Região e Tipo de Escola', fontsize=13, fontweight='bold')
    ax.set_ylabel('Número de Candidatos')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    salvar(fig, 'g5')

# -------------------------------------------------------
# G6 — Barras horizontais: Estado
# -------------------------------------------------------
def g6():
    dados = df['SG_UF_PROVA'].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(dados.index, dados.values, color='#2c7bb6', edgecolor='white')
    ax.set_title('Candidatos por Estado (top 27)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Número de Candidatos')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    salvar(fig, 'g6')

# -------------------------------------------------------
# G7 — Box plot: Notas por Área
# -------------------------------------------------------
def g7():
    dados_plot = [df[a].dropna().values for a in AREAS]
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(dados_plot, labels=AREAS_SHORT, patch_artist=True, showfliers=False)
    cores_box = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    for patch, c in zip(bp['boxes'], cores_box):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    ax.set_title('Distribuição das Notas por Área', fontsize=13, fontweight='bold')
    ax.set_ylabel('Nota')
    ax.set_ylim(0, 1000)
    salvar(fig, 'g7')

# -------------------------------------------------------
# G8 — Mediana por Área e Tipo de Escola
# -------------------------------------------------------
def g8():
    dados = df.groupby('Tipo de Escola')[AREAS].median()
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(AREAS_SHORT))
    w = 0.35
    ax.bar(x - w/2, dados.loc['Pública'].values, w, label='Pública', color='#1f77b4')
    ax.bar(x + w/2, dados.loc['Privada'].values, w, label='Privada', color='#ff7f0e')
    ax.set_xticks(x)
    ax.set_xticklabels(AREAS_SHORT)
    ax.legend()
    ax.set_title('Mediana das Notas por Área e Tipo de Escola', fontsize=13, fontweight='bold')
    ax.set_ylabel('Mediana')
    ax.set_ylim(0, 1000)
    for i, v in enumerate(dados.loc['Pública'].values):
        ax.text(i - w/2, v + 10, f'{v:.0f}', ha='center', fontsize=8)
    for i, v in enumerate(dados.loc['Privada'].values):
        ax.text(i + w/2, v + 10, f'{v:.0f}', ha='center', fontsize=8)
    salvar(fig, 'g8')

# -------------------------------------------------------
# R1.1 — Mediana por Área: Pública vs Privada (repetido)
# -------------------------------------------------------
def r11():
    g8()

# -------------------------------------------------------
# R1.3 — % acima de 600
# -------------------------------------------------------
def r13():
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(AREAS_SHORT))
    w = 0.35
    pub_pct = []
    priv_pct = []
    for a in AREAS:
        pub_pct.append((df[df['Tipo de Escola']=='Pública'][a] > 600).mean() * 100)
        priv_pct.append((df[df['Tipo de Escola']=='Privada'][a] > 600).mean() * 100)
    ax.bar(x - w/2, pub_pct, w, label='Pública', color='#1f77b4')
    ax.bar(x + w/2, priv_pct, w, label='Privada', color='#ff7f0e')
    ax.set_xticks(x)
    ax.set_xticklabels(AREAS_SHORT)
    ax.legend()
    ax.set_title('% Candidatos com Nota > 600', fontsize=13, fontweight='bold')
    ax.set_ylabel('%')
    for i, v in enumerate(pub_pct):
        ax.text(i - w/2, v + 1, f'{v:.1f}%', ha='center', fontsize=8)
    for i, v in enumerate(priv_pct):
        ax.text(i + w/2, v + 1, f'{v:.1f}%', ha='center', fontsize=8)
    salvar(fig, 'r13')

# -------------------------------------------------------
# R1.4 — Histograma sobreposto
# -------------------------------------------------------
def r14():
    fig, ax = plt.subplots(figsize=(8, 5))
    pub = df[df['Tipo de Escola']=='Pública']['Nota Média'].dropna()
    priv = df[df['Tipo de Escola']=='Privada']['Nota Média'].dropna()
    ax.hist(pub, bins=80, alpha=0.5, label='Pública', color='#1f77b4', density=True)
    ax.hist(priv, bins=80, alpha=0.5, label='Privada', color='#ff7f0e', density=True)
    ax.legend()
    ax.set_title('Distribuição da Nota Média Geral', fontsize=13, fontweight='bold')
    ax.set_xlabel('Nota Média')
    ax.set_ylabel('Densidade')
    salvar(fig, 'r14')

# -------------------------------------------------------
# R2.1 — Linha: Renda x Nota Média
# -------------------------------------------------------
def r21():
    dados = df.groupby('Renda Familiar', observed=True)['Nota Média'].median()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(range(len(dados)), dados.values, '-o', color='#2c7bb6', linewidth=2, markersize=8)
    ax.set_xticks(range(len(dados)))
    ax.set_xticklabels(dados.index, fontsize=10)
    ax.set_title('Relação entre Renda Familiar e Nota Média', fontsize=13, fontweight='bold')
    ax.set_ylabel('Mediana da Nota Média')
    ax.set_ylim(400, 700)
    for i, v in enumerate(dados.values):
        ax.text(i, v + 10, f'{v:.1f}', ha='center', fontsize=10)
    salvar(fig, 'r21')

# -------------------------------------------------------
# R2.2 — Heatmap: Área x Renda
# -------------------------------------------------------
def r22():
    dados = df.groupby('Renda Familiar', observed=True)[AREAS].median()
    fig, ax = plt.subplots(figsize=(8, 3))
    im = ax.imshow(dados.values, cmap='RdYlGn', aspect='auto', vmin=400, vmax=800)
    ax.set_xticks(range(len(AREAS_SHORT)))
    ax.set_xticklabels(AREAS_SHORT)
    ax.set_yticks(range(len(dados.index)))
    ax.set_yticklabels(dados.index)
    ax.set_title('Mediana das Notas por Área e Faixa de Renda', fontsize=13, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Mediana')
    for i in range(len(dados.index)):
        for j in range(len(AREAS_SHORT)):
            ax.text(j, i, f'{dados.values[i,j]:.0f}', ha='center', va='center', fontsize=10, fontweight='bold')
    salvar(fig, 'r22')

# -------------------------------------------------------
# R2.3 — Barras: Distribuição por Renda
# -------------------------------------------------------
def r23():
    dados = df.groupby('Renda Familiar', observed=True).size()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(len(dados)), dados.values, color='#2c7bb6', edgecolor='white', width=0.5)
    ax.set_xticks(range(len(dados)))
    ax.set_xticklabels(dados.index)
    ax.set_title('Distribuição de Candidatos por Renda', fontsize=13, fontweight='bold')
    ax.set_ylabel('Número de Candidatos')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    for i, v in enumerate(dados.values):
        ax.text(i, v + 5000, f'{v:,}', ha='center', fontsize=10)
    salvar(fig, 'r23')

# -------------------------------------------------------
# R2.4 — Barras agrupadas: Renda x Escola
# -------------------------------------------------------
def r24():
    dados = df.groupby(['Renda Familiar', 'Tipo de Escola'], observed=True)['Nota Média'].median().unstack()
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(dados.index))
    w = 0.35
    ax.bar(x - w/2, dados['Pública'].values, w, label='Pública', color='#1f77b4')
    ax.bar(x + w/2, dados['Privada'].values, w, label='Privada', color='#ff7f0e')
    ax.set_xticks(x)
    ax.set_xticklabels(dados.index)
    ax.legend()
    ax.set_title('Mediana por Renda e Tipo de Escola', fontsize=13, fontweight='bold')
    ax.set_ylabel('Mediana da Nota Média')
    ax.set_ylim(400, 700)
    for i, v in enumerate(dados['Pública'].values):
        ax.text(i - w/2, v + 5, f'{v:.0f}', ha='center', fontsize=9)
    for i, v in enumerate(dados['Privada'].values):
        ax.text(i + w/2, v + 5, f'{v:.0f}', ha='center', fontsize=9)
    salvar(fig, 'r24')

print('Gerando gráficos...')
g1(); g2(); g3(); g4(); g5(); g6(); g7()
print('---')
r11(); r13(); r14()
print('---')
r21(); r22(); r23(); r24()
print('Pronto!')
