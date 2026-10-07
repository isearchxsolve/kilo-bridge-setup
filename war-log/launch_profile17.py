import subprocess
import os
import sys

url = sys.argv[1] if len(sys.argv) > 1 else "https://www.linkedin.com/feed/"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
EXTENSION_PATH = r"C:\Users\Admin\AppData\Local\hermes\node\node_modules\@agent360\browser-mcp\extension"
cmd = [
    CHROME,
    "--profile-directory=Profile 17",
    "--start-maximized",
    f"--load-extension={EXTENSION_PATH}",
    url
]
p = subprocess.Popen(cmd)
print(f"Launched Profile 17 (PID {p.pid}) with URL: {url}")
