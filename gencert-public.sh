#!/usr/bin/env bash

# Copyright 2021 Paolo Smiraglia <paolo.smiraglia@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# DESC: Usage help
# ARGS: None
# OUTS: None
function script_usage() {
    cat << EOF
create X.509 certificates according to Avviso SPID n.29 v3.

Usage:
  -h|--help               # Displays this help
  -i|--interactive        # asks for options from console when is not set with envirement

Enviroments:
  COMMON_NAME		  # string,  example "Comune di Roma"
  DAYS			  # integer, example "3650"
  ENTITY_ID		  # string,  example "https://spid.comune.roma.it/metadata"
  LOCALITY_NAME		  # string,  example "Roma"
  ORGANIZATION_IDENTIFIER # string,  example "PA:IT-c_h501"
  ORGANIZATION_NAME       # string,  example "Comune di Roma"
  MD_ALG		  # must be one of [sha256, sha512],   default: "sha512"
  KEY_LEN		  # must be one of [2048, 3072, 4096], default: "3072"
EOF
}

# DESC: Parameter parser
# ARGS: $@ (optional): Arguments provided to the script
# OUTS: Variables indicating command-line parameters and options
function parse_params() {
    local param
    while [[ $# -gt 0 ]]; do
        param="$1"
        shift
        case $param in
            -h | --help)
                script_usage
                exit 0
                ;;
            -i | --interactive)
                INTERACTIVE=true
                ;;
            *)
                die "Invalid parameter was provided: $param" 1
                ;;
        esac
    done
}

# DESC: Exit script with the given message
# ARGS: $1 (required): Message to print on exit
#       $2 (optional): Exit code (defaults to 1)
# OUTS: None
# NOTE: The convention used in this script for exit codes is:
#       0: Normal exit
#       1: Abnormal exit due to external error
#       2: Abnormal exit due to script error
die() {
  local msg=${1}
  local code=${2-1} # default exit status 1
  echo $msg
  exit $code
}

parse_params "$@"

crt="crt.pem"
csr="csr.pem"
key="key.pem"

### check input parameters

# check KEY_LEN
KEY_LEN=${KEY_LEN:="3072"}
if [ $(echo ${KEY_LEN} | grep -c -P "^(2048|3072|4096)$") -ne 1 ]; then
    die "[E] KEY_LEN must be one of [2048, 3072, 4096], now ${KEY_LEN}"
fi

# check MD_ALG
MD_ALG=${MD_ALG:="sha512"}
if [ $(echo ${MD_ALG} | grep -c -P "^(sha256|sha512)$") -ne 1 ]; then
    die "[E] MD_ALG must be one of [sha256, sha512], now ${MD_ALG}"
fi

# check COMMON_NAME
if [[ -z $COMMON_NAME && -n $INTERACTIVE ]]; then
  read -p 'COMMON_NAME: ' COMMON_NAME
