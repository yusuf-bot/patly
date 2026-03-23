#!/usr/bin/env python3
"""
patly/client.py

Gasless Polymarket position redemption with automatic fee collection.
The server handles all signing and relaying using Builder API keys.

Usage:
    import patly, os
    patly.init(api_key=os.getenv("PATLY_API_KEY"), pk=os.getenv("PK"))
    patly.redeem("btc-updown-15m-1234567890", "YES")
"""

import logging
from typing import Optional

import requests

log = logging.getLogger("patly")

_DEFAULT_URL = "http://patly.duckdns.org"


class Patly:
    def __init__(self, api_key: str, pk: str = None, url: str = _DEFAULT_URL):
        self._api_key = api_key
        self._url     = url.rstrip("/")
        self._headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    def redeem(self, slug: str, won_side: str) -> dict:
        """
        Redeem a winning Polymarket position.
        Server handles all signing, gas, and fee collection.

        Args:
            slug:     Market slug e.g. "btc-updown-15m-1234567890"
            won_side: "YES" or "NO"

        Returns:
            {"status": "redeemed", "tx_hash": "0x...", "polygonscan": "..."}
        """
        r = requests.post(
            f"{self._url}/redeem",
            headers=self._headers,
            json={"slug": slug, "won_side": won_side.upper()},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()
        if r.status_code == 409:
            return {"status": "already_redeemed", "slug": slug}
        raise RuntimeError(f"Redeem failed: {r.status_code} {r.text[:300]}")

    def status(self) -> dict:
        r = requests.get(f"{self._url}/status", headers=self._headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def history(self, limit: int = 50) -> list:
        r = requests.get(
            f"{self._url}/redeems",
            headers=self._headers,
            params={"limit": limit},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()


# ── Module-level API ──────────────────────────────────────────────────────────

_instance: Optional[Patly] = None


def init(api_key: str, pk: str = None, url: str = _DEFAULT_URL):
    global _instance
    _instance = Patly(api_key=api_key, pk=pk, url=url)
    log.info(f"[patly] initialized")


def redeem(slug: str, won_side: str):
    if _instance is None:
        log.error("[patly] Call patly.init() first")
        return
    try:
        result = _instance.redeem(slug, won_side)
        log.info(f"[patly] ✅ {slug}: {result.get('tx_hash', result.get('status', ''))}")
    except Exception as e:
        log.error(f"[patly] ❌ {slug}: {e}")