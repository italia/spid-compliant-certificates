# SPID Compliant Certificate

The repository contains a solution to create X.509 certificates according to
[Avviso SPID n.29 v3](https://www.agid.gov.it/sites/default/files/repository_files/spid-avviso-n29v3-specifiche_sp_pubblici_e_privati_0.pdf).

**NOTE:** The solution is provided "AS-IS" and does not represent an official
implementation from Agenzia per l'Italia Digitale.

## Private key, CSR and Self-signed certificate for public sector (with Docker)

1.  Copy the file `gencert-env.public.example.sh` into `gencert-env.sh` and edit it according to your
    needs, following the rules in the bottom section **Configuration parameters**

3.  Run the script `gencert-with-docker.sh`

3.  Enjoy with your new self-signed certificate

        $ ls ./generated-certs/
        crt.pem  csr.pem  key.pem

    NOTE: This generates also a certificate signing request (`csr.pem`)
    that can be submitted to AgID in order to obtain a signed certificate.

## Private key, CSR and Self-signed certificate for public sector

1.  Run the following commands to configure the environment according to your
    needs

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

2.  Generate the private key (`key.pem`), the self-signed certificate (`crt.pem`)
    and the certificate signing request (`csr.pem`) with the following command

        $ ./gencert-public.sh

    The output produced by the script (see the ASN.1 dumps) allows to check
    if the specifications were honoured.

## Private key and CSR for private sector (with Docker)

1.  Copy the file `gencert-env.private.example.sh` into `gencert-env.sh` and edit it according to your
    needs, following the rules in the bottom section **Configuration parameters**

3.  Run the script `gencert-with-docker.sh`

3.  Enjoy with your new private key and CSR

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

        $ ./gencert-private.sh

## Validate generated certificate (with Docker)

  if you want to check the generated certificate file (default: `generated-certs/crt.pem`)
  you need only to launch the script `validate-crt-with-docker.sh` and check the output in the console.

  if you want to change the certificate file to validate, just change the env variable `CERT_FILE` inside
  `validate-crt-with-docker.sh` and launch the script.

  NOTE: the first execution takes some time, because the docker image needs to compile
  the python package `cryptography` from source; after that, every other execution is immediate.

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
