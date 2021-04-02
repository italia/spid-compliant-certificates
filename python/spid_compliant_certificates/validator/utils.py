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

import base64
import os
from typing import Tuple


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
