-- Consultas de validação executadas após a carga

-- 1. Volume por tabela
SELECT 'dim_municipio' AS tabela, COUNT(*) AS linhas FROM dim_municipio
UNION ALL SELECT 'dim_curso', COUNT(*) FROM dim_curso
UNION ALL SELECT 'fato_stem', COUNT(*) FROM fato_stem;

-- 2. Cobertura temporal
SELECT ano, COUNT(*) AS cursos FROM fato_stem GROUP BY ano ORDER BY ano;

-- 3. Linhas da fato sem município (ex.: registros sem localização informada)
SELECT COUNT(*) AS fato_sem_municipio FROM fato_stem WHERE id_municipio IS NULL;

-- 4. Distribuição por área STEM
SELECT c.nome_area_geral, COUNT(DISTINCT c.id_curso) AS cursos
FROM dim_curso c
GROUP BY c.nome_area_geral
ORDER BY cursos DESC;

-- 5. Exemplo de consulta analítica: participação feminina nas matrículas por ano
SELECT
    f.ano,
    SUM(f.qtd_matriculas_feminino)  AS matriculas_fem,
    SUM(f.qtd_matriculas_masculino) AS matriculas_masc,
    ROUND(100.0 * SUM(f.qtd_matriculas_feminino)
          / NULLIF(SUM(f.qtd_matriculas_feminino) + SUM(f.qtd_matriculas_masculino), 0), 1) AS pct_feminino
FROM fato_stem f
GROUP BY f.ano
ORDER BY f.ano;

-- 6. Tamanho ocupado no banco (limite do plano gratuito)
SELECT pg_size_pretty(pg_database_size(current_database())) AS tamanho_banco;
