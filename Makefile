#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/pip install -r requirements.txt

.PHONY: buildout
buildout:
	rm -f .installed.cfg
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/python bin/buildout

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: cleanall
cleanall:
	rm -fr lib bin/buildout develop-eggs downloads eggs parts .installed.cfg
