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

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# logging
formatter = logging.Formatter('[%(levelname)1.1s] %(lineno)d %(message)s')  # noqa
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
LOG.addHandler(sh)

MD_ALGS = {
    'sha256': hashes.SHA256(),
    'sha512': hashes.SHA512(),
}


def _validate_private_arguments(args):
    # validate organizationIdentifier
    pattern = r'^(CF:IT-[a-zA-Z0-9]{16}|VATIT-\d{11})$'
    if not re.match(pattern, args.org_id):
        emsg = ('Invalid value for organization identifier (%s)'
                % args.org_id)
        raise ValueError(emsg)


def _validate_public_arguments(args):
    # validate organizationIdentifier
    pattern = r'^PA:IT-\d{11}$'
    if not re.match(pattern, args.org_id):
        emsg = ('Invalid value for organization identifier (%s)'
                % args.org_id)
        raise ValueError(emsg)


def validate_arguments(args):
    if args.sector == 'private':
        _validate_private_arguments(args)
    elif args.sector == 'public':
        _validate_public_arguments(args)
    else:
        emsg = 'Invalid value for sector (%s)' % args.sector
        raise Exception(emsg)


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


def gen_csr(key, args):
    # certificate policies
    policies = []
    if args.sector == 'private':
        policies.append(x509.PolicyInformation(
            x509.ObjectIdentifier('1.3.76.16'), [
                x509.UserNotice(None, 'cert_SP_Privati')
            ]
        ))

        policies.append(x509.PolicyInformation(
            x509.ObjectIdentifier('1.3.76.16.4.3.1'), [
                x509.UserNotice(None, 'Service Provider SPID Privato')
            ]
        ))
    elif args.sector == 'public':
        policies.append(x509.PolicyInformation(
            x509.ObjectIdentifier('1.3.76.16'), [
                x509.UserNotice(None, 'cert_SP_Pubblici')
            ]
        ))

        policies.append(x509.PolicyInformation(
            x509.ObjectIdentifier('1.3.76.16.4.2.1'), [
                x509.UserNotice(None, 'Service Provider SPID Pubblico')
            ]
        ))
    else:
        emsg = 'Invalid value for sector (%s)' % args.sector
        raise Exception(emsg)

    # init csr builder
    builder = x509.CertificateSigningRequestBuilder()

    # compose subject name
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, args.org_name),
        x509.NameAttribute(NameOID.COMMON_NAME, args.common_name),
        # uri
        x509.NameAttribute(x509.ObjectIdentifier('2.5.4.83'), args.entity_id),  # noqa
        # organizationIdentifier
        x509.NameAttribute(x509.ObjectIdentifier('2.5.4.97'), args.org_id),  # noqa
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'IT'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, args.locality_name),
    ]))

    # add extensions
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=False
    )

    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True
    )

    builder = builder.add_extension(
        x509.CertificatePolicies(policies),
        critical=False
    )

    # sign the csr
    csr = builder.sign(key, MD_ALGS[args.md_alg])

    # write to file
    with open(str(args.csr_out), "wb") as fp:
        fp.write(csr.public_bytes(serialization.Encoding.PEM))
        fp.close()


def generate(args):
    # validate arguments
    validate_arguments(args)

    # generate private key
    key = gen_private_key(args.key_size, str(args.key_out))

    # generate the csr
    gen_csr(key, args)

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
