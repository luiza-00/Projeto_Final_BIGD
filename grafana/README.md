# Configuração do Grafana Cloud

1. Crie uma conexão PostgreSQL no Grafana Cloud usando os dados do serviço Aiven.
2. Ative TLS/SSL (`SSL Mode: require`) e use as credenciais como segredos da conexão.
3. Importe `dashboards/observatorio-stem.json`.
4. Na importação, associe a fonte de dados PostgreSQL criada e substitua o UID `AIVEN_POSTGRES_UID` pelo UID real, se o Grafana não fizer o mapeamento automaticamente.
5. O painel monitora volume, ano mais recente, tamanho do banco e evolução das matrículas. Ele não mede a execução do ETL diretamente, pois o ETL atual não grava logs de execução no PostgreSQL.

**Segurança:** nunca publique senha, host privado ou token em JSON versionado. Configure as credenciais diretamente na interface/secret store do Grafana.
