resource "google_cloud_run_domain_mapping" "apex-domain" {

  name     = var.domain
  location = google_cloud_run_v2_service.app.location

  metadata {
    namespace = var.gcp_project_id
  }

  spec {
    route_name     = google_cloud_run_v2_service.app.name
    force_override = true
  }

}
