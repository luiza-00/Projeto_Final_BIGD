import importlib.util
import os
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

RAIZ = Path(__file__).resolve().parent.parent
DDL_PATH = RAIZ / "sql" / "01_ddl.sql"

AREAS_STEM = ("05", "06", "07")

COLUNAS_QTD = {
    "quantidade_ingressantes_feminino": "qtd_ingressantes_feminino",
    "quantidade_ingressantes_masculino": "qtd_ingressantes_masculino",
    "quantidade_matriculas_feminino": "qtd_matriculas_feminino",
    "quantidade_matriculas_masculino": "qtd_matriculas_masculino",
    "quantidade_concluintes_feminino": "qtd_concluintes_feminino",
    "quantidade_concluintes_masculino": "qtd_concluintes_masculino",
    "quantidade_ingressantes_financiamento": "qtd_ingressantes_financiamento",
    "quantidade_matriculas_reserva_vaga_social_renda_familiar": "qtd_matriculas_reserva_renda_familiar",
    "quantidade_concluintes_reserva_vaga_social_renda_familiar": "qtd_concluintes_reserva_renda_familiar",
}


def em_colab() -> bool:
    return importlib.util.find_spec("google.colab") is not None


def segredo(nome: str, padrao: str | None = None) -> str:
    valor = os.getenv(nome)
    if valor is None and em_colab():
        from google.colab import userdata
        try:
            valor = userdata.get(nome)
        except Exception:
            valor = None
    if valor is None:
        valor = padrao
    if valor is None:
        raise RuntimeError(f"Variável '{nome}' não definida. Veja o .env.example.")
    return valor


def carregar_env() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(RAIZ / ".env")
    except ImportError:
        pass


def cliente_bigquery() -> bigquery.Client:
    projeto = segredo("GCP_PROJECT_ID")
    if em_colab():
        from google.colab import auth
        auth.authenticate_user()
    return bigquery.Client(project=projeto)


def engine_postgres():
    url = URL.create(
        "postgresql+psycopg2",
        username=segredo("PG_USER"),
        password=segredo("PG_PASSWORD"),
        host=segredo("PG_HOST"),
        port=int(segredo("PG_PORT")),
        database=segredo("PG_DATABASE", "defaultdb"),
        query={"sslmode": "require"},
    )
    return create_engine(url)


def extrair(client: bigquery.Client, ano_inicio: int) -> pd.DataFrame:
    colunas = ",\n        ".join(f"c.{c}" for c in COLUNAS_QTD)
    query = f"""
    WITH dic_org AS (
        SELECT chave, valor
        FROM `basedosdados.br_inep_censo_educacao_superior.dicionario`
        WHERE id_tabela = 'curso' AND nome_coluna = 'tipo_organizacao_academica'
    )
    SELECT
        c.ano,
        c.id_curso,
        c.nome_curso,
        c.id_ies,
        c.id_municipio,
        m.nome      AS nome_municipio,
        m.sigla_uf,
        c.id_area_geral,
        c.nome_area_geral,
        d.valor     AS tipo_organizacao_academica,
        {colunas}
    FROM `basedosdados.br_inep_censo_educacao_superior.curso` c
    LEFT JOIN `basedosdados.br_bd_diretorios_brasil.municipio` m
        ON c.id_municipio = m.id_municipio
    LEFT JOIN dic_org d
        ON c.tipo_organizacao_academica = d.chave
    WHERE LPAD(CAST(c.id_area_geral AS STRING), 2, '0') IN UNNEST(@areas)
      AND c.ano >= @ano_inicio
    """
    config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ArrayQueryParameter("areas", "STRING", list(AREAS_STEM)),
        bigquery.ScalarQueryParameter("ano_inicio", "INT64", ano_inicio),
    ])
    df = client.query(query, job_config=config).to_dataframe()
    print(f"[extração] {len(df):,} linhas extraídas (ano >= {ano_inicio})")
    return df


