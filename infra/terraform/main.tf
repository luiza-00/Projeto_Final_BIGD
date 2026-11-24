resource "aiven_pg" "obs_stem" {
  project                = var.aiven_project
  service_name           = var.pg_service_name
  cloud_name             = var.pg_cloud
  plan                   = var.pg_plan
  termination_protection = var.pg_termination_protection

  pg_user_config {
    pg_version = var.pg_version
  }
}
