init:
	pipenv install -d

test:
	pipenv run pytest tests

fix:
	pipenv run pytest -x -v tests

lint:
	pipenv run pylint src/opera/; \
	pipenv run pylint --disable=no-self-use tests/opera/; \
	pipenv run mypy src/opera/ tests/opera/
