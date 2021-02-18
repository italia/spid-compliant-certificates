#!/usr/bin/env python3

import base64
import logging
import os
import unittest
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import Extension

formatter = logging.Formatter('[%(asctime)s][%(levelname)1.1s] %(message)s')
fh = logging.FileHandler('validator.log', mode='w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
LOG.addHandler(fh)


def pem_to_der(cert_file: str) -> Tuple[bytes, str]:
    if not os.path.exists(cert_file):
        msg = 'File at %s not found' % cert_file
        return None, msg

    lines = []
    with open(cert_file, 'r') as fp:
        lines = fp.readlines()
        fp.close()

    if ('-----BEGIN CERTIFICATE-----' not in lines[0]):
        msg = 'Certificate at %s must be a PEM' % cert_file
        return None, msg

    if ('-----END CERTIFICATE-----' not in lines[len(lines)-1]):
        msg = 'Certificate at %s must be a PEM' % cert_file
        return None, msg

    b64_data = ''.join([line[:-1] for line in lines[1:-1]])
    der = base64.b64decode(b64_data)

    return der, None


def key_usage_is_ok(e: Extension) -> bool:
    is_ok = False

    # check if extension is critical
    if not e.critical:
        return is_ok

    # check the requested key usage
    for usage in ['content_commitment',
                  'digital_signature']:
        if not getattr(e.value, usage):
            # requested usage is not present
            return is_ok

    # check the not requested key usage
    try:
        for usage in ['crl_sign',
                      'data_encipherment',
                      'decipher_only',
                      'encipher_only',
                      'key_agreement',
                      'key_cert_sign',
                      'key_encipherment']:
            if getattr(e.value, usage):
                # not requested usage is present
                return is_ok
    except Exception:
        pass

    # the extension is ok
    is_ok = True
    return is_ok


def basic_constraints_is_ok(e: Extension) -> bool:
    is_ok = False

    # check if extension is not critical
    if e.critical:
        return is_ok

    # check if CA is FALSE
    if e.value.ca:
        return is_ok

    # the extension is ok
    is_ok = True
    return is_ok


def certificate_policies_is_ok(e: Extension) -> Tuple[bool, str]:
    is_ok = False

    # check if extension is not critical
    if e.critical:
        msg = 'Extension with OID %s can\'t be critical' % e.oid.dotted_string
        return is_ok, msg

    # check policies
    mandatory_policies = ['1.3.76.16', '1.3.76.16.4.2.1']

    policies = e.value
    cert_policies = [p.policy_identifier.dotted_string for p in policies]

    for p in mandatory_policies:
        if p not in cert_policies:
            msg = 'Policy %s is missing' % p
            return is_ok, msg

    for p in policies:
        if p.policy_identifier.dotted_string == '1.3.76.16':
            for q in p.policy_qualifiers:
                if isinstance(q, x509.extensions.UserNotice):
                    if q.explicit_text != 'cert_SP_Pubblici':
                        msg = ('UserNotice.ExplicitText for policy %s is not valid (%s)'  # noqa
                               % (p.policy_identifier.dotted_string, q.explicit_text))  # noqa
                        return is_ok, msg
        elif p.policy_identifier.dotted_string == '1.3.76.16.4.2.1':
            for q in p.policy_qualifiers:
                if isinstance(q, x509.extensions.UserNotice):
                    if q.explicit_text != 'Service Provider SPID Pubblico':
                        msg = ('UserNotice.ExplicitText for policy %s is not valid (%s)'  # noqa
                               % (p.policy_identifier.dotted_string, q.explicit_text))  # noqa
                        return is_ok, msg
        else:
            pass

    # the extension is ok
    is_ok = True
    return is_ok, None


class TestPublicSectorSPIDCertificate(unittest.TestCase):
    def setUp(self):
        der, msg = pem_to_der(os.getenv('CERT_FILE', 'crt.pem'))
        if der:
            self.cert = x509.load_der_x509_certificate(der)
        else:
            self.fail(msg)

    def test_key_type_and_size(self):
        pk = self.cert.public_key()
        self.assertTrue(isinstance(pk, rsa.RSAPublicKey))
        self.assertGreaterEqual(pk.key_size, 2048)

    def test_digest_algorithm(self):
        allowed_algs = [hashes.SHA256, hashes.SHA384, hashes.SHA512]
        alg_is_ok = False

        _alg = self.cert.signature_hash_algorithm
        for alg in allowed_algs:
            if isinstance(_alg, alg):
                alg_is_ok = True

        self.assertTrue(alg_is_ok)

    def test_mandatory_extensions(self):
        mandatory_exts = [
            '2.5.29.15',  # keyUsage
            '2.5.29.19',  # basicConstraints
            '2.5.29.32',  # certificatePolicies
        ]

        extensions = self.cert.extensions
        cert_exts = [ext.oid.dotted_string for ext in extensions]

        # check if all the mandatory extensions are present
        for ext in mandatory_exts:
            self.assertIn(ext, cert_exts)

        # check the extensions content
        for ext in extensions:
            if ext.oid.dotted_string == '2.5.29.15':
                self.assertTrue(key_usage_is_ok(ext))
            elif ext.oid.dotted_string == '2.5.29.19':
                self.assertTrue(basic_constraints_is_ok(ext))
            elif ext.oid.dotted_string == '2.5.29.32':
                res, msg = certificate_policies_is_ok(ext)
                self.assertTrue(res, msg=msg)
            else:
                pass

    def test_subject_dn(self):
        mandatory_attrs = [
            '2.5.4.10',  # organizationName
            '2.5.4.3',   # commonName
            '2.5.4.6',   # countryName
            '2.5.4.7',   # localityName
            '2.5.4.83',  # uri
            '2.5.4.97',  # organizationIdentifier
        ]
        not_allowed_attrs = {
            '1.2.840.113549.1.9.1',  # emailAddress
            '2.5.4.4',               # surname
            '2.5.4.41',              # name
            '2.5.4.42',              # givenName
            '2.5.4.43',              # initials
            '2.5.4.65',              # pseudonym
        }

        subj = self.cert.subject
        subj_attrs = [attr.oid.dotted_string for attr in subj]

        # check if not allowed attrs are present
        for attr in not_allowed_attrs:
            self.assertNotIn(attr, subj_attrs)

        # check if all the mandatory attre are present
        for attr in mandatory_attrs:
            self.assertIn(attr, subj_attrs)

        # check attr the value
        for attr in subj:
            self.assertIsNotNone(attr.value)

            oid = attr.oid.dotted_string
            value = attr.value
            if oid == '2.5.4.97':
                self.assertTrue(value.startswith('PA:IT-'))
            elif oid == '2.5.4.6':
                self.assertEqual(len(value), 2)


if __name__ == '__main__':
    unittest.main(verbosity=int(os.getenv('VERBOSITY', '1')))
