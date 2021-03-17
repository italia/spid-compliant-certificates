default: install

flake8:
	flake8 bin/* spid_compliant_certificates/*.py setup.py

isort-diff:
	isort bin/* spid_compliant_certificates/*.py setup.py --diff

isort:
	isort bin/* spid_compliant_certificates/*.py setup.py

cleanup:
	rm -fr *.pem

install:
	pip install .

public: install cleanup
	spid-compliant-certificates generator \
		--key-size 3072 \
		--common-name "AgID" \
		--days 365 \
		--entity-id https://spid.agid.gov.it \
		--locality-name Roma \
		--org-id "PA:IT-c_h501" \
		--org-name "Agenzia per l'Italia Digitale" \
		--sector public

private: install cleanup
	spid-compliant-certificates generator \
		--key-size 3072 \
		--common-name "AgID" \
		--days 365 \
		--entity-id https://spid.agid.gov.it \
		--locality-name Roma \
		--org-id "VATIT-12345678901" \
		--org-name "Agenzia per l'Italia Digitale" \
		--sector private

validate-public:
	spid-compliant-certificates validator

validate-private:
	spid-compliant-certificates validator --sector private

docker-build:
	docker build --tag psmiraglia/spid-compliant-certificates .

docker-prepare:
	mkdir -pv certs

docker-gpub: docker-build docker-prepare
	docker run -ti --rm -v "$(shell pwd)/certs:/certs" \
		psmiraglia/spid-compliant-certificates generator \
			--key-size 3072 \
			--common-name "A.C.M.E" \
			--days 365 \
			--entity-id "https://spid.acme.it" \
			--locality-name "Roma" \
			--org-id "PA:IT-c_h501" \
			--org-name "A Company Making Everything" \
			--sector public

docker-vpub: docker-build docker-prepare
	docker run -ti --rm -v "$(shell pwd)/certs:/certs" \
		psmiraglia/spid-compliant-certificates validator \
			--sector public

docker-gpriv: docker-build docker-prepare
	docker run -ti --rm -v "$(shell pwd)/certs:/certs" \
		psmiraglia/spid-compliant-certificates generator \
			--key-size 3072 \
			--common-name "A.C.M.E" \
			--days 365 \
			--entity-id "https://spid.acme.it" \
			--locality-name "Roma" \
			--org-id "VATIT-12345678901" \
			--org-name "A Company Making Everything" \
			--sector private

docker-vpriv: docker-build docker-prepare
	docker run -ti --rm -v "$(shell pwd)/certs:/certs" \
		psmiraglia/spid-compliant-certificates validator \
			--sector private

docker-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile
