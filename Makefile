test:
	python -m pytest -s -v tests

coverage:
	py.test -s -vv --cov-report=html --cov=groom tests

.PHONY: test coverage
