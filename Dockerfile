# Copyright 2020 Paolo Smiraglia <paolo.smiraglia@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

FROM alpine:latest
LABEL maintainer="Paolo Smiraglia <paolo.smiraglia@gmail.com>"

RUN apk update \
    && apk add --no-cache \
        curl \
        grep \
        openssl

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint
COPY gencert-private.sh /usr/local/bin/gencert-private
COPY gencert-public.sh /usr/local/bin/gencert-public
RUN chmod +x \
    /usr/local/bin/docker-entrypoint \
    /usr/local/bin/gencert-private \
    /usr/local/bin/gencert-public
ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]

WORKDIR /output
