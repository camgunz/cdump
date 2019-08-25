.PHONY: test dumptest parsetest install help

test: install
	rm -f defs.mp
	cdump serialize -o defs.mp /usr/include/stdlib.h /usr/include/stdio.h
	cdump deserialize defs.mp

dumptest: install
	cdump dump /usr/include/stdio.h

parsetest: install
	cdump parse /usr/include/stdlib.h

install:
	python setup.py install

help:
	@echo "Commands: test | dumptest | parsetest | install"
