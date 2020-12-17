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
        LOCALITY_NAME=Roma
        ORGANIZATION_IDENTIFIER=PA:IT-c_h501
        ORGANIZATION_NAME=Comune di Roma
        SERIAL_NUMBER=1234567890
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
        cert.pem  privkey.pem

## Self-signed certificate for public sector

1.  Create your configuration file from the template

        $ cp spid_public.conf.example spid_public.conf

    then, according to your needs,  customise the values for `commonName`,
    `countryName`, `localityName`, `organizationIdentifier`, `organizationName`,
    `serialNumber` and `uri`.

2.  Generate the self-signed certificate

        $ openssl req -new -x509 -config spid_public.conf -days 730 \
            -keyout privkey.pem -out cert.pem -extensions req_ext

3.  Verify if the certificate honours the specifications

        $ openssl asn1parse -inform PEM -oid oids.conf -i -in cert.pem

    You should see something like that

            0:d=0  hl=4 l=1240 cons: SEQUENCE          
            4:d=1  hl=4 l= 832 cons:  SEQUENCE          
            8:d=2  hl=2 l=   3 cons:   cont [ 0 ]        
           10:d=3  hl=2 l=   1 prim:    INTEGER           :02
           13:d=2  hl=2 l=   9 prim:   INTEGER           :AA3271D8002CD344
           24:d=2  hl=2 l=  13 cons:   SEQUENCE          
           26:d=3  hl=2 l=   9 prim:    OBJECT            :sha384WithRSAEncryption
           37:d=3  hl=2 l=   0 prim:    NULL              
           39:d=2  hl=3 l= 158 cons:   SEQUENCE          
           42:d=3  hl=2 l=  23 cons:    SET               
           44:d=4  hl=2 l=  21 cons:     SEQUENCE          
           46:d=5  hl=2 l=   3 prim:      OBJECT            :commonName
           51:d=5  hl=2 l=  14 prim:      UTF8STRING        :Comune di Roma
           67:d=3  hl=2 l=  11 cons:    SET               
           69:d=4  hl=2 l=   9 cons:     SEQUENCE          
           71:d=5  hl=2 l=   3 prim:      OBJECT            :countryName
           76:d=5  hl=2 l=   2 prim:      PRINTABLESTRING   :IT
           80:d=3  hl=2 l=  13 cons:    SET               
           82:d=4  hl=2 l=  11 cons:     SEQUENCE          
           84:d=5  hl=2 l=   3 prim:      OBJECT            :localityName
           89:d=5  hl=2 l=   4 prim:      UTF8STRING        :Roma
           95:d=3  hl=2 l=  21 cons:    SET               
           97:d=4  hl=2 l=  19 cons:     SEQUENCE          
           99:d=5  hl=2 l=   3 prim:      OBJECT            :organizationIdentifier
          104:d=5  hl=2 l=  12 prim:      UTF8STRING        :PA:IT-c_h501
          118:d=3  hl=2 l=  23 cons:    SET               
          120:d=4  hl=2 l=  21 cons:     SEQUENCE          
          122:d=5  hl=2 l=   3 prim:      OBJECT            :organizationName
          127:d=5  hl=2 l=  14 prim:      UTF8STRING        :Comune di Roma
          143:d=3  hl=2 l=  17 cons:    SET               
          145:d=4  hl=2 l=  15 cons:     SEQUENCE          
          147:d=5  hl=2 l=   3 prim:      OBJECT            :serialNumber
          152:d=5  hl=2 l=   8 prim:      PRINTABLESTRING   :12345678
          162:d=3  hl=2 l=  36 cons:    SET               
          164:d=4  hl=2 l=  34 cons:     SEQUENCE          
          166:d=5  hl=2 l=   3 prim:      OBJECT            :uri
          171:d=5  hl=2 l=  27 prim:      UTF8STRING        :https://spid.comune.roma.it
          200:d=2  hl=2 l=  30 cons:   SEQUENCE          
          202:d=3  hl=2 l=  13 prim:    UTCTIME           :201201182009Z
          217:d=3  hl=2 l=  13 prim:    UTCTIME           :201231182009Z
          232:d=2  hl=3 l= 158 cons:   SEQUENCE          
          235:d=3  hl=2 l=  23 cons:    SET               
          237:d=4  hl=2 l=  21 cons:     SEQUENCE          
          239:d=5  hl=2 l=   3 prim:      OBJECT            :commonName
          244:d=5  hl=2 l=  14 prim:      UTF8STRING        :Comune di Roma
          260:d=3  hl=2 l=  11 cons:    SET               
          262:d=4  hl=2 l=   9 cons:     SEQUENCE          
          264:d=5  hl=2 l=   3 prim:      OBJECT            :countryName
          269:d=5  hl=2 l=   2 prim:      PRINTABLESTRING   :IT
          273:d=3  hl=2 l=  13 cons:    SET               
          275:d=4  hl=2 l=  11 cons:     SEQUENCE          
          277:d=5  hl=2 l=   3 prim:      OBJECT            :localityName
          282:d=5  hl=2 l=   4 prim:      UTF8STRING        :Roma
          288:d=3  hl=2 l=  21 cons:    SET               
          290:d=4  hl=2 l=  19 cons:     SEQUENCE          
          292:d=5  hl=2 l=   3 prim:      OBJECT            :organizationIdentifier
          297:d=5  hl=2 l=  12 prim:      UTF8STRING        :PA:IT-c_h501
          311:d=3  hl=2 l=  23 cons:    SET               
          313:d=4  hl=2 l=  21 cons:     SEQUENCE          
          315:d=5  hl=2 l=   3 prim:      OBJECT            :organizationName
          320:d=5  hl=2 l=  14 prim:      UTF8STRING        :Comune di Roma
          336:d=3  hl=2 l=  17 cons:    SET               
          338:d=4  hl=2 l=  15 cons:     SEQUENCE          
          340:d=5  hl=2 l=   3 prim:      OBJECT            :serialNumber
          345:d=5  hl=2 l=   8 prim:      PRINTABLESTRING   :12345678
          355:d=3  hl=2 l=  36 cons:    SET               
          357:d=4  hl=2 l=  34 cons:     SEQUENCE          
          359:d=5  hl=2 l=   3 prim:      OBJECT            :uri
          364:d=5  hl=2 l=  27 prim:      UTF8STRING        :https://spid.comune.roma.it
          393:d=2  hl=4 l= 418 cons:   SEQUENCE          
          397:d=3  hl=2 l=  13 cons:    SEQUENCE          
          399:d=4  hl=2 l=   9 prim:     OBJECT            :rsaEncryption
          410:d=4  hl=2 l=   0 prim:     NULL              
          412:d=3  hl=4 l= 399 prim:    BIT STRING        
          815:d=2  hl=2 l=  23 cons:   cont [ 3 ]        
          817:d=3  hl=2 l=  21 cons:    SEQUENCE          
          819:d=4  hl=2 l=  19 cons:     SEQUENCE          
          821:d=5  hl=2 l=   3 prim:      OBJECT            :X509v3 Certificate Policies
          826:d=5  hl=2 l=  12 prim:      OCTET STRING      [HEX DUMP]:300A300806062B4C10040201
          840:d=1  hl=2 l=  13 cons:  SEQUENCE          
          842:d=2  hl=2 l=   9 prim:   OBJECT            :sha384WithRSAEncryption
          853:d=2  hl=2 l=   0 prim:   NULL              
          855:d=1  hl=4 l= 385 prim:  BIT STRING

    To check the `CertificatePolicies`, get the right offset from the previous output

        [...]
          821:d=5  hl=2 l=   3 prim:      OBJECT            :X509v3 Certificate Policies
          826:d=5  hl=2 l=  12 prim:      OCTET STRING      [HEX DUMP]:300A300806062B4C10040201
          ^^^
        [...]

    then run the following command
 
        $ openssl asn1parse -inform PEM -oid oids.conf -i -in cert.pem -strparse 826

    You should see something like that

            0:d=0  hl=2 l=  10 cons: SEQUENCE          
            2:d=1  hl=2 l=   8 cons:  SEQUENCE          
            4:d=2  hl=2 l=   6 prim:   OBJECT            :spid-publicsector-SP
