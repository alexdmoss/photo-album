#!/usr/bin/env bash

# at the moment we assume that nginx & php app version numbers are linked
VERSION=1.1
NGINX_IMAGE_NAME=photos-nginx
PHP_IMAGE_NAME=photos-app

# GCP
GCP_PROJECT_NAME=moss-work
# used for creation of GCS bucket only
# - careful if clashes with where GKE running (europe-west2)
GCP_REGION=us-east1
GCP_BUCKET_NAME=wedding-photos-bkt

# Kubernetes
NAMESPACE=photo-album
