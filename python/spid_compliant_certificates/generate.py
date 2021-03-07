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
import re

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

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
    policies = [
        x509.PolicyInformation(
            x509.ObjectIdentifier('1.3.76.16'), [
                x509.UserNotice(None, 'AgIDroot')
            ]
        )
    ]
    if args.sector == 'private':
        policies.append(
            x509.PolicyInformation(
                x509.ObjectIdentifier('1.3.76.16.4.3.1'), [
                    x509.UserNotice(None, 'cert_SP_Priv')
                ]
            )
        )
    elif args.sector == 'public':
        policies.append(
            x509.PolicyInformation(
                x509.ObjectIdentifier('1.3.76.16.4.2.1'), [
                    x509.UserNotice(None, 'cert_SP_Pub')
                ]
            )
        )
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
