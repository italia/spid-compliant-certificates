# Validator

A script to check the certificate specifications.

Install dependencies

    $ pip install -r requirements.txt

Run the tests for public sector certificate

    $ CERT_FILE=/path/to/cert/file.pem python3 -m unittest -v validator.TestPublicSector
    test_digest_algorithm (validator.TestPublicSector) ... ok
    test_extensions (validator.TestPublicSector) ... ok
    test_key_type_and_size (validator.TestPublicSector) ... ok
    test_subject_dn (validator.TestPublicSector) ... ok

    ----------------------------------------------------------------------
    Ran 4 tests in 0.016s

    OK

Run the tests for private sector certificate

    $ CERT_FILE=/path/to/cert/file.pem python3 -m unittest -v validator.TestPrivateSector
    test_digest_algorithm (validator.TestPrivateSector) ... ok
    test_extensions (validator.TestPrivateSector) ... ok
    test_key_type_and_size (validator.TestPrivateSector) ... ok
    test_subject_dn (validator.TestPrivateSector) ... ok

    ----------------------------------------------------------------------
    Ran 4 tests in 0.016s

    OK
