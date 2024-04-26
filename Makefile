.PHONY: clean install install-menu uninstall

clean:
	pip uninstall coinbase-cli
	rm -rf build/ coinbase_cli.egg-info/
	#rm -rf coinbase_cli.egg-info/ build/ ~/.local/lib/python3.10/site-packages/coinbase_cli*

install:
	pip install .

INSTALL_DESKTOP = "$${HOME}"/.local/share/applications
INSTALL_ICON = "$${HOME}"/.local/share/icons/hicolor/scalable/apps
TERMINAL=x-terminal-emulator

install-menu:
	mkdir -p $(INSTALL_DESKTOP)
	mkdir -p $(INSTALL_ICON)
	install -m 644 -p share/icons/hicolor/scalable/apps/icon-buy-and-sell.svg $(INSTALL_ICON)/icon-buy-and-sell.svg
	desktop-file-install --dir=$(INSTALL_DESKTOP) \
						 -m 644 \
						 --set-key=Exec --set-value="$(TERMINAL) --geometry 250x60+800+300 -e coinbase" \
						 --set-icon=$(INSTALL_ICON)/icon-buy-and-sell.svg \
						 share/applications/coinbase.desktop

uninstall:
	cd $(HOME) && pip uninstall coinbase-cli
