# SPID Compliant Certificate

The repository contains a solution to create X.509 certificates according to
[Avviso SPID n.29 v3](https://www.agid.gov.it/sites/default/files/repository_files/spid-avviso-n29v3-specifiche_sp_pubblici_e_privati_0.pdf).

**NOTE:** The solution is provided "AS-IS" and does not represent an official
implementation from Agenzia per l'Italia Digitale.

## Private key, CSR and Self-signed certificate for public sector (with Docker)

1.  Build the Docker image

        $ docker build --tag psmiraglia/spid-compliant-certificates .

2.  Run the following command to configure the environment according to your
    needs

        $ cat > my.env <<EOF
        COMMON_NAME=Comune di Roma
        DAYS=3650
        ENTITY_ID=https://spid.comune.roma.it
        KEY_LEN=3072
        LOCALITY_NAME=Roma
        MD_ALG=sha512
        ORGANIZATION_IDENTIFIER=PA:IT-c_h501
        ORGANIZATION_NAME=Comune di Roma
        SPID_SECTOR=public
        EOF

3.  Create a directory where new certificate(s) will be stored

        $ mkdir /tmp/mycert

4.  Run the container as in the following

        $ docker run -ti --rm \
            --env-file my.env \
            -v "/tmp/mycert:/output" \
            psmiraglia/spid-compliant-certificates

5.  Enjoy with your new self-signed certificate

        $ ls /tmp/mycert
        crt.pem  csr.pem  key.pem

    NOTE: The container generates also a certificate signing request (`csr.pem`)
    that can be submitted to AgID in order to obtain a signed certificate.

## Private key, CSR and Self-signed certificate for public sector

1.  Run the following commands to configure the environment according to your
    needs

        $ cat > myenv.sh <<EOF
        export COMMON_NAME="Comune di Roma"
        export DAYS="3650"
        export ENTITY_ID="https://spid.comune.roma.it"
        export KEY_LEN="3072"
        export LOCALITY_NAME="Roma"
        export MD_ALG="sha512"
        export ORGANIZATION_IDENTIFIER="PA:IT-c_h501"
        export ORGANIZATION_NAME="Comune di Roma"
        EOF
        $ chmod +x myenv.sh && source myenv.sh

2.  Generate the private key (`key.pem`), the self-signed certificate (`crt.pem`)
    and the certificate signing request (`csr.pem`) with the following command

        $ ./gencert-public.sh

    The output produced by the script (see the ASN.1 dumps) allows to check
    if the specifications were honoured.

## Private key and CSR for private sector (with Docker)

1.  Build the Docker image

        $ docker build --tag psmiraglia/spid-compliant-certificates .

2.  Run the following command to configure the environment according to your
    needs

        $ cat > my.env <<EOF
        COMMON_NAME=Comune di Roma
        ENTITY_ID=https://spid.comune.roma.it
        KEY_LEN=3072
        LOCALITY_NAME=Roma
        MD_ALG=sha256
        ORGANIZATION_IDENTIFIER="VATIT-02438750586"
        ORGANIZATION_NAME=Comune di Roma
        SPID_SECTOR=private
        EOF

3.  Create a directory where the new private key and CSR will be stored

        $ mkdir /tmp/mycert

4.  Run the container as in the following

        $ docker run -ti --rm \
            --env-file my.env \
            -v "/tmp/mycert:/output" \
            psmiraglia/spid-compliant-certificates

5.  Enjoy with your new private key and CSR

        $ ls /tmp/mycert
        csr.pem  key.pem

## Private key and CSR for private sector

1.  Run the following commands to configure the environment according to your
    needs

        $ cat > myenv.sh <<EOF
        export COMMON_NAME="Comune di Roma"
        export ENTITY_ID="https://spid.comune.roma.it"
        export KEY_LEN="3072"
        export LOCALITY_NAME="Roma"
        export MD_ALG="sha256"
        export ORGANIZATION_IDENTIFIER="VATIT-02438750586"
        export ORGANIZATION_NAME="Comune di Roma"
        EOF
        $ chmod +x myenv.sh && source myenv.sh

2.  Generate the private key (`key.pem`) and the certificate signing request
    (`csr.pem`) with the following command

        $ ./gencert-private.sh

## Configuration parameters

This section documents the configuration parameters that can be set as
environment variable.

### Commons

*   `COMMON_NAME`: short name of the service provider (example: `AgID`, default: `""`)
*   `ENTITY_ID`: value of the `entityID` attribute in `<EntityDescriptor>` element (default: `""`)
*   `KEY_LEN`: length of the private key (default: `"2048"`)
*   `LOCALITY_NAME`: extended name of the locality (example: `Roma`, default: `""`)
*   `MD_ALG`: digest algorithm to be used (default: `"sha256"`)
*   `ORGANIZATION_NAME`: extended name of the service provider (example: `Agenzia per l'Italia Digitale`, default: `""`)

### Public sector specific

*   `DAYS`: validity of the self-signed certificate (default: `730`)
*   `ORGANIZATION_IDENTIFIER`: service provider identifier in the form of `PA:IT-<IPA Code>` (example: `PA:IT-c_h501`, default: `""`)

### Private sector specific

*   `ORGANIZATION_IDENTIFIER`: service provider identifier in the form of `VATIT-<partita iva>` or `CF:IT-<codice fiscale>` (default: `""`)
