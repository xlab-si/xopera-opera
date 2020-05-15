init:
	pipenv install -d

.PHONY: unit_test
unit_test:
	pipenv run pytest tests/unit

fix:
	pipenv run pytest -x tests

build:
	pipenv run python setup.py sdist bdist_wheel

test_release: env-guard-TWINE_USERNAME env-guard-TWINE_PASSWORD
	pipenv run twine upload --repository testpypi --non-interactive dist/*

release: env-guard-TWINE_USERNAME env-guard-TWINE_PASSWORD
	pipenv run twine upload --non-interactive dist/*

env-guard-%:
	@ if [ "${${*}}" = "" ]; then \
	  echo "Environment variable $* not set"; \
	  exit 1; \
	fi
