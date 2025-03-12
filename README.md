# IDH Expert - Análise e Insights com Base no IDH dos Municípios Brasileiros

## Descrição
O IDH Expert é um aplicativo web desenvolvido como projeto acadêmico para analisar o Índice de Desenvolvimento Humano (IDH) de municípios brasileiros com população de até 100.000 habitantes. Utilizando dados públicos validados fornecidos pela escola, o app permite visualizar o IDH médio por estado, explorar detalhes socioeconômicos e de infraestrutura por município, e simular o impacto de mudanças em indicadores-chave no IDH. O projeto é hospedado no Streamlit Community Cloud e utiliza machine learning (XGBoost) para previsões.

## Funcionalidades
- Visualização de IDH: Gráfico interativo do IDH médio por estado.
- Análise por município: Tabelas com indicadores de educação, emprego/renda e infraestrutura, incluindo correlações com IDH calculadas pelo coeficiente de Spearman.
- Simulador: Ajuste de indicadores (ex.: % de pobres, produtividade) para prever o impacto no IDH.
- Dados públicos: Baseado em dados abertos, promovendo transparência e acessibilidade.

## Pré-requisitos
- Python 3.8 ou superior
- Bibliotecas: `streamlit`, `xgboost`, `pandas`, `numpy`, `plotly`, `scikit-learn`
- Git (para clonar o repositório)

## Instalação
1. Clone o repositório:
``````
git clone https://github.com/seu-usuario/idh-expert.git
cd idh-expert
``````

2. Crie um ambiente virtual (opcional, mas recomendado):

``````
python -m venv venv
source venv/bin/activate  
# No Windows: venv\Scripts\activate
``````

3. Instale as dependências:

``````
pip install -r requirements.txt
``````

4. Execute o app localmente:

``````
streamlit run app.py
``````

## Uso
- **Online**: Acesse o app diretamente em [https://idh-expert-yvanrherzhsbjumifmwps6.streamlit.app/] (atualize com o URL após o deploy).
- **Localmente**: Após a instalação, o app abrirá no seu navegador padrão. Explore as páginas "Home" (gráfico por estado), "Filtrar por Estado" (seleção de município) e "Detalhes do Município" (análise e simulação).
- **Simulador**: Ajuste os sliders na página de detalhes para ver como mudanças em indicadores afetam o IDH previsto.

## Estrutura do Projeto

``````
idh-expert/
├── app.py              # Código principal do Streamlit
├── df_exported.csv     # Dados públicos processados
├── models/             # Modelos treinados (XGBoost e scaler)
│   ├── modelo_idh_xgboost_6vars_scaled.json
│   ├── scaler_6vars.pkl
├── xgb_model.py        # Funções para carregar e prever com o modelo
├── requirements.txt    # Dependências do projeto
├── utils/              # Módulo de utilidades
│   ├── data_prep.py    # Funções de preparação de dados
│   └── init.py
└── .gitignore          # Arquivo para ignorar arquivos (ex.: .DS_Store)
``````

## Sobre os Dados
O IDH Expert utiliza dados públicos validados fornecidos pela escola, extraídos de fontes brasileiras confiáveis para analisar o IDH de municípios com até 100.000 habitantes. As bases de dados incluem:

- **IBGE (Instituto Brasileiro de Geografia e Estatística)**: Censo Demográfico 2010 (indicadores demográficos, econômicos e de infraestrutura), Estatísticas do Registro Civil (nascimentos, óbitos), e Censo dos Serviços de Saúde (2009).
- **RAIS (Relação Anual de Informações Sociais - Ministério do Trabalho e Emprego)**: Dados de trabalho formal, salários e setores econômicos.
- **Atlas do Desenvolvimento Humano no Brasil (PNUD)**: Expectativa de Vida e Taxa de Pobreza, baseados no Censo 2010.
- **MDIC (Ministério da Indústria, Comércio Exterior e Serviços)**: Dados de importação e exportação.
- **INEP (Instituto Nacional de Estudos e Pesquisas Educacionais)**: Dados educacionais.

### Período dos Dados
Os dados abrangem o período de **2009 a 2015**, com a maioria dos indicadores demográficos e alguns econômicos fixados em **2010** (Censo Demográfico). Indicadores como Média Salarial e Número de Médicos por Milhares de Habitantes estão atualizados até **2015**, enquanto dados de saúde, como Número de Camas em Hospitais, são de **2009**.

### Geração dos Dados
Os indicadores foram gerados a partir de:
- **Censo Demográfico 2010**: Coleta primária de dados por entrevistas domiciliares para indicadores como Taxa de Pobreza e Expectativa de Vida.
- **RAIS**: Microdados de trabalhadores formais para calcular médias salariais, número de médicos e outros indicadores de emprego.
- **Cálculos derivados**: Proporções (ex.: % de pobres, Médicos por milhares de habitantes) e divisões (ex.: Produtividade = PIB / População Empregada).
- **Atlas Brasil**: Indicadores como Taxa de Pobreza e Expectativa de Vida foram processados pelo PNUD com base no Censo 2010.

### Limitações
- Muitos indicadores estão fixados em 2010, o que não captura mudanças após esse ano.
- Alguns indicadores combinam dados de anos diferentes (ex.: Médicos de 2014 com população de 2010), o que pode introduzir pequenos desajustes.
- Dados mais recentes (ex.: Censo 2022) não foram usados, pois não estavam disponíveis no momento da coleta.

## Contribuição
Este projeto é aberto para contribuições! Se desejar adicionar funcionalidades (ex.: novos indicadores ou visualizações), envie um pull request ou abra uma issue no GitHub.

## Licença
Este projeto está licenciado sob a [Licença MIT](LICENSE.md).

## Agradecimentos
- Agradecimentos à escola por fornecer os dados validados e à comunidade acadêmica por disponibilizar dados públicos.
- Suporte técnico da IA Grok 3, da xAI, por assistência no desenvolvimento.

## Contato
Para dúvidas, sugestões ou colaborações, entre em contato via [rafaelpessi@yahoo.com.br] ou abra uma issue neste repositório.