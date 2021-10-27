POETRY ?= poetry
REPO ?= https://github.com/aws/aws-elastic-beanstalk-cli-setup

clean:
	find . -name '__pycache__' | xargs rm -rf
	find . -type f -name "*.pyc" -delete

install-dev:
	$(POETRY) install

lint:
	$(POETRY) run black --check $(name) tests
	$(POETRY) run flake8 --config setup.cfg $(name) tests

format:
	$(POETRY) run black $(name) tests

test:
	$(POETRY) run pytest tests

run: install-dev
	$(POETRY) run python -m pull_requests.app ${REPO}

.PHONY: clean install-dev lint test run
