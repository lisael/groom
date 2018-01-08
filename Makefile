PYTEST?=py.test

test:
	${PYTEST} -s -v tests

coverage:
	SHORT_TESTS=1 ${PYTEST} -s -vv --cov-report=html --cov=groom tests

stdlib_coverage:
	${PYTEST} -s -vv --cov-report=html --cov=groom tests

.PHONY: test coverage
