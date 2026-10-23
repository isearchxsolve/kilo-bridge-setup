r"""check_wallet_balance.py - Check TimeBucks wallet balance and earnings ledger.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "wallet_check")
with T.session(lane) as client:
    print("Navigating to https://timebucks.com/publishers/index.php?pg=earn...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn"})
    time.sleep(3)

    # Extract wallet, bonus, referral, and total earnings
    res = client._js(r"""
        (function() {
            var bodyText = document.body.innerText;
            var header = document.querySelector('header, .header, #header, .navbar');
            
            // Try to find wallet elements
            var walletEl = document.querySelector('#walletBalance, .wallet-balance, .current-balance, #headerWallet');
            
            // Extract all matches for $X.XXX
            var matches = Array.from(document.body.innerText.matchAll(/\$[\d,]+\.\d{3}/g)).map(m => m[0]);

            return {
                url: window.location.href,
                title: document.title,
                walletElText: walletEl ? walletEl.innerText : null,
                dollarMatches: matches.slice(0, 15),
                bodySnippet: bodyText.slice(0, 800)
            };
        })()
    """)

    print("WALLET & BALANCE INFO:\n", json.dumps(res, indent=2))
    shot = lane.shot(client, "timebucks_wallet_balance_live")
    print("Screenshot:", shot)
