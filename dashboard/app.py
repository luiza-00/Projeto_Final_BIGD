"""Observatório STEM — painel analítico em Streamlit."""
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="Observatório STEM", page_icon="🎓", layout="wide")
px.defaults.color_discrete_sequence = ["#D6467E", "#5A1E3D", "#E07AA3", "#8E2A57"]



def get_engine():
    def config(key, default=None):
        # Primeiro tenta variável de ambiente; depois Streamlit Secrets.
        value = os.getenv(key)
        if value:
            return value
        try:
            return st.secrets.get(key, default)
        except Exception:
            return default

    required = ["PG_HOST", "PG_PORT", "PG_USER", "PG_PASSWORD"]
    values = {key: config(key) for key in required}
    missing = [key for key, value in values.items() if not value]

    if missing:
        st.error("Configure as credenciais: " + ", ".join(missing))
        st.stop()

    url = URL.create(
        "postgresql+psycopg2",
        username=values["PG_USER"],
        password=values["PG_PASSWORD"],
        host=values["PG_HOST"],
        port=int(values["PG_PORT"]),
        database=config("PG_DATABASE", "defaultdb"),
        query={"sslmode": "require"},
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=300)



@st.cache_resource
def engine():
    return get_engine()


@st.cache_resource(ttl=3600, show_spinner="Consultando o PostgreSQL...")
def load_data():
    query = text("""
        SELECT f.ano, m.sigla_uf, m.nome_municipio,
               c.id_curso, c.id_area_geral, c.nome_area_geral, c.nome_curso,
               f.qtd_ingressantes_feminino, f.qtd_ingressantes_masculino,
               f.qtd_matriculas_feminino, f.qtd_matriculas_masculino,
               f.qtd_concluintes_feminino, f.qtd_concluintes_masculino,
               f.qtd_ingressantes_financiamento,
               f.qtd_matriculas_reserva_renda_familiar,
               f.qtd_concluintes_reserva_renda_familiar
        FROM fato_stem f
        JOIN dim_municipio m ON m.id_municipio = f.id_municipio
        JOIN dim_curso c ON c.id_curso = f.id_curso
    """)
    with engine().connect() as conn:
        df = pd.read_sql(query, conn)
    for col in ["sigla_uf", "nome_municipio", "id_area_geral", "nome_area_geral", "nome_curso"]:
        df[col] = df[col].astype("string[pyarrow]")
    return df


st.title("🎓 Observatório de Evasão e Retenção em Cursos STEM")
st.caption("Censo da Educação Superior · INEP / Base dos Dados · Recorte de áreas STEM 05, 06 e 07")

try:
    df = load_data()
except Exception as exc:
    st.error("Não foi possível consultar o PostgreSQL. Verifique as credenciais e se o ETL já foi executado.")
    st.exception(exc)
    st.stop()

if df.empty:
    st.warning("O banco ainda não possui dados. Execute primeiro o pipeline em etl/etl_stem.py.")
    st.stop()

# Filtros da lateral
st.sidebar.header("Filtros")
years = sorted(df["ano"].dropna().astype(int).unique().tolist())
selected_years = st.sidebar.slider("Período", min_value=int(min(years)), max_value=int(max(years)), value=(int(min(years)), int(max(years))))
ufs = sorted(df.loc[df.sigla_uf != "NI", "sigla_uf"].dropna().unique().tolist())
selected_ufs = st.sidebar.multiselect("UF", ufs, default=[])
areas = sorted(df["nome_area_geral"].dropna().unique().tolist())
selected_areas = st.sidebar.multiselect("Área STEM", areas, default=areas)
sex = st.sidebar.selectbox("Grupo de sexo", ["Todos", "Feminino", "Masculino"])
metric_label = st.sidebar.selectbox("Métrica dos gráficos", ["Matrículas", "Ingressantes", "Concluintes", "Financiamento de ingressantes", "Matrículas com reserva por renda"])

filtered = df[df.ano.between(selected_years[0], selected_years[1])].copy()
if selected_ufs:
    filtered = filtered[filtered.sigla_uf.isin(selected_ufs)]
if selected_areas:
    filtered = filtered[filtered.nome_area_geral.isin(selected_areas)]

if filtered.empty:
    st.info("Não há dados para o recorte selecionado. Ajuste os filtros na lateral.")
    st.stop()

pairs = {
    "Matrículas": ("qtd_matriculas_feminino", "qtd_matriculas_masculino"),
    "Ingressantes": ("qtd_ingressantes_feminino", "qtd_ingressantes_masculino"),
    "Concluintes": ("qtd_concluintes_feminino", "qtd_concluintes_masculino"),
}
if metric_label in pairs:
    female_col, male_col = pairs[metric_label]
    filtered["valor_feminino"] = filtered[female_col].fillna(0)
    filtered["valor_masculino"] = filtered[male_col].fillna(0)
    filtered["total_metrica"] = filtered.valor_feminino + filtered.valor_masculino
    if sex == "Feminino":
        filtered["valor_selecionado"] = filtered.valor_feminino
    elif sex == "Masculino":
        filtered["valor_selecionado"] = filtered.valor_masculino
    else:
        filtered["valor_selecionado"] = filtered.total_metrica
elif metric_label == "Financiamento de ingressantes":
    filtered["valor_selecionado"] = filtered.qtd_ingressantes_financiamento.fillna(0)
