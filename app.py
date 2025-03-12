import streamlit as st

# Configuração da página
st.set_page_config(page_title="IDH Expert", page_icon="📊", layout="wide")

# Script global para controle de scroll com delay
st.markdown("""
    <script>
        function forceScrollToTop() {
            setTimeout(function() {
                window.scrollTo(0, 0);
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            }, 100);
        }
    </script>
""", unsafe_allow_html=True)

import pandas as pd
from utils.data_prep import *
import plotly.express as px
import locale
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go
from models.xgb_model import load_trained_model, predict_idh
from utils.data_prep import load_and_filter_data, get_municipality_data

@st.cache_data
def load_data():
    return pd.read_csv('df_exported.csv')

@st.cache_resource
def prepare_model():
    model, scaler, features = load_trained_model()
    return model, scaler, features

# Carregar dados e modelo com indicadores de progresso
with st.spinner('Carregando dados...'):
    df = load_data()
    df_filtered = df[df['População residente'] <= 100000].copy()
    
with st.spinner('Preparando modelo...'):
    model, scaler, features = prepare_model()

# Inicialização do session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False

if 'selected_municipality' not in st.session_state:
    st.session_state.selected_municipality = None

# Função para classificar IDH
def classificar_idh(valor):
    if valor < 0.500:
        return "IDH Baixo"
    elif valor < 0.800:
        return "IDH Médio"
    elif valor < 0.900:
        return "IDH Alto"
    else:
        return "IDH Muito Alto"

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        locale.setlocale(locale.LC_ALL, '')

# Carregar os dados
@st.cache_data
def load_data():
    df = pd.read_csv('df_exported.csv')
    df['classificacao_idh'] = df['IDH'].apply(classificar_idh)
    return df

df = load_data()

