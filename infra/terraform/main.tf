# =====================================================================
# Banco de dados de destino: PostgreSQL gerenciado no Aiven
# =====================================================================
resource "aiven_pg" "obs_stem" {
  project      = var.aiven_project
  service_name = var.pg_service_name
  cloud_name   = var.pg_cloud
  plan         = var.pg_plan

  # Evita exclusão acidental do banco com os dados carregados
  termination_protection = true

  pg_user_config {
    pg_version = var.pg_version
  }
}

# =====================================================================
# Origem dos dados: acesso ao BigQuery (Base dos Dados) no Google Cloud
# =====================================================================
resource "google_project_service" "bigquery" {
  project            = var.gcp_project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

# Conta de serviço dedicada ao ETL, com o mínimo de permissão necessário
resource "google_service_account" "etl" {
  project      = var.gcp_project_id
  account_id   = "obs-stem-etl"
  display_name = "Observatório STEM - ETL"
  description  = "Executa consultas de leitura nos dados públicos da Base dos Dados"
}

# Permite apenas executar jobs de consulta (os dados da Base dos Dados são públicos).
# A chave JSON NÃO é criada pelo Terraform para não ficar gravada no state.
resource "google_project_iam_member" "etl_job_user" {
  project = var.gcp_project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.etl.email}"

  depends_on = [google_project_service.bigquery]
}
