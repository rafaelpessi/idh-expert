import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="PredictGov", page_icon="📊", layout="wide")

# Inicialização do estado da página
if 'page' not in st.session_state:
    st.session_state.page = 'home'

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

# Dicionário de regiões
regioes = {
    'Acre': 'Norte',
    'Alagoas': 'Nordeste',
    'Amapá': 'Norte',
    'Amazonas': 'Norte',
    'Bahia': 'Nordeste',
    'Ceará': 'Nordeste',
    'Distrito Federal': 'Centro-Oeste',
    'Espírito Santo': 'Sudeste',
    'Goiás': 'Centro-Oeste', 
    'Maranhão': 'Nordeste', 
    'Mato Grosso': 'Centro-Oeste', 
    'Mato Grosso do Sul': 'Centro-Oeste', 
    'Minas Gerais': 'Sudeste', 
    'Pará': 'Norte', 
    'Paraíba': 'Nordeste', 
    'Paraná': 'Sul', 
    'Pernambuco': 'Nordeste', 
    'Piauí': 'Nordeste', 
    'Rio de Janeiro': 'Sudeste',
    'Rio Grande do Norte': 'Nordeste', 
    'Rio Grande do Sul': 'Sul', 
    'Rondônia': 'Norte', 
    'Roraima': 'Norte', 
    'Santa Catarina': 'Sul', 
    'São Paulo': 'Sudeste', 
    'Sergipe': 'Nordeste', 
    'Tocantins': 'Norte'
}

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
    #df = pd.read_csv('novo_dataset.csv')
    #df = pd.read_excel('Cidade_Sirius.xlsx')
    df = pd.read_csv('df_exported.csv')
    df['regiao'] = df['estado'].map(regioes)
    df['classificacao_idh'] = df['IDH'].apply(classificar_idh)
    return df

df = load_data()

# Lógica de navegação entre páginas
if st.session_state.page == 'home':
    # Página inicial
    st.title('PredictGov | Otimizando Investimentos Municipais')
    st.write('Explore dados e preveja investimentos para aumentar o IDH dos municípios brasileiros.')

    # Criar duas colunas principais com proporção ajustada e gap maior
    col_graficos, col_metricas = st.columns([0.65, 0.35], gap="large")

    # Coluna da esquerda (gráficos)
    with col_graficos:
        st.markdown("### Análise do IDH por região e estado")
        
        tab1, tab2 = st.tabs(["IDH Médio por Região", "IDH Médio por Estado"])
        
        with tab1:
            df_regiao = df.groupby('regiao')['IDH'].mean().sort_values().reset_index()
            fig_regiao = px.bar(df_regiao, 
                            x='regiao',
                            y='IDH',
                            color='IDH',
                            text=df_regiao['IDH'].round(2),
                            color_continuous_scale='RdYlBu')
            
            fig_regiao.update_layout(
                xaxis_title="Região",
                yaxis_title="IDH Médio",
                showlegend=False,
                margin=dict(l=20, r=20, t=30, b=20),  # Ajuste das margens
                height=400  # Altura fixa para melhor proporção
            )
            fig_regiao.update_traces(textposition='outside')
            st.plotly_chart(fig_regiao, use_container_width=True)
        
        with tab2:
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
        # Adicionar espaço à esquerda usando CSS
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

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🏠 Filtrar por Estado", key="filtrar_por_estado", use_container_width=True):
            st.session_state.page = "filter_state"
            st.rerun()
            
    with col_btn2:
        if st.button("🔍 Filtrar por Município", key="filtrar_por_municipio", use_container_width=True):
            st.session_state.page = "filter_city"
            st.rerun()

# INÍCIO DA VISUALIZAÇÃO POR ESTADO