# Lógica de navegação entre páginas
if st.session_state.page == 'home':
    # Página inicial
    st.title('IDH Expert')
    st.write('Explore dados e obtenha insights para aumentar o IDH dos municípios brasileiros.')

    # Criar duas colunas principais com proporção ajustada e gap maior
    col_graficos, col_metricas = st.columns([0.65, 0.35], gap="large")

    # Coluna da esquerda (gráfico)
    with col_graficos:
        st.markdown("### IDH Médio por Estado")
        
        # Gráfico de IDH por Estado (ordenado do menor para o maior)
        df_estado = df.groupby('estado')['IDH'].mean().sort_values().reset_index()
        fig_estado = px.bar(df_estado, 
                        x='estado', 
                        y='IDH',
                        color='IDH',
                        color_continuous_scale='RdYlBu')
        
        fig_estado.update_layout(
            xaxis_title="Estado",
            yaxis_title="IDH Médio",
            showlegend=False
        )
        st.plotly_chart(fig_estado, use_container_width=True)

    # Coluna da direita (métricas)
    with col_metricas:
        st.markdown("""
            <style>
            [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
                margin-left: 2rem;
            }
            [data-testid="stMetricValue"] {
                font-size: 22px;
            }
            [data-testid="stMetricLabel"] {
                font-size: 14px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### Indicadores nacionais")
        
        # Métricas formatadas
        st.metric("📊 IDH Médio", f"{df['IDH'].mean():.3f}")
        st.metric("👥 População Total", f"{df['População residente'].sum():,.0f}".replace(',', '.'))
        st.metric("💰 % de Pobres", f"{df['% de pobres'].mean():.1f}%")
        st.metric("📈 Produtividade Média", f"R$ {df['Produtividade'].mean():,.2f}".replace(',', '.'))
        
        st.write("")
        st.write("")

    style_metric_cards()

    if st.button("🏠 Filtrar por Estado", key="filtrar_por_estado", use_container_width=True):
        st.session_state.page = "filter_state"
        st.markdown(
            """
            <script>
                window.scrollTo(0, 0);
            </script>
            """,
            unsafe_allow_html=True
        )
        st.rerun()

# INÍCIO DA VISUALIZAÇÃO POR ESTADO
elif st.session_state.page == 'filter_state':
    st.title("Análise por Estado")
    
    estado_selecionado = st.selectbox(
        "Selecione um estado",
        options=sorted(df['estado'].unique())
    )
    
    if estado_selecionado:
        df_estado = df[df['estado'] == estado_selecionado].copy()
        
        col_graf, col_metricas = st.columns([0.7, 0.3], gap="large")
        
        with col_graf:
            df_estado['faixa_idh'] = df_estado['IDH'].apply(classificar_idh)
            df_contagem = df_estado['faixa_idh'].value_counts().reset_index()
            df_contagem.columns = ['Faixa', 'Quantidade']

            fig_dist = px.bar(df_contagem, 
                            x='Faixa', 
                            y='Quantidade',
                            title='Distribuição dos Municípios por Faixa de IDH',
                            color='Faixa',
                            color_discrete_map={
                                'IDH Muito Alto': '#1a9850',
                                'IDH Alto': '#91cf60',
                                'IDH Médio': '#fc8d59',
                                'IDH Baixo': '#d73027'
                            })
            
            fig_dist.update_layout(
                showlegend=False,
                xaxis_title="Faixa",
                yaxis_title="Quantidade de Municípios"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col_metricas:
            st.markdown("### Indicadores do Estado")
            
            st.metric("Total de Municípios", len(df_estado))
            st.metric("População Total", f"{df_estado['População residente'].sum():,.0f}")
            st.metric("IDH Médio", f"{df_estado['IDH'].mean():.3f}")
            st.metric("% de Pobres", f"{df_estado['% de pobres'].mean():.1f}%")
            
            st.write("")
            st.write("")
            
        st.subheader("Ranking dos Municípios por IDH")

        df_ranking = df_estado[['estado', 'nomeLocalidade', 'IDH', 'População residente', '% de pobres', 'Produtividade', 'PIB Municipal']].sort_values('IDH', ascending=False)

        items_por_pagina = 10
        total_items = len(df_ranking)
        total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina

        pagina = st.number_input('Página', min_value=1, max_value=total_paginas, value=1) - 1

        inicio = pagina * items_por_pagina
        fim = min(inicio + items_por_pagina, total_items)

        df_pagina = df_ranking.iloc[inicio:fim].copy()

        df_pagina['População residente'] = df_pagina['População residente'].map('{:,.0f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_pagina['% de pobres'] = df_pagina['% de pobres'].map('{:.1f}'.format).str.replace('.', ',') + '%'
        df_pagina['Produtividade'] = df_pagina['Produtividade'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_pagina['PIB Municipal'] = df_pagina['PIB Municipal'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_pagina['IDH'] = df_pagina['IDH'].map('{:.3f}'.format).str.replace('.', ',')

        st.dataframe(
            df_pagina.set_index('estado').rename(columns={
                'nomeLocalidade': 'Município',
                'População residente': 'População'
            }),
            column_config={
                "Município": st.column_config.TextColumn(width="medium"),
                "IDH": st.column_config.TextColumn(width="small"),
                "População": st.column_config.TextColumn(width="medium"),
                "% de pobres": st.column_config.TextColumn(width="small"),
                "Produtividade": st.column_config.TextColumn(width="medium"),
                "PIB Municipal": st.column_config.TextColumn(width="medium")
            },
            use_container_width=True
        )

        st.text(f'Mostrando {inicio+1}-{fim} de {total_items} municípios')

        st.markdown("""
            **Notas:**
            - **Produtividade**: PIB municipal dividido pela população economicamente ativa e ocupada
            - **PIB Municipal**: Valor calculado seguindo metodologia do IBGE alinhada às recomendações das Nações Unidas
        """)

        st.markdown("---")
        st.subheader("Municípios com Maior Potencial de Investimento")

        def calcular_score_potencial(row, pop_max):
            idh_norm = 1 - row['IDH']
            pobres_norm = 1 - (row['% de pobres'] / 100)
            pop_norm = 1 - (row['População residente'] / pop_max)
            
            peso_idh = 0.5
            peso_pobres = 0.3
            peso_pop = 0.2
            
            return (idh_norm * peso_idh) + (pobres_norm * peso_pobres) + (pop_norm * peso_pop)

        df_potencial = df_estado.copy()
        pop_max = df_potencial['População residente'].max()
        df_potencial['score'] = df_potencial.apply(lambda x: calcular_score_potencial(x, pop_max), axis=1)
        df_top10 = df_potencial.nlargest(10, 'score')[['estado', 'nomeLocalidade', 'IDH', 'População residente', '% de pobres', 'Produtividade', 'PIB Municipal']]

        df_top10 = df_top10.rename(columns={'nomeLocalidade': 'Município'})

        df_top10['População residente'] = df_top10['População residente'].map('{:,.0f}'.format).str.replace(',', '.')
        df_top10['% de pobres'] = df_top10['% de pobres'].map('{:.1f}%'.format)
        df_top10['Produtividade'] = df_top10['Produtividade'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_top10['PIB Municipal'] = df_top10['PIB Municipal'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_top10['IDH'] = df_top10['IDH'].map('{:.3f}'.format)

        st.write("Top 10 municípios com maior potencial de melhoria do IDH através de investimentos:")

        st.markdown("""
        **Critérios de seleção:**
        - IDH mais baixo (50% do peso)
        - Menor percentual de pobres (30% do peso)
        - Menor população (20% do peso)
        """)

        st.dataframe(
            df_top10.set_index('estado'),
            column_config={
                "": st.column_config.TextColumn(width=150),
                "Município": st.column_config.TextColumn(width=200),
                "IDH": st.column_config.TextColumn(width=100),
                "População residente": st.column_config.TextColumn("População", width=120),
                "% de pobres": st.column_config.TextColumn(width=100),
                "Produtividade": st.column_config.TextColumn(width=150),
                "PIB Municipal": st.column_config.TextColumn(width=150)
            },
            hide_index=False,
            use_container_width=True
        )

        for idx, row in df_top10.iterrows():
            if st.button(f"Ver detalhes - {row['Município']}", key=f"btn_{idx}"):
                st.session_state.page = 'municipality_detail'
                st.session_state.selected_municipality = row['Município']
                st.markdown('<script>forceScrollToTop();</script>', unsafe_allow_html=True)
                st.rerun()

        st.markdown("---")

        if st.button("← Voltar"):
            st.session_state.page = "home"
            st.rerun()

# INÍCIO DA VISUALIZAÇÃO POR MUNICÍPIO
            
elif st.session_state.page == 'municipality_detail':
    # Componente invisível no topo absoluto
    st.markdown('<div style="position: absolute; top: 0;"></div>', unsafe_allow_html=True)
    st.markdown('<script>forceScrollToTop();</script>', unsafe_allow_html=True)

    st.title("Análise Detalhada do Município")
    
    if st.session_state.selected_municipality:
        municipio = st.session_state.selected_municipality
        df_mun = df[df['nomeLocalidade'] == municipio].iloc[0]
        df_estado = df[df['estado'] == df_mun['estado']]
        media_nacional = df['IDH'].mean()
        
        # Botão de voltar
        if st.button("← Voltar"):
            st.session_state.page = "filter_state"
            st.rerun()
            
        # Cabeçalho com informações básicas
        st.header(f"{municipio} - {df_mun['estado']}")

        # Cards com indicadores principais
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            idh_diff = df_mun['IDH'] - media_nacional
            color = "red" if idh_diff < 0 else "gray"
            st.markdown(f"""
                <h3 style='margin: 0; font-size: 1rem; font-weight: 600'>IDH Municipal</h3>
                <p style='font-size: 2rem; margin: 0'>{df_mun['IDH']:.3f}</p>
                <p style='color: {color}; margin: 0'>Média nacional: {media_nacional:.3f}</p>
            """, unsafe_allow_html=True)

        with col2:
            pop_percent = (df_mun['População residente']/df_estado['População residente'].sum()*100)
            st.markdown(f"""
                <h3 style='margin: 0; font-size: 1rem; font-weight: 600'>População</h3>
                <p style='font-size: 2rem; margin: 0'>{format(df_mun['População residente'], ',.0f').replace(',', '.')}</p>
                <p style='color: gray; margin: 0'>{pop_percent:.1f}% do estado</p>
            """, unsafe_allow_html=True)

        with col3:
            pobres_diff = df_mun['% de pobres'] - df_estado['% de pobres'].mean()
            color = "red" if pobres_diff > 0 else "gray"
            st.markdown(f"""
                <h3 style='margin: 0; font-size: 1rem; font-weight: 600'>% de Pobres</h3>
                <p style='font-size: 2rem; margin: 0'>{df_mun['% de pobres']:.1f}%</p>
                <p style='color: {color}; margin: 0'>Média estadual: {df_estado['% de pobres'].mean():.1f}%</p>
            """, unsafe_allow_html=True)

        with col4:
            salario_diff = df_mun['Média Salarial'] - df_estado['Média Salarial'].mean()
            color = "red" if salario_diff < 0 else "gray"
            st.markdown(f"""
                <h3 style='margin: 0; font-size: 1rem; font-weight: 600'>Média Salarial</h3>
                <p style='font-size: 2rem; margin: 0'>R$ {df_mun['Média Salarial']:,.2f}</p>
                <p style='color: {color}; margin: 0'>Média estadual: R$ {df_estado['Média Salarial'].mean():,.2f}</p>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # SEÇÃO DE TABELAS DE INDICADORES SOCIOECONOMICOS E INFRAESTRUTURA
        st.markdown("<h3 style='margin: 20px 0; font-size: 1.1rem; font-weight: bold;'>Diagnóstico por Área</h3>", unsafe_allow_html=True)

        # Tabela de Educação
        st.markdown("<h4 style='margin: 10px 0; font-size: 1rem; font-weight: bold;'>Educação</h4>", unsafe_allow_html=True)

        # Correlações com IDH (Spearman)
        education_correlations = {
            'Ativos com Alto Nível Educacional': 0.635790,
            'Ativos com Médio Nível Educacional': 0.304849,
            'Ativos com Baixo Nível Educacional': -0.464217
        }

        # Calcular as diferenças
        differences = []
        for indicator in ['Ativos com Alto Nível Educacional', 'Ativos com Médio Nível Educacional', 'Ativos com Baixo Nível Educacional']:
            local_val = float(df_mun[indicator])
            national_val = df[indicator].mean()
            diff = local_val - national_val
            color = 'red' if diff < 0 else 'green'
            differences.append(f"<span style='color: {color}'>{'+'if diff > 0 else ''}{diff:.1f}%</span>")

        # Criar o dicionário com todas as colunas
        education_data = {
            'Indicador': ['Ativos com Alto Nível Educacional', 'Ativos com Médio Nível Educacional', 'Ativos com Baixo Nível Educacional'],
            'Índice Local': [f"{df_mun['Ativos com Alto Nível Educacional']:.1f}%", f"{df_mun['Ativos com Médio Nível Educacional']:.1f}%", f"{df_mun['Ativos com Baixo Nível Educacional']:.1f}%"],
            'Média Estadual': [f"{df_estado['Ativos com Alto Nível Educacional'].mean():.1f}%", f"{df_estado['Ativos com Médio Nível Educacional'].mean():.1f}%", f"{df_estado['Ativos com Baixo Nível Educacional'].mean():.1f}%"],
            'Média Nacional': [f"{df['Ativos com Alto Nível Educacional'].mean():.1f}%", f"{df['Ativos com Médio Nível Educacional'].mean():.1f}%", f"{df['Ativos com Baixo Nível Educacional'].mean():.1f}%"],
            'Diferença p/ Média Nacional': differences,
            'Correlação c/ IDH': [f"{education_correlations['Ativos com Alto Nível Educacional']:.3f}", f"{education_correlations['Ativos com Médio Nível Educacional']:.3f}", f"{education_correlations['Ativos com Baixo Nível Educacional']:.3f}"]
        }

        # Criar e exibir a tabela
        df_education = pd.DataFrame(education_data)
        styled_table = (df_education.style
            .hide(axis='index')
            .set_properties(**{'text-align': 'center', 'padding': '8px'})
            .set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f0f2f6'), ('padding', '8px')]},
                {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '8px')]}
            ])
        )
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)

        # TABELA DE EMPREGO E RENDA (com PIB Municipal)
        st.markdown("<h4 style='margin: 10px 0; font-size: 1rem; font-weight: bold;'>Emprego e Renda</h4>", unsafe_allow_html=True)

        # Correlações com IDH (Spearman)
        income_correlations = {
            '% de pobres': -0.833024,
            'Média Salarial': 0.390501,
            'Produtividade': 0.612564,
            'PIB Municipal': 0.337092
        }

        # Calcular as diferenças
        income_differences = []
        for indicator in ['% de pobres', 'Média Salarial', 'Produtividade', 'PIB Municipal']:
            local_val = float(df_mun[indicator])
            national_val = df[indicator].mean()
            diff = local_val - national_val
            if indicator == '% de pobres':
                color = 'red' if diff > 0 else 'green'
                income_differences.append(f"<span style='color: {color}'>{'+'if diff > 0 else ''}{diff:.1f}%</span>")
            else:
                color = 'red' if diff < 0 else 'green'
                income_differences.append(f"<span style='color: {color}'>{'+'if diff > 0 else ''}R$ {diff:,.2f}</span>")

        # Criar o dicionário com todas as colunas
        income_data = {
            'Indicador': ['% de pobres', 'Média Salarial', 'Produtividade', 'PIB Municipal'],
            'Índice Local': [f"{df_mun['% de pobres']:.1f}%", f"R$ {df_mun['Média Salarial']:,.2f}", f"R$ {df_mun['Produtividade']:,.2f}", f"R$ {df_mun['PIB Municipal']:,.2f}"],
            'Média Estadual': [f"{df_estado['% de pobres'].mean():.1f}%", f"R$ {df_estado['Média Salarial'].mean():,.2f}", f"R$ {df_estado['Produtividade'].mean():,.2f}", f"R$ {df_estado['PIB Municipal'].mean():,.2f}"],
            'Média Nacional': [f"{df['% de pobres'].mean():.1f}%", f"R$ {df['Média Salarial'].mean():,.2f}", f"R$ {df['Produtividade'].mean():,.2f}", f"R$ {df['PIB Municipal'].mean():,.2f}"],
            'Diferença p/ Média Nacional': income_differences,
            'Correlação c/ IDH': [f"{income_correlations['% de pobres']:.3f}", f"{income_correlations['Média Salarial']:.3f}", f"{income_correlations['Produtividade']:.3f}", f"{income_correlations['PIB Municipal']:.3f}"]
        }

        # Criar e exibir a tabela
        df_income = pd.DataFrame(income_data)
        styled_table = (df_income.style
            .hide(axis='index')
            .set_properties(**{'text-align': 'center', 'padding': '8px'})
            .set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f0f2f6'), ('padding', '8px')]},
                {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '8px')]}
            ])
        )
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)

        # TABELA DE INFRAESTRUTURA E RECURSOS DE SAÚDE
        st.markdown("<h4 style='margin: 10px 0; font-size: 1rem; font-weight: bold;'>Infraestrutura e Recursos de Saúde</h4>", unsafe_allow_html=True)

        # Correlações com IDH (Spearman)
        health_correlations = {
            'Taxa de Saneamento Básico': 0.319285,
            'Médicos por milhares de habitantes': 0.398484,
            'Hospitais por milhares de habitantes': 0.332249
        }

        # Calcular as diferenças
        health_differences = []
        for indicator in ['Taxa de Saneamento Básico', 'Médicos por milhares de habitantes', 'Hospitais por milhares de habitantes']:
            local_val = float(df_mun[indicator])
            national_val = df[indicator].mean()
            diff = local_val - national_val
            if indicator == 'Taxa de Saneamento Básico':
                color = 'red' if diff < 0 else 'green'
                health_differences.append(f"<span style='color: {color}'>{'+'if diff > 0 else ''}{diff:.1f}%</span>")
            else:
                color = 'red' if diff < 0 else 'green'
                health_differences.append(f"<span style='color: {color}'>{'+'if diff > 0 else ''}{diff:.3f}</span>")

        # Criar o dicionário com todas as colunas
        health_data = {
            'Indicador': ['Taxa de Saneamento Básico', 'Médicos por milhares de habitantes', 'Hospitais por milhares de habitantes'],
            'Índice Local': [f"{df_mun['Taxa de Saneamento Básico']:.1f}%", f"{df_mun['Médicos por milhares de habitantes']:.3f}", f"{df_mun['Hospitais por milhares de habitantes']:.3f}"],
            'Média Estadual': [f"{df_estado['Taxa de Saneamento Básico'].mean():.1f}%", f"{df_estado['Médicos por milhares de habitantes'].mean():.3f}", f"{df_estado['Hospitais por milhares de habitantes'].mean():.3f}"],
            'Média Nacional': [f"{df['Taxa de Saneamento Básico'].mean():.1f}%", f"{df['Médicos por milhares de habitantes'].mean():.3f}", f"{df['Hospitais por milhares de habitantes'].mean():.3f}"],
            'Diferença p/ Média Nacional': health_differences,
            'Correlação c/ IDH': [f"{health_correlations['Taxa de Saneamento Básico']:.3f}", f"{health_correlations['Médicos por milhares de habitantes']:.3f}", f"{health_correlations['Hospitais por milhares de habitantes']:.3f}"]
        }

        # Criar e exibir a tabela
        df_health = pd.DataFrame(health_data)
        styled_table = (df_health.style
            .hide(axis='index')
            .set_properties(**{'text-align': 'center', 'padding': '8px'})
            .set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold'), ('background-color', '#f0f2f6'), ('padding', '8px')]},
                {'selector': 'td', 'props': [('text-align', 'center'), ('padding', '8px')]}
            ])
        )
        st.markdown(styled_table.to_html(), unsafe_allow_html=True)

        # SEÇÃO DE RECOMENDAÇÕES (mantida como estava)
        st.markdown("<br><hr style='margin: 30px 0; border: 0.5px solid #e6e6e6;'><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 20px 0; font-size: 1.1rem; font-weight: bold;'>Recomendações por Área</h3>", unsafe_allow_html=True)

        media_alto_estado = df_estado['Ativos com Alto Nível Educacional'].mean()
        media_baixo_estado = df_estado['Ativos com Baixo Nível Educacional'].mean()
        media_pobres = df_estado['% de pobres'].mean()
        media_saneamento_estado = df_estado['Taxa de Saneamento Básico'].mean()

        media_nacional_alto = df['Ativos com Alto Nível Educacional'].mean()
        media_nacional_baixo = df['Ativos com Baixo Nível Educacional'].mean()
        media_nacional_pobres = df['% de pobres'].mean()
        media_nacional_saneamento = df['Taxa de Saneamento Básico'].mean()
            
        medicos = df_mun['Médicos por milhares de habitantes']
        media_estado_medicos = df_estado['Médicos por milhares de habitantes'].mean()
        media_nacional_medicos = df['Médicos por milhares de habitantes'].mean()

        hospitais = df_mun['Hospitais por milhares de habitantes']
        media_estado_hospitais = df_estado['Hospitais por milhares de habitantes'].mean()
        media_nacional_hospitais = df['Hospitais por milhares de habitantes'].mean()
            
        alto_nivel = df_mun['Ativos com Alto Nível Educacional']
        medio_nivel = df_mun['Ativos com Médio Nível Educacional']
        baixo_nivel = df_mun['Ativos com Baixo Nível Educacional']

        pobres = df_mun['% de pobres']
        diferenca_pobres = pobres - media_nacional_pobres

        saneamento = df_mun['Taxa de Saneamento Básico']
        diferenca_saneamento = saneamento - media_nacional_saneamento

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<h4 style='font-size: 1rem; font-weight: bold;'>Educação</h4>", unsafe_allow_html=True)
            recomendacoes_educacao = []
            if alto_nivel < media_nacional_alto:
                recomendacoes_educacao.append("• Investir em programas de educação superior e qualificação profissional")
            if medio_nivel < df['Ativos com Médio Nível Educacional'].mean():
                recomendacoes_educacao.append("• Fortalecer programas de ensino técnico e profissionalizante")
            if baixo_nivel > media_nacional_baixo:
                recomendacoes_educacao.append("• Desenvolver programas de redução da evasão escolar e educação de jovens e adultos")
            
            if not recomendacoes_educacao:
                st.markdown("<p style='color: green;'>Indicadores educacionais acima da média nacional.</p>", unsafe_allow_html=True)
            else:
                for rec in recomendacoes_educacao:
                    st.markdown(rec)

        with col2:
            st.markdown("<h4 style='font-size: 1rem; font-weight: bold;'>Emprego e Renda</h4>", unsafe_allow_html=True)
            recomendacoes_renda = []
            if pobres > media_nacional_pobres:
                recomendacoes_renda.append("• Desenvolver programas de geração de emprego e renda")
                recomendacoes_renda.append("• Criar iniciativas de capacitação profissional")
            
            if not recomendacoes_renda:
                st.markdown("<p style='color: green;'>Indicadores de renda acima da média nacional.</p>", unsafe_allow_html=True)
            else:
                for rec in recomendacoes_renda:
                    st.markdown(rec)

        with col3:
            st.markdown("<h4 style='font-size: 1rem; font-weight: bold;'>Infraestrutura e Saúde</h4>", unsafe_allow_html=True)
            recomendacoes_saude = []
            if saneamento < media_nacional_saneamento:
                recomendacoes_saude.append("• Ampliar investimentos em infraestrutura de saneamento básico")
            if medicos < media_nacional_medicos:
                recomendacoes_saude.append("• Desenvolver programas de atração e fixação de profissionais de saúde")
                recomendacoes_saude.append("• Criar incentivos para estabelecimento de clínicas e consultórios médicos")
            if hospitais < media_nacional_hospitais:
                recomendacoes_saude.append("• Investir na construção ou ampliação de unidades de saúde")
                recomendacoes_saude.append("• Estabelecer parcerias para implementação de postos de atendimento")
            
            if not recomendacoes_saude:
                st.markdown("<p style='color: green;'>Indicadores de saúde acima da média nacional.</p>", unsafe_allow_html=True)
            else:
                for rec in recomendacoes_saude:
                    st.markdown(rec)

        # Fechando todas as colunas anteriores
        st.write("")

        # Início da seção do simulador

        st.markdown("<br><hr style='margin: 30px 0; border: 0.5px solid #e6e6e6;'><br>", unsafe_allow_html=True)

        # Função de callback para o reset
        def reset_values():
            # Atualizar diretamente os valores no Session State
            st.session_state.pobres = float(mun_data['% de pobres'])
            st.session_state.alto_nivel = float(mun_data['Ativos com Alto Nível Educacional'])
            st.session_state.produtividade = float(mun_data['Produtividade'])
            st.session_state.medicos = float(mun_data['Médicos por milhares de habitantes'])
            st.session_state.media_salarial = float(mun_data['Média Salarial'])
            st.session_state.pib = float(mun_data['PIB Municipal'])

        # Título da seção
        st.markdown("<p style='font-size: 1.1rem; font-weight: bold;'>Simulador de Impacto por Indicador Relevante</p>", unsafe_allow_html=True)

        # Dados atuais do município
        mun_data = get_municipality_data(df_filtered, st.session_state.selected_municipality)

        # Inicializar valores no Session State (se ainda não existirem)
        if 'pobres' not in st.session_state:
            st.session_state.pobres = float(mun_data['% de pobres'])
        if 'alto_nivel' not in st.session_state:
            st.session_state.alto_nivel = float(mun_data['Ativos com Alto Nível Educacional'])
        if 'produtividade' not in st.session_state:
            st.session_state.produtividade = float(mun_data['Produtividade'])
        if 'medicos' not in st.session_state:
            st.session_state.medicos = float(mun_data['Médicos por milhares de habitantes'])
        if 'media_salarial' not in st.session_state:
            st.session_state.media_salarial = float(mun_data['Média Salarial'])
        if 'pib' not in st.session_state:
            st.session_state.pib = float(mun_data['PIB Municipal'])

        # Criar colunas com espaçamento aumentado
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("<p style='font-weight: bold; margin-bottom: 20px;'>Ajuste os Indicadores:</p>", unsafe_allow_html=True)
            
            # Sliders para ajuste (sem value, usando apenas Session State)
            st.slider(
                "% de pobres",
                min_value=0.0,
                max_value=100.0,
                key='pobres',
                step=0.1
            )

            st.slider(
                "Ativos com Alto Nível Educacional (%)",
                min_value=0.0,
                max_value=50.0,
                key='alto_nivel',
                step=0.1
            )

            st.slider(
                "Produtividade (R$)",
                min_value=0.0,
                max_value=float(df_filtered['Produtividade'].max()),
                key='produtividade',
                step=100.0
            )

            st.slider(
                "Médicos por milhares de habitantes",
                min_value=0.0,
                max_value=float(df_filtered['Médicos por milhares de habitantes'].max()),
                key='medicos',
                step=0.001
            )

            st.slider(
                "Média Salarial (R$)",
                min_value=500.0,
                max_value=5000.0,
                key='media_salarial',
                step=50.0
            )

            st.slider(
                "PIB Municipal (R$)",
                min_value=0.0,
                max_value=float(df_filtered['PIB Municipal'].max()),
                key='pib',
                step=1000.0
            )

            # Botão de reset após os sliders
            st.button("Resetar Valores", on_click=reset_values)

        with col2:
            st.markdown("<p style='font-weight: bold; margin-bottom: 20px;'>Impacto Estimado no IDH:</p>", unsafe_allow_html=True)
            
            # Preparar dados para previsão
            input_data = pd.DataFrame({
                '% de pobres': [st.session_state.pobres],
                'Ativos com Alto Nível Educacional': [st.session_state.alto_nivel],
                'Produtividade': [st.session_state.produtividade],
                'Médicos por milhares de habitantes': [st.session_state.medicos],
                'Média Salarial': [st.session_state.media_salarial],
                'PIB Municipal': [st.session_state.pib]
            })[features]

            # Fazer previsão
            idh_previsto = predict_idh(model, scaler, features, input_data)
            
            # Mostrar IDH Atual
            col2.metric(
                "IDH Atual",
                f"{mun_data['IDH']:.3f}"
            )
            
            # Calcular diferença
            diferenca = idh_previsto - mun_data['IDH']
            
            # Verificar se houve alteração nos valores originais
            valores_alterados = (
                st.session_state.pobres != float(mun_data['% de pobres']) or
                st.session_state.alto_nivel != float(mun_data['Ativos com Alto Nível Educacional']) or
                st.session_state.produtividade != float(mun_data['Produtividade']) or
                st.session_state.medicos != float(mun_data['Médicos por milhares de habitantes']) or
                st.session_state.media_salarial != float(mun_data['Média Salarial']) or
                st.session_state.pib != float(mun_data['PIB Municipal'])
            )
            
            # Mostrar IDH Previsto
            if valores_alterados:
                col2.metric(
                    "IDH Previsto",
                    f"{idh_previsto:.3f}",
                    f"{diferenca:+.3f}"
                )
            else:
                col2.metric(
                    "IDH Previsto",
                    f"{mun_data['IDH']:.3f}",
                    None
                )