.PHONY: help venv depinstall install linux_test macos_test linux_parsetest macos_parsetest

help:
	@echo "Commands: linux_test | linux_parsetest | macos_test | macos_parsetest"
	@echo "          depinstall | install"

venv:
ifeq ($(VIRTUAL_ENV), )
	$(error "Not running in a virtualenv")
endif

depinstall: venv
	@pip install -r dev-requirements.txt

install: depinstall
	@python setup.py install

linux_test: install
	@rm -f defs.mp
	@cdump serialize -o defs.mp $$(cat musl-libc.txt)
	@cdump deserialize defs.mp

macos_test: install
	@rm -f defs.mp
	@cdump serialize --preprocessor=/usr/bin/clang --libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib -o defs.mp $$(cat macos-libc.txt)
	# @cdump deserialize defs.mp

linux_parsetest: install
	@cdump parse $$(cat musl-libc.txt)

macos_parsetest: install
	@cdump parse --preprocessor=/usr/bin/clang --libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib $$(cat macos-libc.txt)

