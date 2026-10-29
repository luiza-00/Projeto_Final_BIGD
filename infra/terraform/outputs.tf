output "pg_host" {
  description = "Host do PostgreSQL"
  value       = aiven_pg.obs_stem.service_host
}

output "pg_port" {
  description = "Porta do PostgreSQL"
  value       = aiven_pg.obs_stem.service_port
}

output "pg_user" {
  description = "Usuário administrador"
  value       = aiven_pg.obs_stem.service_username
}

output "pg_password" {
  description = "Senha do banco"
  value       = aiven_pg.obs_stem.service_password
  sensitive   = true
}

output "etl_service_account" {
  description = "E-mail da conta de serviço do ETL"
  value       = google_service_account.etl.email
}
