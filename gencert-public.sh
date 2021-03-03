#!/bin/sh

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
if [ -z ${COMMON_NAME} ]; then
    echo "[E] COMMON_NAME must be set"
    exit 1
fi

LOCALITY_NAME=${LOCALITY_NAME:=""}
if [ -z ${LOCALITY_NAME} ]; then
    echo "[E] LOCALITY_NAME must be set"
    exit 1
fi

ORGANIZATION_IDENTIFIER=${ORGANIZATION_IDENTIFIER:=""}
if [ -z ${ORGANIZATION_IDENTIFIER} ]; then
    echo "[E] ORGANIZATION_IDENTIFIER must be set"
    exit 1
fi

if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -c '^PA:IT-') -ne 1 ]; then
    echo "[E] ORGANIZATION_IDENTIFIER must be in the format of 'PA:IT-<IPA code>'"
    exit 1
fi

IPA_CODE=$(echo ${ORGANIZATION_IDENTIFIER} | sed -e "s/PA:IT-//g")
CHECK_URL="https://indicepa.gov.it/ricerca/n-dettaglioamministrazione.php?cod_amm=${IPA_CODE}"
if [ $(curl -s ${CHECK_URL} | grep -c ${IPA_CODE}) -lt 1 ]; then
    echo "[E] ORGANIZATION_IDENTIFIER refers to something that does not exists"
    echo "[I] Check it by yourself at ${CHECK_URL}"
    exit 1
fi

ORGANIZATION_NAME=${ORGANIZATION_NAME:=""}
if [ -z ${ORGANIZATION_NAME} ]; then
    echo "[E] ORGANIZATION_NAME must be set"
    exit 1
fi

ENTITY_ID=${ENTITY_ID:=""}
if [ -z ${ENTITY_ID} ]; then
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
agid=1.3.76.16
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
policyIdentifier=agid
userNotice=@agid_notice

[ agid_notice ]
explicitText="cert_SP_Pubblici"

[ spid_policies ]
policyIdentifier=spid-publicsector-SP
userNotice=@spid_notice

[ spid_notice ]
explicitText="Service Provider SPID Pubblico"
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
1.3.76.16 agid Agenzia per l'Italia Digitale
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
