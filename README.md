# Coinbase CLI

A Command Line Interface to interact with the Coinbase Advance API via the official "Coinbase Advanced API Python SDK" from Coinbase. This CLI provides a simple way to interact with the API via a command line with a limited subset of commands that are useful for manually submitting trades and tracking orders.

This is useful at times of high load when the website becomes unstable but the API remains responsive. Additionally, some functionality, such as portfolios, is only available via the API and not via the website.

## Usage
The CLI can be used as single use commands, or via a shell which enables multiple commands while retaining command history and providing tab completions.

### Single commands
Single use commands are available for the following.

#### Main command
```text
Usage: coinbase [-h] [-v] {product, assets, portfolios, price, fees, fills, orders, cancel, market, limit} ...

subcommands:
  {product, assets, portfolios, price, fees, fills, orders, cancel, market, limit}
    product             Get/Set product_id
    assets              List of assets with available balances
    portfolios          Portfolios
    price               Get current BTC-USD price
    fees                Get current fees
    fills               Get list of fills
    orders              Get list of orders
    cancel              Cancel orders
    market              Market order
    limit               Limit order
```

Some examples of the sub-commands. Full sub-command help can be found using the help command line flag after the sub-command.
#### Portfolios sub-command
```text
Usage: coinbase portfolios [-h] {list, balance, create, delete, move} ...

subcommands:
  {list, balance, create, delete, move}
    list                List portfolios
    balance             Balance for Portfolio UUID
    create              Create portfolio
    delete              Delete portfolio
    move                Move funds between portfolios
```

#### Market sub-command
```text
Usage: coinbase market [-h] {buy, sell} size

positional arguments:
  {buy, sell}  BUY or SELL side market order
  size         size (in USD) of order
```

#### Limit sub-command
```text
Usage: coinbase limit [-h] {buy, sell} size limit_price

positional arguments:
  {buy, sell}  BUY or SELL side limit order
  size         size (in USD) of order
  limit_price  limit price (in USD)
```

### Shell
Alternatively, by entering just the command `coinbase`, without arguments, one can enter a shell which follows the same syntax as the single use commands without needing to type coinbase before each sub-command, and includes shell history and tab completion.

```shell
$ coinbase 
```
```text
Coinbase API Interactive Shell
(coinbase) help

Documented commands (use 'help -v' for verbose/'help <topic>' for details):

Coinbase
========
assets  coinbase  fills  market  portfolios  product
cancel  fees      limit  orders  price     
```
Use the tab completion to discover the commands and get hints for the arguments required. The `help` or `?` command before any command prints the help from the argument parser for that sub-command. Typing `help coinbase` or just `coinbase` will print the help from the main argument parser as seen in the single use commands section above. The `help` command alone just displays the help as formatted by `cmd2.Cmd` as seen here.

## Requirements

The requirements are listed in `requirements.txt` and are installed via `pip`.
```requirements.txt
coinbase-advanced-py
cmd2
pandas
```

* `coinbase-advanced-py` is the official Coinbase Advanced API Python SDK (https://coinbase.github.io/coinbase-advanced-py/).
* `cmd2` is an extension of `cmd` from the standard library, which provide a line-oriented command interpreter, but extends upon it to provide operability with the `argparse` module for building the command line argument parser (https://cmd2.readthedocs.io/en/latest/).
* `pandas` is used for table formatting of output (https://pandas.pydata.org/docs/index.html).

## API Key

An API key from Coinbase Advanced Trading needs to be generated (https://docs.cloud.coinbase.com/advanced-trade-api/docs/rest-api-auth#creating-trading-keys), downloaded and saved to root directory.

## Installation

Clone the repository.
```shell
git clone https://github.com/neilsummers/coinbase-cli.git
cd coinbase-cli
```

The CLI can be installed via pip.
```shell
pip install .
```
The executable `coinbase` is installed your local bin location which is typically `~/.local/bin`. The key is saved in the python library install location.

Additionally, a `Makefile` is provided for install, which also contains a linux menu entry.
```shell
make install
make install-menu
```
You can customize the terminal program used with
```shell
make TERMINAL=xfce4-terminal install-menu
```

### Uninstall

The key and executable can be removed using
```shell
pip uninstall coinbase-cli
```
Note that this will not work from the root directory.

Alternatively, use the makefile command which works around this limitation.
```shell
make uninstall
```
