.PHONY: help venv depinstall install linux_test macos_test linux_parsetest macos_parsetest

help:
	@echo "Commands: linux_test | linux_parsetest |"
	@echo "          macos_test | macos_test_json | macos_parsetest |"
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
	@cdump serialize --preprocessor=/usr/bin/clang -o defs.mp $$(cat musl-libc.txt)
	@cdump deserialize defs.mp

macos_test: install
	@rm -f defs.mp
	@cdump serialize --preprocessor=/usr/bin/clang --libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib -o defs.mp $$(cat macos-libc.txt)
	# @cdump deserialize defs.mp

macos_test_json: install
	@rm -f defs.mp
	@cdump serialize --preprocessor=/usr/bin/clang --libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib --format=json -o defs.json $$(cat macos-libc.txt)

linux_parsetest: install
	@cdump parse --preprocessor=/usr/bin/clang $$(cat musl-libc.txt)

macos_parsetest: install
	@cdump parse --preprocessor=/usr/bin/clang --libclang=/Library/Developer/CommandLineTools/usr/lib/libclang.dylib $$(cat macos-libc.txt)

