MAIN_MODULE=./x2gbfs

.PHONY: lint-fix
lint-fix:
	ruff --fix ${MAIN_MODULE}
	black ${MAIN_MODULE}
	# mypy has no fix mode, we run it anyway to report (unfixable) errors
	mypy ${MAIN_MODULE}

.PHONY: lint-check
lint-check:
	$(PROXY_RUN) ruff ${MAIN_MODULE}
	$(PROXY_RUN) black -S --check --diff ${MAIN_MODULE}
	mypy ${MAIN_MODULE}

