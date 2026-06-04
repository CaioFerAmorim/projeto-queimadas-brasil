import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Queimadas no Brasil",
    page_icon="🔥",
    layout="wide"
)

# ── Carregamento dos dados ──────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "simulacao_queimadas_brasil.csv"))
    df["data"] = pd.to_datetime(df["data"])
    return df

df = carregar_dados()

# ── Título ──────────────────────────────────────────────────────────────────
st.title("🔥 Análise de Queimadas no Brasil (2015–2024)")
st.markdown("""
Este dashboard apresenta uma análise interativa dos focos de queimadas no Brasil,
permitindo identificar padrões regionais, sazonalidade e áreas críticas entre 2015 e 2024.
""")

st.divider()

# ── Filtros ─────────────────────────────────────────────────────────────────
st.sidebar.title("🎛️ Filtros")

anos = sorted(df["ano"].unique())
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos)

meses = sorted(df["mes"].unique())
mes_sel = st.sidebar.multiselect("Mês", meses, default=meses)

regioes = sorted(df["regiao"].unique())
regiao_sel = st.sidebar.multiselect("Região", regioes, default=regioes)

estados = sorted(df["uf"].unique())
estado_sel = st.sidebar.multiselect("Estado (UF)", estados, default=estados)

biomas = sorted(df["bioma"].unique())
bioma_sel = st.sidebar.multiselect("Bioma", biomas, default=biomas)

riscos = sorted(df["nivel_risco"].unique())
risco_sel = st.sidebar.multiselect("Nível de Risco", riscos, default=riscos)

# ── Aplicar filtros ─────────────────────────────────────────────────────────
df_f = df[
    (df["ano"].isin(ano_sel)) &
    (df["mes"].isin(mes_sel)) &
    (df["regiao"].isin(regiao_sel)) &
    (df["uf"].isin(estado_sel)) &
    (df["bioma"].isin(bioma_sel)) &
    (df["nivel_risco"].isin(risco_sel))
]

# ── KPIs ────────────────────────────────────────────────────────────────────
st.subheader("📌 Indicadores Principais (KPIs)")

total_focos = int(df_f["focos_queimada"].sum())
area_total = round(df_f["area_atingida_km2"].sum(), 2)

estado_critico = (
    df_f.groupby("uf")["focos_queimada"].sum().idxmax()
    if not df_f.empty else "N/A"
)

regiao_critica = (
    df_f.groupby("regiao")["focos_queimada"].sum().idxmax()
    if not df_f.empty else "N/A"
)

mes_critico = (
    df_f.groupby("mes")["focos_queimada"].sum().idxmax()
    if not df_f.empty else "N/A"
)

media_anual = round(
    df_f.groupby("ano")["focos_queimada"].sum().mean(), 1
) if not df_f.empty else 0

col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

col1.metric("🔥 Total de Focos", f"{total_focos:,}")
col2.metric("🌍 Área Total Atingida (km²)", f"{area_total:,.2f}")
col3.metric("📍 Estado Mais Afetado", estado_critico)
col4.metric("🗺️ Região Mais Crítica", regiao_critica)
col5.metric("📅 Mês Mais Crítico", f"Mês {mes_critico}")
col6.metric("📊 Média Anual de Focos", f"{media_anual:,}")

st.divider()

# ── Gráfico 1: Evolução temporal ────────────────────────────────────────────
st.subheader("📈 Evolução Temporal dos Focos de Queimadas")

evolucao = df_f.groupby("ano")["focos_queimada"].sum().reset_index()
fig1 = px.line(
    evolucao, x="ano", y="focos_queimada",
    markers=True,
    labels={"ano": "Ano", "focos_queimada": "Focos de Queimada"},
    title="Total de Focos por Ano"
)
fig1.update_layout(template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
**Interpretação:** O gráfico acima mostra a evolução anual dos focos de queimadas.
Picos indicam anos com maior incidência, possivelmente associados a períodos de seca intensa ou
expansão agropecuária.
""")

st.divider()

# ── Gráfico 2: Barras por estado ────────────────────────────────────────────
st.subheader("🏛️ Comparação entre Estados")

por_estado = df_f.groupby("uf")["focos_queimada"].sum().reset_index()
por_estado = por_estado.sort_values("focos_queimada", ascending=False)
fig2 = px.bar(
    por_estado, x="uf", y="focos_queimada",
    color="focos_queimada",
    color_continuous_scale="Reds",
    labels={"uf": "Estado", "focos_queimada": "Focos de Queimada"},
    title="Focos de Queimadas por Estado"
)
fig2.update_layout(template="plotly_white")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
**Interpretação:** Estados com maior número de focos exigem atenção ambiental prioritária.
Regiões com vegetação densa e períodos secos prolongados tendem a concentrar mais ocorrências.
""")

st.divider()

# ── Gráfico 3: Barras por bioma ─────────────────────────────────────────────
st.subheader("🌿 Análise por Bioma")

