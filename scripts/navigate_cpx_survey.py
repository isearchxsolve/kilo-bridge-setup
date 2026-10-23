r"""navigate_cpx_survey.py - Navigate directly to $1.35 CPX survey URL and inspect.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

cpx_url = (
    "https://web.timesurveys.com/entry/"
    "ZXlKcGRpSTZJbkJTTVRBMkwxcEplRVJoYjNWcWVVdzFiazFOVEdjOVBTSXNJbTFoWXlJNkltVmxZVFUyWkdWaU16TTNPREJqWVRSaFptSTFPR000TWpZM1kyUm1aR1U0T0RjelpqRTJZVGxtWkRRMk5USTRZMlkxTldGbU1qSXdZVGc1WkRjeVlqZ2lMQ0oyWVd4MVpTSTZJbnBuT1VkVVdWRkxUa2xNTVZkSlZYTTVTbFl6YVVKT1EzVlNXWGhhZUVFMFptNVNiQ3RGSzBwYU5YaHlZMDFpUm1WeGNuSXplV3N3ZVM4MU5IUlZibGh5WjBSRFdUZE9lR3hXV0RKeU0zcFRRVU50UTNaalVuaEhRVEF3UVhZek0yWXpTSFJuYnpCTk1XRmpSSFJ4ZGxSd2RXZFllREpCTURGbFQzRnZVazVsYW5kNmRVcFNjbWxoUlVoTFZraFRWbWt4WjNKRmVEaEhNMWhvU0RST01rbDFPVmhKTTBsV1ZEVlRjQzgxTXpKclNXSjJNRmhZTWxZclQyVm9aVFp1UzNjemMyczJORmgwTlRSVk4zcHJTUzk1VERGU1lVMXJOMVJVV0RKRFdHWTBRVUkzTVdKaVpYcERUMUZzTkRoVlVWbG9PSFI2WTNOWGRXUlFTemc0WW1zeGExcElaWGRDVm5sbFNHTk9jalk1WlVsalNraDZZbVpLTm5jNGFVcDNaREUzVTNkRmJXZ3JjMlk0Vmt4RVYxRkhabTQwWTNGbmJXRjZiM2xHUVcxa1RsZHBOQzluVXpoaWVrSktibTVJSzBwSFRDdDFkalp1Tm5STmNFbGljRU41VkZGMWIyMUpVREZ4ZUUxek4wVm5lalVyWm1ONGNtWXlZWGhLYWpaV1ZURnBZMjh5V0RCUmRVSmFlSGQzVjI5WGNIQlhhVVJUWXpNdlp6SmxNbUpaU0hWeFEwdFdaVUpETUU1QlNWVk1abWw1VlhoaGMzUlJUMGx0TUVaUFIwUnNhMnAxTVRSR1VGZFdhazFJY2twR1dFaE5NM0Z0TUV4SWFrSmpOVEpPWVVscloxUjBTVk5zWW5WMFptOUZXVU5LZFdkMGNEUlRlUzgxUkZocWJGSnphR2gxVTBOVVdrWm1LMDlHV1UxT1JVZFVSRVIzUVQwOUluMD0"
    "?fid=01M4H0WS04B8W36JM91DPQEESC&slot=20"
)

lane = T.Lane("timebucks", "navigate_cpx")
with T.session(lane) as client:
    print("Navigating directly to CPX survey URL...")
    client.call_tool("browser_navigate", {"url": cpx_url})
    time.sleep(5)

    info = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id || '',
                val: (el.value || el.innerText || '').trim()
            })).filter(x => x.val.length > 0 && x.val.length < 50);

            return {
                url: window.location.href,
                title: document.title,
                inputs: inputs.slice(0, 15),
                bodySnippet: document.body.innerText.slice(0, 1200)
            };
        })()
    """)

    print("CPX SURVEY DIRECT PAGE INFO:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "timebucks_cpx_survey_direct_view")
    print("Screenshot:", shot)
