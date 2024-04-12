#!/home/neil/CoinbaseCLI/venv/bin/python3
import sys
from argparse import ArgumentParser
from uuid import uuid4
from json import dumps

import pandas as pd
from coinbase.rest import RESTClient


pd.options.display.max_rows = 20
pd.options.display.float_format = '{:.6f}'.format

# currency_formatter = '$ {:,.2f}'.format
currency_formatter = '{:.2f}'.format
base_size_formatter = '{:.8f}'.format
quote_size_formatter = '{:.2f}'.format
limit_price_formatter = '{:.2f}'.format


def time_formatter(time_string):
    return time_string[:19]


def parse_args(cli_args=None):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-commands')
    parser.set_defaults(
        assets=False,
        portfolios=False,
        list_portfolios=False,
        balance_portfolio=False,
        create_portfolio=False,
        delete_portfolio=False,
        move_portfolio=False,
        price=False,
        fees=False,
        fills=False,
        orders=False,
        cancel=False,
        order_id=None,
        market=False,
        limit=False,
    )

    parser_assets = subparsers.add_parser('assets', help='List of assets with available balances')
    parser_assets.set_defaults(assets=True)

    parser_portfolios = subparsers.add_parser('portfolios', help='Portfolios')
    parser_portfolios.set_defaults(portfolios=True)
    portfolio_subparsers = parser_portfolios.add_subparsers()
    list_portfolios = portfolio_subparsers.add_parser('list', help='List portfolios')
    list_portfolios.set_defaults(list_portfolios=True)
    balance_portfolio = portfolio_subparsers.add_parser('balance', help='Balance for Portfolio UUID')
    balance_portfolio.set_defaults(balance_portfolio=True)
    balance_portfolio.add_argument('uuid', type=str,
                                   help='UUID of portfolio')
    create_portfolio = portfolio_subparsers.add_parser('create', help='Create portfolio')
    create_portfolio.set_defaults(create_portfolio=True)
    create_portfolio.add_argument('name', type=str,
                                  help='Name of portfolio to create')
    delete_portfolio = portfolio_subparsers.add_parser('delete', help='Delete portfolio')
    delete_portfolio.set_defaults(delete_portfolio=True)
    delete_portfolio.add_argument('uuid', type=str,
                                  help='UUID of portfolio to delete')
    move_portfolio = portfolio_subparsers.add_parser('move', help='Move funds between portfolios')
    move_portfolio.set_defaults(move_portfolio=True)
    move_portfolio.add_argument('value', type=float,
                                help='Value of funds to move')
    move_portfolio.add_argument('currency', choices=['usd', 'btc', 'USD', 'BTC'], type=str,
                                help='Currency of funds to move')
    move_portfolio.add_argument('source', type=str,
                                help='Move from FROM portfolio with UUID')
    move_portfolio.add_argument('target', type=str,
                                help='Move from TO portfolio with UUID')

    parser_price = subparsers.add_parser('price', help='Get current BTC-USD price')
    parser_price.set_defaults(price=True)

    parser_fees = subparsers.add_parser('fees', help='Get current fees')
    parser_fees.set_defaults(fees=True)

    parser_fills = subparsers.add_parser('fills', help='Get list of fills')
    parser_fills.set_defaults(fills=True)
    parser_fills.add_argument('--limit', default=10, type=int,
                              help='limit number of fills')
    parser_fills.add_argument('--product_id', default=None, type=str,
                              help='Get fills for only PRODUCT_ID (default: All) e.g. BTC-USD')
    parser_fills.add_argument('--start', default=None, type=str,
                              help="start date or datetime (e.g. '1970-01-01')")
    parser_fills.add_argument('--end', default=None, type=str,
                              help="end date or datetime (e.g. '1970-01-01T00:00:00.000Z')")

    parser_orders = subparsers.add_parser('orders', help='Get list of orders')
    parser_orders.set_defaults(orders=True)
    parser_orders.add_argument('--limit', default=10, type=int,
                               help='limit number of orders (default: 10)')
    parser_orders.add_argument('--product_id', default=None, type=str,
                               help='Get orders for only PRODUCT_ID (default: All) e.g. BTC-USD')
    parser_orders.add_argument('--start', default=None, type=str,
                               help="start date or datetime (e.g. '1970-01-01')")
    parser_orders.add_argument('--end', default=None, type=str,
                               help="end date or datetime (e.g. '1970-01-01T00:00:00.000Z')")
    parser_orders.add_argument('--status', default=None, type=str,
                               help="filter orders on status type [OPEN, CANCELLED, FILLED]")

    parser_cancel = subparsers.add_parser('cancel', help='Cancel orders')
    parser_cancel.set_defaults(cancel=True, order_ids=None)
    parser_cancel.add_argument('order_id', type=str, nargs='*',
                               help="order_id of order to cancel, "
                                    "multiple order_ids can be specified after the flag (up to 100), "
                                    "all open orders canceled if omitted")

    parser_market = subparsers.add_parser('market', help='Market order')
    parser_market.set_defaults(market=True)
    parser_market.add_argument('side', type=str, choices=['buy', 'sell'],
                               help="BUY or SELL side market order")
    parser_market.add_argument('size', type=float,
                               help='size (in USD) of order')

    parser_limit = subparsers.add_parser('limit', help='Limit order')
    parser_limit.set_defaults(limit=True)
    parser_limit.add_argument('side', type=str, choices=['buy', 'sell'],
                               help="BUY or SELL side limit order")
    parser_limit.add_argument('size', type=float,
                              help='size (in USD) of order')
    parser_limit.add_argument('limit_price', type=float,
                              help='limit price (in USD)')

    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='verbose output')

    arguments = parser.parse_args(cli_args)
    if arguments.order_id:
        arguments.order_ids = arguments.order_id
    if arguments.verbose:
        print(arguments)
    return parser, arguments


