import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("coinpayu", "inspect_click_handler")
with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": "https://www.rewardjoy.com/dashboard/ads_surf"})
    time.sleep(3)

    info = client._js(r"""
        (function() {
            var el = document.querySelector('.ags-description');
            if (!el) return { error: 'Not found' };

            // Check vue instance
            var vue = el.__vue__ || (el.parentElement && el.parentElement.__vue__) || (el.closest('.frameless-ad-box') && el.closest('.frameless-ad-box').__vue__);

            var vueMethods = [];
            var vueProps = null;
            if (vue) {
                vueProps = {
                    item: vue.item || vue.ad || vue.data,
                    timer: vue.time || vue.timer
                };
                for (var k in vue) {
                    if (typeof vue[k] === 'function') vueMethods.push(k);
                }
            }

            return {
                titleAttr: el.getAttribute('title'),
                hasVue: !!vue,
                vueProps: vueProps,
                vueMethods: vueMethods.slice(0, 20)
            };
        })()
    """)
    print("VUE INSPECTION:\n", json.dumps(info, indent=2))
