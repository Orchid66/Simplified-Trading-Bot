# Binance Futures Testnet — Trading Bot

A clean, minimal Python CLI application for placing orders on Binance USDT-M Futures Testnet.

---

## Features

| Requirement | Status |
|---|---|
| Market orders (BUY / SELL) | ✅ |
| Limit orders (BUY / SELL) | ✅ |
| Stop-Market orders *(bonus)* | ✅ |
| CLI with argparse validation | ✅ |
| Structured code (client / orders / validators / logging) | ✅ |
| Rotating log file (`logs/trading_bot.log`) | ✅ |
| Exception handling (API errors, network failures, bad input) | ✅ |
| Clear console output with request summary + response details | ✅ |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # BinanceClient — HMAC signing, HTTP layer, error types
│   ├── orders.py          # Order building, submission, and pretty-printing
│   ├── validators.py      # Input validation (raises ValidationError on bad input)
│   └── logging_config.py  # Rotating file + console logging setup
├── cli.py                 # CLI entry point (argparse)
├── logs/
│   ├── market_order.log   # Sample log — MARKET order
│   └── limit_order.log    # Sample log — LIMIT order
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Register on Binance Futures Testnet

1. Go to <https://testnet.binancefuture.com>
2. Sign in with your GitHub account.
3. Click **"Generate API Key"** — copy and store your key and secret.

### 2. Clone / unzip the project

```bash
git clone https://github.com/<your-username>/trading_bot.git
cd trading_bot
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set your API credentials

The bot reads credentials from environment variables — never hard-code them.

**macOS / Linux (bash / zsh):**
```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

**Windows (PowerShell):**
```powershell
$env:BINANCE_API_KEY = "your_testnet_api_key"
$env:BINANCE_API_SECRET = "your_testnet_api_secret"
```

---

## How to Run

### General syntax

```
python cli.py --symbol SYMBOL --side BUY|SELL --type MARKET|LIMIT|STOP_MARKET \
              --quantity QTY [--price PRICE] [--stop-price STOP_PRICE]
```

| Flag | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Trading pair (e.g. `BTCUSDT`, `ETHUSDT`) |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` | ✅ | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | ✅ | Amount in base asset (e.g. `0.001` BTC) |
| `--price` | LIMIT only | Limit price |
| `--stop-price` | STOP_MARKET only | Stop trigger price |
| `--base-url` | ❌ | Override API base URL (default: testnet) |

---

### Example 1 — Market BUY

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

**Console output:**
```
  ──────────────────────────────────────────────────────
              ORDER REQUEST
  ──────────────────────────────────────────────────────
  Symbol          : BTCUSDT
  Side            : BUY
  Type            : MARKET
  Quantity        : 0.001
  ──────────────────────────────────────────────────────

              ORDER RESPONSE
  ──────────────────────────────────────────────────────
  Order ID        : 4751823694
  Client OID      : web_yPqkXvNmJz7TrQBcFhDE
  Symbol          : BTCUSDT
  Status          : FILLED
  Type            : MARKET
  Side            : BUY
  Orig Qty        : 0.001
  Executed Qty    : 0.001
  Avg Price       : 97342.10000
  Reduce Only     : False
  Time In Force   : GTC
  Created At      : 2025-07-12 09:14:22
  ──────────────────────────────────────────────────────
  ✓  Order placed SUCCESSFULLY
```

---

### Example 2 — Limit SELL

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 105000
```

The order will appear as `NEW` on the order book and fill if the market reaches your price.

---

### Example 3 — Stop-Market BUY *(bonus order type)*

```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 95000
```

The order triggers a market buy when the price falls to (or through) `$95 000`.

---

### Example 4 — ETH Limit BUY

```bash
python cli.py --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.01 --price 3200
```

---

### Validation error example

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
# → ✗  Input Error: price is required for this order type but was not provided.
```

---

## Logging

All activity is written to `logs/trading_bot.log` (rotating, 5 MB × 3 backups):

```
2025-07-12 09:14:22 | DEBUG    | trading_bot | POST /fapi/v1/order | params={...}
2025-07-12 09:14:22 | DEBUG    | trading_bot | Response HTTP 200 | body={...}
2025-07-12 09:14:22 | INFO     | trading_bot | Order accepted → orderId=4751823694 status=FILLED
```

The **API signature is never written to the log file**.  
Sample logs for a MARKET order and a LIMIT order are included in `logs/`.

---

## Assumptions

1. **Testnet only** — the default `--base-url` points to `https://testnet.binancefuture.com`.  
   Pass `--base-url https://fapi.binance.com` to target live trading *(at your own risk)*.

2. **USDT-M Futures** — all symbols must be USDT-margined perpetuals supported by the testnet.

3. **Credentials via environment variables** — the bot does not accept keys as CLI flags  
   to avoid accidental exposure in shell history.

4. **Quantities** — the testnet enforces the same lot-size/min-notional rules as production.  
   If you get error `-1111` (invalid precision) or `-1013` (invalid quantity), check the  
   symbol's filter rules via:  
   ```bash
   curl "https://testnet.binancefuture.com/fapi/v1/exchangeInfo?symbol=BTCUSDT" | python -m json.tool
   ```

5. **No position-mode check** — the bot assumes the account is in **One-way Position Mode**  
   (the testnet default). Hedge Mode requires an additional `positionSide` parameter.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `requests` | ≥ 2.31.0 | HTTP client for REST API calls |

No third-party Binance SDK is used — all API interactions are raw HTTPS calls with  
HMAC-SHA256 signatures, which makes the code fully transparent and easy to audit.

---

## Running Tests (optional smoke test)

```bash
# Verify the validator catches a missing price for LIMIT orders
python -c "
from bot.validators import validate_order_inputs
try:
    validate_order_inputs('BTCUSDT', 'BUY', 'LIMIT', 0.001, price=None)
except Exception as e:
    print('Caught expected error:', e)
"
```
