#!/usr/bin/env bash
set -euoE pipefail

pushd "$(dirname "${BASH_SOURCE[0]}")/../terraform/" >/dev/null

terraform init -backend-config=bucket="${GCP_PROJECT_ID}"-apps-tfstate -backend-config=prefix="${APP_NAME}"

if [[ ${CI_SERVER:-} == "yes" ]]; then
    IMAGE_TAG=${IMAGE_NAME}:${CI_COMMIT_SHA}-$(echo "${CI_COMMIT_TIMESTAMP}" | sed 's/[:+]/./g')
    terraform apply -auto-approve -var gcp_project_id="${GCP_PROJECT_ID}" \
        -var app_name="${APP_NAME}" \
        -var image_tag="${IMAGE_TAG}" \
        -var region="${REGION}" \
        -var domain="${DOMAIN}" \
        -var port="${PORT}"
else
    terraform plan -var gcp_project_id="${GCP_PROJECT_ID}" \
        -var app_name="${APP_NAME}" \
        -var image_tag="${IMAGE_TAG}" \
        -var region="${REGION}" \
        -var domain="${DOMAIN}" \
        -var port="${PORT}"
fi

popd >/dev/null
