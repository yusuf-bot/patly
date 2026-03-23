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

When you call `patly.redeem()`, your private key **never leaves your machine**. Here's exactly what happens:

1. Patly fetches the market's `conditionId` and verifies it's resolved on-chain
2. A **Safe multisend transaction** is built locally on your machine containing:
   - `redeemPositions()` — claims your winning USDC
   - `USDC.transfer($0.01 → Patly)` — fee, paid from your winnings
3. The transaction is **signed locally** using your private key via `eth_account` — standard Ethereum signing, your key never moves
4. Only the **signature bytes** are transmitted to Patly — mathematically impossible to reverse into a private key
5. Patly relays the signed transaction through Polymarket's gasless Builder relayer

Your private key is used identically to how MetaMask signs transactions — it produces a signature and nothing else is transmitted.

Everything is **gasless** (Polymarket covers gas) and **atomic** — the $0.01 fee only transfers if the redemption succeeds.

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
r = requests.post("http://patly.dev/register", json={
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
p = Patly(api_key="...", pk="0x...")

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

## Bot integration
```python
import patly, os
from dotenv import load_dotenv
load_dotenv()

patly.init(
    api_key=os.getenv("PATLY_API_KEY"),
    pk=os.getenv("PK"),
)

def on_market_resolved(slug: str, won_side: str):
    patly.redeem(slug, won_side)
```

---

## Security

Your private key is used **only** to produce a cryptographic signature, locally, using Python's `eth_account` library — the same library Polymarket's own SDK uses. The signing happens in-process on your machine and the key is never serialized, logged, or transmitted.

| What happens | Where |
|---|---|
| Build `redeemPositions()` calldata | Your machine |
| Build fee transfer calldata | Your machine |
| Sign transaction with PK (via `eth_account`) | Your machine, in-process |
| What's sent to Patly | 65-byte ECDSA signature only |
| What Patly sees | Signature + slug + won_side |
| What Patly never sees | Your private key |

A valid ECDSA signature cannot be reversed to recover a private key — this is a mathematical guarantee of elliptic curve cryptography, not a policy.

You can verify this yourself by inspecting the open-source client or running a packet capture (Wireshark) — you will see the signature but never any key material.

---

## Pricing

| | |
|---|---|
| Registration | Free |
| Per redemption | $0.01 USDC |
| How it's paid | Bundled atomically into your redeem tx |
| Separate balance needed | ❌ No |
| Gas needed | ❌ No |

---

## Requirements

- Python 3.10+
- A Polymarket wallet with winning positions to redeem

---

## Environment variables

| Variable | Description |
|---|---|
| `PATLY_API_KEY` | Your Patly API key (from `/register`) |
| `PK` | Private key of your Polymarket wallet — used only for local signing |

---

## Service

- **Network**: Polygon (eip155:137)
- **API**: http://patly.dev
- **Source**: github.com/yourhandle/patly