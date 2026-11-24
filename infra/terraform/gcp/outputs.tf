output "etl_service_account" {
  description = "E-mail da conta de serviço do ETL"
  value       = google_service_account.etl.email
}
