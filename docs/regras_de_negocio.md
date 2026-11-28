# Regras de negócio

Cada regra e onde ela está aplicada no projeto.

## Seleção dos dados

| Código | Regra | Onde está aplicada |
|---|---|---|
| RN01 | Somente cursos das áreas STEM | `etl/etl_stem.py`: filtro `AREAS_STEM` (05, 06, 07) na consulta ao BigQuery |
| RN02 | Período 2015–2024 | `etl/etl_stem.py`: filtro `ano >= ANO_INICIO` (2015); a base vai até 2024 |
| RN03 | Fontes oficiais | Censo da Educação Superior (INEP) via Base dos Dados |
| RN04 | Registros sem informação mínima tratados ou descartados | `tratar()`: sem `id_curso` é descartado; município inválido vai para `0000000` "NAO INFORMADO" |
| RN05 | Agrupamento por ano, curso e município | Grão da `fato_stem`: `(ano, id_curso, id_municipio)` |

## Tratamento e qualidade

| Código | Regra | Onde está aplicada |
|---|---|---|
| RN06 | Duplicados tratados no ETL | Dicionário agrupado por código antes da junção; linhas com a mesma chave somadas (392) |
| RN07 | Padronização de categorias | Área com 2 dígitos, nomes sem espaços extras e em maiúsculas |
| RN08 | Tipagem numérica adequada | Quantidades como inteiro (`INTEGER` no banco) |
| RN09 | Datas compatíveis com o PostgreSQL | A base não tem datas; o ano é `SMALLINT` |
| RN10 | Nulo não vira zero | Quantidades vazias mantidas como `NULL` |
| RN11 | Sem dados pessoais | A base é agregada por curso, município e ano |
| RN12 | Limite de 1 GB do Aiven | Banco com 131 MB após a carga |

## Indicadores (KPIs)

| Código | Regra | Onde está aplicada |
|---|---|---|
| RN13 | Total = femininas + masculinas | `dashboard/app.py`: indicador "Matrículas (F + M)" |
| RN14 | Participação feminina = femininas ÷ total × 100 | `dashboard/app.py`: indicador "Participação feminina" e gráfico "Participação feminina por ano e área" |
| RN15 | Cursos distintos no recorte | `dashboard/app.py`: contagem por `id_curso` |
| RN16 | Recalcular conforme os filtros | Todos os indicadores e gráficos usam o recorte filtrado |
| RN17 | Comparações com os mesmos critérios | Gráfico RN14 aplica o mesmo cálculo a todos os anos e áreas |
| RN18 | Evasão só com dados e metodologia adequados | Não calculada; registrada como limitação |

## Dashboard

| Código | Regra | Onde está aplicada |
|---|---|---|
| RN19 | Filtros por ano, estado, área e sexo | Barra lateral do dashboard |
| RN20 | Métrica atualiza os gráficos | Seletor "Métrica dos gráficos" |
| RN21 | Indicadores só do recorte selecionado | Cálculos feitos sobre o recorte filtrado |
| RN22 | Mensagem quando não houver dados | Aviso "Não há dados para o recorte selecionado" |
| RN23 | Dados detalhados em tabela | "Detalhamento por curso e município" |
| RN24 | Exportação em CSV | Botão "Baixar dados filtrados (CSV)" |
| RN25 | Dados iguais aos do PostgreSQL | O dashboard consulta o banco diretamente |

## Segurança e infraestrutura

| Código | Regra | Onde está aplicada |
|---|---|---|
| RN26 | Credenciais fora do repositório | Secrets do Colab e do Streamlit, `.env` local e `.gitignore` |
| RN27 | Conexão com SSL | `sslmode=require` no ETL e no dashboard |
| RN28 | Infraestrutura versionada em Terraform | `infra/terraform/` |
| RN29 | Acesso restrito a origens autorizadas | Parcial: acesso por usuário, senha e SSL. A lista de IPs do Aiven está aberta porque o Colab e o Streamlit Cloud não têm IP fixo |
| RN30 | Princípios da LGPD | Somente dados agregados e públicos |

## Interpretação dos resultados

| Código | Regra | Onde está aplicada |
|---|---|---|
| RN31 | Falta de raça/cor é limitação, não ausência de desigualdade | README (limitações) e dashboard |
| RN32 | Ingressantes × concluintes não é taxa de evasão | README e dashboard |
| RN33 | Resultados descritivos, sem causalidade | README e dashboard |
| RN34 | Mulheres e homens comparados no mesmo recorte | Indicadores e gráfico RN14 usam o mesmo filtro para os dois grupos |
| RN35 | Análise de gênero e raça depende de dados | Registrada como próximo passo |
