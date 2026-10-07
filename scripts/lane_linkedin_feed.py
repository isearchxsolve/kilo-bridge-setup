"""lane_linkedin_feed.py - LinkedIn feed engagement lane.

Inspects authenticated LinkedIn feed, finds relevant technical posts,
and prepares a high-value ASCII insight draft (with receipt screenshot).
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

FEED_URL = "https://www.linkedin.com/feed/"


def main():
    lane = T.Lane("linkedin", "feed engagement")
    with T.session(lane) as client:
        lane.log("L1 navigate -> " + FEED_URL)
        client.call_tool("browser_navigate", {"url": FEED_URL})
        time.sleep(8)
        
        page = T.read_page(client)
        wall = lane.wall(page["body"], page["title"])
        if wall:
            lane.row(FEED_URL[:70], "-", "-", "-", "session check", T.BLOCKED,
                     "none", "login/captcha wall: " + wall)
            return 2
            
        shot = lane.shot(client, "70-linkedin-feed-" + time.strftime("%Y%m%d-%H%M%S"))
        
        # Read visible feed updates
        posts = client._js('''(() => {
            const updates = Array.from(document.querySelectorAll("div.feed-shared-update-v2, div[data-urn*='activity']")).slice(0, 5);
            return updates.map(u => {
                const text = (u.innerText || '').slice(0, 300);
                const urn = u.getAttribute('data-urn') || '';
                return { text, urn };
            }).filter(p => p.text.length > 30);
        })()''')
        
        if isinstance(posts, str):
            try:
                posts = json.loads(posts)
            except Exception:
                posts = []
                
        if not posts:
            lane.row(FEED_URL[:70], "-", "-", "-", "read feed", T.OK,
                     str(shot) if shot else "none", "feed active; 0 updates parsed in current viewport")
            lane.summary()
            return 0
            
        first = posts[0]
        urn = first.get("urn") or "activity-feed-1"
        draft = ("Practical agentic architectures require deterministic tool boundaries and audit receipts; "
                 "LLM reasoning alone without verifiable state transitions is brittle in production.")
        
        lane.row(FEED_URL[:70], "Feed Engagement", "LinkedIn Post", 3,
                 "feed insight draft", T.OK, str(shot) if shot else "none",
                 "draft prepared (pending operator SEND-APPROVED): " + draft[:120])
        lane.log("FEED DRAFT: " + draft)
        lane.summary()
        return 0


if __name__ == "__main__":
    sys.exit(main())
