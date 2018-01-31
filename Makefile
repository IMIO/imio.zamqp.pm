#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/pip install setuptools==38.2.4
	./bin/python bootstrap.py --version=2.10.0

.PHONY: buildout
buildout:
	rm -f .installed.cfg
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: cleanall
cleanall:
	rm -fr lib bin/buildout develop-eggs downloads eggs parts .installed.cfg
