# List of all integration test scenarios
integration_test_scenarios := $(wildcard tests/integration/*/runme.sh)

# Default opera executable (tailored for developers). Can be overridden by
# setting the OPERA environment variable to something else.
OPERA ?= "pipenv run opera"

# Variables for Sphinx documentation build (you can set these variables from the command line).
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = docs
BUILDDIR      = docs/_build

# Point pipenv to the right file since we can execute tests from a subdir.
export PIPENV_PIPFILE := $(realpath Pipfile)

.PHONY: init
init:
	pipenv install -d

.PHONY: unit_test
unit_test:
	pipenv run pytest tests/unit

.PHONY: fix
fix:
	pipenv run pytest -x tests

.PHONY: integration_test
integration_test: $(integration_test_scenarios)

.PHONY: $(integration_test_scenarios)
$(integration_test_scenarios):
	cd $(dir $@) && bash $(notdir $@) $(OPERA)


.PHONY: examples_test
examples_test:
	cd examples && bash runme.sh $(OPERA)

.PHONY: build
build:
	pipenv run python setup.py sdist bdist_wheel

.PHONY: test_release
test_release: env-guard-TWINE_USERNAME env-guard-TWINE_PASSWORD
	pipenv run twine upload --repository testpypi --non-interactive dist/*

.PHONY: release
release: env-guard-TWINE_USERNAME env-guard-TWINE_PASSWORD
	pipenv run twine upload --non-interactive dist/*

env-guard-%:
	@ if [ "${${*}}" = "" ]; then \
	  echo "Environment variable $* not set"; \
	  exit 1; \
	fi

.PHONY: docs
docs:
	pipenv run sphinx-build docs docs/_build
