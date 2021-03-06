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
import logging
import os
import pathlib
import re
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# logging
formatter = logging.Formatter('[%(levelname)1.1s] %(message)s')  # noqa
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
LOG.addHandler(sh)


def validate_arguments(args):
    # validate value for organization identifier
    if args.sector == 'private':
        pattern = r'^(CF:IT-[a-zA-Z0-9]{16}|VATIT-\d{11})$'
    elif args.sector == 'public':
        pattern = r'^PA:IT-\d{11}$'
    else:
        emsg = 'Invalid value for sector (%s)' % args.sector
        raise Exception(emsg)

    if not re.match(pattern, args.org_id):
        emsg = ('Invalid value for organization identifier (%s)'
                % args.org_id)
        raise ValueError(emsg)


def gen_private_key(key_size: int, outfile: str) -> rsa.RSAPrivateKey:
    # check if the private key file already exists
    if os.path.exists(outfile):
        emsg = 'File %s already exists' % outfile
        raise Exception(emsg)

    # generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    # write to file
    with open(outfile, "wb") as fp:
        fp.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        fp.close()

    return key


def generate(args):
    # validate arguments
    validate_arguments(args)

    # generate private key
    key = gen_private_key(args.key_size, str(args.key_out))

    # generate the csr
    print('generate a CSR and store in %s'
          % (args.csr_out))

    if args.sector == 'public':
        # generate self-signed
        print('generate self-signed certificate and store in %s'
              % (args.crt_out))


def not_empty_string(value):
    if not re.match(r'^\S(.*\S)?$', value):
        emsg = 'Format "%s" is not accepted' % value
        raise argparse.ArgumentTypeError(emsg)
    return value


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
        '--md-alg',
        action='store',
        choices=['sha256', 'sha512'],
        default='sha256',
        help='digest algorithm',
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

    p.add_argument(
        '--common-name',
        action='store',
        required=True,
        type=not_empty_string
    )

    p.add_argument(
        '--days',
        action='store',
        required=True,
        type=int
    )

    p.add_argument(
        '--entity-id',
        action='store',
        required=True,
        type=not_empty_string
    )

    p.add_argument(
        '--locality-name',
        action='store',
        required=True,
        type=not_empty_string
    )

    p.add_argument(
        '--org-id',
        action='store',
        required=True,
        type=not_empty_string
    )

    p.add_argument(
        '--org-name',
        action='store',
        required=True,
        type=not_empty_string
    )

    args = p.parse_args()

    try:
        generate(args)
    except Exception as e:
        LOG.error(e)
        sys.exit(1)

    sys.exit(0)

# vim: ft=python
