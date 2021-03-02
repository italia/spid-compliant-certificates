#!/bin/sh

# generate configuration file

openssl_conf=$(mktemp)

cat > "${openssl_conf}" <<EOF
oid_section=spid_oids

[ req ]
default_bits=2048
default_md=sha256
distinguished_name=dn
encrypt_key=no
prompt=no
req_extensions=req_ext

[ spid_oids ]
agid=1.3.76.16
spid-privatesector-SP=1.3.76.16.4.3.1
spid-publicsector-SP=1.3.76.16.4.2.1
uri=2.5.4.83

[ dn ]
commonName=${ENTITY_ID}
countryName=IT
localityName=${LOCALITY_NAME}
stateOrProvinceName=${PROVINCIE}
organizationIdentifier=VATID-${PIVA}
organizationName=${ORGANIZATION_NAME}
serialNumber=VATID-${PIVA}
uri=${ENTITY_ID}
emailAddress=${EMAIL}

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

openssl req -config ${openssl_conf} -new -newkey rsa:2048 -nodes -keyout privkey.pem -out CSR.csr -extensions req_ext 2>/dev/null

cat <<EOF
## --------------------------------------------------------------------------
## Text dump of the certificate signing request
## --------------------------------------------------------------------------
$(openssl req -in CSR.csr -noout -text)
EOF

# configure labels for new OIDs

oids_conf=oids.conf
cat > ${oids_conf} <<EOF
1.3.76.16 agid Agenzia per l'Italia Digitale
1.3.76.16.4.3.1 spid-privatesector-SP spid-privatesector-SP
2.5.4.83 uri uri
EOF

cat <<EOF
## --------------------------------------------------------------------------
## Generated OID configuration
## --------------------------------------------------------------------------
$(cat ${oids_conf})
EOF


cat <<EOF
## --------------------------------------------------------------------------
## Extract hash in sha256 from private key
## --------------------------------------------------------------------------
$(openssl rsa -noout -modulus -in privkey.pem | openssl sha256)
EOF

# cleanup

rm -fr ${openssl_conf} ${oids_conf}
