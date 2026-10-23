r"""record_captcha_gate.py - Record BLOCKED ledger entry for Clicks CAPTCHA gate.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "clicks_captcha")
lane.row(
    source="https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads",
    role="microtask_worker",
    company="TimeBucks",
    score=1,
    step="clicks_captcha_gate",
    status=T.BLOCKED,
    receipt=lane.evid / "timebucks_clicks_unlocked_view.png",
    note="1-time CAPTCHA required to display click campaigns. Waiting for operator click."
)
print("Ledger recorded BLOCKED for Clicks CAPTCHA gate.")
