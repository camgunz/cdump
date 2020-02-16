.PHONY: test parsetest install help

help:
	@echo "Commands: test | parsetest | install"

venv:
ifeq ($(VIRTUAL_ENV), )
	$(error "Not running in a virtualenv")
endif

install: venv
	python setup.py install

test: install
	rm -f defs.mp
	cdump serialize -o defs.mp $$(cat musl-libc.txt)
	# cdump serialize --libclang='/usr/local/Cellar/llvm/8.0.0_1/Toolchains/LLVM8.0.0.xctoolchain/usr/lib/libclang.dylib' -o defs.mp $$(cat musl-libc.txt)
	cdump deserialize defs.mp

parsetest: install
	cdump parse $$(cat musl-libc.txt)
	# cdump parse --libclang='/usr/local/Cellar/llvm/8.0.0_1/Toolchains/LLVM8.0.0.xctoolchain/usr/lib/libclang.dylib' $$(cat musl-libc.txt)

