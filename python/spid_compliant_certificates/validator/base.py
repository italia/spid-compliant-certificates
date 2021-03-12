# Copyright 2021 Paolo Smiraglia <paolo.smiraglia@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from iso3166 import Country, countries

from spid_compliant_certificates.validator.custom_oid import (
    OID_INITIALS, OID_NAME, OID_ORGANIZATION_IDENTIFIER, OID_URI)
from spid_compliant_certificates.validator.utils import pem_to_der


class TestBase(unittest.TestCase):
    sector = None

    def setUp(self):
        der, msg = pem_to_der(os.getenv('CERT_FILE', 'crt.pem'))
        if der:
            self.cert = x509.load_der_x509_certificate(der)
        else:
            self.fail(msg)

    def test_key_type_and_size(self):
        pk = self.cert.public_key()

        # check the keypair type
        exp_pk_type = 'RSA'
        pk_type = 'RSA' if isinstance(pk, rsa.RSAPublicKey) else 'NOT ALLOWED'
        msg = 'The keypair must be %s' % exp_pk_type
        self.assertEqual(pk_type, exp_pk_type, msg=msg)

        # check the key size
        min_size = 2048
        allowed_sizes = [2048, 3072, 4096]
        size = pk.key_size

        msg = ('The key size must be greater than or equal to %d (now: %d)'
               % (min_size, size))
        self.assertGreaterEqual(size, min_size)

        msg = ('The key size must be one of %s (now: %d)'
               % (allowed_sizes, size))
        self.assertIn(size, allowed_sizes, msg=msg)

    def test_digest_algorithm(self):
        allowed_algs = [hashes.SHA256.name, hashes.SHA512.name]
        alg = self.cert.signature_hash_algorithm.name

        msg = ('The digest algorithm must be one of %s (now: %s)'
               % (allowed_algs, alg))
        self.assertIn(alg, allowed_algs, msg=msg)

    def test_basic_constraints(self):
        extensions = self.cert.extensions

        # basicConstraints: CA:FALSE
        ext_cls = x509.BasicConstraints
        ext_name = ext_cls.oid._name

        try:
            ext = extensions.get_extension_for_class(ext_cls)

            msg = '%s: can not be set as critical' % ext_name
            self.assertFalse(ext.critical, msg=msg)

            msg = '%s: CA must be FALSE' % ext_name
            self.assertFalse(ext.value.ca, msg=msg)
        except x509.ExtensionNotFound:
            self.fail('%s must be present' % ext_name)

    def test_key_usage(self):
        extensions = self.cert.extensions

        # keyUsage: critical;nonRepudiation
        ext_cls = x509.KeyUsage
        ext_name = ext_cls.oid._name

        try:
            ext = extensions.get_extension_for_class(ext_cls)

            msg = '%s: must be set as critical' % ext_name
            self.assertTrue(ext.critical, msg=msg)

            for usage in ['content_commitment', 'digital_signature']:
                msg = '%s: %s must be set' % (ext_name, usage)
                self.assertTrue(getattr(ext.value, usage), msg=msg)

            for usage in ['crl_sign', 'data_encipherment', 'decipher_only',
                          'encipher_only', 'key_agreement', 'key_cert_sign',
                          'key_encipherment']:
                msg = '%s: %s must be unset' % (ext_name, usage)
                self.assertFalse(getattr(ext.value, usage), msg=msg)
        except x509.ExtensionNotFound:
            self.fail('%s must be present' % ext_name)
        except Exception:
            pass

    def test_certificate_policies(self):
        extensions = self.cert.extensions

        # certificatePolicies: agIDcert(agIDcert)
        ext_cls = x509.CertificatePolicies
        ext_name = ext_cls.oid._name

        # expected policies
        exp_policies = [
            '1.3.76.16.6'  # agIDCert
        ]

        if self.sector == 'private':
            exp_policies.append('1.3.76.16.4.3.1')  # spid-private-sp

        if self.sector == 'public':
            exp_policies.append('1.3.76.16.4.2.1')  # spid-public-sp

        try:
            ext = extensions.get_extension_for_class(ext_cls)

            # check if critical
            msg = '%s: can nont be set as critical' % ext_name
            self.assertFalse(ext.critical, msg=msg)

            # check if expected policies are present
            policies = ext.value
            for ep in exp_policies:
                is_present = any(
                    p.policy_identifier.dotted_string == ep for p in policies
                )
                msg = '%s: policy %s must be present' % (ext_name, ep)
                self.assertTrue(is_present, msg=msg)

            # check the content of the policies
            for p in policies:
                oid = p.policy_identifier.dotted_string
                if oid == '1.3.76.16.6':
                    for q in p.policy_qualifiers:
                        if isinstance(q, x509.extensions.UserNotice):
                            exp_etext = 'agIDcert'
                            etext = q.explicit_text

                            msg = '%s: policy %s must have ' % (ext_name, oid)
                            msg += ('UserNotice.ExplicitText=%s (now: %s)'
                                    % (exp_etext, etext))
                            self.assertEqual(etext, exp_etext, msg=msg)
                if oid == '1.3.76.16.4.2.1':
                    for q in p.policy_qualifiers:
                        if isinstance(q, x509.extensions.UserNotice):
                            exp_etext = 'cert_SP_Pub'
                            etext = q.explicit_text

                            msg = '%s: policy %s must have ' % (ext_name, oid)
                            msg += ('UserNotice.ExplicitText=%s (now: %s)'
                                    % (exp_etext, etext))
                            self.assertEqual(etext, exp_etext, msg=msg)
                if oid == '1.3.76.16.4.3.1':
                    for q in p.policy_qualifiers:
                        if isinstance(q, x509.extensions.UserNotice):
                            exp_etext = 'cert_SP_Priv'
                            etext = q.explicit_text

                            msg = '%s: policy %s must have ' % (ext_name, oid)
                            msg += ('UserNotice.ExplicitText=%s (now: %s)'
                                    % (exp_etext, etext))
                            self.assertEqual(etext, exp_etext, msg=msg)
        except x509.ExtensionNotFound:
            self.fail('%s must be present' % ext_name)

    def test_subject_dn(self):
        mandatory_attrs = [
            OID_ORGANIZATION_IDENTIFIER,
            OID_URI,
            x509.OID_COMMON_NAME,
            x509.OID_COUNTRY_NAME,
            x509.OID_LOCALITY_NAME,
            x509.OID_LOCALITY_NAME,
            x509.OID_ORGANIZATION_NAME,
        ]

        not_allowed_attrs = [
            OID_INITIALS,
            OID_NAME,
            x509.OID_EMAIL_ADDRESS,
            x509.OID_GIVEN_NAME,
            x509.OID_PSEUDONYM,
            x509.OID_SURNAME,
        ]

        subj = self.cert.subject
        subj_attrs = [attr.oid for attr in subj]

        # check if not allowed attrs are present
        for attr in not_allowed_attrs:
            msg = ('Name attribute [%s, %s] is not allowed in subjectDN'
                   % (attr._name, attr.dotted_string))
            self.assertNotIn(attr._name, subj_attrs, msg=msg)

        # check if all the mandatory attre are present
        for attr in mandatory_attrs:
            msg = ('Name attribute [%s, %s] must be present in subjectDN'
                   % (attr._name, attr.dotted_string))
            self.assertIn(attr, mandatory_attrs, msg=msg)

        # check the name attribute value
        for attr in subj:
            msg = ('Value for name attribute [%s, %s] can not be empty'
                   % (attr.oid._name, attr.oid.dotted_string))
            self.assertIsNotNone(attr.value, msg=msg)

            value = attr.value
            if attr.oid == OID_ORGANIZATION_IDENTIFIER:
                if self.sector == 'public':
                    prefix = 'PA:IT-'
                    msg = ('Value for name attribute [%s, %s] must start with "%s"'  # noqa
                           % (attr.oid._name, attr.oid.dotted_string, prefix))
                    self.assertTrue(value.startswith(prefix), msg=msg)
                if self.sector == 'private':
                    prefix_1 = 'CF:IT-'
                    prefix_2 = 'VATIT-'
                    msg = ('Value for name attribute [%s, %s] must start with "%s" of "%s"'  # noqa
                           % (attr.oid._name, attr.oid.dotted_string,
                              prefix_1, prefix_2))
                    self.assertTrue(any([
                        value.startswith(prefix_1),
                        value.startswith(prefix_2),
                    ]), msg=msg)
            if attr.oid == x509.OID_COUNTRY_NAME:
                msg = ('Value for name attribute [%s, %s] is not a valid country code (%s)'  # noqa
                       % (attr.oid._name, attr.oid.dotted_string, value))
                try:
                    self.assertIsInstance(
                        countries.get(value),
                        Country,
                        msg=msg
                    )
                except KeyError:
                    self.fail(msg)
