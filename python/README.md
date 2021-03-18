# spid-compliant-certificates

Python native solution to generate and validate X.509 certificates according
to Avviso SPID n.29 v3.

## Installation

Nothing more than

    $ pip install .

## Usage

Generate private key, self-signed X.509 ertificate and CSR for public sector
SPID service provider

    $ spid-compliant-certificates generator \
		--key-size 3072 \
		--common-name "A.C.M.E" \
		--days 365 \
		--entity-id https://spid.acme.it \
		--locality-name Roma \
		--org-id "PA:IT-c_h501" \
		--org-name "A Company Making Everything" \
		--sector public
    [D] Starting new HTTPS connection (1): indicepa.gov.it:443
    [D] https://indicepa.gov.it:443 "GET /ricerca/n-dettaglioamministrazione.php?cod_amm=c_h501 HTTP/1.1" 200 23778
    [I] Private key saved to key.pem
    [I]   Inspect with OpenSSL: openssl rsa -in key.pem -noout -text
    [I] CSR saved to csr.pem
    [I]   Inspect with OpenSSL: openssl req -in csr.pem -noout -text
    [I]   Inspect with OpenSSL: openssl asn1parse -i -inform PEM -in csr.pem
    [I] Self-signed certificate saved to crt.pem
    [I]   Inspect with OpenSSL: openssl x509 -noout -text -in crt.pem
    [I]   Inspect with OpenSSL: openssl asn1parse -i -inform PEM -in crt.pem

Validate the self-signed X.509 certificate

    $ spid-compliant-certificates validator --sector public
    [I] Validating certificate crt.pem against public sector specifications
    [I] Checking the key type and size: success
    [I] Checking the signature digest algorithm: success
    [I] Checking the SubjectDN: success
    [I] Checking basicConstraints x509 extension: success
    [I] Checking keyUsage x509 extension: success
    [I] Checking certificatePolicies x509 extension: success

Generate private key and CSR for private sector SPID service provider

    $ spid-compliant-certificates generator \
		--key-size 3072 \
		--common-name "A.C.M.E" \
		--days 365 \
		--entity-id https://spid.acme.it \
		--locality-name Roma \
        --org-id "VATIT-12345678901" \
		--org-name "A Company Making Everything" \
		--sector private
    [I] Private key saved to key.pem
    [I]   Inspect with OpenSSL: openssl rsa -in key.pem -noout -text
    [I] CSR saved to csr.pem
    [I]   Inspect with OpenSSL: openssl req -in csr.pem -noout -text
    [I]   Inspect with OpenSSL: openssl asn1parse -i -inform PEM -in csr.pem

Are you looking for further info?

    $ spid-compliant-certificates --help
    $ spid-compliant-certificates generator --help
    $ spid-compliant-certificates validator --help
