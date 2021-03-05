#!/bin/sh

ENV_FILE="`pwd`/gencert-env.sh"
OUTPUT_DIR="`pwd`/generated-certs"

docker build --tag psmiraglia/spid-compliant-certificates .
docker run -it --rm --env-file "${ENV_FILE}" -v "${OUTPUT_DIR}:/output" psmiraglia/spid-compliant-certificates
