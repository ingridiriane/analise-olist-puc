import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go
import json
from urllib.request import urlopen

# ==============================================================================
# CONFIGURAÇÃO INICIAL E CARREGAMENTO
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Olist - Análise de Dados",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caminhos dos arquivos
DATA_DIR = 'dados'
CAMINHO_DADOS = os.path.join(DATA_DIR, 'olist_lite.zip')
CAMINHO_RELATORIO = os.path.join(DATA_DIR, 'relatorio_analise.txt')
# --- CORREÇÃO DE CAMINHOS PARA O GITHUB ---
# Usamos '.' para indicar a pasta atual (raiz do repositório)
DATA_DIR = '.' 
# Usamos o arquivo ZIP (versão leve)
CAMINHO_DADOS = 'olist_lite.zip' 
CAMINHO_RELATORIO = 'relatorio_analise.txt'

@st.cache_data
def carregar_dados():
    # Verifica se o arquivo existe
    if not os.path.exists(CAMINHO_DADOS):
        st.error(f"Arquivo {CAMINHO_DADOS} não encontrado. Rode o script 'atividade.py' primeiro.")
        st.error(f"ERRO CRÍTICO: O arquivo '{CAMINHO_DADOS}' não foi encontrado no GitHub. Verifique se você fez o upload do arquivo .zip corretamente.")
        return pd.DataFrame()

    df = pd.read_csv(CAMINHO_DADOS, compression='zip')
    
    # Garantir que colunas de data sejam datetime
    cols_data = ['data_compra', 'data_entrega', 'data_estimada']
    for col in cols_data:
        df[col] = pd.to_datetime(df[col])
        
    return df
    try:
        # compression='zip' permite ler o arquivo compactado diretamente
        df = pd.read_csv(CAMINHO_DADOS, compression='zip')
        
        # Garantir que colunas de data sejam datetime
        if 'data_compra' in df.columns:
            df['data_compra'] = pd.to_datetime(df['data_compra'])
            
        return df
    except Exception as e:
        st.error(f"Erro ao ler o arquivo de dados: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_relatorio():
    if os.path.exists(CAMINHO_RELATORIO):
        with open(CAMINHO_RELATORIO, 'r', encoding='utf-8') as f:
            return f.read()
    return "Relatório não encontrado."
    return "Relatório técnico não encontrado."

# Carrega os dados
df = carregar_dados()
@@ -88,14 +95,17 @@
    "Clusterização (ML)"
])

# Se o dataframe estiver vazio, paramos por aqui para não dar erro nos gráficos
if df.empty:
    st.stop()

# ==============================================================================
# ABA 1: PERGUNTA 1 (Tempo e Região) - VERSÃO DE ELITE
# ABA 1: PERGUNTA 1 (Tempo e Região)
# ==============================================================================
with tab_p1:
    st.markdown("### 📊 P1: Monitoramento Temporal e Geográfico")

    # --- PREPARAÇÃO DO MAPA (GEOJSON) ---
    # Função interna para pegar o desenho do Brasil
    @st.cache_data
    def carregar_mapa_brasil():
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
@@ -113,8 +123,7 @@
    with col_kpi:
        st.subheader("⏱️ Eficiência Logística")

        # 1. GAUGE CHART (Velocímetro)
        # Mostra o tempo médio atual em relação a metas aceitáveis
        # GAUGE CHART (Velocímetro)
        tempo_medio = df['tempo_total'].mean()

        fig_gauge = go.Figure(go.Indicator(
@@ -124,14 +133,14 @@
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 30], 'tickwidth': 1, 'tickcolor': "#17202A"},
                'bar': {'color': "#154360"}, # Azul Marinho
                'bar': {'color': "#154360"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 10], 'color': "#2ECC71"}, # Verde (Ótimo)
                    {'range': [10, 18], 'color': "#F1C40F"}, # Amarelo (Atenção)
                    {'range': [18, 30], 'color': "#E74C3C"}  # Vermelho (Crítico)
                    {'range': [0, 10], 'color': "#2ECC71"},
                    {'range': [10, 18], 'color': "#F1C40F"},
                    {'range': [18, 30], 'color': "#E74C3C"}
                ],
            }
        ))
