.PHONY: help install typecheck lint format test python-test examples examples-chat examples-recruitment examples-index makedocs docs-check verify system-check

help:
	@./project.sh help

install:
	@./project.sh install

typecheck:
	@./project.sh typecheck

lint:
	@./project.sh lint

format:
	@./project.sh format

test:
	@./project.sh test

python-test:
	@./project.sh python-test

examples:
	@./project.sh examples

examples-chat:
	@./project.sh examples-chat

examples-recruitment:
	@./project.sh examples-recruitment

examples-index:
	@./project.sh examples-index

makedocs:
	@./project.sh makedocs

docs-check:
	@./project.sh makedocs
	@git diff --exit-code -- README.md docs/documentation-index.md docs/examples-artifacts-index.md examples examples-chat examples-recruitment

verify:
	@./project.sh verify

system-check:
	@./project.sh system-check