fi
if [ $(echo ${COMMON_NAME} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    die "[E] COMMON_NAME must be set"
fi

# check LOCALITY_NAME
if [[ -z $LOCALITY_NAME && -n $INTERACTIVE ]]; then
  read -p 'LOCALITY_NAME: ' LOCALITY_NAME
fi
if [ $(echo ${LOCALITY_NAME} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    die "[E] LOCALITY_NAME must be set"
fi

# check ORGANIZATION_IDENTIFIER
if [[ -z $ORGANIZATION_IDENTIFIER && -n $INTERACTIVE ]]; then
  read -p 'ORGANIZATION_IDENTIFIER: ' ORGANIZATION_IDENTIFIER
fi
if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    die "[E] ORGANIZATION_IDENTIFIER must be set"
fi
if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -c '^PA:IT-') -ne 1 ]; then
    die "[E] ORGANIZATION_IDENTIFIER must be in the format of 'PA:IT-<IPA code>'"
fi
IPA_CODE=$(echo ${ORGANIZATION_IDENTIFIER} | sed -e "s/PA:IT-//g")
JSON1='{"paginazione":{"campoOrdinamento":"codAoo","tipoOrdinamento":"asc","paginaRichiesta":1,"numTotalePagine":null,"numeroRigheTotali":null,"paginaCorrente":null,"righePerPagina":null},"codiceFiscale":null,"codUniAoo":null,"desAoo":null,"denominazioneEnte":null,"codEnte":"'
JSON2='","codiceCategoria":null,"area":null}'
JSON="${JSON1}${IPA_CODE}${JSON2}"
if curl -X POST https://indicepa.gov.it/PortaleServices/api/aoo -H "Content-Type: application/json" -d ${JSON} | grep -qv '"numeroRigheTotali":1'; then
    die "[E] ORGANIZATION_IDENTIFIER refers to something that does not exists \n [I] Check it by yourself at ${CHECK_URL}"
fi

# check ORGANIZATION_NAME
if [[ -z $ORGANIZATION_NAME && -n $INTERACTIVE ]]; then
  read -p 'ORGANIZATION_NAME: ' ORGANIZATION_NAME
fi
if [ $(echo ${ORGANIZATION_NAME} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    die "[E] ORGANIZATION_NAME must be set"
fi

# check ENTITY_ID
if [[ -z $ENTITY_ID && -n $INTERACTIVE ]]; then
  read -p 'ENTITY_ID: ' ENTITY_ID
fi
if [ $(echo ${ENTITY_ID} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    die "[E] ENTITY_ID must be set"
fi

# generate configuration file

openssl_conf=$(mktemp)

if [ $(openssl version | grep -c "OpenSSL 1.0") -ge 1 ]; then
    ORGID_OID="organizationIdentifier=2.5.4.97"
    ORGID_LABEL="2.5.4.97 organizationIdentifier organizationIdentifier"
else
    ORGID_OID=""
    ORGID_LABEL=""
fi

cat > ${openssl_conf} <<EOF
oid_section=spid_oids

[ req ]
default_bits=${KEY_LEN}
default_md=${MD_ALG}
distinguished_name=dn
encrypt_key=no
prompt=no
req_extensions=req_ext

[ spid_oids ]
agidcert=1.3.76.16.6
spid-publicsector-SP=1.3.76.16.4.2.1
uri=2.5.4.83
${ORGID_OID}

[ dn ]
commonName=${COMMON_NAME}
countryName=IT
localityName=${LOCALITY_NAME}
organizationIdentifier=${ORGANIZATION_IDENTIFIER}
organizationName=${ORGANIZATION_NAME}
uri=${ENTITY_ID}

[ req_ext ]
basicConstraints=CA:FALSE
keyUsage=critical,digitalSignature,nonRepudiation
certificatePolicies=@agid_policies,@spid_policies

[ agid_policies ]
policyIdentifier=agidcert
userNotice=@agidcert_notice

[ agidcert_notice ]
explicitText="agIDcert"

[ spid_policies ]
policyIdentifier=spid-publicsector-SP
userNotice=@spid_notice

[ spid_notice ]
explicitText="cert_SP_Pub"
EOF

cat <<EOF
## --------------------------------------------------------------------------
## Generated OpenSSL configuration
## --------------------------------------------------------------------------

$(cat ${openssl_conf})

EOF

# generate selfsigned certificate

openssl req -new -x509 -config ${openssl_conf} \
    -days ${DAYS:=730} \
    -keyout ${key} -out ${crt} \
    -extensions req_ext 2>/dev/null

cat <<EOF
## --------------------------------------------------------------------------
## Text dump of the self-signed certificate
## --------------------------------------------------------------------------

$(openssl x509 -noout -text -in ${crt})

EOF

# generate certificate signing request

openssl req \
    -config ${openssl_conf} \
    -key ${key} \
    -new -out ${csr} 2>/dev/null

cat <<EOF
## --------------------------------------------------------------------------
## Text dump of the certificate signing request
## --------------------------------------------------------------------------

$(openssl req -in ${csr} -noout -text)

EOF

# configure labels for new OIDs

oids_conf=$(mktemp)
cat > ${oids_conf} <<EOF
1.3.76.16.6 agIDcert agIDcert
1.3.76.16.4.2.1 spid-publicsector-SP spid-publicsector-SP
2.5.4.83 uri uri
${ORGID_LABEL}
EOF

cat <<EOF
## --------------------------------------------------------------------------
## Generated OID configuration
## --------------------------------------------------------------------------

$(cat ${oids_conf})

EOF

# dump (ASN.1) the certificate

cat <<EOF
## --------------------------------------------------------------------------
## ASN.1 dump of the self-signed certificate
## --------------------------------------------------------------------------

$(openssl asn1parse -inform PEM -oid ${oids_conf} -i -in ${crt})

EOF

offset=$(openssl asn1parse -inform PEM -oid ${oids_conf} -i -in ${crt} | grep "X509v3 Certificate Policies" -A1 | tail -1 | cut -d':' -f1 | sed 's/^[ \t]*//')
cat <<EOF
## --------------------------------------------------------------------------
## ASN.1 dump for CertificatePolicies section
## --------------------------------------------------------------------------

$(openssl asn1parse -inform PEM -oid ${oids_conf} -i -in ${crt} -strparse ${offset})

EOF

# cleanup

rm -fr ${openssl_conf} ${oids_conf}

# vim: syntax=sh cc=80 tw=79 ts=4 sw=4 sts=4 et sr
