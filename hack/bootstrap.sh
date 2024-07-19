#!/usr/bin/env bash

# not done in terraform as the CI account does not get given enough permission to do this in the data project (needs project IAM)

if [[ -z $K8S_PROJECT_ID ]]; then
  echo "You must export the Project ID of the GKE cluster as K8S_PROJECT_ID"
  exit 1
fi

if [[ -z $FS_PROJECT_ID ]]; then
  echo "You must export the Project ID of the Firestore database as FS_PROJECT_ID"
  exit 1
fi

gcloud iam service-accounts create exercise-tracker \
  --display-name=exercise-tracker \
  --description="Workload Identity access to Datastore" \
  --project="$K8S_PROJECT_ID"

gcloud projects add-iam-policy-binding "$FS_PROJECT_ID" \
  --member="serviceAccount:exercise-tracker@$K8S_PROJECT_ID.iam.gserviceaccount.com" \
  --role=roles/datastore.user > /dev/null

gcloud secrets create auth-api --project="$FS_PROJECT_ID"
gcloud secrets add-iam-policy-binding auth-api \
    --project="$FS_PROJECT_ID" \
    --member="serviceAccount:exercise-tracker@$K8S_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Grant the serviceAccount.actAs permission to the exercise-tracker service account
gcloud iam service-accounts add-iam-policy-binding "exercise-tracker@$K8S_PROJECT_ID.iam.gserviceaccount.com" \
  --member="serviceAccount:app-ci@$FS_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --project="$K8S_PROJECT_ID"
