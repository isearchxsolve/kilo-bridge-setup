r"""timebucks_auto_runner.py - Automated microtask worker for TimeBucks.

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
import re
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

BASE_URL = "https://timebucks.com"
EARN_URL = f"{BASE_URL}/publishers/index.php?pg=earn"
CLICKS_URL = f"{BASE_URL}/publishers/index.php?pg=earn&tab=view_content_ads"
SLIDES_URL = f"{BASE_URL}/publishers/index.php?pg=earn&tab=slideshows"
PUSH_URL = f"{BASE_URL}/publishers/index.php?pg=earn&tab=push_clicks"
PAYMENT_SETTINGS_URL = f"{BASE_URL}/publishers/index.php?pg=setting#paypal-changes"
TASKS_URL = f"{BASE_URL}/publishers/index.php?pg=earn&tab=tasks_tasks"


class TimeBucksRunner:
    def __init__(self, lane: T.Lane):
        self.lane = lane

    def check_auth_and_balance(self, client) -> dict:
        """Inspects current session to determine if logged in and extracts balance."""
        client.call_tool("browser_navigate", {"url": EARN_URL})
        time.sleep(3.5)
        page = T.read_page(client)
        url = page.get("url", "")
        body = page.get("body", "")
        title = page.get("title", "")

        wall_token = self.lane.wall(body, title)
        is_login = "login" in url.lower() or "signup" in url.lower() or "sign up" in body.lower()[:300]
        has_cloudflare = "verifying" in body.lower() or "cloudflare" in body.lower()

        if wall_token or (is_login and "earn" not in url.lower()):
            shot_path = self.lane.shot(client, f"timebucks_blocked_{int(time.time())}")
            self.lane.row(
                source=url,
                role="microtask_worker",
                company="TimeBucks",
                score=0,
                step="auth_check",
                status=T.BLOCKED,
                receipt=shot_path,
                note=f"Login gate or CAPTCHA detected: {wall_token or 'Login screen'}"
            )
            return {"authenticated": False, "reason": "Login/CAPTCHA wall", "receipt": str(shot_path)}

        # Extract balance via JS DOM evaluation
        balance_info = client._js("""
            (function() {
                var text = document.body.innerText || '';
                var match = text.match(/Wallet:\\s*\\$([0-9\\.]+)/i) ||
                            text.match(/Balance:\\s*\\$([0-9\\.]+)/i) ||
                            text.match(/\\$([0-9\\.]+\\d)/);
                var balVal = match ? match[1] : null;

                var balEl = document.querySelector('.current_balance, #current_balance, .wallet-balance, .header-balance');
                if (balEl) balVal = balEl.innerText.replace(/[^0-9.]/g, '');

                return {
                    found: !!balVal,
                    balance: balVal || '0.00'
                };
            })()
        """)

        shot_path = self.lane.shot(client, f"timebucks_earn_dashboard_{int(time.time())}")
        self.lane.row(
            source=url,
            role="microtask_worker",
            company="TimeBucks",
            score=1,
            step="auth_check",
            status=T.OK,
            receipt=shot_path,
            note=f"Authenticated. Current balance: ${balance_info.get('balance', 'unknown')}"
        )

        return {
            "authenticated": True,
            "balance": balance_info.get("balance", "0.00"),
            "url": url,
            "receipt": str(shot_path)
        }

    def run_clicks_tab(self, client, max_clicks: int = 5) -> int:
        """Executes available view content / click ads."""
        self.lane.log("--- Executing Clicks Tab ---")
        client.call_tool("browser_navigate", {"url": CLICKS_URL})
        time.sleep(3.5)

        page = T.read_page(client)
        if "captcha required" in page.get("body", "").lower():
            shot = self.lane.shot(client, f"timebucks_clicks_captcha_{int(time.time())}")
            self.lane.row(
                source=CLICKS_URL,
                role="microtask_worker",
                company="TimeBucks",
                score=1,
                step="clicks_captcha_gate",
                status=T.BLOCKED,
                receipt=shot,
                note="1-time CAPTCHA required to display click campaigns. Waiting for operator click."
            )
            self.lane.log("[ACTION REQUIRED] 1-time CAPTCHA required on Clicks tab. Please confirm on Chrome window.")
            return 0

        completed = 0
        for i in range(max_clicks):
            # Probe available view buttons
            offer_data = client._js("""
                (function() {
                    var buttons = Array.from(document.querySelectorAll('input[type="submit"], input[type="button"], button, a.btn'));
                    var viewBtn = buttons.find(b => {
                        var txt = (b.value || b.innerText || '').toLowerCase().trim();
                        return txt === 'view' || txt.includes('view ad') || txt === 'click';
                    });
                    if (!viewBtn) return {found: false};

                    // Extract offer payout and timer if available
                    var row = viewBtn.closest('tr, .offer_row, .card, div');
                    var rowText = row ? row.innerText : '';
                    return {
                        found: true,
                        text: rowText.slice(0, 200)
                    };
                })()
            """)

            if not offer_data or not offer_data.get("found"):
                self.lane.log(f"No more view buttons found on clicks tab after {completed} tasks.")
                break

            self.lane.log(f"Found click offer: {offer_data.get('text', '')[:60]}... Clicking View.")
            
            # Click View button
            click_res = client._js("""
                (function() {
                    var buttons = Array.from(document.querySelectorAll('input[type="submit"], input[type="button"], button, a.btn'));
                    var viewBtn = buttons.find(b => {
                        var txt = (b.value || b.innerText || '').toLowerCase().trim();
                        return txt === 'view' || txt.includes('view ad') || txt === 'click';
                    });
                    if (viewBtn) {
                        viewBtn.click();
                        return true;
                    }
                    return false;
                })()
            """)

            if not click_res:
                break

            # Pacing wait for timer (ad view countdown: default 10-15s)
            self.lane.log("Waiting 12s for view timer countdown...")
            time.sleep(12)

            # Switch back to main tab if a new tab was opened
            tabs = client.list_tabs()
            if len(tabs) > 1:
                # Find the TimeBucks tab and switch back
                for t in tabs:
                    if "timebucks.com" in t.get("url", ""):
                        client.switch_tab(t["id"])
                        break

            completed += 1
            shot = self.lane.shot(client, f"timebucks_click_done_{completed}_{int(time.time())}")
            self.lane.row(
                source=CLICKS_URL,
                role="microtask_worker",
                company="TimeBucks",
                score=1,
                step=f"click_ad_{completed}",
                status=T.APPLIED_STEP,
                receipt=shot,
                note=f"Completed click ad #{completed}"
            )
            time.sleep(2)

        return completed


def main():
    parser = argparse.ArgumentParser(description="TimeBucks automated microtask runner.")
    parser.add_argument("--check-auth", action="store_true", help="Check login status and balance.")
    parser.add_argument("--max-tasks", type=int, default=10, help="Max tasks per cycle.")
    parser.add_argument("--loop", action="store_true", help="Run continuously with pacing.")
    args = parser.parse_args()

    lane = T.Lane("timebucks", "auto_runner")
    runner = TimeBucksRunner(lane)

    with T.session(lane) as client:
        status = runner.check_auth_and_balance(client)
        lane.log(f"Auth status: {json.dumps(status, indent=2)}")

        if not status.get("authenticated"):
            lane.log("[ACTION REQUIRED] Operator must complete login/CAPTCHA on Chrome Profile 17.")
            sys.exit(1)

        if args.check_auth:
            lane.log("Check-auth mode finished.")
            return

        clicks_done = runner.run_clicks_tab(client, max_clicks=args.max_tasks)
        lane.log(f"Cycle completed. Total clicks done: {clicks_done}")
        lane.summary()


if __name__ == "__main__":
    main()
