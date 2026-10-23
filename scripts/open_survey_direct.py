r"""open_survey_direct.py - Open the survey URL directly via browser_navigate.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "survey_direct")
survey_url = "https://web.timesurveys.com/entry/ZXlKcGRpSTZJblpZTW5WT2FWTXZSRmhIZVhwU1JYbG9PVFV6Tm5jOVBTSXNJbTFoWXlJNklqSmxaak5pTVRjMU1qTmhabU0yTURFeVptWXdNVFl3TnpaaU5XVmtZV1JrT0RJeE0ySTBZbVF5Wm1JMk1UZG1OMlV3WVRJeVlqUmhNVEJpWlRsak9USWlMQ0oyWVd4MVpTSTZJbVpVWkZaMGEwbFVkMm80TUc1VVpqaEtRWE5WUjNSYVIwSmpXbGRuVkdsQ2N6ZHpVR0kzVjJZeFZXMU1TVGhrV1dOR1lXNWpWbEZZZDJ4cE4waDBVRWhVUzNaT1NYVjJhbEpGYkRaak5FcHZiWFZPUjB0MVJUZFFNV1JEWkVsaGVqTXhhRWcwSzBwM2NIZGpRbmxITDFjM1NuSlNVREZ2VVRCdFZXUmlNbGRMTW1nMFVVcHZiR1VyTWxkWFdXNUxka1ZvYWsxS1ZVMUZWQzlzTjI1QlNtcEhSekpwTmpscFR5c3lkMlpVT1VWQ1pDdHhjRGRZSzBWbWJrMTVSVkZGVVRKclJtWm5iblJVVVdGUGJucHZWMEo0ZDBKMFkzSjJNVUZsZGtWSlpHcFJOVkJyZFVsYWNWcFNOMDF1Y2psR2FHOHhOM1Y2WW1oeFdYcEpRbmx3VWpGb1F5dEhWazlQVVRCM1pHMHZSSFY0V1Rac1ZWUmFTMDloYUhSc09HSldVbGhMTjI1RWRWUk1TRE5QUzBGaE5HdGlXR1JNWW05YVZTOXRiVzlSVTNSeWNHMXJWbVI1VG5oRE5tdHBVbFU0YVc5V1kxZEhUR05tY1V4Mk9IbEVRM0pJY1ZwUmNuTkpWVTlHYWxsSlEwRkROVTVTTlVJck1XOUNSSFV2WnpWcVVtc3JWVzV1SzNscFVrOUxlVzl3V0VZM2FsRXpWMHhoT1ZOdVVqRlRRbVJRYWtoRFR6Tm1lbUZ0UzBoWFluWktla0pXUVdWWFUzRlVNMlp4U0VONFQzRkNiRlJoWWtOclFVNVFlbE00WlZGeWFuTlFOV2hxUzAxV1FUWk1ha0YzWlhsRFkzUlNRbWRoTTI5TlIyWnNhV3B1TmxkbU4wYzBUV2hZZFhacllrbE9TSFkyWjIxRE9YTlphRXhvYUZCM1YwbGpaVWd2ZEd0alUzWjNkVGRwZUdFMlNVdElhUzkyZUhkTWJIWmxUMGR4UjFCbk1ucGpiQzltYjBSdFdXdHBZemxNTDJ3emNEaHBVMFZvZFV4Vk5WTnFNRkJQUWxOa1ZrTlJVM1o0TW1wdmEzSmhNV3hTVFVkVmQzVXZRVEJXU1Zob1EyVktaV2hSTDJWcU5IWndjbEJIUVRkUE1YVm9ZM0V4VEdsUVNuQlNZVWwxWTBseFF6ZE5NVUZ1YmxvdkwwMVFVV3AwZWtkaGNUTllaVmhOWldWdlRFRjBTWFJMVURkT1NubzRXa3B1UlZCT1pGWktWbTV1YkZST1dEWXhiazU0VEZCbWJYQlBhbTl1U2xNeFdTOVVORFEzVVdKeFQwMHhiejBpZlE9PQ?fid=01M4GX8TEKF8GN9Q9392DKF5E6&slot=0"

with T.session(lane) as client:
    print("Navigating directly to survey URL...")
    client.call_tool("browser_navigate", {"url": survey_url})
    time.sleep(5)

    page = T.read_page(client)
    print("PAGE TITLE:", page.get("title"))
    print("PAGE URL:", page.get("url"))

    shot = lane.shot(client, "survey_landing_live")
    print("Screenshot saved to:", shot)

    content = client._js(r"""
        (function() {
            var inputs = Array.from(document.querySelectorAll('input, select, textarea, button')).map(i => ({
                tag: i.tagName,
                type: i.type,
                name: i.name,
                value: i.value,
                text: (i.innerText || '').slice(0, 50)
            }));

            return {
                url: window.location.href,
                bodySnippet: document.body.innerText.slice(0, 1500),
                inputs: inputs
            };
        })()
    """)

    print("SURVEY LANDING CONTENT:\n", json.dumps(content, indent=2))
