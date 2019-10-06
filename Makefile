.PHONY: test parsetest install help

test: install
	rm -f defs.mp
	cdump serialize -o defs.mp $$(cat musl-libc.txt)
	# cdump serialize --libclang='/usr/local/Cellar/llvm/8.0.0_1/Toolchains/LLVM8.0.0.xctoolchain/usr/lib/libclang.dylib' -o defs.mp $$(cat musl-libc.txt)
	cdump deserialize defs.mp

parsetest: install
	cdump parse $$(cat musl-libc.txt)
	# cdump parse --libclang='/usr/local/Cellar/llvm/8.0.0_1/Toolchains/LLVM8.0.0.xctoolchain/usr/lib/libclang.dylib' $$(cat musl-libc.txt)

install:
	python setup.py install

help:
	@echo "Commands: test | parsetest | install"
