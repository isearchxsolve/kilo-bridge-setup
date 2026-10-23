r"""inspect_youtube_profile.py - Check authenticated YouTube profile on Profile 17.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "check_yt")
with T.session(lane) as client:
    print("Navigating to https://www.youtube.com/channel/UC9SPmYqr3fGiP95b76tnUag...")
    client.call_tool("browser_navigate", {"url": "https://www.youtube.com/channel/UC9SPmYqr3fGiP95b76tnUag"})
    time.sleep(4)

    info = client._js(r"""
        (function() {
            var subBtn = document.querySelector('ytd-subscribe-button-renderer button, #subscribe-button button');
            var avatar = document.querySelector('#avatar-btn, button#avatar-btn, ytd-topbar-menu-button-renderer');
            var bodyText = document.body.innerText.slice(0, 1000);

            return {
                url: window.location.href,
                title: document.title,
                hasSubscribeBtn: !!subBtn,
                subBtnText: subBtn ? subBtn.innerText.trim() : null,
                avatarFound: !!avatar,
                bodySnippet: bodyText
            };
        })()
    """)
    print("YOUTUBE INFO:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "youtube_channel_check")
    print("Screenshot:", shot)
