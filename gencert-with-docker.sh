#!/bin/sh

ENV_FILE="`pwd`/docker.env"
OUTPUT_DIR="`pwd`/generated-certs"

if [ ! -f ${ENV_FILE} ]; then
   echo "[E] the env file '${ENV_FILE}' with the configuration for generating certificates doesn't exists"
   exit 1
fi

if [ ! -d ${OUTPUT_DIR} ]; then
   echo "[E] the output directory for certificates '${OUTPUT_DIR}' doesn't exists"
   exit 1
fi

docker build --tag psmiraglia/spid-compliant-certificates .
docker run -it --rm --env-file "${ENV_FILE}" -v "${OUTPUT_DIR}:/output" psmiraglia/spid-compliant-certificates
