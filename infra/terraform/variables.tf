# ---------- Aiven ----------
variable "aiven_project" {
  description = "Nome do projeto no Aiven"
  type        = string
}

variable "pg_service_name" {
  description = "Nome do serviço PostgreSQL no Aiven"
  type        = string
  default     = "obsstem"
}

variable "pg_plan" {
  description = "Plano do serviço (free tier). Conferir o nome exato no Aiven Console."
  type        = string
  default     = "free-1-1gb"
}

variable "pg_cloud" {
  description = "Região/nuvem do serviço no Aiven (ex.: do-nyc)"
  type        = string
  default     = "do-nyc"
}

variable "pg_version" {
  description = "Versão do PostgreSQL"
  type        = string
  default     = "16"
}

# ---------- Google Cloud ----------
variable "gcp_project_id" {
  description = "Projeto GCP usado para executar as consultas no BigQuery"
  type        = string
}

variable "gcp_region" {
  description = "Região padrão do GCP"
  type        = string
  default     = "southamerica-east1"
}
