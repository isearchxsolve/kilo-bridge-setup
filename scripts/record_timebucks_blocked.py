import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_tools as T

lane = T.Lane("timebucks", "auth_gate")
lane.row(
    source="https://timebucks.com/index.php?pg=login",
    role="microtask_runner",
    company="TimeBucks",
    score=0,
    step="login_gate",
    status="BLOCKED",
    receipt=lane.evid / "timebucks_login_modal.png",
    note="Cloudflare Turnstile CAPTCHA and credentials required. Operator human login gate."
)
print("Ledger recorded BLOCKED for timebucks auth gate.")
