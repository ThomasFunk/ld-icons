PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
DATADIR ?= $(PREFIX)/share/ld-icons
DESTDIR ?=

PYTHON ?= python3

INSTALL ?= install
RM ?= rm -rf

.PHONY: all install uninstall reinstall

all:
	@echo "Nothing to build. Use: make install"

install:
	$(INSTALL) -d "$(DESTDIR)$(DATADIR)"
	$(INSTALL) -d "$(DESTDIR)$(BINDIR)"
	$(INSTALL) -m 755 ldicons.py "$(DESTDIR)$(DATADIR)/ldicons.py"
	$(INSTALL) -m 644 ldicons.conf "$(DESTDIR)$(DATADIR)/ldicons.conf"
	$(INSTALL) -m 644 Not-Found-Icon.svg "$(DESTDIR)$(DATADIR)/Not-Found-Icon.svg"
	cp -r locale "$(DESTDIR)$(DATADIR)/"
	cp -r protocols "$(DESTDIR)$(DATADIR)/"
	printf '%s\n' '#!/usr/bin/env sh' \
		'exec "$(PYTHON)" "$(DATADIR)/ldicons.py" "$$@"' \
		> "$(DESTDIR)$(BINDIR)/ldicons"
	chmod 755 "$(DESTDIR)$(BINDIR)/ldicons"

uninstall:
	$(RM) "$(DESTDIR)$(BINDIR)/ldicons"
	$(RM) "$(DESTDIR)$(DATADIR)"

reinstall: uninstall install