@@ -141,8 +150,7 @@
    with col_area:
        st.subheader("📈 Tendência de Vendas (Acumulado)")

        # 2. AREA CHART (Gráfico de Área com Gradiente)
        # Mais elegante que a linha simples
        # AREA CHART
        df['mes_dt'] = df['data_compra'].dt.to_period('M').astype(str)
        df_temporal = df.groupby('mes_dt')['order_id'].nunique().reset_index()

@@ -154,7 +162,7 @@
            labels={'mes_dt': 'Mês', 'order_id': 'Pedidos'},
            template="plotly_white"
        )
        fig_area.update_traces(line_color='#0E6251', fillcolor='rgba(14, 98, 81, 0.3)') # Verde Petróleo Transparente
        fig_area.update_traces(line_color='#0E6251', fillcolor='rgba(14, 98, 81, 0.3)')
        st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("---")
@@ -165,45 +173,40 @@
    with col_mapa:
        st.subheader("🇧🇷 Mapa de Calor de Vendas (Brasil)")

        # 3. CHOROPLETH MAP (Mapa Coroplético)
        # Agrupando por Estado (Sigla)
        # CHOROPLETH MAP
        df_mapa = df.groupby('estado_cliente')['order_id'].nunique().reset_index()

        if brazil_geo:
            fig_map = px.choropleth(
                df_mapa,
                geojson=brazil_geo,
                locations='estado_cliente', # Coluna com sigla 'SP', 'RJ'
                featureidkey='properties.sigla', # Onde está a sigla no GeoJSON
                locations='estado_cliente',
                featureidkey='properties.sigla',
                color='order_id',
                color_continuous_scale='Blues', # Gradiente Azul
                color_continuous_scale='Blues',
                title="Intensidade de Vendas por Estado",
                template="plotly_white"
            )
            fig_map.update_geos(fitbounds="locations", visible=False) # Foca no Brasil e remove o resto do mundo
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(height=500, margin={"r":0,"t":30,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Não foi possível carregar o mapa. Verifique sua conexão.")

    with col_rank:
        st.subheader("🏆 Top 10 Estados (Lollipop Chart)")
        st.subheader("🏆 Top 10 Estados")

        # 4. LOLLIPOP CHART (Gráfico de Pirulito)
        # Muito mais limpo que barras para rankings
        # LOLLIPOP CHART
        df_top10 = df_mapa.sort_values(by='order_id', ascending=True).tail(10)

        fig_lolly = go.Figure()
        
        # Desenha a linha (o "palito")
        fig_lolly.add_trace(go.Scatter(
            x=df_top10['order_id'],
            y=df_top10['estado_cliente'],
            mode='markers',
            marker=dict(color='#D35400', size=12) # Laranja Queimado
            marker=dict(color='#D35400', size=12)
        ))

        # Desenha as linhas horizontais para conectar
        for i in range(len(df_top10)):
            fig_lolly.add_shape(
                type='line',
@@ -219,13 +222,13 @@
            height=500
        )
        st.plotly_chart(fig_lolly, use_container_width=True)

# ==============================================================================
# ABA 2: PERGUNTA 2 (Preço e Categorias) - GESTÃO DE PORTFÓLIO
# ABA 2: PERGUNTA 2 (Preço e Categorias)
# ==============================================================================
with tab_p2:
    st.markdown("### 🏷️ P2: Análise de Preço e Mix de Produtos")

    # KPIs de Produto
    col1, col2, col3 = st.columns(3)
    ticket_medio = df['preco'].mean()
    categoria_top = df['categoria'].mode()[0]
@@ -237,199 +240,137 @@

    st.markdown("---")

    # --- LINHA 1: PARETO (O GRÁFICO REI DA GESTÃO) ---
    st.subheader("📊 Curva ABC (Pareto) de Faturamento por Categoria")
    st.caption("Identificando as poucas categorias que geram a maior parte da receita (Regra 80/20).")
    st.subheader("📊 Curva ABC (Pareto) de Faturamento")

    # 1. Preparação dos dados para Pareto
    # PARETO
    df_pareto = df.groupby('categoria')['preco'].sum().reset_index()
    df_pareto = df_pareto.sort_values(by='preco', ascending=False)

    # Cálculo do Acumulado
    df_pareto['acumulado'] = df_pareto['preco'].cumsum()
    df_pareto['percentual_acumulado'] = (df_pareto['acumulado'] / df_pareto['preco'].sum()) * 100

    # Pegamos apenas as Top 20 categorias para o gráfico não ficar ilegível
    df_pareto_top = df_pareto.head(20)

    # 2. Construção do Gráfico Combo (Barras + Linha)
    fig_pareto = go.Figure()
    
    # Barras (Faturamento)
    fig_pareto.add_trace(go.Bar(
        x=df_pareto_top['categoria'],
        y=df_pareto_top['preco'],
        name='Faturamento (R$)',
        marker_color='#154360' # Azul Escuro
        x=df_pareto_top['categoria'], y=df_pareto_top['preco'],
        name='Faturamento (R$)', marker_color='#154360'
    ))
    
    # Linha (% Acumulado)
    fig_pareto.add_trace(go.Scatter(
        x=df_pareto_top['categoria'],
        y=df_pareto_top['percentual_acumulado'],
        name='% Acumulado',
        yaxis='y2', # Eixo secundário
        mode='lines+markers',
        marker=dict(color='#D35400') # Laranja
        x=df_pareto_top['categoria'], y=df_pareto_top['percentual_acumulado'],
        name='% Acumulado', yaxis='y2', mode='lines+markers', marker=dict(color='#D35400')
    ))

    # Layout de dois eixos
    fig_pareto.update_layout(
        title="Top 20 Categorias: Faturamento vs. Acumulado",
        yaxis=dict(title="Faturamento (R$)"),
        yaxis2=dict(
            title="% Acumulado",
            overlaying='y',
            side='right',
            range=[0, 110]
        ),
        template="plotly_white",
        legend=dict(x=0.5, y=1.1, orientation='h')
        yaxis2=dict(title="% Acumulado", overlaying='y', side='right', range=[0, 110]),
        template="plotly_white", legend=dict(x=0.5, y=1.1, orientation='h')
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("---")

    # --- LINHA 2: ELASTICIDADE E COMPOSIÇÃO ---
    col_scatter, col_sun = st.columns([2, 1])

    with col_scatter:
        st.subheader("📉 Relação Preço vs. Volume (Elasticidade)")
        st.caption("Cada bolha é uma categoria. Bolhas maiores faturam mais.")
        st.subheader("📉 Relação Preço vs. Volume")

        # Agrupando: Preço Médio vs Quantidade de Vendas
        # SCATTER
        df_elasticidade = df.groupby('categoria').agg(
            preco_medio=('preco', 'mean'),
            qtd_vendas=('order_id', 'nunique'),
            faturamento=('preco', 'sum')
        ).reset_index()

        # Removendo outliers extremos para visualizar melhor (opcional)
        df_elasticidade = df_elasticidade[df_elasticidade['preco_medio'] < 2000]

        fig_scatter = px.scatter(
            df_elasticidade,
            x='preco_medio',
            y='qtd_vendas',
            size='faturamento', # Tamanho da bolha
            color='qtd_vendas',
            hover_name='categoria',
            df_elasticidade, x='preco_medio', y='qtd_vendas',
            size='faturamento', color='qtd_vendas', hover_name='categoria',
            title="Produtos mais caros vendem menos?",
            labels={'preco_medio': 'Preço Médio (R$)', 'qtd_vendas': 'Qtd. Vendas'},
            template="plotly_white",
            color_continuous_scale='Viridis'
            template="plotly_white", color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_sun:
        st.subheader("☀️ Sunburst de Categorias")

        # Selecionando Top 15 para o Sunburst ficar bonito
        # SUNBURST
        df_sun = df_pareto.head(15)
        
        fig_sun = px.sunburst(
            df_sun,
            path=['categoria'],
            values='preco',
            df_sun, path=['categoria'], values='preco',
            title="Share de Faturamento (Top 15)",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig_sun, use_container_width=True)

# ==============================================================================
# ABA 3: PERGUNTA 3 (Satisfação e Logística) - A VOZ DO CLIENTE
# ABA 3: PERGUNTA 3 (Satisfação)
# ==============================================================================
with tab_p3:
    st.markdown("### ⭐ P3: Impacto da Logística na Satisfação (NPS/Reviews)")
    st.markdown("### ⭐ P3: Impacto da Logística na Satisfação")

    # KPIs de Satisfação
    col1, col2, col3 = st.columns(3)
    
    avg_score = df['review_score'].mean()
    qtd_atrasos = df[df['atraso_entrega'] > 0].shape[0]
    perc_atrasos = (qtd_atrasos / df.shape[0]) * 100

    col1.metric("Nota Média (1-5)", f"{avg_score:.2f} ⭐")
    col2.metric("Pedidos com Atraso", f"{qtd_atrasos:,}".replace(',', '.'))
    col3.metric("Taxa de Atraso", f"{perc_atrasos:.1f}%", delta_color="inverse") # Vermelho se alto
    col3.metric("Taxa de Atraso", f"{perc_atrasos:.1f}%", delta_color="inverse")

    st.markdown("---")

    # --- LINHA 1: DISTRIBUIÇÃO E CORRELAÇÃO ---
    col_hist, col_corr = st.columns(2)

    with col_hist:
        st.subheader("📊 Distribuição das Notas")
        st.caption("Volume de avaliações por quantidade de estrelas.")

        # Contagem de notas
        df_notas = df['review_score'].value_counts().reset_index()
        df_notas.columns = ['Nota', 'Quantidade']
        df_notas = df_notas.sort_values('Nota')

        # Cores semafóricas (Vermelho -> Verde)
        cores_notas = {1: '#E74C3C', 2: '#E67E22', 3: '#F1C40F', 4: '#3498DB', 5: '#2ECC71'}

        fig_hist = px.bar(
            df_notas, 
            x='Nota', 
            y='Quantidade',
            text_auto=True,
            title="Histograma de Avaliações",
            template="plotly_white"
            df_notas, x='Nota', y='Quantidade', text_auto=True,
            title="Histograma de Avaliações", template="plotly_white"
        )
        # Aplicando as cores manualmente para dar impacto
        fig_hist.update_traces(marker_color=[cores_notas[n] for n in df_notas['Nota']])
        fig_hist.update_traces(marker_color=[cores_notas.get(n, '#333') for n in df_notas['Nota']])
        fig_hist.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_corr:
        st.subheader("📉 Atraso vs. Satisfação (Prova Real)")
        st.caption("Como a nota média cai conforme o tempo de entrega aumenta?")
        st.subheader("📉 Atraso vs. Satisfação")

        # Agrupando por dias de entrega (limitando a 50 dias para tirar outliers extremos do gráfico)
        df_corr = df[df['tempo_total'] <= 50].groupby('tempo_total')['review_score'].mean().reset_index()

        fig_corr = px.line(
            df_corr, 
            x='tempo_total', 
            y='review_score',
            markers=True,
            df_corr, x='tempo_total', y='review_score', markers=True,
            title="Correlação: Tempo de Entrega x Nota Média",
            labels={'tempo_total': 'Dias para Entregar', 'review_score': 'Nota Média'},
            template="plotly_white"
        )
        # Adiciona uma linha de tendência vermelha para dramatizar a queda
        fig_corr.add_scatter(
            x=df_corr['tempo_total'], 
            y=df_corr['review_score'], 
            mode='lines', 
            line=dict(color='red', width=2, dash='dot'),
            name='Tendência'
            x=df_corr['tempo_total'], y=df_corr['review_score'], 
            mode='lines', line=dict(color='red', width=2, dash='dot'), name='Tendência'
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("---")

    # --- LINHA 2: QUALIDADE POR CATEGORIA ---
    st.subheader("🏆 Qualidade Percebida por Categoria (Top 15)")
    st.caption("Quais categorias recebem mais 5 estrelas proporcionalmente?")

    # Selecionando Top 15 categorias por volume
    top_cats = df['categoria'].value_counts().head(15).index
    df_top_cats = df[df['categoria'].isin(top_cats)]

    # Tabela cruzada: Categoria nas linhas, Nota nas colunas (normalizado %)
    df_qualidade = pd.crosstab(df_top_cats['categoria'], df_top_cats['review_score'], normalize='index') * 100
    df_qualidade = df_qualidade.reset_index()

    # Gráfico de Barras Empilhadas 100%
    fig_stack = px.bar(
        df_qualidade, 
        x=[1, 2, 3, 4, 5], 
        y='categoria', 
        orientation='h',
        df_qualidade, x=[1, 2, 3, 4, 5], y='categoria', orientation='h',
        title="Composição das Notas por Categoria (%)",
        labels={'value': '% do Total', 'categoria': 'Categoria', 'variable': 'Nota'},
        template="plotly_white",
@@ -439,29 +380,21 @@
    st.plotly_chart(fig_stack, use_container_width=True)

# ==============================================================================
# ABA 4: MACHINE LEARNING (Clusterização) - A INTELIGÊNCIA DO DADO
# ABA 4: MACHINE LEARNING (Clusterização)
# ==============================================================================
with tab_ml:
    st.markdown("### 🤖 P4: Segmentação de Clientes (K-Means)")
    st.markdown("""
    O algoritmo agrupou os pedidos em 4 perfis comportamentais baseados em **Preço** e **Tempo de Entrega**.
    Abaixo, visualizamos as características de cada "Tribo" de clientes.
    """)
    st.markdown("---")

    # --- LINHA 1: VISÃO ESPACIAL (SCATTER) ---
    st.subheader("📍 Mapa dos Clusters (Preço vs. Tempo)")
    st.caption("Cada ponto é um pedido. Observe como o algoritmo separou os grupos.")

    # Amostra de dados para o gráfico não ficar pesado
    df_sample = df.sample(n=min(5000, df.shape[0]), random_state=42)

    # ATENÇÃO: Usando coluna 'grupos' conforme seu arquivo processado
    fig_cluster = px.scatter(
        df_sample, 
        x='tempo_total', 
        y='preco', 
        color='grupos',  # <--- CORRIGIDO: Agora usa 'grupos'
        symbol='grupos', # <--- CORRIGIDO: Agora usa 'grupos'
        df_sample, x='tempo_total', y='preco', 
        color='grupos', symbol='grupos',
        title="Dispersão dos Pedidos Identificados pelo K-Means",
        labels={'tempo_total': 'Dias de Entrega', 'preco': 'Valor do Pedido (R$)'},
        template="plotly_white",
@@ -473,17 +406,15 @@

    st.markdown("---")

    # --- LINHA 2: PERFIL DOS GRUPOS (RADAR CHART) ---
    # --- LINHA 2: PERFIL DOS GRUPOS (RADAR) ---
    col_radar, col_stat = st.columns([1, 1])

    with col_radar:
        st.subheader("🕸️ Personalidade dos Clusters (Radar)")
        st.caption("Comparativo das médias normalizadas (0 a 1).")

        # CORRIGIDO: Agrupando por 'grupos'
        # Agrupando por 'grupos'
        df_medias = df.groupby('grupos')[['preco', 'tempo_total', 'frete']].mean()

        # Normalização Min-Max para o Radar
        df_norm = (df_medias - df_medias.min()) / (df_medias.max() - df_medias.min())
        df_norm = df_norm.reset_index()

@@ -493,39 +424,30 @@
        for i, row in df_norm.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row['preco'], row['tempo_total'], row['frete']],
                theta=categorias,
                fill='toself',
                name=row['grupos'] # <--- CORRIGIDO
                theta=categorias, fill='toself', name=row['grupos']
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            height=400,
            template="plotly_white"
            showlegend=True, height=400, template="plotly_white"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_stat:
        st.subheader("📝 Estatísticas Reais por Grupo")
        st.caption("Valores médios reais.")

        # 1. CÁLCULO NOS DADOS BRUTOS
        # CORRIGIDO: Agrupando por 'grupos'
        # Cálculo nos dados brutos
        df_stats = df.groupby('grupos')[['preco', 'tempo_total', 'frete']].mean()

        # Descobrimos quem é o "Grupo Rico"
        # Grupo Rico (Maior preço)
        grupo_rico = df_stats['preco'].idxmax()

        # 2. FORMATAÇÃO PARA VISUALIZAÇÃO
        # Formatação
        tabela_visual = df_stats.reset_index()
        tabela_visual.columns = ['Cluster (Perfil)', 'Ticket Médio', 'Tempo Médio', 'Frete Médio']
        
        tabela_visual['Ticket Médio'] = tabela_visual['Ticket Médio'].apply(lambda x: f"R$ {x:.2f}")
        tabela_visual['Tempo Médio'] = tabela_visual['Tempo Médio'].apply(lambda x: f"{x:.1f} dias")
        tabela_visual['Frete Médio'] = tabela_visual['Frete Médio'].apply(lambda x: f"R$ {x:.2f}")

        st.table(tabela_visual)
        

        st.success(f"💡 Insight: O grupo **{grupo_rico}** é o que traz maior receita unitária.")
