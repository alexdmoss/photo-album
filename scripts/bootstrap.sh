#!/usr/bin/env bash

if [[ -z $GCP_PROJECT_ID ]]; then
  echo "You must export the Project ID of the GKE cluster as K8S_PROJECT_ID"
  exit 1
fi

gcloud iam service-accounts create photo-album \
  --display-name=photo-album \
  --description="Workload Identity access for photo-album" \
  --project="$GCP_PROJECT_ID"
