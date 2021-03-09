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
	spid-compliant-certificates \
		--key-size 3072 \
		--common-name "AgID" \
		--days 365 \
		--entity-id https://spid.agid.gov.it \
		--locality-name Roma \
		--org-id "PA:IT-12345678901" \
		--org-name "Agenzia per l'Italia Digitale" \
		--sector public

private: install cleanup
	spid-compliant-certificates \
		--key-size 3072 \
		--common-name "AgID" \
		--days 365 \
		--entity-id https://spid.agid.gov.it \
		--locality-name Roma \
		--org-id "VATIT-12345678901" \
		--org-name "Agenzia per l'Italia Digitale" \
		--sector private
