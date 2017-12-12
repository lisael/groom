PYTEST?=py.test

test:
	${PYTEST} -s -v tests

coverage:
	${PYTEST} -s -vv --cov-report=html --cov=groom tests

.PHONY: test coverage
