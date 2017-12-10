test:
	python -m pytest -s -v tests

coverage:
	py.test -s --cov-report=html --cov=groom tests

.PHONY: test coverage
