data "google_storage_bucket" "photo-album" {
    name = "alexos-photo-album-albums"
    project = var.gcp_project_id
}

resource "google_storage_bucket_iam_member" "runtime-can-read-photos" {
    bucket = data.google_storage_bucket.photo-album.name
    role   = "roles/storage.objectViewer"
    member = "serviceAccount:${google_service_account.runtime.email}"
}
