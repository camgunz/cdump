.PHONY: test dumptest parsetest install

test: install
	rm -f defs.db
	cdump db -f defs.db /usr/include/stdlib.h /usr/include/stdio.h

dumptest: install
	cdump dump /usr/include/stdio.h

parsetest: install
	cdump parse /usr/include/stdlib.h

install:
	python setup.py install

help:
	@echo "Commands: test | dumptest | parsetest | install"
