import streamlit as st
import pandas as pd
import plotly.express as px
import os

BASE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title='ENEM 2024 — Dashboard', layout='wide')

@st.cache_resource
def load_data():
    df = pd.read_csv(
        os.path.join(BASE, 'enem_2024_limpo.csv.gz'),
        encoding='utf-8', compression='gzip',
        dtype_backend='pyarrow', engine='pyarrow'
    )
    ORDEM_RENDA = ['Nenhuma renda', 'Até R$1.320']
    df['Renda Familiar'] = pd.Categorical(df['Renda Familiar'], categories=ORDEM_RENDA, ordered=True)
    return df

df = load_data()

AREAS = ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação']

st.sidebar.header('Filtros')

regioes_disp = ['Todas'] + sorted(df['Região'].dropna().unique().tolist())
regiao_sel = st.sidebar.multiselect('Região', regioes_disp, default=['Todas'])

escola_sel = st.sidebar.multiselect(
    'Tipo de Escola', ['Pública', 'Privada'], default=['Pública', 'Privada']
)

sexo_sel = st.sidebar.multiselect(
    'Sexo', ['Masculino', 'Feminino'], default=['Masculino', 'Feminino']
)

mask = df['Tipo de Escola'].isin(escola_sel) & df['Sexo'].isin(sexo_sel)
if 'Todas' not in regiao_sel:
    mask &= df['Região'].isin(regiao_sel)
df_filt = df[mask]
df_long = df_filt.sample(min(50000, len(df_filt))).melt(
    id_vars=['Tipo de Escola'],
    value_vars=AREAS,
    var_name='Área', value_name='Nota'
)

st.sidebar.metric('Candidatos selecionados', f'{len(df_filt):,}')

tab1, tab2, tab3 = st.tabs([
    'Caracterização do Dataset',
    'RQ1 — Tipo de Escola vs. Desempenho',
    'RQ2 — Renda Familiar vs. Desempenho'
])

def safe_chart(fig, key=None, **kwargs):
    try:
        st.plotly_chart(fig, **kwargs)
    except Exception:
        st.warning(f'Gráfico indisponível para este recorte.' if key else '')

with tab1:
    st.header('Caracterização dos Candidatos do ENEM 2024')
    st.markdown(
        'Dos **~3,9 milhões** de participantes do ENEM 2024, restaram **~960 mil** após '
        'remover treineiros, manter apenas quem compareceu a **todas as provas** e '
        'teve **nota válida** em todas as áreas, além de filtrar apenas escolas '
        'públicas e privadas (excluindo não informado).'
    )
    st.markdown(
        'Os dados combinam dois microdados do INEP: '
        '**PARTICIPANTES** (perfil do candidato) e '
        '**RESULTADOS** (notas por área e presença). '
        'O cruzamento foi feito pelo índice de linha (sequencial), '
        'já que ambos os CSVs têm a mesma ordem de inscrição.'
    )

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    total = len(df_filt)
    pct_pub = (df_filt['Tipo de Escola'] == 'Pública').mean() * 100 if total > 0 else 0
    pct_priv = (df_filt['Tipo de Escola'] == 'Privada').mean() * 100 if total > 0 else 0
    med_nota = df_filt['Nota Média'].median() if total > 0 else 0

    col_k1.metric('Total de Candidatos', f'{total:,}')
    col_k2.metric('Escola Pública', f'{pct_pub:.1f}%')
    col_k3.metric('Escola Privada', f'{pct_priv:.1f}%')
    col_k4.metric('Mediana Nota Média Geral', f'{med_nota:.1f}')

    st.subheader('G1 — Distribuição por Tipo de Escola')
    g1_data = df_filt['Tipo de Escola'].value_counts().reset_index()
    g1_data.columns = ['Tipo de Escola', 'Contagem']
    g1 = px.pie(
        g1_data, names='Tipo de Escola', values='Contagem',
        title='Distribuição por Tipo de Escola',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'}
    )
    safe_chart(g1, 'g1')

    st.subheader('G2 — Distribuição por Raça/Cor')
    g2_data = df_filt['Raça/Cor'].value_counts().reset_index()
    g2_data.columns = ['Raça/Cor', 'Contagem']
    g2 = px.bar(
        g2_data, y='Raça/Cor', x='Contagem',
        orientation='h', title='Candidatos por Raça/Cor',
        color='Raça/Cor', text_auto=True
    )
    g2.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    safe_chart(g2, width='stretch')

    st.subheader('G3 — Distribuição por Faixa Etária')
    age_order = ['<17','17','18','19','20','21','22','23','24','25',
                 '26–30','31–35','36–40','41–45','46–50','51–55','56–60',
                 '61–65','66–70','>70']
    g3_data = df_filt['Faixa Etária'].value_counts().reindex(age_order).dropna().reset_index()
    g3_data.columns = ['Faixa Etária', 'Contagem']
    g3 = px.bar(
        g3_data, x='Faixa Etária', y='Contagem',
        title='Candidatos por Faixa Etária',
        color='Contagem', color_continuous_scale='Blues'
    )
    safe_chart(g3, width='stretch')

    st.subheader('G4 — Distribuição por Sexo')
    g4_data = df_filt['Sexo'].value_counts().reset_index()
    g4_data.columns = ['Sexo', 'Contagem']
    g4 = px.pie(
        g4_data, names='Sexo', values='Contagem',
        title='Distribuição por Sexo',
        color_discrete_map={'Masculino': '#2ca02c', 'Feminino': '#d62728'}
    )
    safe_chart(g4, width='stretch')

    st.subheader('G5 — Candidatos por Região e Tipo de Escola')
    g5_data = df_filt.groupby(['Região', 'Tipo de Escola']).size().reset_index(name='Contagem')
    g5 = px.bar(
        g5_data, x='Região', y='Contagem', color='Tipo de Escola',
        barmode='group', title='Candidatos por Região e Tipo de Escola',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'}
    )
    safe_chart(g5, width='stretch')

    st.subheader('G6 — Candidatos por Estado')
    g6_data = df_filt['SG_UF_PROVA'].value_counts().head(27).reset_index()
    g6_data.columns = ['UF', 'Contagem']
    g6 = px.bar(
        g6_data, y='UF', x='Contagem',
        orientation='h', title='Candidatos por Estado (top 27)',
        color='Contagem', text_auto=True
    )
    g6.update_layout(yaxis={'categoryorder': 'total ascending'})
    safe_chart(g6, width='stretch')

    st.subheader('G7 — Distribuição das Notas por Área')
    st.markdown('**Dataset Completo**')
    g7 = px.box(
        df_long, x='Área', y='Nota',
        title='Distribuição das Notas por Área',
        color='Área'
    )
    safe_chart(g7, width='stretch')
    st.markdown('**Pública vs. Privada**')
    g7b = px.box(
        df_long, x='Área', y='Nota', color='Tipo de Escola',
        title='Distribuição das Notas por Área e Tipo de Escola',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'}
    )
    safe_chart(g7b, width='stretch')

    st.subheader('G8 — Mediana por Área e Tipo de Escola')
    g8_data = df_filt.groupby('Tipo de Escola')[AREAS].median().reset_index()
    g8_long = g8_data.melt(id_vars='Tipo de Escola', var_name='Área', value_name='Mediana')
    g8 = px.bar(
        g8_long, x='Área', y='Mediana', color='Tipo de Escola',
        barmode='group',
        title='Mediana das Notas por Área e Tipo de Escola',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'},
        text_auto='.1f'
    )
    safe_chart(g8, width='stretch')

