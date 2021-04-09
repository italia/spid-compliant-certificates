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

from packaging.utils import canonicalize_version
from packaging.version import Version

# major version
_maj = 0

# minor version
_min = 1

# micro version
_mic = 0

# release level (alpha, beta, rc, final)
_rel = 'alpha'

# serial
_ser = 0

# version info
version_info = (
    _maj,
    _min,
    _mic,
    _rel,
    _ser
)

# legacy version string
legacy_version = (f'{_maj}.{_min}.{_mic}{_rel}{_ser}' if _rel != 'final'
                  else f'{_maj}.{_min}.{_mic}')

# canonical version
version = canonicalize_version(Version(legacy_version))
