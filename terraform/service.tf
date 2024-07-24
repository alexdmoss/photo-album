data "google_service_account" "runtime" {
  project    = var.gcp_project_id
  account_id = "run-${var.app_name}"
}

resource "google_cloud_run_v2_service" "app" {

  name     = var.app_name
  project  = var.gcp_project_id
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  launch_stage = "BETA"

  template {

    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    containers {

      image = var.image_tag

      ports {
        container_port = var.port
      }

      resources {
        startup_cpu_boost = true
        cpu_idle = true
      }

      env {
        name = "SKIP_TAILWIND_GENERATION"
        value = "true"
      }

      env {
        name = "AUTH_PROJECT_ID"
        value = var.auth_project_id
      }

      volume_mounts {
        name = "photos-bucket"
        mount_path = "/photos"
      }

      startup_probe {
        initial_delay_seconds = 30
        timeout_seconds       = 1
        period_seconds        = 3
        failure_threshold     = 1

        http_get {
          path = "/health"
        }
      }

      liveness_probe {
        http_get {
          path = "/health"
        }
      }

    }

    timeout = "60s"

    volumes {
      name = "photos-bucket"
      gcs {
        bucket = data.google_storage_bucket.photo-album.name
        read_only = true
      }
    }
    scaling {
      min_instance_count = 1
      max_instance_count = 2
    }

    service_account = data.google_service_account.runtime.email

  }

}

resource "google_cloud_run_v2_service_iam_member" "allow-public-acess" {
  location = google_cloud_run_v2_service.app.location
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
