#!/usr/bin/env bash
set -euoE pipefail

pushd "$(dirname "${BASH_SOURCE[0]}")/../k8s/" >/dev/null


echo "-> [INFO] Applying Kubernetes yaml"

kubectl apply -f ../namespace.yaml
kustomize edit set image "${SERVICE}"="${IMAGE_TAG}"
kustomize build . | envsubst "\$GCP_PROJECT_ID \$AUTH_PROJECT_ID \$ALLOWED_USERS" | kubectl apply -n "${APP_NAME}" -f -
kubectl rollout status deploy/"${APP_NAME}"-"${SERVICE}" -n "${APP_NAME}" --timeout=300s

popd >/dev/null
