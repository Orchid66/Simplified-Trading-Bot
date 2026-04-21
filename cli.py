#!/usr/bin/env python3
"""
cli.py — Command-line entry point for the Binance Futures trading bot.

Usage examples
──────────────
# Market BUY 0.001 BTC
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL 0.002 BTC at $100 000
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 100000

# Stop-Market BUY 0.001 BTC (triggers at $95 000)
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000

Credentials
───────────
Export your Binance Futures Testnet API credentials before running:

    export BINANCE_API_KEY="your_api_key"
    export BINANCE_API_SECRET="your_api_secret"

On Windows (PowerShell):
    $env:BINANCE_API_KEY = "your_api_key"
    $env:BINANCE_API_SECRET = "your_api_secret"
"""

import argparse
import os
import sys

from bot.client import BinanceClient, BinanceAPIError, BinanceNetworkError, TESTNET_BASE_URL
from bot.orders import place_order
from bot.validators import validate_order_inputs, ValidationError
from bot.logging_config import setup_logging

logger = setup_logging()

# ── Credential helpers ────────────────────────────────────────────────────────


def _load_credentials() -> tuple[str, str]:
    """Read API credentials from environment variables."""
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print(
            "\n  ✗  Missing credentials.\n"
            "     Set environment variables before running:\n\n"
            "       export BINANCE_API_KEY='<your key>'\n"
            "       export BINANCE_API_SECRET='<your secret>'\n"
        )
        sys.exit(1)

    return api_key, api_secret


# ── Argument parser ───────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python cli.py",
        description=(
            "──────────────────────────────────────────────────\n"
            "  Binance Futures Testnet — Trading Bot\n"
            "──────────────────────────────────────────────────\n"
            "  Supports MARKET, LIMIT, and STOP_MARKET orders.\n"
            "  Credentials are read from environment variables.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  # Market BUY\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n\n"
            "  # Limit SELL\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT "
            "--quantity 0.002 --price 100000\n\n"
            "  # Stop-Market BUY\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET "
            "--quantity 0.001 --stop-price 95000\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        required=True,
        metavar="SYMBOL",
        help="Trading pair symbol, e.g. BTCUSDT or ETHUSDT.",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order direction: BUY or SELL.",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        metavar="ORDER_TYPE",
        help="Order type: MARKET | LIMIT | STOP_MARKET.",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        metavar="QTY",
        help="Order quantity (in base asset units, e.g. 0.001 for BTC).",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=None,
        metavar="PRICE",
        help="Limit price (required for LIMIT orders, ignored for MARKET).",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        type=float,
        default=None,
        metavar="STOP_PRICE",
        help="Stop trigger price (required for STOP_MARKET orders).",
    )
    parser.add_argument(
        "--base-url",
        default=TESTNET_BASE_URL,
        metavar="URL",
        help=f"Binance API base URL (default: {TESTNET_BASE_URL}).",
    )

    return parser


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # 1. Validate inputs ───────────────────────────────────────────────────────
    try:
        symbol, side, order_type, quantity, price, stop_price = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        logger.error(f"Validation error: {exc}")
        print(f"\n  ✗  Input Error: {exc}\n")
        parser.print_usage(sys.stderr)
        sys.exit(1)

    # 2. Load credentials & build client ──────────────────────────────────────
    api_key, api_secret = _load_credentials()
    client = BinanceClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url=args.base_url,
    )
    logger.info(f"Client ready → base_url={args.base_url}")

    # 3. Place the order ───────────────────────────────────────────────────────
    try:
        place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except (BinanceAPIError, BinanceNetworkError, ValueError):
        sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