else:
    filtered["valor_selecionado"] = filtered.qtd_matriculas_reserva_renda_familiar.fillna(0)

# KPIs: os nulos são preservados na origem; para somatórios de contagem, NULL não contribui.
fem = filtered.qtd_matriculas_feminino.sum()
masc = filtered.qtd_matriculas_masculino.sum()
total = fem + masc
share = (100 * fem / total) if total else 0
k1, k2, k3, k4 = st.columns(4)
k1.metric("Matrículas (F + M)", f"{total:,.0f}".replace(",", "."))
k2.metric("Matrículas femininas", f"{fem:,.0f}".replace(",", "."))
k3.metric("Participação feminina", f"{share:.1f}%")
k4.metric("Cursos no recorte", f"{filtered.id_curso.nunique():,}".replace(",", "."))

st.divider()
st.subheader("Participação feminina nas matrículas")
st.caption("Matrículas femininas ÷ matrículas totais × 100, com o mesmo critério para todos os anos e áreas do recorte.")
cols_mat = ["qtd_matriculas_feminino", "qtd_matriculas_masculino"]
rn14 = filtered.groupby(["ano", "nome_area_geral"], as_index=False)[cols_mat].sum()
rn14_total = rn14.groupby("ano", as_index=False)[cols_mat].sum().assign(nome_area_geral="Total STEM")
rn14 = pd.concat([rn14, rn14_total], ignore_index=True)
rn14["matriculas"] = rn14.qtd_matriculas_feminino + rn14.qtd_matriculas_masculino
rn14["participacao_feminina"] = 100 * rn14.qtd_matriculas_feminino / rn14.matriculas.where(rn14.matriculas > 0)
left, right = st.columns(2)
with left:
    st.markdown("**Participação feminina por ano e área**")
    fig = px.line(rn14, x="ano", y="participacao_feminina", color="nome_area_geral", markers=True,
                  labels={"ano": "Ano", "participacao_feminina": "Participação feminina (%)", "nome_area_geral": "Área"})
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, width="stretch")
with right:
    st.markdown("**Peso de cada área nas matrículas**")
    peso = rn14[rn14.nome_area_geral != "Total STEM"]
    fig = px.bar(peso, x="ano", y="matriculas", color="nome_area_geral",
                 labels={"ano": "Ano", "matriculas": "Participação nas matrículas (%)", "nome_area_geral": "Área"})
    fig.update_layout(barnorm="percent")
    fig.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig, width="stretch")

st.divider()
left, right = st.columns(2)
with left:
    st.subheader(f"Evolução — {metric_label}")
    trend = filtered.groupby("ano", as_index=False)["valor_selecionado"].sum()
    fig = px.line(trend, x="ano", y="valor_selecionado", markers=True, labels={"ano": "Ano", "valor_selecionado": "Quantidade"})
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Participação nas matrículas por sexo")
    sex_data = pd.DataFrame({"Sexo": ["Feminino", "Masculino"], "Matrículas": [fem, masc]})
    fig = px.pie(sex_data, names="Sexo", values="Matrículas", hole=.45)
    fig.update_traces(marker=dict(colors=["#D6467E", "#5A1E3D"]), sort=False)
    st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Distribuição por área STEM")
    area_data = filtered.groupby("nome_area_geral", as_index=False)["valor_selecionado"].sum().sort_values("valor_selecionado", ascending=False)
    fig = px.bar(area_data, x="nome_area_geral", y="valor_selecionado", labels={"nome_area_geral": "Área", "valor_selecionado": "Quantidade"})
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Distribuição por UF")
    uf_data = filtered[filtered.sigla_uf != "NI"].groupby("sigla_uf", as_index=False)["valor_selecionado"].sum().sort_values("valor_selecionado", ascending=False).head(15)
    fig = px.bar(uf_data, x="sigla_uf", y="valor_selecionado", labels={"sigla_uf": "UF", "valor_selecionado": "Quantidade"})
    st.plotly_chart(fig, width="stretch")

st.subheader("Detalhamento por curso e município")
detail = (filtered.groupby(["ano", "sigla_uf", "nome_municipio", "nome_area_geral", "nome_curso"], as_index=False)["valor_selecionado"].sum().sort_values("valor_selecionado", ascending=False))
st.dataframe(detail, width="stretch", hide_index=True)
st.download_button("Baixar dados filtrados (CSV)", detail.to_csv(index=False).encode("utf-8-sig"), "observatorio_stem_filtrado.csv", "text/csv")

with st.expander("Limites metodológicos e interpretação"):
    st.markdown("""
    - A base atualmente carregada contém indicadores agregados por **curso × município × ano** e desagregação por sexo.
    - O modelo atual **não possui raça/cor**. Portanto, não permite análise interseccional gênero × raça/cor nem conclusões sobre a ODS 18.
    - O Censo agregado utilizado não acompanha a trajetória individual de uma coorte. Por isso, este painel **não calcula taxa real de evasão ou retenção**.
    - Ingressantes e concluintes no mesmo ano são populações distintas; a razão entre eles não deve ser interpretada como taxa de conclusão ou evasão.
    - Os resultados são indicadores descritivos de participação e distribuição, não relações causais.
    """)

st.caption("Fonte: INEP — Censo da Educação Superior, via Base dos Dados. Atualização depende da execução do ETL.")
