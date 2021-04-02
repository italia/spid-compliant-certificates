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


def certificate_policies(extensions: x509.Extensions, sector: str) -> List[Tuple[bool, str]]:  # noqa
    checks = []

    # certificatePolicies: agIDcert(agIDcert)
    ext_cls = x509.CertificatePolicies
    ext_name = ext_cls.oid._name

    # expected policies
    exp_policies = [
        '1.3.76.16.6'  # agIDCert
    ]

    if sector == 'private':
        exp_policies.append('1.3.76.16.4.3.1')  # spid-private-sp

    if sector == 'public':
        exp_policies.append('1.3.76.16.4.2.1')  # spid-public-sp

    try:
        ext = extensions.get_extension_for_class(ext_cls)

        # check if critical
        msg = '%s can not be set as critical' % ext_name
        res = FAILURE if ext.critical else SUCCESS
        checks.append((res, msg))

        # check if expected policies are present
        policies = ext.value
        for ep in exp_policies:
            is_present = any(
                p.policy_identifier.dotted_string == ep for p in policies
            )
            msg = 'policy %s must be present' % (ep)
            res = SUCCESS if is_present else FAILURE
            checks.append((res, msg))

        # check the content of the policies
        for p in policies:
            oid = p.policy_identifier.dotted_string
            if oid == '1.3.76.16.6':
                for q in p.policy_qualifiers:
                    if isinstance(q, x509.extensions.UserNotice):
                        exp_etext = 'agIDcert'
                        etext = q.explicit_text

                        msg = 'policy %s must have ' % (oid)
                        msg += ('UserNotice.ExplicitText=%s (now: %s)'
                                % (exp_etext, etext))

                        res = FAILURE if etext != exp_etext else SUCCESS
                        checks.append((res, msg))

            if sector == 'public' and oid == '1.3.76.16.4.2.1':
                for q in p.policy_qualifiers:
                    if isinstance(q, x509.extensions.UserNotice):
                        exp_etext = 'cert_SP_Pub'
                        etext = q.explicit_text

                        msg = 'policy %s must have ' % (oid)
                        msg += ('UserNotice.ExplicitText=%s (now: %s)'
                                % (exp_etext, etext))

                        res = FAILURE if etext != exp_etext else SUCCESS
                        checks.append((res, msg))
            if sector == 'private' and oid == '1.3.76.16.4.3.1':
                for q in p.policy_qualifiers:
                    if isinstance(q, x509.extensions.UserNotice):
                        exp_etext = 'cert_SP_Priv'
                        etext = q.explicit_text

                        msg = 'policy %s must have ' % (oid)
                        msg += ('UserNotice.ExplicitText=%s (now: %s)'
                                % (exp_etext, etext))

                        res = FAILURE if etext != exp_etext else SUCCESS
                        checks.append((res, msg))
    except x509.ExtensionNotFound:
        msg = '%s must be present' % ext_name
        checks.append((FAILURE, msg))

    return checks
