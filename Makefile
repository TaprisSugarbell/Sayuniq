.DEFAULT_GOAL := lint

package_dir := source
code_dir := $(package_dir)
user_uid := $(shell id -u)
user_gid := $(shell id -g)

# =================================================================================================
# Code quality
# =================================================================================================

.PHONY: lint
lint:
	isort --check-only $(code_dir)
	black --check --diff $(code_dir)
	ruff $(package_dir)
	mypy $(package_dir)

.PHONY: reformat
reformat:
	poetry run black $(code_dir)
	poetry run isort $(code_dir)

# =================================================================================================
# Environment
# =================================================================================================

.PHONY: s i idev
s:
	poetry shell
i:
	poetry install --without=dev
idev:
	poetry install --with=dev


.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf `find . -name .pytest_cache`
	rm -rf *.egg-info
	rm -f report.html
	rm -f .coverage
	rm -rf {build,dist,site,.cache,.mypy_cache,.ruff_cache,reports}

.PHONY: dup dupd ddown dbuild
dup:
	docker compose up
dupd:
	docker compose up -d
ddown:
	docker compose down --rmi local
dbuild:
	docker compose build --build-arg USER_UID=${user_uid} --build-arg USER_GID=${user_gid}
