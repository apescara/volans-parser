terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
  default     = "clinica-volans"
}

variable "region" {
  description = "The GCP region to deploy resources in"
  type        = string
  default     = "us-east1"
}

variable "zone" {
  description = "The GCP zone to deploy resources in"
  type        = string
  default     = "us-east1-a"
}

resource "google_storage_bucket" "bucket" {
  name     = "archivos-base"
  location = var.region
  project  = var.project_id
}

data "google_storage_project_service_account" "gcs_account" {
  project = var.project_id
}

// Grant pubsub.publisher permission to storage project service account
resource "google_project_iam_binding" "google_storage_project_service_account_is_pubsub_publisher" {
  project = var.project_id
  for_each = {
    for role in [
      "roles/pubsub.publisher",
      "roles/storage.bucketViewer",
    ] : role => role
  }
  role = each.value
  members = [
    data.google_storage_project_service_account.gcs_account.member,
  ]
}

resource "google_service_account" "cloud_function_sa" {
  account_id   = "sa-clinica-volans"
  display_name = "sa-clinica-volans"
  description  = "Cuenta de servicio"
  project      = var.project_id
}

resource "google_project_iam_member" "cloud_function_sa" {
  project = var.project_id
  for_each = {
    for role in [
      "roles/cloudfunctions.serviceAgent",
      "roles/eventarc.eventReceiver",
      "roles/storage.objectUser",
      "roles/storage.bucketViewer",
      "roles/bigquery.admin",
    ] : role => role
  }
  role   = each.value
  member = google_service_account.cloud_function_sa.member
}

output "bucket" {
  value = google_storage_bucket.bucket.name
}

output "sa_email" {
  value = google_service_account.cloud_function_sa.email
}