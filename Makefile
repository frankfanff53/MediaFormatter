install:
	pip install -e .

style:
	black --line-length 79 --target-version py311 --exclude "config" .
	isort --profile black --force-grid-wrap=0 .

check:
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive --exclude "config" .
	isort --profile black --check-only --force-grid-wrap=0 .

.PHONY: style check
