#!/bin/sh

CERT_FILE=${CERT_FILE:="$(pwd)/generated-certs/crt.pem"}
CERT_FILE_MOUNT_POINT="/run/spid-complaint-certificates-validator/crt.pem"

set -e

echo "### Starting validation of certificate file at '${CERT_FILE}':\n"
cat $CERT_FILE
echo ""

docker build --tag psmiraglia/spid-compliant-certificates-validator validator/
docker run -it --rm -v "${CERT_FILE}:${CERT_FILE_MOUNT_POINT}:ro" -e CERT_FILE="${CERT_FILE_MOUNT_POINT}" psmiraglia/spid-compliant-certificates-validator
