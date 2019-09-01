.PHONY: test parsetest install help

test: install
	rm -f defs.mp
	cdump serialize --libclang='/usr/local/Cellar/llvm/8.0.0_1/Toolchains/LLVM8.0.0.xctoolchain/usr/lib/libclang.dylib' -o defs.mp /usr/include/stdlib.h /usr/include/stdio.h
	cdump deserialize defs.mp

parsetest: install
	cdump parse --libclang='/usr/local/Cellar/llvm/8.0.0_1/Toolchains/LLVM8.0.0.xctoolchain/usr/lib/libclang.dylib' /usr/include/stdlib.h

install:
	python setup.py install

help:
	@echo "Commands: test | parsetest | install"
