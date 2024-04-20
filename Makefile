.PHONY: clean install

clean:
	pip uninstall coinbase-cli
	rm -rf build/ coinbase_cli.egg-info/
	#rm -rf coinbase_cli.egg-info/ build/ ~/.local/lib/python3.10/site-packages/coinbase_cli*

install:
	pip install .