with tab2:
    st.header('RQ1 — Tipo de Escola e Desempenho no ENEM 2024')
    st.info(
        '**Pergunta:** Como o tipo de escola (pública vs. privada) '
        'influencia o desempenho dos candidatos no ENEM 2024?'
    )

    st.subheader('R1.1 — Mediana por Área: Pública vs. Privada')
    r11_data = df_filt.groupby('Tipo de Escola')[AREAS].median().reset_index()
    r11_long = r11_data.melt(id_vars='Tipo de Escola', var_name='Área', value_name='Mediana')
    r11 = px.bar(
        r11_long, x='Área', y='Mediana', color='Tipo de Escola',
        barmode='group',
        title='Mediana das Notas por Área: Pública vs. Privada',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'},
        text_auto='.1f'
    )
    safe_chart(r11, width='stretch')

    st.subheader('R1.2 — Distribuição das Notas: Pública vs. Privada')
    r12 = px.box(
        df_long, x='Área', y='Nota', color='Tipo de Escola',
        title='Distribuição das Notas por Área: Pública vs. Privada',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'}
    )
    safe_chart(r12, width='stretch')

    st.subheader('R1.3 — % de Candidatos com Nota > 600: Pública vs. Privada')
    try:
        r13_data = []
        for area in AREAS:
            grp = df_filt.groupby('Tipo de Escola')
            total_escola = grp.size()
            acima_escola = grp[area].apply(lambda x: (x > 600).sum())
            pct = (acima_escola / total_escola * 100).reset_index()
            pct.columns = ['Tipo de Escola', 'Percentual']
            pct['Área'] = area
            r13_data.append(pct)
        r13_df = pd.concat(r13_data, ignore_index=True)
        r13 = px.bar(
            r13_df, x='Área', y='Percentual', color='Tipo de Escola',
            barmode='group',
            title='% de Candidatos com Nota > 600 por Área',
            color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'},
            text_auto='.1f'
        )
        r13.update_layout(yaxis_title='% Candidatos')
        safe_chart(r13, width='stretch')
    except Exception:
        st.warning('Gráfico R1.3 indisponível para este recorte.')

    st.subheader('R1.4 — Distribuição da Nota Média Geral por Tipo de Escola')
    r14 = px.histogram(
        df_filt.sample(min(50000, len(df_filt))), x='Nota Média', color='Tipo de Escola',
        opacity=0.5, barmode='overlay', nbins=50,
        title='Distribuição da Nota Média Geral: Pública vs. Privada',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'},
        labels={'Nota Média': 'Nota Média Geral', 'count': 'Frequência'}
    )
    safe_chart(r14, width='stretch')

    med_por_escola = df_filt.groupby('Tipo de Escola')[AREAS].median()
    if 'Privada' in med_por_escola.index and 'Pública' in med_por_escola.index:
        gaps = med_por_escola.loc['Privada'] - med_por_escola.loc['Pública']
        maior_gap_area = gaps.idxmax()
        menor_gap_area = gaps.idxmin()
        gap_mt = gaps['Matemática']
        st.success(
            f'**Insights:**'
            f'\n- Candidatos de escolas privadas têm mediana **{gap_mt:.1f} pontos** acima '
            f'das públicas em Matemática.'
            f'\n- A maior diferença está em **{maior_gap_area}** ({gaps[maior_gap_area]:.1f} pts).'
            f'\n- A menor diferença está em **{menor_gap_area}** ({gaps[menor_gap_area]:.1f} pts).'
        )

