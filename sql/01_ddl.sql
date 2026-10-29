-- Modelo dimensional (esquema estrela). Grão da fato: curso x ano.

DROP TABLE IF EXISTS raw_censo_stem;
DROP TABLE IF EXISTS fato_stem;
DROP TABLE IF EXISTS dim_curso;
DROP TABLE IF EXISTS dim_municipio;

CREATE TABLE dim_municipio (
    id_municipio     CHAR(7)      PRIMARY KEY,
    nome_municipio   VARCHAR(100) NOT NULL,
    sigla_uf         CHAR(2)      NOT NULL
);

CREATE TABLE dim_curso (
    id_curso                   VARCHAR(20)  PRIMARY KEY,
    nome_curso                 VARCHAR(255) NOT NULL,
    id_ies                     VARCHAR(20),
    tipo_organizacao_academica VARCHAR(100),
    id_area_geral              VARCHAR(2)   NOT NULL,
    nome_area_geral            VARCHAR(150) NOT NULL
);

CREATE TABLE fato_stem (
    ano                                    SMALLINT    NOT NULL,
    id_curso                               VARCHAR(20) NOT NULL REFERENCES dim_curso (id_curso),
    id_municipio                           CHAR(7)              REFERENCES dim_municipio (id_municipio),
    qtd_ingressantes_feminino              INTEGER,
    qtd_ingressantes_masculino             INTEGER,
    qtd_matriculas_feminino                INTEGER,
    qtd_matriculas_masculino               INTEGER,
    qtd_concluintes_feminino               INTEGER,
    qtd_concluintes_masculino              INTEGER,
    qtd_ingressantes_financiamento         INTEGER,
    qtd_matriculas_reserva_renda_familiar  INTEGER,
    qtd_concluintes_reserva_renda_familiar INTEGER,
    PRIMARY KEY (ano, id_curso)
);

CREATE INDEX idx_fato_municipio ON fato_stem (id_municipio);
CREATE INDEX idx_fato_ano       ON fato_stem (ano);
CREATE INDEX idx_curso_area     ON dim_curso (id_area_geral);
CREATE INDEX idx_municipio_uf   ON dim_municipio (sigla_uf);
