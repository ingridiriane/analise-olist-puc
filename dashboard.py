import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go
import json
from urllib.request import urlopen

# ==============================================================================
# CONFIGURAÇÃO INICIAL
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Olist - Executive View",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONFIGURAÇÃO DE CAMINHOS ---
DATA_DIR = '.' 
CAMINHO_DADOS = 'olist_lite.zip' 
CAMINHO_RELATORIO = 'relatorio_analise.txt'

# ==============================================================================
# FUNÇÃO DE CARGA DE DADOS (VERSÃO BLINDADA)
# ==============================================================================
@st.cache_data
def carregar_dados():
    if not os.path.exists(CAMINHO_DADOS):
        return None
    
    try:
        df = pd.read_csv(CAMINHO_DADOS, compression='zip')
        
        # 1. Limpeza de nomes de colunas (tira espaços extras)
        df.columns = df.columns.str.strip()
        
        # 2. Conversão Forçada de Datas (Blinda o erro de AttributeError)
        cols_data = ['data_compra', 'data_entrega', 'data_estimada']
        for col in cols_data:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 3. Criando colunas auxiliares APENAS se a conversão funcionou
        if 'data_compra' in df.columns:
            # Remove linhas onde a data de compra é nula (erro de conversão)
            df = df.dropna(subset=['data_compra'])
            
            df['hora_compra'] = df['data_compra'].dt.hour
            df['dia_semana'] = df['data_compra'].dt.day_name()
            
            # Tradução dos dias
            mapa_dias = {
                'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta', 
                'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            df['dia_semana_pt'] = df['dia_semana'].map(mapa_dias)
            
        return df
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_relatorio():
    if os.path.exists(CAMINHO_RELATORIO):
        with open(CAMINHO_RELATORIO, 'r', encoding='utf-8') as f:
            return f.read()
    return "Relatório não encontrado."

# Carrega os dados
df = carregar_dados()

# ==============================================================================
# BARRA LATERAL (CONTROLE)
# ==============================================================================
st.sidebar.title("🛠️ Controle")

# Botão de Emergência para Limpar Cache (Ajuda a resolver erros de atualização)
if st.sidebar.button("🔄 Recarregar Dados (Limpar Cache)"):
    st.cache_data.clear()
    st.rerun()

if df is not None and not df.empty:
    st.sidebar.metric("Total de Pedidos", f"{df.shape[0]:,}".replace(',', '.'))
    st.sidebar.metric("Faturamento Total", f"R$ {df['preco'].sum():,.2f}")
    
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        "⬇️ Baixar Relatório Técnico",
        data=carregar_relatorio(),
        file_name='relatorio_analise.txt'
    )

st.sidebar.markdown("---")
st.sidebar.caption("Dados: Olist E-Commerce")

# Verifica se o DF carregou bem antes de tentar criar gráficos
if df is None or df.empty:
    st.error("⚠️ Não foi possível carregar os dados. Verifique se 'olist_lite.zip' está na pasta.")
    st.stop()

# ==============================================================================
# ESTRUTURA DE ABAS
# ==============================================================================
st.title("🛒 Dashboard Estratégico de E-commerce")

tab_overview, tab_p1, tab_p2, tab_p3, tab_ml = st.tabs([
    "🔍 Visão Geral",
    "P1: Tempo e Região",
    "P2: Preço e Categorias",
    "P3: Satisfação",
    "Clusterização (ML)"
])