with tab3:
    st.header('RQ2 — Renda Familiar e Desempenho no ENEM 2024')
    st.info(
        '**Pergunta:** Qual a relação entre a renda familiar mensal '
        'e o desempenho médio no ENEM 2024?'
    )
    st.warning(
        '**Limitação:** O microdado do ENEM 2024 contém apenas 2 dos 20 valores '
        'possíveis para **Q006** (renda familiar): **A** ("Nenhuma renda") e '
        '**B** ("Até R$1.320"). As demais 18 faixas (C–T) não estão presentes '
        'neste ano, independentemente dos filtros aplicados. Com apenas dois '
        'grupos de baixa renda, as medianas são naturalmente muito próximas.'
    )

    st.subheader('R2.1 — Relação entre Renda Familiar e Nota Média (Mediana)')
    r21_data = df_filt.groupby('Renda Familiar', observed=True)['Nota Média'].median().reset_index()
    r21 = px.line(
        r21_data, x='Renda Familiar', y='Nota Média',
        markers=True, title='Relação entre Renda Familiar e Nota Média (Mediana)',
        labels={'Renda Familiar': 'Faixa de Renda', 'Nota Média': 'Mediana da Nota Média'}
    )
    r21.update_layout(xaxis_tickangle=-45)
    safe_chart(r21, width='stretch')

    st.subheader('R2.2 — Mediana das Notas por Área e Faixa de Renda')
    r22_data = df_filt.groupby('Renda Familiar', observed=True)[AREAS].median().reset_index()
    r22 = px.bar(
        r22_data.melt(id_vars='Renda Familiar', var_name='Área', value_name='Mediana'),
        x='Área', y='Mediana', color='Renda Familiar',
        barmode='group', text_auto='.0f',
        title='Mediana das Notas por Área e Faixa de Renda'
    )
    safe_chart(r22, width='stretch')

    st.subheader('R2.3 — Distribuição de Candidatos por Faixa de Renda')
    r23_data = df_filt.groupby('Renda Familiar', observed=True).size().reset_index(name='Contagem')
    r23 = px.bar(
        r23_data, x='Renda Familiar', y='Contagem',
        title='Distribuição de Candidatos por Faixa de Renda',
        color='Contagem', color_continuous_scale='Viridis',
        labels={'Renda Familiar': 'Faixa de Renda', 'Contagem': 'Número de Candidatos'}
    )
    r23.update_layout(xaxis_tickangle=-45)
    safe_chart(r23, width='stretch')

    st.subheader('R2.4 — Mediana por Renda e Tipo de Escola')
    r24_data = df_filt.groupby(['Renda Familiar', 'Tipo de Escola'], observed=True)['Nota Média'].median().reset_index()
    r24 = px.bar(
        r24_data, x='Renda Familiar', y='Nota Média', color='Tipo de Escola',
        barmode='group',
        title='Mediana da Nota Média por Renda e Tipo de Escola',
        color_discrete_map={'Pública': '#1f77b4', 'Privada': '#ff7f0e'},
        labels={'Renda Familiar': 'Faixa de Renda', 'Nota Média': 'Mediana da Nota Média'}
    )
    r24.update_layout(xaxis_tickangle=-45)
    safe_chart(r24, width='stretch')

    renda_groups = df_filt.groupby('Renda Familiar', observed=True)['Nota Média'].median()
    if len(renda_groups) >= 2:
        med_menor = renda_groups.iloc[0]
        med_maior = renda_groups.iloc[-1]
        pct_change = ((med_maior - med_menor) / med_menor) * 100 if med_menor > 0 else 0

        diffs = renda_groups.diff().dropna()
        max_jump_idx = diffs.idxmax()
        max_jump_val = diffs.max()
        prev_idx = renda_groups.index.get_loc(max_jump_idx) - 1
        prev_label = renda_groups.index[prev_idx]

        st.success(
            f'**Insights:**'
            f'\n- A mediana da nota média sobe **{pct_change:.1f}%** da menor faixa '
            f'("{renda_groups.index[0]}": {med_menor:.1f}) para a maior faixa '
            f'("{renda_groups.index[-1]}": {med_maior:.1f}).'
            f'\n- O maior salto ocorre entre "{prev_label}" e "{max_jump_idx}" '
            f'(+{max_jump_val:.1f} pts).'
        )
