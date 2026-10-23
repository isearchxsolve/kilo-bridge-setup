r"""get_youtube_user_name.py - Check logged in YouTube channel name.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "yt_user")
with T.session(lane) as client:
    res = client._js(r"""
        (function() {
            var avatar = document.querySelector('button#avatar-btn, #avatar-btn');
            var signIn = document.querySelector('a[aria-label*="Sign in"], a[href*="accounts.google.com"]');
            var img = avatar ? avatar.querySelector('img') : null;
            return {
                avatarFound: !!avatar,
                avatarAlt: img ? img.alt : null,
                avatarSrc: img ? img.src : null,
                signInFound: !!signIn
            };
        })()
    """)
    print("YT AUTH STATE:", json.dumps(res, indent=2))
