PREFIX := /usr

install:
	mkdir -p $(DESTDIR)$(PREFIX)/{bin,share/{applications,chronoslnx}}
	install -Dm644 *.py $(DESTDIR)$(PREFIX)/share/chronoslnx
	install -Dm644 ChronosLNX.desktop $(DESTDIR)$(PREFIX)/share/applications
	install -Dm755 chronoslnx.sh $(DESTDIR)$(PREFIX)/bin/chronoslnx
	install -Dm644 schedule.csv $(DESTDIR)$(PREFIX)/share/chronoslnx
	cp -R themes $(DESTDIR)$(PREFIX)/share/chronoslnx
