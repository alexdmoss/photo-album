#!/usr/bin/env bash
#
# [ADM, 2017-08-15] deploy.sh [--install]
#
# Deploys latest image to GKE by applying Kubernetes deployment manifest,
# after automatically updating with latest image tag in GCR.
#
# If --install specified, it is first-time execution. Following are performed:
#  1. Namespace created
#  2. GCP Cloud Storage bucket created
#  3. Ingress defined

# source global variables
. ./config/vars.sh

# check required variables set
if [[ -z ${GCP_PROJECT_NAME} ]];  then echo "[ERROR] GCP_PROJECT_NAME not set, aborting.";  exit 1; fi
if [[ -z ${GCP_REGION} ]];        then echo "[ERROR] GCP_REGION not set, aborting.";        exit 1; fi
if [[ -z ${GCP_BUCKET_NAME} ]];   then echo "[ERROR] GCP_BUCKET_NAME not set, aborting.";   exit 1; fi
if [[ -z ${NAMESPACE} ]];         then echo "[ERROR] NAMESPACE not set, aborting.";         exit 1; fi
if [[ -z ${NGINX_IMAGE_NAME} ]];  then echo "[ERROR] NGINX_IMAGE_NAME not set, aborting.";  exit 1; fi
if [[ -z ${PHP_IMAGE_NAME} ]];    then echo "[ERROR] PHP_IMAGE_NAME not set, aborting.";    exit 1; fi

NGINX_BUILD_IMAGE=eu.gcr.io/${GCP_PROJECT_NAME}/${NGINX_IMAGE_NAME}
PHP_BUILD_IMAGE=eu.gcr.io/${GCP_PROJECT_NAME}/${PHP_IMAGE_NAME}

# installing for first time - run one-time setup activities
if [[ $1 == "--install" ]]; then

  set -x

  # creates the namespace
  kubectl apply -f ./k8s/create-namespace.yml

  # creates gcloud storage bucket
  gsutil mb -p ${GCP_PROJECT}  -l ${GCP_REGION} -c regional gs://${GCP_BUCKET_NAME}/

  # creates the GCP load balancer (ingress), which includes static IP
  kubectl apply -f ./k8s/create-ingress.yml

fi

# get latest build info pushed to GCR (assumes NGINX & PHP version are linked)
LATEST_TAG=$(gcloud container images list-tags ${PHP_BUILD_IMAGE} --sort-by="~timestamp" --limit=1 --format='value(tags)')
if [[ $(echo $LATEST_TAG | grep -c ",") -gt 0 ]]; then LATEST_TAG=$(echo $LATEST_TAG | awk -F, '{print $2}'); fi

set -x

# substitute in version and bucket info into NGINX manifest and apply it
cat ./k8s/${NGINX_IMAGE_NAME}.yml | sed 's#${IMAGE_VERSION}#'${LATEST_TAG}'#g' | sed 's#${GCP_BUCKET_NAME}#'${GCP_BUCKET_NAME}'#g' | kubectl apply -f -

# substitute in version and bucket info into PHP app manifest and apply it
cat ./k8s/${PHP_IMAGE_NAME}.yml | sed 's#${IMAGE_VERSION}#'${LATEST_TAG}'#g' | sed 's#${GCP_BUCKET_NAME}#'${GCP_BUCKET_NAME}'#g' | kubectl apply -f -
