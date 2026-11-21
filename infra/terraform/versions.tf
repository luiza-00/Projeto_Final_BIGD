terraform {
  required_version = ">= 1.5"

  required_providers {
    aiven = {
      source  = "aiven/aiven"
      version = "~> 4.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
provider "aiven" {}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}
