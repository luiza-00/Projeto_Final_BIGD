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
  description = "Plano do serviço (free tier)"
  type        = string
  default     = "free-1-1gb"
}

variable "pg_cloud" {
  description = "Região do serviço no Aiven"
  type        = string
  default     = "do-nyc"
}

variable "pg_version" {
  description = "Versão do PostgreSQL"
  type        = string
  default     = "16"
}

variable "pg_termination_protection" {
  description = "Impede a exclusão acidental do banco"
  type        = bool
  default     = true
}
