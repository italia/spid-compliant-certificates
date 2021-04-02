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

from spid_compliant_certificates.validator import checks
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
        _checks = checks.key_type_and_size(self.cert)
        for res, msg in _checks:
            self.assertTrue(res, msg=msg)

    def test_digest_algorithm(self):
        alg = self.cert.signature_hash_algorithm.name
        _checks = checks.digest_algorithm(alg)
        for res, msg in _checks:
            self.assertTrue(res, msg=msg)

    def test_basic_constraints(self):
        extensions = self.cert.extensions
        _checks = checks.basic_constraints(extensions)
        for res, msg in _checks:
            self.assertTrue(res, msg=msg)

    def test_key_usage(self):
        extensions = self.cert.extensions
        _checks = checks.key_usage(extensions)
        for res, msg in _checks:
            self.assertTrue(res, msg=msg)

    def test_certificate_policies(self):
        extensions = self.cert.extensions
        sector = self.sector
        _checks = checks.certificate_policies(extensions, sector)
        for res, msg in _checks:
            self.assertTrue(res, msg=msg)

    def test_subject_dn(self):
        subj = self.cert.subject
        sector = self.sector
        _checks = checks.subject_dn(subj, sector)
        for res, msg in _checks:
            self.assertTrue(res, msg=msg)
