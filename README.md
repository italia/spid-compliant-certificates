# SPID Compliant Certificate

The repository contains a solution to create X.509 certificates according to
[Avviso SPID n.29 v3](https://www.agid.gov.it/sites/default/files/repository_files/spid-avviso-n29v3-specifiche_sp_pubblici_e_privati_0.pdf).

**NOTE:** The solution is provided "AS-IS" and does not represent an official
implementation from Agenzia per l'Italia Digitale.

## Private key, CSR and self-signed certificate for public sector (with Docker)

1.  Create and edit the `docker.env` file according to your needs
    (see [Configuration parameters](#configuration-parameters))

        $ cp public.env.example docker.env
        $ editor docker.env

2.  Run the script `gencert-with-docker.sh`

        $ chmod +x gencert-with-docker.sh
        $ ./gencert-with-docker.sh

3.  Enjoy with your new private key (`key.pem`) and self-signed certificate
    (`crt.pem`)

        $ ls ./generated-certs/
        crt.pem  csr.pem  key.pem

    NOTE: This generates also a certificate signing request (`csr.pem`)
    that can be submitted to AgID in order to obtain a signed certificate.

## Private key, CSR and self-signed certificate for public sector

1.  Run the following commands to configure the environment according to your
    needs (see [Configuration parameters](#configuration-parameters))

        $ cat > myenv.sh <<EOF
        export COMMON_NAME="Comune di Roma"
        export DAYS="3650"
        export ENTITY_ID="https://spid.comune.roma.it/metadata"
        export KEY_LEN="3072"
        export LOCALITY_NAME="Roma"
        export MD_ALG="sha512"
        export ORGANIZATION_IDENTIFIER="PA:IT-c_h501"
        export ORGANIZATION_NAME="Comune di Roma"
        EOF
        $ chmod +x myenv.sh && source myenv.sh

2.  Generate the private key (`key.pem`), the self-signed certificate
    (`crt.pem`) and the certificate signing request (`csr.pem`) with the
    following command

        $ chmod +x gencert-public.sh
        $ ./gencert-public.sh

    The output produced by the script (see the ASN.1 dumps) allows to check
    if the specifications were honoured.

## Private key and CSR for private sector (with Docker)

1.  Create and edit the `docker.env` file according to your needs
    (see [Configuration parameters](#configuration-parameters))

        $ cp private.env.example docker.env
        $ editor docker.env

2.  Run the script `gencert-with-docker.sh`

        $ chmod +x gencert-with-docker.sh
        $ ./gencert-with-docker.sh

3.  Enjoy with your new private key (`key.pem`) and CSR (`csr.pem`)

        $ ls ./generated-certs/
        csr.pem  key.pem

## Private key and CSR for private sector

1.  Run the following commands to configure the environment according to your
    needs

        $ cat > myenv.sh <<EOF
        export COMMON_NAME="Comune di Roma"
        export ENTITY_ID="https://spid.comune.roma.it/metadata"
        export KEY_LEN="3072"
        export LOCALITY_NAME="Roma"
        export MD_ALG="sha256"
        export ORGANIZATION_IDENTIFIER="VATIT-02438750586"
        export ORGANIZATION_NAME="Comune di Roma"
        EOF
        $ chmod +x myenv.sh && source myenv.sh

2.  Generate the private key (`key.pem`) and the certificate signing request
    (`csr.pem`) with the following command

        $ chmod +x gencert-private.sh
        $ ./gencert-private.sh

## Validate the certificate

The following steps can be followed to verify the compliancy of certificates
generated with the tools in this repository and certificates generated/obtained
from third parties.

### With Docker

Run the script `validate-crt-with-docker.sh`

    $ chmod +x validate-crt-with-docker.sh
    $ ./validate-crt-with-docker.sh

By default, it will validate the certificate at

    generated-certs/crt.pem

Such a default path can be modified by setting the `CERT_FILE` envvar

    $ chmod +x validate-crt-with-docker.sh
    $ CERT_FILE=/path/to/your/crt.pem ./validate-crt-with-docker.sh

NOTE: The first script execution could take some time, because the Docker
image needs to be built. Following execution will be immediate.

### With command line

Install the required Python packages

    $ cd validator
    $ pip install -r requirements.txt

Run the Python tests suite

    $ ./validator.py

By default, it will validate the certificate at

    ./crt.pem

Such a default path can be modified by setting the `CERT_FILE` envvar

    $ CERT_FILE=/path/to/your/crt.pem ./validator.py

## Configuration parameters

This section documents the configuration parameters that can be set as
environment variable.

### Commons

*   `COMMON_NAME`: short name of the service provider
    (example: `AgID`, default: `""`)

*   `ENTITY_ID`: value of the `entityID` attribute in `<EntityDescriptor>`
    element
    (example: `https://spid.agid.gov.it`, default: `""`)

*   `KEY_LEN`: length of the private key
    (allowd values: `[2048, 3072, 4096]`, default: `2048`)

*   `LOCALITY_NAME`: extended name of the locality
    (example: `Roma`, default: `""`)

*   `MD_ALG`: digest algorithm to be used
    (allowed values: `[sha256, sha512], `default: `sha256`)

*   `ORGANIZATION_NAME`: extended name of the service provider
    (example: `Agenzia per l'Italia Digitale`, default: `""`)

### Public sector specific

*   `DAYS`: validity of the self-signed certificate
    (example: `3650`, default: `730`)

*   `ORGANIZATION_IDENTIFIER`: service provider identifier in the form of
    `PA:IT-<IPA Code>`
    (example: `PA:IT-c_h501`, default: `""`)

### Private sector specific

*   `ORGANIZATION_IDENTIFIER`: service provider identifier in the form of
    `VATIT-<partita iva>` or `CF:IT-<codice fiscale>`
    (example: `VATIT-12345678901`, default: `""`)