elif st.session_state.page == 'filter_state':
    st.title("Análise por Estado")
    
    estado_selecionado = st.selectbox(
        "Selecione um estado",
        options=sorted(df['estado'].unique())
    )
    
    if estado_selecionado:
        df_estado = df[df['estado'] == estado_selecionado]
        
        # Criar duas colunas principais
        col_graf, col_metricas = st.columns([0.7, 0.3], gap="large")
        
        # Coluna da esquerda (gráfico)
        with col_graf:
            # Gráfico de distribuição por IDH
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
        
        # Coluna da direita (métricas)
        with col_metricas:
            st.markdown("### Indicadores do Estado")
            
            st.metric("Total de Municípios", len(df_estado))
            st.metric("População Total", f"{df_estado['População residente'].sum():,.0f}")
            st.metric("IDH Médio", f"{df_estado['IDH'].mean():.3f}")
            st.metric("% de Pobres", f"{df_estado['% de pobres'].mean():.1f}%")
            
            st.write("")
            st.write("")
            
        # Ranking dos municípios
        st.subheader("Ranking dos Municípios por IDH")

        # Criar o dataframe para o ranking
        df_ranking = df_estado[['estado', 'nomeLocalidade', 'IDH', 'População residente', '% de pobres', 'Produtividade', 'PIB Municipal']].sort_values('IDH', ascending=False)

        # Configurações da paginação
        items_por_pagina = 10
        total_items = len(df_ranking)
        total_paginas = (total_items + items_por_pagina - 1) // items_por_pagina

        # Seletor de página
        pagina = st.number_input('Página', min_value=1, max_value=total_paginas, value=1) - 1

        # Calcular índices de início e fim
        inicio = pagina * items_por_pagina
        fim = min(inicio + items_por_pagina, total_items)

        # Filtrar dados para a página atual
        df_pagina = df_ranking.iloc[inicio:fim].copy()

        # Formatar os valores numéricos
        df_pagina['População residente'] = df_pagina['População residente'].map('{:,.0f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_pagina['% de pobres'] = df_pagina['% de pobres'].map('{:.1f}'.format).str.replace('.', ',') + '%'
        df_pagina['Produtividade'] = df_pagina['Produtividade'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_pagina['PIB Municipal'] = df_pagina['PIB Municipal'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_pagina['IDH'] = df_pagina['IDH'].map('{:.3f}'.format).str.replace('.', ',')

        # Exibir o dataframe com configurações melhoradas
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

        # Informação sobre a paginação
        st.text(f'Mostrando {inicio+1}-{fim} de {total_items} municípios')

        # Adicionar legendas após a tabela
        st.markdown("""
            **Notas:**
            - **Produtividade**: PIB municipal dividido pela população economicamente ativa e ocupada
            - **PIB Municipal**: Valor calculado seguindo metodologia do IBGE alinhada às recomendações das Nações Unidas
        """)

        # Após o ranking atual, adicionar:
        st.markdown("---")
        st.subheader("Municípios com Maior Potencial de Investimento")

        # Criar função para calcular o score
        def calcular_score_potencial(row, pop_max):
            # Normalizar os valores entre 0 e 1 (onde 1 é melhor para investimento)
            idh_norm = 1 - row['IDH']  # Inverter para que menor IDH = maior score
            pobres_norm = 1 - (row['% de pobres'] / 100)  # Inverter para que menor % = maior score
            pop_norm = 1 - (row['População residente'] / pop_max)  # Inverter para que menor população = maior score
            
            # Pesos para cada critério
            peso_idh = 0.5  # 50% do peso
            peso_pobres = 0.3  # 30% do peso
            peso_pop = 0.2  # 20% do peso
            
            # Calcular score final
            return (idh_norm * peso_idh) + (pobres_norm * peso_pobres) + (pop_norm * peso_pop)

        # Calcular scores e selecionar top 10
        df_potencial = df_estado.copy()
        pop_max = df_potencial['População residente'].max()
        df_potencial['score'] = df_potencial.apply(lambda x: calcular_score_potencial(x, pop_max), axis=1)
        df_top10 = df_potencial.nlargest(10, 'score')[['estado', 'nomeLocalidade', 'IDH', 'População residente', '% de pobres', 'Produtividade', 'PIB Municipal']]

        # Renomear coluna
        df_top10 = df_top10.rename(columns={'nomeLocalidade': 'Município'})

        # Formatar os valores
        df_top10['População residente'] = df_top10['População residente'].map('{:,.0f}'.format).str.replace(',', '.')
        df_top10['% de pobres'] = df_top10['% de pobres'].map('{:.1f}%'.format)
        df_top10['Produtividade'] = df_top10['Produtividade'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_top10['PIB Municipal'] = df_top10['PIB Municipal'].map('R$ {:,.2f}'.format).str.replace('.', '*').str.replace(',', '.').str.replace('*', ',')
        df_top10['IDH'] = df_top10['IDH'].map('{:.3f}'.format)


        # Exibir a tabela com configurações visuais melhoradas
        st.write("Top 10 municípios com maior potencial de melhoria do IDH através de investimentos:")

        # Configurar e exibir o dataframe
        st.dataframe(
            df_top10.set_index('estado'),
            column_config={
                "": st.column_config.TextColumn(width=150),  # estado
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

        # Adicionar botões de ação para cada município
        for idx, row in df_top10.iterrows():
            if st.button(f"Ver detalhes - {row['Município']}", key=f"btn_{idx}"):
                st.session_state.page = 'municipality_detail'
                st.session_state.selected_municipality = row['Município']
                st.rerun()

        st.markdown("""
        **Critérios de seleção:**
        - IDH mais baixo (50% do peso)
        - Menor percentual de pobres (30% do peso)
        - Menor população (20% do peso)
        """)

        st.markdown("---")

        if st.button("← Voltar"):
                st.session_state.page = "home"
                st.rerun()

# FINAL DA VISUALIZAÇÃO POR ESTADO
                
# INÍCIO DA VISUALIZAÇÃO POR MUNICÍPIO

elif st.session_state.page == 'municipality_detail':
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
            prod_diff = df_mun['Produtividade'] - df_estado['Produtividade'].mean()
            color = "red" if prod_diff < 0 else "gray"
            st.markdown(f"""
                <h3 style='margin: 0; font-size: 1rem; font-weight: 600'>Produtividade</h3>
                <p style='font-size: 2rem; margin: 0'>R$ {df_mun['Produtividade']:,.2f}</p>
                <p style='color: {color}; margin: 0'>Média estadual: R$ {df_estado['Produtividade'].mean():,.2f}</p>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Comparativo com médias
        st.markdown("<br><br>", unsafe_allow_html=True)  # Adiciona espaço vertical
        st.subheader("Análise Comparativa")

        # Criar DataFrame para o gráfico de radar
        metricas = ['IDH', '% de pobres', 'Produtividade', 'PIB Municipal']
        valores_mun = [df_mun[m] for m in metricas]
        valores_estado = [df_estado[m].mean() for m in metricas]

        # Normalizar os valores para melhor comparação
        max_valores = {
            'IDH': 1,
            '% de pobres': 100,
            'Produtividade': max(df_estado['Produtividade'].max(), df_mun['Produtividade']),
            'PIB Municipal': max(df_estado['PIB Municipal'].max(), df_mun['PIB Municipal'])
        }

        valores_mun_norm = [df_mun[m]/max_valores[m] for m in metricas]
        valores_estado_norm = [df_estado[m].mean()/max_valores[m] for m in metricas]

        # Criar DataFrame no formato correto para o gráfico polar
        df_radar = pd.DataFrame({
            'Métrica': metricas * 2,
            'Valor': valores_mun_norm + valores_estado_norm,
            'Tipo': ['Município'] * 4 + ['Média Estadual'] * 4
        })

        # Gráfico de radar melhorado
        fig = px.line_polar(
            df_radar,
            r='Valor',
            theta='Métrica',
            color='Tipo',
            line_close=True,
            color_discrete_sequence=['#2ecc71', '#3498db'],  # Cores mais agradáveis
            title='Comparativo de Indicadores'
        )

        # Melhorar o layout do gráfico
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickformat='.0%',  # Formato percentual
                    showticklabels=True
                ),
                angularaxis=dict(
                    direction="clockwise",
                    period=4
                )
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.1,
                xanchor="right",
                x=1
            ),
            margin=dict(t=100, b=50),  # Aumentar margens
            height=500  # Altura fixa para melhor visualização
        )

        # Adicionar espaço vertical antes do gráfico
        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        # Adicionar espaço vertical após o gráfico
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")

        # Diagnóstico de Áreas Críticas

        # Antes da seção de diagnóstico, calcular as médias estaduais
        media_alto_estado = df_estado['Ativos com Alto Nível Educacional'].mean()
        media_baixo_estado = df_estado['Ativos com Baixo Nível Educacional'].mean()
        media_pobres = df_estado['% de pobres'].mean()
        media_saneamento_estado = df_estado['Taxa de Saneamento Básico'].mean()

        # Agora podemos usar essas variáveis na seção de diagnóstico
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Diagnóstico de Áreas Críticas")

        col1, col2 = st.columns(2)

        with col1:
            # Indicadores Críticos
            st.markdown("<p style='font-size: 1.1rem; font-weight: bold;'>Indicadores Críticos</p>", unsafe_allow_html=True)
            
            # Calcular médias nacionais
            media_nacional_alto = df['Ativos com Alto Nível Educacional'].mean()
            media_nacional_baixo = df['Ativos com Baixo Nível Educacional'].mean()
            media_nacional_pobres = df['% de pobres'].mean()
            media_nacional_saneamento = df['Taxa de Saneamento Básico'].mean()
            
            # Médicos por mil habitantes
            medicos = df_mun['Médicos por milhares de habitantes']
            media_estado_medicos = df_estado['Médicos por milhares de habitantes'].mean()
            media_nacional_medicos = df['Médicos por milhares de habitantes'].mean()

            # Hospitais por mil habitantes
            hospitais = df_mun['Hospitais por milhares de habitantes']
            media_estado_hospitais = df_estado['Hospitais por milhares de habitantes'].mean()
            media_nacional_hospitais = df['Hospitais por milhares de habitantes'].mean()
            
            # Educação
            st.markdown("<p style='font-weight: bold;'>Educação:</p>", unsafe_allow_html=True)
            alto_nivel = df_mun['Ativos com Alto Nível Educacional']
            medio_nivel = df_mun['Ativos com Médio Nível Educacional']
            baixo_nivel = df_mun['Ativos com Baixo Nível Educacional']

            # Alto Nível Educacional
            st.markdown("""
            • Ativos com Alto Nível Educacional:
            <div style='margin-left: 20px;'>
                Local: {:.1f}%<br>
                Média Estadual: {:.1f}%<br>
                Média Nacional: {:.1f}%
            </div>
            <div style='margin-left: 20px; margin-bottom: 10px; color: {};'>
                Diferença do município comparado à média nacional: {}{:.1f}%
            </div>
            <hr style='margin: 10px 0; border: 0.5px solid #e6e6e6;'>
            """.format(
                alto_nivel,
                media_alto_estado,
                media_nacional_alto,
                "red" if (alto_nivel - media_nacional_alto) < 0 else "gray",
                "" if (alto_nivel - media_nacional_alto) > 0 else "-",
                abs(alto_nivel - media_nacional_alto)
            ), unsafe_allow_html=True)

            # Médio Nível Educacional
            st.markdown("""
            • Ativos com Médio Nível Educacional:
            <div style='margin-left: 20px;'>
                Local: {:.1f}%<br>
                Média Estadual: {:.1f}%<br>
                Média Nacional: {:.1f}%
            </div>
            <div style='margin-left: 20px; margin-bottom: 10px; color: {};'>
                Diferença do município comparado à média nacional: {}{:.1f}%
            </div>
            <hr style='margin: 10px 0; border: 0.5px solid #e6e6e6;'>
            """.format(
                medio_nivel,
                df_estado['Ativos com Médio Nível Educacional'].mean(),
                df['Ativos com Médio Nível Educacional'].mean(),
                "red" if (medio_nivel - df['Ativos com Médio Nível Educacional'].mean()) < 0 else "gray",
                "+" if (medio_nivel - df['Ativos com Médio Nível Educacional'].mean()) > 0 else "-",
                abs(medio_nivel - df['Ativos com Médio Nível Educacional'].mean())
            ), unsafe_allow_html=True)
            
            # Baixo Nível Educacional
            st.markdown("""
            • Ativos com Baixo Nível Educacional:
            <div style='margin-left: 20px;'>
                Local: {:.1f}%<br>
                Média Estadual: {:.1f}%<br>
                Média Nacional: {:.1f}%
            </div>
            <div style='margin-left: 20px; margin-bottom: 10px; color: {};'>
                Diferença do município comparado à média nacional: {}{:.1f}%
            </div>
            <hr style='margin: 10px 0; border: 0.5px solid #e6e6e6;'>
            """.format(
                baixo_nivel,
                media_baixo_estado,
                media_nacional_baixo,
                "red" if (baixo_nivel - media_nacional_baixo) > 0 else "gray",
                "+" if (baixo_nivel - media_nacional_baixo) > 0 else "-",
                abs(baixo_nivel - media_nacional_baixo)
            ), unsafe_allow_html=True)

            # Indicadores Socioeconômicos e Infraestrutura
            st.markdown("<p style='font-weight: bold;'>Indicadores Socioeconômicos e Infraestrutura:</p>", unsafe_allow_html=True)
            
            # Percentual de Pobres
            pobres = df_mun['% de pobres']
            diferenca_pobres = pobres - media_nacional_pobres
            st.markdown("""
            • Percentual de Pobres:
            <div style='margin-left: 20px;'>
                Local: {:.1f}%<br>
                Média Estadual: {:.1f}%<br>
                Média Nacional: {:.1f}%
            </div>
            <div style='margin-left: 20px; margin-bottom: 10px; color: {};'>
                Diferença do município comparado à média nacional: {}{:.1f}%
            </div>
            <hr style='margin: 10px 0; border: 0.5px solid #e6e6e6;'>
            """.format(
                pobres,
                media_pobres,
                media_nacional_pobres,
                "red" if (pobres - media_nacional_pobres) > 0 else "gray",
                "+" if (pobres - media_nacional_pobres) > 0 else "-",
                abs(pobres - media_nacional_pobres)
            ), unsafe_allow_html=True)
            
            # Taxa de Saneamento Básico
            saneamento = df_mun['Taxa de Saneamento Básico']
            diferenca_saneamento = saneamento - media_nacional_saneamento
            st.markdown("""
            • Taxa de Saneamento Básico:
            <div style='margin-left: 20px;'>
                Local: {:.1f}%<br>
                Média Estadual: {:.1f}%<br>
                Média Nacional: {:.1f}%
            </div>
            <div style='margin-left: 20px; margin-bottom: 10px; color: {};'>
                Diferença do município comparado à média nacional: {}{:.1f}%
            </div>
            """.format(
                saneamento,
                media_saneamento_estado,
                media_nacional_saneamento,
                "red" if (saneamento - media_nacional_saneamento) < 0 else "gray",
                "+" if (saneamento - media_nacional_saneamento) > 0 else "-",
                abs(saneamento - media_nacional_saneamento)
            ), unsafe_allow_html=True)

        with col2:
            st.markdown("<p style='font-size: 1.1rem; font-weight: bold;'>Recomendações Prioritárias</p>", unsafe_allow_html=True)
            st.markdown("<p style='color: gray; font-size: 0.9rem;'>Com base na análise dos indicadores, sugerimos:</p>", unsafe_allow_html=True)
            
            recomendacoes = []
            
            if alto_nivel < media_nacional_alto:
                recomendacoes.append("• Investir em programas de educação superior e qualificação profissional")
            if medio_nivel < df['Ativos com Médio Nível Educacional'].mean():
                recomendacoes.append("• Fortalecer programas de ensino técnico e profissionalizante")
            if baixo_nivel > media_nacional_baixo:
                recomendacoes.append("• Desenvolver programas de redução da evasão escolar e educação de jovens e adultos")
            if pobres > media_nacional_pobres:
                recomendacoes.append("• Desenvolver programas de geração de emprego e renda")
                recomendacoes.append("• Criar iniciativas de capacitação profissional")
            if saneamento < media_nacional_saneamento:
                recomendacoes.append("• Ampliar investimentos em infraestrutura de saneamento básico")
            if medicos < media_nacional_medicos:
                recomendacoes.append("• Desenvolver programas de atração e fixação de profissionais de saúde")
                recomendacoes.append("• Criar incentivos para estabelecimento de clínicas e consultórios médicos")
            if hospitais < media_nacional_hospitais:
                recomendacoes.append("• Investir na construção ou ampliação de unidades de saúde")
                recomendacoes.append("• Estabelecer parcerias para implementação de postos de atendimento")

            if not recomendacoes:
                st.markdown("<p style='color: green;'>Município apresenta desempenho acima da média nacional nos indicadores críticos.</p>", unsafe_allow_html=True)
            else:
                for rec in recomendacoes:
                    st.markdown(rec)

        # Seção de indicadores de saúde e longevidade
        
        # Adicionar separação visual
        st.markdown("<br><hr style='margin: 20px 0; border: 0.5px solid #e6e6e6;'><br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<p style='font-weight: bold;'>Infraestrutura e Recursos de Saúde</p>", unsafe_allow_html=True)
            
            st.markdown(f"""
                • Médicos por mil habitantes:
                <div style='margin-left: 20px;'>
                    Local: {medicos:.3f}<br>
                    Média Estadual: {media_estado_medicos:.3f}<br>
                    Média Nacional: {media_nacional_medicos:.3f}
                </div>
                <div style='margin-left: 20px; margin-bottom: 10px; color: {"red" if medicos < media_nacional_medicos else "gray"}'>
                    Diferença do município comparado à média nacional: {'+' if medicos > media_nacional_medicos else ''}{(medicos - media_nacional_medicos):.3f}
                </div>
                <hr style='margin: 10px 0; border: 0.5px solid #e6e6e6;'>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
                • Hospitais por mil habitantes:
                <div style='margin-left: 20px;'>
                    Local: {hospitais:.3f}<br>
                    Média Estadual: {media_estado_hospitais:.3f}<br>
                    Média Nacional: {media_nacional_hospitais:.3f}
                </div>
                <div style='margin-left: 20px; margin-bottom: 10px; color: {"red" if hospitais < media_nacional_hospitais else "gray"}'>
                    Diferença do município comparado à média nacional: {'+' if hospitais > media_nacional_hospitais else ''}{(hospitais - media_nacional_hospitais):.3f}
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("<p style='font-weight: bold;'>Indicadores Demográficos</p>", unsafe_allow_html=True)
            
            # Criar DataFrame para o gráfico
            dados_demograficos = pd.DataFrame({
                'Indicador': ['Óbitos até 1 ano', 'Óbitos totais', 'Nascidos'],
                'Taxa Municipal': [
                    df_mun['Óbitos até 1 ano de idade por milhares de habitantes'],
                    df_mun['Óbitos por milhares de habitantes'],
                    df_mun['Nascidos por milhares de habitantes']
                ],
                'Média Estadual': [
                    df_estado['Óbitos até 1 ano de idade por milhares de habitantes'].mean(),
                    df_estado['Óbitos por milhares de habitantes'].mean(),
                    df_estado['Nascidos por milhares de habitantes'].mean()
                ]
            })
            
            fig = px.bar(dados_demograficos,
                        x='Indicador',
                        y=['Taxa Municipal', 'Média Estadual'],
                        barmode='group',
                        title='Nascimentos e Óbitos por Mil Habitantes',
                        color_discrete_sequence=['#2ecc71', '#3498db'])
            
            fig.update_layout(
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        
        # Adicionar espaço após a seção de diagnóstico
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Nova seção de detalhamento educacional
        st.subheader("Detalhamento Educacional")

        # Criar DataFrame para o gráfico de distribuição de estudantes
        dados_educacao = pd.DataFrame({
            'Nível': ['Ensino Primário', 'Ensino Secundário', 'Ensino Superior'],
            'Estudantes Local': [
                df_mun['Estudantes Ensino primário'],
                df_mun['Estudantes Ensino secundário'],
                df_mun['Estudantes Ensino superior']
            ],
            'Média Estadual': [
                df_estado['Estudantes Ensino primário'].mean(),
                df_estado['Estudantes Ensino secundário'].mean(),
                df_estado['Estudantes Ensino superior'].mean()
            ]
        })

        # Criar gráfico de barras com plotly
        fig = go.Figure(data=[
            go.Bar(name='Município', 
                x=dados_educacao['Nível'], 
                y=dados_educacao['Estudantes Local'],
                marker_color='#2ecc71'),
            go.Bar(name='Média Estadual', 
                x=dados_educacao['Nível'], 
                y=dados_educacao['Média Estadual'],
                marker_color='#3498db')
        ])

        # Atualizar layout do gráfico
        fig.update_layout(
            title='Distribuição de Estudantes por Nível de Ensino',
            barmode='group',
            xaxis_title='Nível de Ensino',
            yaxis_title='Número de Estudantes',
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)

        # Adicionar análise textual
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<p style='font-size: 1.1rem; font-weight: bold;'>Análise da Distribuição</p>", unsafe_allow_html=True)
            
            # Calcular percentuais em relação à média estadual
            for nivel in ['primário', 'secundário', 'superior']:
                valor_local = df_mun[f'Estudantes Ensino {nivel}']
                media_estado = df_estado[f'Estudantes Ensino {nivel}'].mean()
                diff_percent = ((valor_local - media_estado) / media_estado) * 100
                
                st.markdown(f"""
                • Ensino {nivel.title()}:
                <div style='margin-left: 20px; margin-top: 0px; margin-bottom: 35px; color: {"red" if diff_percent < 0 else "gray"}'>
                    Diferença em relação à média estadual: {'+' if diff_percent > 0 else ''}{diff_percent:.1f}%
                </div>
                """, unsafe_allow_html=True)


        with col2:
            st.markdown("<p style='font-size: 1.1rem; font-weight: bold;'>Análise da Rede de Ensino</p>", unsafe_allow_html=True)
            
            # Calcular total de estudantes
            total_estudantes = (df_mun['Estudantes Ensino primário'] + 
                            df_mun['Estudantes Ensino secundário'] + 
                            df_mun['Estudantes Ensino superior'])
            
            # Calcular percentuais por nível
            perc_primario = (df_mun['Estudantes Ensino primário'] / total_estudantes) * 100
            perc_secundario = (df_mun['Estudantes Ensino secundário'] / total_estudantes) * 100
            perc_superior = (df_mun['Estudantes Ensino superior'] / total_estudantes) * 100
            
            # População em idade escolar (jovens)
            pop_jovem = df_mun['População residente'] * (df_mun['Porcentagem de Jovens'] / 100)
            taxa_atendimento = (total_estudantes / pop_jovem) * 100
            
            st.markdown(f"""
            • Total de Estudantes: {format(total_estudantes, ',.0f').replace(',', '.')}

            • Distribuição percentual:
            <div style='margin-left: 20px; margin-top: 2px; margin-bottom: 10px;'>
                - Ensino Primário: {perc_primario:.1f}%<br>
                - Ensino Secundário: {perc_secundario:.1f}%<br>
                - Ensino Superior: {perc_superior:.1f}%
            </div>
            
            • Taxa de Atendimento Escolar:
            <div style='margin-left: 20px; margin-top: 2px; margin-bottom: 10px;'>
                {taxa_atendimento:.1f}% da população jovem (pessoas entre 0 e 24 anos)
            </div>
            """, unsafe_allow_html=True)

        # Relação nível educacional x renda
            
        # Adicionar separação visual
        st.markdown("<br><hr style='margin: 20px 0; border: 0.5px solid #e6e6e6;'><br>", unsafe_allow_html=True)

        # Título da seção
        st.markdown("<p style='font-size: 1.1rem; font-weight: bold;'>Relação Nível Educacional x Renda</p>", unsafe_allow_html=True)

        # Criar duas colunas
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de distribuição dos ativos por nível educacional
            st.markdown("<p style='font-weight: bold;'>Distribuição dos Ativos por Nível Educacional</p>", unsafe_allow_html=True)
            
            dados_ativos = pd.DataFrame({
                'Nível': ['Baixo', 'Médio', 'Alto'],
                'Percentual': [
                    df_mun['Ativos com Baixo Nível Educacional'],
                    df_mun['Ativos com Médio Nível Educacional'],
                    df_mun['Ativos com Alto Nível Educacional']
                ]
            })
            
            fig = px.pie(dados_ativos, 
                        values='Percentual', 
                        names='Nível',
                        color_discrete_sequence=['#2ecc71', '#f1c40f', '#e74c3c'])
            
            fig.update_layout(
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=0
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("<p style='font-weight: bold;'>Indicadores de Renda por Nível Educacional</p>", unsafe_allow_html=True)
            
            # Formatação dos indicadores
            taxa_desemprego = df_mun['Taxa de desemprego']
            media_salarial = df_mun['Média Salarial']

            st.markdown(f"""
            • Taxa de Desemprego Geral: {taxa_desemprego:.1f}%<br>
            • Média Salarial: R$ {format(media_salarial, ',.2f').replace(',', '.')}<br>
            • Trabalhadores Especializados: {df_mun['Percentual de trabalhadores especializados']:.1f}% do total<br>
            • Taxa de Desemprego Jovem: {df_mun['Taxa de desemprego dos jovens']:.1f}%
            """, unsafe_allow_html=True)
