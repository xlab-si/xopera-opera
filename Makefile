init:
	pipenv install -d

test:
	pipenv run pytest tests

fix:
	pipenv run pytest -x tests