class CoinbaseCLI(object):
    def __init__(self):
        self.client = RESTClient(key_file='./coinbase_cloud_api_key.json')

    @staticmethod
    def create_args(**kwargs):
        return kwargs

    @staticmethod
    def create_order_id():
        return str(uuid4())

    @staticmethod
    def to_iso8601(time_string):
        if time_string is not None:
            return pd.Timestamp(time_string).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def accounts(self, asset):
        accounts = self.client.get_accounts()['accounts']
        accounts_for_asset = [
            account for account in accounts if account['currency'] == asset.upper()
        ]
        for account in accounts_for_asset:
            print(f"{account['uuid']} {account['available_balance']['value']} {account['available_balance']['currency']}")
        return accounts_for_asset[0]['uuid']  # if there are multiple portfolios will this return more than one account per asset?

    def assets(self):
        accounts = self.client.get_accounts()['accounts']
        accounts_with_balance = [
            account for account in accounts if float(account['available_balance']['value']) > 0
        ]
        for account in accounts_with_balance:
            print(f"{account['uuid']} {account['available_balance']['value']} {account['available_balance']['currency']}")

    def portfolios(self):
        portfolios = self.client.get_portfolios()['portfolios']
        df = pd.DataFrame(portfolios)
        print(df.to_string(index=False))
        return df

    def portfolio_balances(self, uuid):
        breakdown = self.client.get_portfolio_breakdown(uuid)['breakdown']
        for asset in breakdown['spot_positions']:
            if asset['asset'] == 'USD':
                print(f"{asset['total_balance_fiat']} {asset['asset']}")
            if asset['asset'] == 'BTC':
                print(f"{asset['total_balance_crypto']} {asset['asset']}")

    def create_portfolio(self, name):
        portfolio = self.client.create_portfolio(name)
        df = pd.DataFrame([portfolio])
        print(df.to_string(index=False))

    def delete_portfolio(self, uuid):
        self.client.delete_portfolio(uuid)
        self.portfolios()

    def move_portfolio_funds(self, value, currency, source, target):
        print('BEFORE:')
        self.portfolio_balances(source)
        self.portfolio_balances(target)
        assert currency in ['USD', 'BTC']
        self.client.move_portfolio_funds(currency_formatter(value), currency.upper(), source, target)
        print('AFTER:')
        self.portfolio_balances(source)
        self.portfolio_balances(target)

    def deposit(self):
        pass

    def withdraw(self):
        pass

    def price(self):
        product_id = 'BTC-USD'
        product = self.client.get_product(product_id=product_id)
        print(f"{product_id} $ {float(product['price']):,.2f}")

    def fees(self):
        fees = self.client.get_transaction_summary()
        df = pd.DataFrame([fees])
        df_ = pd.DataFrame([pd.DataFrame([fees]).pop('fee_tier').values[0]])
        df = pd.concat([df.drop('fee_tier', axis=1), df_], axis=1)
        series = df[['total_volume', 'total_fees', 'pricing_tier', 'usd_from', 'usd_to', 'taker_fee_rate',
                     'maker_fee_rate']].T[0]
        print(series.to_string())

    def fills(self, order_id=None, product_id=None, start=None, end=None, limit=None):
        fills = self.client.get_fills(order_id=order_id,
                                      product_id=product_id,
                                      start_sequence_timestamp=self.to_iso8601(start),
                                      end_sequence_timestamp=self.to_iso8601(end),
                                      limit=limit)['fills']
        if not fills:
            return None
        df = pd.DataFrame(fills).astype(dtype={'price': float, 'size': float, 'commission': float})
        df = df[['trade_time', 'product_id', 'trade_type', 'side', 'price', 'size', 'commission']]
        df = df.eval('proceeds = price * size')
        df = df.eval('total_cost = proceeds + commission')
        print(df.to_string(formatters={
            'trade_time': time_formatter,
            'price': currency_formatter,
            'commission': currency_formatter,
            'proceeds': currency_formatter,
            'total_cost': currency_formatter,
        }, index=False))

    def orders(self, order_id=None, product_id=None, start=None, end=None, limit=None, status=None):
        orders = self.client.list_orders(product_id=product_id,
                                         start_date=self.to_iso8601(start),
                                         end_date=self.to_iso8601(end),
                                         limit=limit,
                                         order_status=status)['orders']
        if not orders:
            return None
        df = pd.DataFrame(orders).astype(dtype={'completion_percentage': float,
                                                'filled_size': float,
                                                'average_filled_price': float,
                                                'filled_value': float,
                                                'total_fees': float,
                                                'total_value_after_fees': float,
                                                })
        df_ = pd.concat([pd.DataFrame(_).T for _ in pd.DataFrame(orders).pop('order_configuration').values]
                        ).reset_index(names='order_type')
        df = pd.concat([df.drop(['order_configuration', 'order_type'], axis=1), df_], axis=1)
        df = df[['order_id', 'product_id', 'status', 'side', 'order_type', 'base_size', 'limit_price', 'created_time',
                 'last_fill_time', 'completion_percentage', 'filled_size', 'average_filled_price', 'filled_value',
                 'total_fees', 'total_value_after_fees']]
        if order_id:
            df = df[df['order_id'] == order_id]
        print(df.to_string(formatters={
            'created_time': time_formatter,
            'last_fill_time': time_formatter,
            'average_filled_price': currency_formatter,
            'filled_value': currency_formatter,
            'total_fees': currency_formatter,
            'total_value_after_fees': currency_formatter,
        }, index=False))
        return df

    def cancel_orders(self, order_ids=None):
        open_orders_ = self.orders(status='OPEN', limit=100)  # max orders that can be canceled in API is 100
        if open_orders_ is not None:
            open_orders_ = open_orders_['order_id'].tolist()
        else:
            open_orders_ = []
        open_orders = open_orders_
        if not open_orders:
            print('No OPEN orders')
            return
        if order_ids is None or not len(order_ids):
            order_ids = open_orders
        invalid_order_ids = []
        for order_id in order_ids:
            if order_id not in open_orders:
                print(f'order_id {order_id} not an open order')
                invalid_order_ids.append(order_id)
        order_ids = [order_id for order_id in order_ids if order_id not in invalid_order_ids]
        if order_ids:
            print(f"client.cancel_orders(order_ids=[{', '.join(order_ids)}])")
            self.client.cancel_orders(order_ids=order_ids)
        else:
            print('no orders to cancel')

    def market_order(self, side, size, product_id='BTC-USD'):
        order_args = self.create_args(side=side.upper(),
                                      product_id=product_id,
                                      quote_size=quote_size_formatter(size))
        preview = self.client.preview_market_order(**order_args)
        print('PREVIEW ORDER:')
        print(dumps(preview, indent=2))
        if not preview['errs']:
            answer = input('Submit order (y)?')
            if answer.lower() == 'y':
                order_id = self.create_order_id()
                self.client.market_order(client_order_id=order_id, **order_args)
                self.orders(order_id=order_id)

    def limit_order(self, side, size, limit_price, product_id='BTC-USD'):
        fee_rate = float(self.client.get_transaction_summary()['fee_tier']['maker_fee_rate'])
        base_size = size * (1 + fee_rate) / limit_price
        order_args = self.create_args(side=side.upper(),
                                      product_id=product_id,
                                      base_size=base_size_formatter(base_size),
                                      limit_price=limit_price_formatter(limit_price),
                                      post_only=True)
        preview = self.client.preview_limit_order_gtc(**order_args)
        print('PREVIEW ORDER:')
        print(dumps(preview, indent=2))
        if not preview['errs']:
            answer = input('Submit order (y)?')
            if answer.lower() == 'y':
                order_id = self.create_order_id()
                self.client.limit_order_gtc(client_order_id=order_id, **order_args)
                self.orders(order_id=order_id)


