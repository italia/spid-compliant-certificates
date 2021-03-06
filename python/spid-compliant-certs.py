#!/usr/bin/env python3

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

import argparse
import pathlib
import sys


def generate(args):
    # validate arguments
    print('validate arguments')

    # generate private key
    print('generate a RSA key of %s bits and store in %s'
          % (args.key_size, args.key_out))

    # generate the csr
    print('generate a CSR and store in %s'
          % (args.csr_out))

    if args.sector == 'public':
        # generate self-signed
        print('generate self-signed certificate and store in %s'
              % (args.crt_out))


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description='aaa',
        epilog=('NOTE: The solution is provided "AS-IS" '
                + 'and does not represent an official implementation '
                + 'from Agenzia per l\'Italia Digitale.'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    p.add_argument(
        '--sector',
        action='store',
        choices=['private', 'public'],
        default='public',
        help='select the specifications to be followed'
    )

    p.add_argument(
        '--key-size',
        action='store',
        choices=[2048, 3072, 4096],
        default=2048,
        help='size of the private key',
        type=int
    )

    p.add_argument(
        '--key-out',
        action='store',
        default='key.pem',
        help='path where the private key will be stored',
        type=pathlib.Path
    )

    p.add_argument(
        '--csr-out',
        action='store',
        default='csr.pem',
        help='path where the csr will be stored',
        type=pathlib.Path
    )

    p.add_argument(
        '--crt-out',
        action='store',
        default='crt.pem',
        help='path where the self-signed certificate will be stored',
        type=pathlib.Path
    )

    args = p.parse_args()

    generate(args)

    sys.exit(0)

# vim: ft=python
