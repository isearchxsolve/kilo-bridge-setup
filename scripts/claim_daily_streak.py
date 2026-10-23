r"""claim_daily_streak.py - Click 'Check In' button on Daily Streak tab to claim daily bonus.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "daily_streak")
with T.session(lane) as client:
    print("Navigating to daily_streak...")
    client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=daily_streak"})
    time.sleep(3.5)

    claim_res = client._js(r"""
        (function() {
            var checkInBtn = Array.from(document.querySelectorAll('input, button, a')).find(b => {
                var val = (b.value || b.innerText || '').trim();
                return val.includes('Check In') || val.includes('Check-in');
            });

            if (checkInBtn) {
                checkInBtn.click();
                return { clicked: true, val: checkInBtn.value || checkInBtn.innerText };
            }
            return { clicked: false };
        })()
    """)

    print("CLAIM RESULT:", json.dumps(claim_res, indent=2))
    time.sleep(3)

    shot = lane.shot(client, "timebucks_daily_streak_claimed")
    print("Screenshot saved to:", shot)

    lane.row(
        source="https://timebucks.com/publishers/index.php?pg=earn&tab=daily_streak",
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="claim_daily_streak",
        status=T.APPLIED_STEP if claim_res.get("clicked") else T.BLOCKED,
        receipt=shot,
        note=f"Daily streak check-in: {claim_res.get('clicked')}"
    )
