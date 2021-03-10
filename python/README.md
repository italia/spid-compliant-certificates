# spid-compliant-certificates

```
$ spid-compliant-certificates --help
usage: spid-compliant-certificates [-h] {generator,validator} ...

Tool to generate/validate x509 certificates according to Avviso SPID n.29 v3

positional arguments:
  {generator,validator}
    generator           execute the script in x509 generator mode
    validator           execute the script in x509 validator mode

optional arguments:
  -h, --help            show this help message and exit

NOTE: The solution is provided "AS-IS" and does not represent an official
implementation from Agenzia per l'Italia Digitale.
```


```
$ spid-compliant-certificates generator --help
usage: spid-compliant-certificates generator [-h] [--sector {private,public}]
                                             [--md-alg {sha256,sha512}]
                                             [--key-size {2048,3072,4096}]
                                             [--key-out KEY_OUT]
                                             [--csr-out CSR_OUT]
                                             [--crt-out CRT_OUT] --common-name
                                             COMMON_NAME --days DAYS
                                             --entity-id ENTITY_ID
                                             --locality-name LOCALITY_NAME
                                             --org-id ORG_ID --org-name
                                             ORG_NAME

optional arguments:
  --common-name COMMON_NAME
  --crt-out CRT_OUT     path where the self-signed certificate will be stored
                        (default: crt.pem)
  --csr-out CSR_OUT     path where the csr will be stored (default: csr.pem)
  --days DAYS
  --entity-id ENTITY_ID
  --key-out KEY_OUT     path where the private key will be stored (default:
                        key.pem)
  --key-size {2048,3072,4096}
                        size of the private key (default: 2048)
  --locality-name LOCALITY_NAME
  --md-alg {sha256,sha512}
                        digest algorithm (default: sha256)
  --org-id ORG_ID
  --org-name ORG_NAME
  --sector {private,public}
                        select the specifications to be followed (default:
                        public)
  -h, --help            show this help message and exit
```

```
$ spid-compliant-certificates validator --help
usage: spid-compliant-certificates validator [-h] [--sector {private,public}]
                                             [--crt-file CRT_FILE]

optional arguments:
  --crt-file CRT_FILE   path where the certificate is stored (default:
                        crt.pem)
  --sector {private,public}
                        select the specifications to be followed (default:
                        public)
  -h, --help            show this help message and exit
```
