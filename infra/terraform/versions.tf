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

  # O state fica local e fora do Git (.gitignore), pois contém a senha do banco.
  # Para trabalho em equipe, pode-se usar um backend remoto, por exemplo:
  # backend "gcs" {
  #   bucket = "obs-stem-tfstate"
  #   prefix = "infra"
  # }
}

# Token lido da variável de ambiente AIVEN_TOKEN (nunca no código)
provider "aiven" {}

# Credenciais lidas de GOOGLE_APPLICATION_CREDENTIALS
# ou de "gcloud auth application-default login"
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}
