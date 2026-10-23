r"""coinpayu_auto_runner.py - Automated microtask worker for CoinPayU.

Uses the hardened lane_tools layer from C:/Users/Admin/Downloads/kilo-bridge-setup.
Obeys all AGENTS.md laws:
- Screenshot = Receipt
- Never touch passwords/credentials
- Do not automate past CAPTCHAs (stops and reports BLOCKED)
- ASCII only logs and receipts
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

BASE_URL = "https://www.coinpayu.com"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
SURF_ADS_URL = f"{BASE_URL}/dashboard/ads_surf"
WINDOW_ADS_URL = f"{BASE_URL}/dashboard/ads_window"


class CoinPayURunner:
    def __init__(self, lane: T.Lane):
        self.lane = lane

    def check_auth_and_balance(self, client) -> dict:
        """Inspects current session to determine if logged in and extracts balance."""
        client.call_tool("browser_navigate", {"url": DASHBOARD_URL})
        time.sleep(3.5)
        page = T.read_page(client)
        url = page.get("url", "")
        body = page.get("body", "")
        title = page.get("title", "")

        wall_token = self.lane.wall(body, title)
        is_login = "login" in url.lower() or "rewardjoy.com" in url.lower()

        if wall_token or is_login:
            shot_path = self.lane.shot(client, f"coinpayu_blocked_{int(time.time())}")
            self.lane.row(
                source=url,
                role="microtask_worker",
                company="CoinPayU",
                score=0,
                step="auth_check",
                status=T.BLOCKED,
                receipt=shot_path,
                note=f"Login gate detected: {wall_token or 'Login redirect'}"
            )
            return {"authenticated": False, "reason": "Login wall", "receipt": str(shot_path)}

        # Extract balance via JS
        balance_info = client._js("""
            (function() {
                var text = document.body.innerText || '';
                var match = text.match(/Main Balance:\\s*([0-9,]+)\\s*Satoshi/i) ||
                            text.match(/([0-9,]+)\\s*Satoshi/i);
                return {
                    found: !!match,
                    balance: match ? match[1] : '0'
                };
            })()
        """)

        shot_path = self.lane.shot(client, f"coinpayu_dashboard_{int(time.time())}")
        self.lane.row(
            source=url,
            role="microtask_worker",
            company="CoinPayU",
            score=1,
            step="auth_check",
            status=T.OK,
            receipt=shot_path,
            note=f"Authenticated. Current balance: {balance_info.get('balance', 'unknown')} Satoshi"
        )

        return {
            "authenticated": True,
            "balance": balance_info.get("balance", "0"),
            "url": url,
            "receipt": str(shot_path)
        }


def main():
    parser = argparse.ArgumentParser(description="CoinPayU automated microtask runner.")
    parser.add_argument("--check-auth", action="store_true", help="Check login status and balance.")
    args = parser.parse_args()

    lane = T.Lane("coinpayu", "auto_runner")
    runner = CoinPayURunner(lane)

    with T.session(lane) as client:
        status = runner.check_auth_and_balance(client)
        lane.log(f"Auth status: {json.dumps(status, indent=2)}")

        if not status.get("authenticated"):
            lane.log("[ACTION REQUIRED] Operator must complete login on Chrome Profile 17.")
            sys.exit(1)

        lane.summary()


if __name__ == "__main__":
    main()
