#!/bin/sh

csr="csr.csr"
key="key.pem"

# check organizationIdentifier valid value (VATID-XXX... or CF:IT-XXX..)

if [ $(echo ${ORGANIZATION_IDENTIFIER} | grep -c -P "^(CF:IT-[\d\w]{16}|VATIT-\d{11})$") -ne 1 ]; then  
    echo "[E] ORGANIZATION_IDENTIFIER must be a valid Partita Iva or Codice Fiscale"
    exit 1
fi

KEY_LEN=${KEY_LEN:="2048"}
if [ $(echo ${KEY_LEN} | grep -c -P "^(2048|3072|4096)$") -ne 1 ]; then
    echo "[E] KEY_LEN must be one of [2048, 3072, 4096], now ${KEY_LEN}"
    exit 1
fi

MD_ALG=${MD_ALG:="sha256"}
if [ $(echo ${MD_ALG} | grep -c -P "^(sha256|sha512)$") -ne 1 ]; then
    echo "[E] MD_ALG must be one of [sha256, sha512], now ${MD_ALG}"
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

cat > "${openssl_conf}" <<EOF
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
spid-privatesector-SP=1.3.76.16.4.3.1
uri=2.5.4.83
${ORGID_OID}

[ dn ]
commonName=${ENTITY_ID}
countryName=IT
localityName=${LOCALITY_NAME}
organizationIdentifier=$ORGANIZATION_IDENTIFIER
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
explicitText="cert_SP_Privati"

[ spid_policies ]
policyIdentifier=spid-privatesector-SP
userNotice=@spid_notice

[ spid_notice ]
explicitText="Service Provider SPID Privato"
EOF

cat <<EOF
## --------------------------------------------------------------------------
## Generated OpenSSL configuration
## --------------------------------------------------------------------------
$(cat ${openssl_conf})
EOF

## --------------------------------------------------------------------------
## Generate certificate private key and signing request
## --------------------------------------------------------------------------

openssl req -config ${openssl_conf} -new \
	-keyout ${key} \
	-out ${csr} 
	-extensions req_ext 2>/dev/null

cat <<EOF
## --------------------------------------------------------------------------
## Text dump of the certificate signing request
## --------------------------------------------------------------------------
$(openssl req -in ${csr} -noout -text)
EOF

# configure labels for new OIDs

oids_conf=oids.conf
cat > ${oids_conf} <<EOF
1.3.76.16 agid Agenzia per l'Italia Digitale
1.3.76.16.4.3.1 spid-privatesector-SP spid-privatesector-SP
2.5.4.83 uri uri
${ORGID_LABEL}
EOF

cat <<EOF
## --------------------------------------------------------------------------
## Generated OID configuration
## --------------------------------------------------------------------------
$(cat ${oids_conf})
EOF


cat <<EOF
## --------------------------------------------------------------------------
## Csr digest in sha256
## --------------------------------------------------------------------------
$(sha256sum ${csr})
EOF

# cleanup

rm -fr ${openssl_conf} ${oids_conf}
