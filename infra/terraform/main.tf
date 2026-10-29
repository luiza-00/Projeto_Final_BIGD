resource "aiven_pg" "obs_stem" {
  project                = var.aiven_project
  service_name           = var.pg_service_name
  cloud_name             = var.pg_cloud
  plan                   = var.pg_plan
  termination_protection = true

  pg_user_config {
    pg_version = var.pg_version
  }
}

resource "google_project_service" "bigquery" {
  project            = var.gcp_project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_service_account" "etl" {
  project      = var.gcp_project_id
  account_id   = "obs-stem-etl"
  display_name = "Observatório STEM - ETL"
}

resource "google_project_iam_member" "etl_job_user" {
  project    = var.gcp_project_id
  role       = "roles/bigquery.jobUser"
  member     = "serviceAccount:${google_service_account.etl.email}"
  depends_on = [google_project_service.bigquery]
}
