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
import pathlib
import re
from typing import Dict

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

MD_ALGS = {
    'sha256': hashes.SHA256(),
    'sha512': hashes.SHA512(),
}

# logging
formatter = logging.Formatter('[%(levelname)1.1s] %(message)s')  # noqa
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(sh)


def _validate_private_arguments(cert_opts: Dict) -> None:
    # validate organizationIdentifier
    pattern = r'^(CF:IT-[a-zA-Z0-9]{16}|VATIT-\d{11})$'
    org_id = cert_opts['org_id']
    if not re.match(pattern, org_id):
        emsg = ('Invalid value for organization identifier (%s)' % org_id)
        raise ValueError(emsg)


def _validate_public_arguments(cert_opts: Dict) -> None:
    # validate organizationIdentifier
    pattern = r'^PA:IT-\d{11}$'
    org_id = cert_opts['org_id']
    if not re.match(pattern, org_id):
        emsg = ('Invalid value for organization identifier (%s)' % org_id)
        raise ValueError(emsg)


def validate_arguments(cert_opts: Dict) -> None:
    sector = cert_opts['sector']
    if sector == 'private':
        _validate_private_arguments(cert_opts)
    elif sector == 'public':
        _validate_public_arguments(cert_opts)
    else:
        emsg = 'Invalid value for sector (%s)' % sector
        raise Exception(emsg)


def gen_private_key(key_size: int, key_out: pathlib.PosixPath) -> rsa.RSAPrivateKey:  # noqa
    # check if the private key file already exists
    if key_out.exists():
        emsg = 'File %s already exists' % key_out
        raise Exception(emsg)

    # generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )

    # write to file
    with open(key_out, "wb") as fp:
        fp.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
        fp.close()

    return key


def gen_csr(key: rsa.RSAPrivateKey, cert_opts: Dict, crypto_opts: Dict) -> None:  # noqa
    sector = cert_opts['sector']

    # certificate policies
    policies = [
        x509.PolicyInformation(
            x509.ObjectIdentifier('1.3.76.16'), [
                x509.UserNotice(None, 'AgIDroot')
            ]
        )
    ]
    if sector == 'private':
        policies.append(
            x509.PolicyInformation(
                x509.ObjectIdentifier('1.3.76.16.4.3.1'), [
                    x509.UserNotice(None, 'cert_SP_Priv')
                ]
            )
        )
    elif sector == 'public':
        policies.append(
            x509.PolicyInformation(
                x509.ObjectIdentifier('1.3.76.16.4.2.1'), [
                    x509.UserNotice(None, 'cert_SP_Pub')
                ]
            )
        )
    else:
        emsg = 'Invalid value for sector (%s)' % sector
        raise Exception(emsg)

    # init csr builder
    builder = x509.CertificateSigningRequestBuilder()

    # compose subject name
    common_name = cert_opts['common_name']
    entity_id = cert_opts['entity_id']
    locality_name = cert_opts['locality_name']
    org_id = cert_opts['org_id']
    org_name = cert_opts['org_name']
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org_name),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        # uri
        x509.NameAttribute(x509.ObjectIdentifier('2.5.4.83'), entity_id),
        # organizationIdentifier
        x509.NameAttribute(x509.ObjectIdentifier('2.5.4.97'), org_id),
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'IT'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
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
    md_alg = MD_ALGS[crypto_opts['md_alg']]
    csr = builder.sign(key, md_alg)

    # write to file
    csr_out = crypto_opts['csr_out']
    with open(str(csr_out), "wb") as fp:
        fp.write(csr.public_bytes(serialization.Encoding.PEM))
        fp.close()


def generate(cert_opts: Dict, crypto_opts: Dict) -> None:
    # validate arguments
    validate_arguments(cert_opts)

    # generate private key
    key_size = crypto_opts['key_size']
    key_out = crypto_opts['key_out']
    key = gen_private_key(key_size, key_out)
    LOG.info('Private key saved to %s' % key_out)
    LOG.info('  Inspect with OpenSSL: openssl rsa -in %s -noout -text'
             % key_out)

    # generate the csr
    csr_out = crypto_opts['csr_out']
    gen_csr(key, cert_opts, crypto_opts)
    LOG.info('CSR saved to %s' % csr_out)
    LOG.info('  Inspect with OpenSSL: openssl req -in %s -noout -text'
             % csr_out)
    LOG.info('  Inspect with OpenSSL: openssl asn1parse -i -inform PEM -in %s'
             % csr_out)

    sector = cert_opts['sector']
    crt_out = crypto_opts['crt_out']
    if sector == 'public':
        # generate self-signed
        print('generate self-signed certificate and store in %s' % crt_out)
