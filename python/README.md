# spid-compliant-certificates

```
usage: spid-compliant-certificates [-h] [--sector {private,public}]
                                   [--md-alg {sha256,sha512}]
                                   [--key-size {2048,3072,4096}]
                                   [--key-out KEY_OUT] [--csr-out CSR_OUT]
                                   [--crt-out CRT_OUT] --common-name
                                   COMMON_NAME --days DAYS --entity-id
                                   ENTITY_ID --locality-name LOCALITY_NAME
                                   --org-id ORG_ID --org-name ORG_NAME

optional arguments:
  -h, --help            show this help message and exit
  --sector {private,public}
                        select the specifications to be followed (default:
                        public)
  --md-alg {sha256,sha512}
                        digest algorithm (default: sha256)
  --key-size {2048,3072,4096}
                        size of the private key (default: 2048)
  --key-out KEY_OUT     path where the private key will be stored (default:
                        key.pem)
  --csr-out CSR_OUT     path where the csr will be stored (default: csr.pem)
  --crt-out CRT_OUT     path where the self-signed certificate will be stored
                        (default: crt.pem)
  --common-name COMMON_NAME
  --days DAYS
  --entity-id ENTITY_ID
  --locality-name LOCALITY_NAME
  --org-id ORG_ID
  --org-name ORG_NAME

NOTE: The solution is provided "AS-IS" and does not represent an official
implementation from Agenzia per l'Italia Digitale.
```
