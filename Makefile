MAIN_MODULE=./x2gbfs
OTHER_MODULES=./tests

.PHONY: lint-fix
lint-fix:
	ruff check --fix ${MAIN_MODULE} ${OTHER_MODULES}
	black ${MAIN_MODULE} ${OTHER_MODULES}
	# mypy has no fix mode, we run it anyway to report (unfixable) errors
	mypy ${MAIN_MODULE} ${OTHER_MODULES}

.PHONY: lint-check
lint-check:
	$(PROXY_RUN) ruff check ${MAIN_MODULE} ${OTHER_MODULES}
	$(PROXY_RUN) black -S --check --diff ${MAIN_MODULE} ${OTHER_MODULES}
	mypy ${MAIN_MODULE} ${OTHER_MODULES}

