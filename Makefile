init:
	pipenv install -d

test:
	pipenv run pytest tests

fix:
	pipenv run pytest -x -v tests

lint:
	pipenv run mypy src/opera/
