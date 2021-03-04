#!/bin/bash

set -euo pipefail

# check input parameters

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
        gencert-private
        ;;
    *)
    echo "[E] SPID_SECTOR must be one of ['public', 'private']"
    exit 1
        ;;
esac
