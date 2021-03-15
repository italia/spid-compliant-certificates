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

from typing import List, Tuple

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa

SUCCESS = True
FAILURE = not SUCCESS

ALLOWED_SIZES = [
    2048,
    3072,
    4096,
]


def key_type_and_size(cert: x509.Certificate) -> Tuple[bool, List[str]]:
    res = SUCCESS
    failures = []

    # get the public key
    pk = cert.public_key()

    # check the keypair type
    exp_pk_type = 'RSA'
    pk_type = 'RSA' if isinstance(pk, rsa.RSAPublicKey) else 'NOT ALLOWED'
    msg = 'The keypair must be %s' % exp_pk_type
    if pk_type != exp_pk_type:
        res = FAILURE
        failures.append(msg)

    # check the key size
    min_size = 2048
    size = pk.key_size

    msg = ('The key size must be greater than or equal to %d (now: %d)'
           % (min_size, size))
    if size < min_size:
        res = FAILURE
        failures.append(msg)

    msg = ('The key size must be one of %s (now: %d)'
           % (ALLOWED_SIZES, size))
    if size not in ALLOWED_SIZES:
        res = FAILURE
        failures.append(msg)

    return res, failures
