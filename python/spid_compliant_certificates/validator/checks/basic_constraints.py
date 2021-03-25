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

SUCCESS = True
FAILURE = not SUCCESS


def basic_constraints(extensions: x509.Extensions) -> List[Tuple[bool, str]]:
    checks = []

    # basicConstraints: CA:FALSE
    ext_cls = x509.BasicConstraints
    ext_name = ext_cls.oid._name

    try:
        ext = extensions.get_extension_for_class(ext_cls)

        msg = '%s can not be set as critical' % ext_name
        res = FAILURE if ext.critical else SUCCESS
        checks.append((res, msg))

        msg = 'CA must be FALSE'
        res = FAILURE if ext.value.ca else SUCCESS
        checks.append((res, msg))
    except x509.ExtensionNotFound:
        msg = '%s must be present' % ext_name
        checks.append((FAILURE, msg))

    return checks
