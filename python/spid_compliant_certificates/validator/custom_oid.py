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

from cryptography import x509


class CustomObjectIdentifier(x509.ObjectIdentifier):
    def __init__(self, dotted_string: str, name: str) -> None:
        super(CustomObjectIdentifier, self).__init__(dotted_string)
        self.name = name

    @property
    def _name(self) -> str:
        return self.name


OID_INITIALS = CustomObjectIdentifier('2.5.4.43', 'initials')
OID_NAME = CustomObjectIdentifier('2.5.4.41', 'name')
OID_ORGANIZATION_IDENTIFIER = CustomObjectIdentifier('2.5.4.97', 'organizationIdentifier')  # noqa
OID_URI = CustomObjectIdentifier('2.5.4.83', 'uri')
