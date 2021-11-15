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


crt="crt.pem"
csr="csr.pem"
key="key.pem"

# check input parameters

KEY_LEN=${KEY_LEN:="3072"}
if [ $(echo ${KEY_LEN} | grep -c -P "^(2048|3072|4096)$") -ne 1 ]; then
    echo "[E] KEY_LEN must be one of [2048, 3072, 4096], now ${KEY_LEN}"
    exit 1
fi

MD_ALG=${MD_ALG:="sha256"}
if [ $(echo ${MD_ALG} | grep -c -P "^(sha256|sha512)$") -ne 1 ]; then
    echo "[E] MD_ALG must be one of [sha256, sha512], now ${MD_ALG}"
    exit 1
fi

COMMON_NAME=${COMMON_NAME:=""}
if [ $(echo ${COMMON_NAME} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    echo "[E] COMMON_NAME must be set"
    exit 1
fi

LOCALITY_NAME=${LOCALITY_NAME:=""}
if [ $(echo ${LOCALITY_NAME} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    echo "[E] LOCALITY_NAME must be set"
    exit 1
fi

ORGANIZATION_IDENTIFIER=${ORGANIZATION_IDENTIFIER:=""}
if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    echo "[E] ORGANIZATION_IDENTIFIER must be set"
    exit 1
fi

if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -c '^PA:IT-') -ne 1 ]; then
    echo "[E] ORGANIZATION_IDENTIFIER must be in the format of 'PA:IT-<IPA code>'"
    exit 1
fi

IPA_CODE=$(echo ${ORGANIZATION_IDENTIFIER} | sed -e "s/PA:IT-//g")

JSON1='{"paginazione":{"campoOrdinamento":"codAoo","tipoOrdinamento":"asc","paginaRichiesta":1,"numTotalePagine":null,"numeroRigheTotali":null,"paginaCorrente":null,"righePerPagina":null},"codiceFiscale":null,"codUniAoo":null,"desAoo":null,"denominazioneEnte":null,"codEnte":"'
JSON2='","codiceCategoria":null,"area":null}'
JSON="${JSON1}${IPA_CODE}${JSON2}"
echo $JSON
if curl -X POST https://indicepa.gov.it/PortaleServices/api/aoo -H "Content-Type: application/json" -d ${JSON} | grep -qv '"numeroRigheTotali":1'; then
    echo "[E] ORGANIZATION_IDENTIFIER refers to something that does not exists"
    echo "[I] Check it by yourself at ${CHECK_URL}"
    exit 1
fi

ORGANIZATION_NAME=${ORGANIZATION_NAME:=""}
if [ $(echo ${ORGANIZATION_NAME} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    echo "[E] ORGANIZATION_NAME must be set"
    exit 1
fi

ENTITY_ID=${ENTITY_ID:=""}
if [ $(echo ${ENTITY_ID} | grep -Pc "^\S(.*\S)?$") -ne 1 ]; then
    echo "[E] ENTITY_ID must be set"
    exit 1
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
