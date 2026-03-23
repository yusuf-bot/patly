# patly

**Gasless Polymarket position redemption. $0.01 per redemption, deducted from your winnings.**

```python
import patly, os
patly.init(api_key=os.getenv("PATLY_API_KEY"), pk=os.getenv("PK"))
patly.redeem("btc-updown-15m-1774088100", "NO")
```

That's it.

---

## How it works

When you call `patly.redeem()`, the library:

1. Fetches the market's `conditionId` from Patly
2. Verifies the market is resolved on-chain
3. Builds a **Safe multisend transaction** containing:
   - `redeemPositions()` — claims your winning USDC into your wallet
   - `USDC.transfer($0.01 → Patly)` — fee, paid from your winnings
4. Signs the transaction **locally** with your private key
5. Sends only the **signature** to Patly — never the key
6. Patly relays it through Polymarket's gasless Builder relayer

Everything is **gasless** (Polymarket pays gas) and **atomic** — the fee only goes through if the redemption succeeds.

---

## Installation

```bash
pip install patly
```

---

## Quickstart

### 1. Register

```python
import requests

r = requests.post("http://patly.duckdns.org/register", json={
    "wallet": "0xYourPolymarketWallet"
})
print(r.json())
# {"api_key": "...", "wallet": "0x...", "message": "Save your API key"}
```

### 2. Set env vars

```env
PATLY_API_KEY=your_api_key_here
PK=0xyour_polymarket_wallet_private_key
```

### 3. Redeem

```python
import patly, os
from dotenv import load_dotenv

load_dotenv()

patly.init(
    api_key=os.getenv("PATLY_API_KEY"),
    pk=os.getenv("PK"),
)

patly.redeem("btc-updown-15m-1774088100", "NO")
# [patly] ✅ btc-updown-15m-1774088100: 0xabc123...
```

---

## API

### Module-level (recommended)

```python
import patly

patly.init(api_key="...", pk="0x...")

patly.redeem("btc-updown-15m-1774088100", "YES")
```

### Class API

```python
from patly import Patly

p = Patly(api_key="...", pk="0x...", url="http://patly.duckdns.org")

# Redeem a position
result = p.redeem("btc-updown-15m-1774088100", "NO")
# {"status": "redeemed", "tx_hash": "0x...", "polygonscan": "https://..."}

# Account stats
p.status()
# {"wallet": "0x...", "redeemed": 12, "pending": 0, "failed": 0}

# History
p.history(limit=20)
# [{"slug": "...", "won_side": "NO", "tx_hash": "0x...", "status": "redeemed", ...}]
```

---

## Bot integration example

```python
import patly, os, logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

patly.init(
    api_key=os.getenv("PATLY_API_KEY"),
    pk=os.getenv("PK"),
)

def on_market_resolved(slug: str, won_side: str):
    patly.redeem(slug, won_side)
```

---

## Security

| Action | Where it happens |
|--------|-----------------|
| Build `redeemPositions()` calldata | Your machine |
| Build fee transfer calldata | Your machine |
| Sign Safe transaction with PK | Your machine |
| Transmit to Patly | Signature only — never the PK |

You can verify with Wireshark or Charles Proxy that no private key bytes are transmitted.

---

## Pricing

| | |
|--|--|
| Registration | Free |
| Per redemption | $0.01 USDC |
| How it's paid | Bundled into your redeem tx — from winnings |
| Separate balance needed | ❌ No |
| Gas needed | ❌ No (gasless via Polymarket relayer) |

---

## Requirements

- Python 3.10+
- A Polymarket wallet with winning positions to redeem
- `py_builder_relayer_client` (Polymarket's Safe signing SDK)

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `PATLY_API_KEY` | Your Patly API key |
| `PK` | Private key of your Polymarket wallet |

---

## Service

- **Network**: Polygon (eip155:137)
- **API**: http://patly.duckdns.org
- **Docs**: https://patly.mintlify.app