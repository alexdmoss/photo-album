data "google_storage_bucket" "photo-album" {
  name    = var.photos_bucket
  project = var.photos_project_id
}

resource "google_storage_bucket_iam_member" "runtime-can-read-photos" {
  bucket = data.google_storage_bucket.photo-album.name
  role   = "roles/storage.objectReader"
  member = "serviceAccount:${data.google_service_account.runtime.email}"
}