def tratar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["ano"] = df["ano"].astype("int16")
    for col in ["id_curso", "id_ies", "id_municipio", "nome_curso", "nome_municipio",
                "sigla_uf", "nome_area_geral", "tipo_organizacao_academica"]:
        df[col] = df[col].astype("string").str.strip()
    df["id_area_geral"] = df["id_area_geral"].astype("string").str.zfill(2)
    df["sigla_uf"] = df["sigla_uf"].str.upper()
    invalido = ~df["id_municipio"].str.fullmatch(r"\d{7}", na=False) | df["nome_municipio"].isna()
    df.loc[invalido, ["id_municipio", "nome_municipio", "sigla_uf"]] = pd.NA
    print(f"[tratamento] {int(invalido.sum())} linhas com município inválido ou ausente")
    df["nome_curso"] = df["nome_curso"].str.upper()

    df = df.rename(columns=COLUNAS_QTD)
    for col in COLUNAS_QTD.values():
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    antes = len(df)
    df = df.dropna(subset=["id_curso"])
    print(f"[tratamento] {antes - len(df)} linhas sem id_curso removidas")
    return df


def modelar(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    recente = df.sort_values("ano", ascending=False)

    dim_municipio = (
        recente.dropna(subset=["id_municipio"])
        [["id_municipio", "nome_municipio", "sigla_uf"]]
        .drop_duplicates("id_municipio")
        .reset_index(drop=True)
    )

    dim_curso = (
        recente[["id_curso", "nome_curso", "id_ies", "tipo_organizacao_academica",
                 "id_area_geral", "nome_area_geral"]]
        .groupby("id_curso", as_index=False, sort=False)
        .first()
    )
    dim_curso["nome_curso"] = dim_curso["nome_curso"].fillna("NAO INFORMADO")

    chaves = ["ano", "id_curso"]
    qtds = list(COLUNAS_QTD.values())
    fato = (
        df.groupby(chaves, as_index=False)
        .agg({"id_municipio": "first", **{c: lambda s: s.sum(min_count=1) for c in qtds}})
    )
    for c in qtds:
        fato[c] = fato[c].astype("Int64")

    print(f"[modelagem] dim_municipio={len(dim_municipio):,} | "
          f"dim_curso={len(dim_curso):,} | fato_stem={len(fato):,}")
    return {"dim_municipio": dim_municipio, "dim_curso": dim_curso, "fato_stem": fato}


def carregar(tabelas: dict[str, pd.DataFrame], engine) -> None:
    ddl = DDL_PATH.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql(ddl)
        for nome in ["dim_municipio", "dim_curso", "fato_stem"]:
            tabelas[nome].to_sql(nome, conn, if_exists="append", index=False,
                                 method="multi", chunksize=2000)
            print(f"[carga] {nome}: {len(tabelas[nome]):,} linhas")


def validar(engine) -> None:
    with engine.connect() as conn:
        for tabela in ["dim_municipio", "dim_curso", "fato_stem"]:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()
            print(f"[validação] {tabela}: {n:,} linhas no banco")
        tamanho = conn.execute(
            text("SELECT pg_size_pretty(pg_database_size(current_database()))")
        ).scalar()
        print(f"[validação] tamanho do banco: {tamanho}")


def main() -> None:
    carregar_env()
    ano_inicio = int(segredo("ANO_INICIO", "2015"))

    df = extrair(cliente_bigquery(), ano_inicio)
    df = tratar(df)
    tabelas = modelar(df)

    saida = RAIZ / "data" / "processed"
    saida.mkdir(parents=True, exist_ok=True)
    for nome, tabela in tabelas.items():
        tabela.to_csv(saida / f"{nome}.csv", index=False)
    print(f"[arquivos] CSVs salvos em {saida}")

    engine = engine_postgres()
    carregar(tabelas, engine)
    validar(engine)


if __name__ == "__main__":
    main()
