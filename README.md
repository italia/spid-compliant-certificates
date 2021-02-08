# SPID Compliant Certificate

The repository contains a solution to create X.509 certificates according to
[Avviso SPID n.29](https://www.agid.gov.it/sites/default/files/repository_files/spid-avviso-n29-specifiche_sp_pubblici_e_privati.pdf).

**NOTE:** The solution is provided "AS-IS" and does not represent an official
implementation from Agenzia per l'Italia Digitale.

## Self-signed certificate for public sector (with Docker)

1.  Build the Docker image

        $ docker build --tag psmiraglia/spid-compliant-certificates .

2.  Run the following command to configure the environment according to your
    needs

        $ cat > my.env <<EOF
        COMMON_NAME=Comune di Roma
        DAYS=3650
        LOCALITY_NAME=Roma
        ORGANIZATION_IDENTIFIER=PA:IT-c_h501
        ORGANIZATION_NAME=Comune di Roma
        SPID_SECTOR=public
        URI=https://spid.comune.roma.it
        EOF

3.  Create a directory where new certificate(s) will be stored

        $ mkdir /tmp/mycert

4.  Run the container as in the following

        $ docker run -ti --rm \
            --env-file my.env \
            -v "/tmp/mycert:/spid-certificate" \
            psmiraglia/spid-compliant-certificates

5.  Enjoy with your new self-signed certificate

        $ ls /tmp/mycert
        crt.pem  csr.pem  key.pem

    NOTE: The container generates also a certificate signing request (`csr.pem`)
    that can be submitted to AgID in order to obtain a signed certificate.

## Self-signed certificate for public sector

1.  Run the following commands to configure the environment according to your
    needs

        $ cat > myenv.sh <<EOF
        export COMMON_NAME="Comune di Roma"
        export DAYS="3650"
        export LOCALITY_NAME="Roma"
        export ORGANIZATION_IDENTIFIER="PA:IT-c_h501"
        export ORGANIZATION_NAME="Comune di Roma"
        export SPID_SECTOR="public"
        export URI="https://spid.comune.roma.it"
        EOF
        $ chmod +x myenv.sh && source myenv.sh

2.  Generate the private key (`key.pem`), the self-signed certificate (`crt.pem`)
    and the certificate signing request (`csr.pem`) with the following command

        $ ./gencert-public.sh

    The output produced by the script (see the ASN.1 dumps) allows to check
    if the specifications were honoured.