if __name__ == '__main__':
    parser, args = parse_args()
    cli = CoinbaseCLI()

    if args.assets:
        cli.assets()

    elif args.portfolios:
        if args.list_portfolios:
            cli.portfolios()
        elif args.balance_portfolio:
            cli.portfolio_balances(args.uuid)
        elif args.create_portfolio:
            cli.create_portfolio(args.name)
        elif args.delete_portfolio:
            cli.delete_portfolio(args.uuid)
        elif args.move_portfolio:
            cli.move_portfolio_funds(args.value, args.currency, args.source, args.target)
        else:
            parser._actions[1].choices['portfolios'].print_usage(sys.stderr)

    elif args.price:
        cli.price()

    elif args.fees:
        cli.fees()

    elif args.fills:
        cli.fills(product_id=args.product_id, start=args.start, end=args.end, limit=args.limit)

    elif args.orders:
        cli.orders(product_id=args.product_id, start=args.start, end=args.end, limit=args.limit, status=args.status)

    elif args.cancel:
        cli.cancel_orders(order_ids=args.order_ids)

    elif args.market:
        cli.market_order(side=args.side, size=args.size)

    elif args.limit:
        cli.limit_order(side=args.side, size=args.size, limit_price=args.limit_price)

    else:
        parser.print_usage(sys.stderr)
