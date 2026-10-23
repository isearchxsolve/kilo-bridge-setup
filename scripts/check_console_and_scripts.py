r"""check_console_and_scripts.py - Check why captcha is not loading.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "console_check")
with T.session(lane) as client:
    url = "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(3)

    debug_data = client._js(r"""
        (function() {
            var scripts = Array.from(document.querySelectorAll('script')).map(s => s.src).filter(Boolean);
            var captchaScripts = scripts.filter(s => s.includes('captcha') || s.includes('turnstile') || s.includes('cloudflare') || s.includes('hcaptcha'));

            // Check if there is an element with id or class turnstile
            var cfDiv = document.querySelector('.cf-turnstile, #cf-turnstile, .g-recaptcha, .h-captcha');

            return {
                allScriptCount: scripts.length,
                captchaScripts: captchaScripts,
                cfDivFound: !!cfDiv,
                cfDivHTML: cfDiv ? cfDiv.outerHTML : null
            };
        })()
    """)
    print("DEBUG DATA:\n", json.dumps(debug_data, indent=2))
