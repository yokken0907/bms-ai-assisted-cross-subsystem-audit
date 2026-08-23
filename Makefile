PYTHON ?= python3

.PHONY: verify verify-full tables
verify:
	$(PYTHON) scripts/verify_all.py

verify-full:
	$(PYTHON) scripts/verify_all.py --fetch-source --strict

tables:
	$(PYTHON) scripts/generate_tables.py