por_bioma = df_f.groupby("bioma")["focos_queimada"].sum().reset_index()
por_bioma = por_bioma.sort_values("focos_queimada", ascending=False)
fig3 = px.bar(
    por_bioma, x="bioma", y="focos_queimada",
    color="focos_queimada",
    color_continuous_scale="Oranges",
    labels={"bioma": "Bioma", "focos_queimada": "Focos de Queimada"},
    title="Focos de Queimadas por Bioma"
)
fig3.update_layout(template="plotly_white")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
**Interpretação:** Biomas com maior vulnerabilidade ao fogo apresentam características
como vegetação seca, baixa umidade e pressão antrópica. O Cerrado e a Amazônia
historicamente concentram os maiores focos.
""")

st.divider()

# ── Gráfico 4: Heatmap mensal ───────────────────────────────────────────────
st.subheader("🗓️ Sazonalidade — Heatmap Mensal")

heatmap_data = df_f.groupby(["ano", "mes"])["focos_queimada"].sum().reset_index()
heatmap_pivot = heatmap_data.pivot(index="ano", columns="mes", values="focos_queimada").fillna(0)

fig4 = go.Figure(data=go.Heatmap(
    z=heatmap_pivot.values,
    x=[f"Mês {m}" for m in heatmap_pivot.columns],
    y=heatmap_pivot.index,
    colorscale="YlOrRd",
    colorbar=dict(title="Focos")
))
fig4.update_layout(
    title="Heatmap de Focos por Ano e Mês",
    xaxis_title="Mês",
    yaxis_title="Ano",
    template="plotly_white"
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
**Interpretação:** O heatmap revela os períodos mais críticos do ano.
Cores mais escuras indicam maior concentração de focos, evidenciando
a sazonalidade das queimadas — geralmente intensificadas entre julho e outubro.
""")

st.divider()

# ── Gráfico 5: Dispersão seca x queimadas ───────────────────────────────────
st.subheader("💧 Relação entre Seca e Focos de Queimadas")

fig5 = px.scatter(
    df_f, x="indice_seca", y="focos_queimada",
    color="regiao",
    size="area_atingida_km2",
    hover_data=["uf", "ano", "mes"],
    labels={
        "indice_seca": "Índice de Seca",
        "focos_queimada": "Focos de Queimada",
        "regiao": "Região"
    },
    title="Correlação entre Índice de Seca e Focos de Queimadas"
)
fig5.update_layout(template="plotly_white")
st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
**Interpretação:** A dispersão evidencia a correlação positiva entre estiagem e queimadas.
Quanto maior o índice de seca, maior a tendência de ocorrência de focos,
confirmando que períodos de estiagem são fatores determinantes.
""")

st.divider()

# ── Gráfico 6: Comparação regional ──────────────────────────────────────────
st.subheader("🗺️ Comparação entre Regiões")

por_regiao = df_f.groupby("regiao")["focos_queimada"].sum().reset_index()
por_regiao = por_regiao.sort_values("focos_queimada", ascending=False)
fig6 = px.bar(
    por_regiao, x="regiao", y="focos_queimada",
    color="regiao",
    labels={"regiao": "Região", "focos_queimada": "Focos de Queimada"},
    title="Focos de Queimadas por Região"
)
fig6.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig6, use_container_width=True)

st.divider()

# ── Tabela dinâmica ──────────────────────────────────────────────────────────
st.subheader("📋 Tabela Dinâmica — Exploração Detalhada")

st.dataframe(
    df_f[[
        "ano", "mes", "regiao", "uf", "bioma",
        "focos_queimada", "area_atingida_km2",
        "indice_seca", "qualidade_ar", "nivel_risco"
    ]].sort_values("focos_queimada", ascending=False).reset_index(drop=True),
    use_container_width=True
)

st.divider()

# ── Conclusão executiva ──────────────────────────────────────────────────────
st.subheader("📝 Conclusão Executiva")

st.markdown("""
A análise dos focos de queimadas no Brasil entre 2015 e 2024 revelou padrões
importantes para a gestão ambiental:

- **Sazonalidade marcante:** Os meses de julho a outubro concentram os maiores
  índices de queimadas, coincidindo com o período de seca em grande parte do território.

- **Regiões críticas:** Norte e Centro-Oeste historicamente apresentam os maiores
  volumes de focos, associados à pressão sobre a Amazônia e o Cerrado.

- **Correlação com seca:** O índice de seca mostrou forte relação positiva com
  o número de focos, indicando que políticas de combate às queimadas devem
  considerar o monitoramento climático.

- **Biomas vulneráveis:** Cerrado e Amazônia concentram a maior parte das
  ocorrências, exigindo atenção prioritária de órgãos ambientais.

- **Tendência temporal:** A análise anual permite identificar anos críticos
  e avaliar a eficácia de políticas públicas de prevenção.

> ⚠️ A redução das queimadas depende de fiscalização efetiva, políticas públicas
> consistentes e conscientização ambiental da população.
""")

st.caption("Desenvolvido para fins acadêmicos — Análise de Queimadas no Brasil 2015–2024")
