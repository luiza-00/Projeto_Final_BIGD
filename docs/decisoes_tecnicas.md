# Decisões técnicas

| # | Decisão | Alternativas consideradas | Justificativa |
|---|---|---|---|
| 1 | Extrair os dados da **Base dos Dados via BigQuery** | Baixar os microdados (CSV) do portal do INEP | Os dados já vêm padronizados e permitem filtrar na origem, sem baixar arquivos de vários GB por ano |
| 2 | **Pandas** para o tratamento | Spark, dbt, SQL direto no BigQuery | Depois do filtro STEM, o volume cabe na memória do Colab; Spark seria um custo desnecessário para esse tamanho |
| 3 | **PostgreSQL** como banco de destino | MongoDB, BigQuery como destino | Os dados são tabulares e relacionais (curso, município, indicadores), e o SQL facilita as análises das próximas fases |
| 4 | **Aiven free tier** | AWS RDS, Supabase, Neon | Gratuito, gerenciado e com provider Terraform oficial |
| 5 | **Esquema estrela** | Tabela única desnormalizada; modelo normalizado (3FN) | Evita repetir nomes de cursos e municípios em cada linha e é adequado a consultas analíticas (agregações por ano, UF e área) |
| 6 | Grão **curso × município × ano** na fato | Curso × ano (descartando ou somando os polos) | A base registra cursos EAD por município de polo; manter esse nível preserva todos os alunos e permite análises regionais |
| 7 | Recorte a partir de **2015** (configurável) | Série completa | Aproximadamente uma década de dados, suficiente para tendências e compatível com o limite de armazenamento |
| 8 | Nulos mantidos como `NULL` | Substituir por 0 | "Não informado" é diferente de "zero" e não deve distorcer médias |
| 9 | DDL explícito com PK/FK | `to_sql` criando as tabelas | Garante tipos corretos, integridade referencial e índices |
| 10 | Carga em **transação única** com recriação das tabelas | Carga incremental | A base é atualizada anualmente; a recarga completa é simples e não deixa o banco em estado parcial |
| 11 | Carga com o comando **COPY** do PostgreSQL | `INSERT` em lotes (`to_sql`) | Cerca de 660 mil linhas na fato; o COPY é muito mais rápido que inserir linha a linha |
| 12 | Segredos em `.env` / Colab Secrets / `AIVEN_TOKEN` | Credenciais no código; arquivo JSON de chave | Nenhum segredo vai para o repositório público |
