import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

survey_link = (
    "https://web.timesurveys.com/entry/"
    "ZXlKcGRpSTZJblZoYldSUVRuRlJNRmR6VWtKM05WWnRZV3hIZW1jOVBTSXNJbTFoWXlJNklqRTBOVEF4TldSa00yRmxaR000TURReU5XWTFNRFl5Wm1OaU5XUXlNMlJoTkdKa05UazNOams1WVdFMU5qTmhOVE16TlRNeU1HWTBOMkU0TmpsaVpHTWlMQ0oyWVd4MVpTSTZJblpqUjFadFZXWk5TVWhJTkVFMmNUQklaMUJKYjNSa0swMUtSREUyV0RCSlJtY3piVFF3U0hoa1lWbzVhVEJzUlc5eU0yTk5WSFpFVGtkd1ZrWlZkVEJFUWxGVlVrOWxSbXBQT0cxTFZtUTRNVEJVWVVoalZGbHBOa0ZWTVUxWVVFZE9WV3R1ZVdOeE5FcDJiMVl4WTJsTWNXWmFaSGR5Y1ZGNVFrWXhaVlZCVEVSTE1XaGlhV3RaZWtVd1puWnRlRFJZYVc1alp6ZDJVakUzZEZOdFpHRlVXRTlaVlVWYVNIRXpTa0Y0Y0ZaR2VYQTRTMVZMZWpCamJrOWtUbTlCVmtZNGJYaHNkM1pyU0hGS1RFZDJRM1ZQYm5WbVNHOHdhV3hKTUd3d1FrTmhObmRHUmt0RVdHUXlSRkpKYWt0cU5WRmlVa2xETW5KWFRWQXpkbFUzWlVkSWVWSkNPRmtyWlZkbVNWRndkMDByVmtrcmVTOVpkRFJQVEV4a1MxUndPR0ZVVVRoS09FaGFOWG93VUU1VFRHVXJZMmd5VDJwS1FuWnRXRUpYV2xGcmRYcHNUbmc1V0VjeWRUazFUbUp1YVVSMVpXbDFlRzh2YTIxMGIzbzNVVmhKTUdaMmRsWXhMM0J5WVhSclZFOWFUalJJY1RsSGJFWkNNbFJIUTNsUU1GRjZSelJEUld0aGFHUnZNRWQyTjNWVFZITlZaRXBxWVVsUlRtdEZPVnB1WVN0M2VFeE9NVFJ0YVhCVU1tWldUbkJETW5GSllYZFlOMHBQVDFaRmFtZGlUbTU0ZERaMVpUaHZSVmRhV1VOdlVWVnllRlJ0ZUVONksyRldPWGgzWVVsaGEwMXFTMWhOVUdKWU1tTkZibGdyWlVKUldVWnFWbG96TmtsV1UxRnpPVXNyY1RWdloybHdaek5CVTNOU2JETkdZMUEzZVRVemJXdFhUWE54VVVsa1J6TnpNbGhVUkVsYVIwOTRWbmxIVDNOWVdIaDZOM1YwU0U4d1pFMWlaR05rWW5sb1UyMUJUV0p4VFRkblR6ZzBOaXRVYmxwR1FtNHlNMk54TDNWNFkzZDZWMVZ2TlUxNGQzRTRlVVpDZVRKNFNuTmFTREJRUnpCM1ZYRTFWU3QwVDNORVVGZHpWM2xIY1ZsTE9GZFFVMGh5YkZGRGRXOWlaekUyUlhZd05IUlJlamhOU21wSVlWQm5ZVmRxSzJWYU9FRk1jRmt4WTFvMWJXbDNWVlIyVDBkVmJURmtUbkZ5VjBFMFp6aE5ORmswTkdwQ1oyaE9Wek4yV1ZCUlFtUkpXVVF5VG5sRmFDdEdTelV4WW5CUmVHc3dNRU56T1ZwVU1WcE1TMFF3UnlKOQ"
    "?fid=01M4H2S1D6QHVTY88EJJENJVCZ&slot=1"
)

lane = T.Lane("timebucks", "navigate_primesurvey")
with T.session(lane) as client:
    print("Navigating to survey entry link...")
    client.call_tool("browser_navigate", {"url": survey_link})
    time.sleep(6)

    info = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(el => ({
                tag: el.tagName,
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                val: (el.value || el.innerText || '').trim()
            })).filter(x => x.val.length > 0 && x.val.length < 50);

            return {
                url: window.location.href,
                title: document.title,
                inputs: inputs.slice(0, 15),
                bodySample: document.body.innerText.slice(0, 1200)
            };
        })()
    """)
    print("SURVEY ENTRY PAGE:\n", json.dumps(info, indent=2))
    shot = lane.shot(client, "timebucks_primesurvey_entry")
    print("Screenshot saved to:", shot)
