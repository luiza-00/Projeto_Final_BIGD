variable "gcp_project_id" {
  description = "Projeto GCP usado para executar as consultas no BigQuery"
  type        = string
}

variable "gcp_region" {
  description = "Região padrão do GCP"
  type        = string
  default     = "southamerica-east1"
}