# ==============================================================================
# ABA: VISÃO GERAL
# ==============================================================================
with tab_overview:
    st.markdown("### 🚀 Resumo Executivo do Negócio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Faturamento Diário")
        # Agrupamento seguro por data
        df['data_apenas'] = df['data_compra'].dt.date
        df_daily = df.groupby('data_apenas')['preco'].sum().reset_index()
        
        fig_daily = px.line(df_daily, x='data_apenas', y='preco', title="Evolução da Receita Diária", template="plotly_white")
        fig_daily.update_traces(line_color='#154360')
        st.plotly_chart(fig_daily, use_container_width=True)
        
        st.subheader("3. Top 5 Categorias (Receita)")
        df_top5_rev = df.groupby('categoria')['preco'].sum().nlargest(5).reset_index()
        fig_top5 = px.bar(df_top5_rev, x='preco', y='categoria', orientation='h', title="Maiores Receitas por Categoria", text_auto='.2s', template="plotly_white")
        fig_top5.update_traces(marker_color='#2E86C1')
        st.plotly_chart(fig_top5, use_container_width=True)

    with col2:
        st.subheader("2. Pedidos por Região")
        df_reg = df['regiao'].value_counts().reset_index()
        df_reg.columns = ['Região', 'Pedidos']
        fig_pie = px.donut(df_reg, names='Região', values='Pedidos', title="Share de Pedidos por Região", hole=0.4, template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("4. Funil de Satisfação")
        df_score = df['review_score'].value_counts().reset_index().sort_values('review_score')
        fig_score = px.bar(df_score, x='review_score', y='count', title="Distribuição Geral de Notas", color='review_score', color_continuous_scale='RdYlGn', template="plotly_white")
        st.plotly_chart(fig_score, use_container_width=True)

# ==============================================================================
# ABA P1: TEMPO E REGIÃO
# ==============================================================================
with tab_p1:
    st.markdown("### 📊 P1: Análise Temporal e Geográfica")
    
    col_kpi, col_area = st.columns([1, 2])
    with col_kpi:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=df['tempo_total'].mean(),
            title={'text': "Tempo Médio (Dias)"},
            gauge={'axis': {'range': [0, 30]}, 'bar': {'color': "#154360"},
                   'steps': [{'range': [0, 10], 'color': "#2ECC71"}, {'range': [10, 30], 'color': "#E74C3C"}]}
        ))
        fig_gauge.update_layout(height=250)
        st.plotly_chart(fig_gauge, use_container_width=True)
    with col_area:
        df['mes_dt'] = df['data_compra'].dt.to_period('M').astype(str)
        df_temp = df.groupby('mes_dt')['order_id'].nunique().reset_index()
        fig_area = px.area(df_temp, x='mes_dt', y='order_id', title="Volume Mensal", template="plotly_white")
        fig_area.update_traces(line_color='#0E6251')
        st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🆕 Novas Análises de Logística")

    col_new1, col_new2 = st.columns(2)
    with col_new1:
        st.subheader("🔥 Mapa de Calor: Hora x Dia")
        df_heat = df.groupby(['dia_semana_pt', 'hora_compra'])['order_id'].nunique().reset_index()
        dias_ordem = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        fig_heat = px.density_heatmap(
            df_heat, x='hora_compra', y='dia_semana_pt', z='order_id',
            category_orders={'dia_semana_pt': dias_ordem},
            title="Concentração de Vendas (Heatmap)",
            labels={'hora_compra': 'Hora do Dia', 'dia_semana_pt': 'Dia', 'order_id': 'Volume'},
            color_continuous_scale='Viridis', template="plotly_white"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_new2:
        st.subheader("🚚 Custo de Frete por Região")
        df_frete = df.groupby('regiao')['frete'].mean().reset_index().sort_values('frete')
        fig_frete = px.bar(
            df_frete, x='frete', y='regiao', orientation='h',
            title="Frete Médio por Região (R$)", text_auto='.2f',
            template="plotly_white", color='frete', color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_frete, use_container_width=True)

    st.markdown("---")
    col_map, col_lol = st.columns([3, 2])
    with col_map:
        st.info("💡 Dica: Para ver o mapa geográfico detalhado, carregue o GeoJSON. Exibindo mapa simplificado.")
        df_mapa = df.groupby('estado_cliente')['order_id'].nunique().reset_index()
        fig_map = px.choropleth(df_mapa, locations='estado_cliente', locationmode="country names", color='order_id', scope="south america", title="Mapa de Vendas (Simulado)")
        st.plotly_chart(fig_map, use_container_width=True)
    with col_lol:
        df_top10 = df_mapa.sort_values('order_id').tail(10)
        fig_lol = px.scatter(df_top10, x='order_id', y='estado_cliente', title="Top 10 Estados (Lollipop)", size='order_id', color='order_id')
        st.plotly_chart(fig_lol, use_container_width=True)

# ==============================================================================
# ABA P2: PREÇO E CATEGORIAS
# ==============================================================================
with tab_p2:
    st.markdown("### 🏷️ P2: Portfólio e Precificação")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Ticket Médio", f"R$ {df['preco'].mean():.2f}")
    c2.metric("Top Categoria", df['categoria'].mode()[0])
    c3.metric("Faturamento", f"R$ {df['preco'].sum():,.0f}")
    
    st.markdown("---")
    
    st.subheader("📊 Pareto (Curva ABC)")
    df_par = df.groupby('categoria')['preco'].sum().sort_values(ascending=False).head(20).reset_index()
    fig_par = px.bar(df_par, x='categoria', y='preco', title="Top 20 Categorias (Receita)", template="plotly_white")
    st.plotly_chart(fig_par, use_container_width=True)
    
    st.markdown("#### 🆕 Análises de Preço Aprofundadas")
    
    col_new3, col_new4 = st.columns(2)
    with col_new3:
        st.subheader("📦 Dispersão de Preços (Boxplot)")
        top_10_cats = df['categoria'].value_counts().head(10).index
        df_box_cat = df[df['categoria'].isin(top_10_cats)]
        fig_box_cat = px.box(df_box_cat, x='categoria', y='preco', title="Distribuição de Preços nas Top 10 Categorias", points=False, template="plotly_white", color='categoria')
        fig_box_cat.update_layout(showlegend=False, yaxis_range=[0, 500])
        st.plotly_chart(fig_box_cat, use_container_width=True)
        
    with col_new4:
        st.subheader("💸 Preço do Produto vs. Frete")
        df_samp = df.sample(min(2000, len(df)))
        fig_scat_frete = px.scatter(df_samp, x='preco', y='frete', title="Correlação: Preço x Frete", trendline="ols", template="plotly_white", opacity=0.6)
        st.plotly_chart(fig_scat_frete, use_container_width=True)

# ==============================================================================
# ABA P3: SATISFAÇÃO
# ==============================================================================
with tab_p3:
    st.markdown("### ⭐ P3: Experiência do Cliente")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Nota Média", f"{df['review_score'].mean():.2f}/5")
    k2.metric("Atrasos", df[df['atraso_entrega']>0].shape[0])
    k3.metric("% Atraso", f"{(df[df['atraso_entrega']>0].shape[0]/len(df))*100:.1f}%")
    
    st.markdown("---")
    st.markdown("#### 🆕 Análise de Felicidade do Cliente")
    
    col_new5, col_new6 = st.columns(2)
    with col_new5:
        st.subheader("🗺️ Satisfação por Região")
        df_score_reg = df.groupby('regiao')['review_score'].mean().reset_index().sort_values('review_score')
        fig_score_reg = px.bar(df_score_reg, x='review_score', y='regiao', orientation='h', title="Nota Média por Região", range_x=[3, 5], template="plotly_white", color='review_score', color_continuous_scale='Bluyl')
        st.plotly_chart(fig_score_reg, use_container_width=True)
        
    with col_new6:
        st.subheader("📉 Impacto do Frete na Nota")
        fig_box_frete = px.box(df, x='review_score', y='frete', title="Distribuição do Valor de Frete por Nota", template="plotly_white", color='review_score')
        fig_box_frete.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_box_frete, use_container_width=True)

    st.markdown("---")
    c_hist, c_line = st.columns(2)
    with c_hist:
        fig_h = px.histogram(df, x='review_score', title="Histograma de Notas", nbins=5)
        st.plotly_chart(fig_h, use_container_width=True)
    with c_line:
        df_corr = df[df['tempo_total']<=50].groupby('tempo_total')['review_score'].mean().reset_index()
        fig_c = px.line(df_corr, x='tempo_total', y='review_score', title="Queda da Nota com o Tempo")
        st.plotly_chart(fig_c, use_container_width=True)

