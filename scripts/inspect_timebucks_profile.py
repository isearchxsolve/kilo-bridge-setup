r"""inspect_timebucks_profile.py - Check required profile fields on TimeBucks.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "profile_inspect")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=settings&tab=profile"
    print("Navigating to profile settings:", url)
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3.5)

    shot = lane.shot(client, "timebucks_profile_settings")
    print("Profile settings shot:", shot)

    fields = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            return inputs.map(i => ({
                tag: i.tagName,
                name: i.name || '',
                id: i.id || '',
                type: i.type || '',
                value: i.value || '',
                placeholder: i.placeholder || '',
                disabled: i.disabled
            })).filter(x => x.type !== 'hidden');
        })()
    """)
    print("PROFILE FIELDS:\n", json.dumps(fields, indent=2))
