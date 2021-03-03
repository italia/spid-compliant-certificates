#!/bin/sh

set -euo pipefail

# check input parameters

COMMON_NAME=${COMMON_NAME:=""}
if [ "X${COMMON_NAME}" == "X" ]; then
    echo "[E] COMMON_NAME must be set"
    exit 1
fi

LOCALITY_NAME=${LOCALITY_NAME:=""}
if [ "X${LOCALITY_NAME}" == "X" ]; then
    echo "[E] LOCALITY_NAME must be set"
    exit 1
fi

ORGANIZATION_IDENTIFIER=${ORGANIZATION_IDENTIFIER:=""}
if [ "X${ORGANIZATION_IDENTIFIER}" == "X" ]; then
    echo "[E] ORGANIZATION_IDENTIFIER must be set"
    exit 1
fi

if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -c '^PA:IT-') -ne 1 ]; then
    echo "[E] ORGANIZATION_IDENTIFIER must be in the format of 'PA:IT-<IPA code>'"
    exit 1
fi

ORGANIZATION_NAME=${ORGANIZATION_NAME:=""}
if [ "X${ORGANIZATION_NAME}" == "X" ]; then
    echo "[E] ORGANIZATION_NAME must be set"
    exit 1
fi

ENTITY_ID=${ENTITY_ID:=""}
if [ "X${ENTITY_ID}" == "X" ]; then
    echo "[E] ENTITY_ID must be set"
    exit 1
fi

SPID_SECTOR=${SPID_SECTOR:=""}
if [ "X${SPID_SECTOR}" == "X" ]; then
    echo "[E] SPID_SECTOR must be set"
    exit 1
fi

case ${SPID_SECTOR} in
    public)
        gencert-public
        ;;
    private)
        echo "[W] To be implemented"
        ;;
    *)
    echo "[E] SPID_SECTOR must be one of ['public', 'private']"
    exit 1
        ;;
esac