# ==============================================================================
# ABA ML: CLUSTERIZAÇÃO
# ==============================================================================
with tab_ml:
    st.markdown("### 🤖 Clusterização (Segmentação de Clientes)")
    
    st.subheader("📍 Mapa dos Clusters")
    df_samp = df.sample(min(3000, len(df)))
    fig_clus = px.scatter(df_samp, x='tempo_total', y='preco', color='grupos', title="Clusters: Preço x Tempo", height=400)
    fig_clus.update_layout(xaxis_range=[0,60], yaxis_range=[0,1000])
    st.plotly_chart(fig_clus, use_container_width=True)
    
    st.markdown("#### 🆕 Perfilamento dos Grupos")
    
    col_new7, col_new8 = st.columns(2)
    with col_new7:
        st.subheader("👥 Tamanho dos Grupos")
        df_count_cl = df['grupos'].value_counts().reset_index()
        df_count_cl.columns = ['Grupo', 'Quantidade']
        fig_count_cl = px.bar(df_count_cl, x='Grupo', y='Quantidade', title="Volume de Clientes por Cluster", template="plotly_white", color='Grupo', text_auto=True)
        st.plotly_chart(fig_count_cl, use_container_width=True)
        
    with col_new8:
        st.subheader("⭐ Satisfação por Grupo")
        fig_box_cl = px.box(df, x='grupos', y='review_score', title="Distribuição de Notas por Cluster", template="plotly_white", color='grupos')
        st.plotly_chart(fig_box_cl, use_container_width=True)

    st.markdown("---")
    st.subheader("📝 Tabela Resumo")
    
    # Cálculo seguro da tabela
    df_stats = df.groupby('grupos')[['preco', 'tempo_total', 'frete', 'review_score']].mean()
    st.dataframe(df_stats.style.format("{:.2f}"))
q
