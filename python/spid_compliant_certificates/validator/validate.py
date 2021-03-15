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

import logging
from typing import List, Tuple

from cryptography import x509

from spid_compliant_certificates.validator import checks
from spid_compliant_certificates.validator.utils import pem_to_der

# logging
formatter = logging.Formatter('[%(levelname)1.1s] %(message)s')  # noqa
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(sh)


def _indent(txt: str, count=1) -> str:
    i = '    '
    return '%s%s' % (i * count, txt)


def _do_check(result: Tuple[bool, List[str]], base_msg: str) -> bool:
    res, failures = result
    is_success = res
    if res:
        LOG.info('%s: success' % base_msg)
    else:
        LOG.error('%s: failure' % base_msg)
        for msg in failures:
            LOG.error(_indent(msg))
    return is_success


def validate(crt_file: str, sector: str) -> None:
    results = []

    # load certificate file
    crt = None
    der, msg = pem_to_der(crt_file)
    if der:
        crt = x509.load_der_x509_certificate(der)
    else:
        raise Exception(msg)

    # check key type and size
    results.append(_do_check(
        checks.key_type_and_size(crt),
        'Checking the key type and size'
    ))

    # check digest algorithm
    results.append(_do_check(
        checks.digest_algorithm(crt.signature_hash_algorithm.name),
        'Checking the signature digest algorithm'
    ))

    # check SubjectDN
    results.append(_do_check(
        checks.subject_dn(crt.subject, sector),
        'Checking the SubjectDN'
    ))

    # check basicConstraints
    results.append(_do_check(
        checks.basic_constraints(crt.extensions),
        'Checking basicConstraints x509 extension'
    ))

    # check keyUsage
    results.append(_do_check(
        checks.key_usage(crt.extensions),
        'Checking keyUsage x509 extension'
    ))

    # check certificatePolicier
    results.append(_do_check(
        checks.certificate_policies(crt.extensions, sector),
        'Checking certificatePolicies x509 extension'
    ))

    for result in results:
        if not result:
            msg = ('The certificate %s does not match %s sector specifications'
                   % (crt_file, sector))
            raise Exception(msg)
