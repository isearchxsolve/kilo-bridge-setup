"""post_linkedin_curated.py - Publish the Double-Edged Sword Option 1 Lead Magnet Post on LinkedIn.

Rules from Baba:
1. NO PRICING MENTIONED (no commercial flags, pure value & engagement).
2. Features Option 1 (Free Service): Live profile match + 3 verified remote roles gift.
3. Engagement Hook: Comment target role or DM to receive the free match.
4. Strict Rule 1 Receipts: Pre-post typed screenshot + post-publish receipt screenshot.
5. Author: Kunal Das.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

POST_TEXT = """The modern job search is structurally broken.

Between ghost job listings, automated rejection filters, and 1,000+ applicants flooding every open portal, qualified professionals are spending 20+ hours a week submitting resumes into digital black holes.

Over my 22 years architecting enterprise systems—from high-scale digital payment gateways to neural agent pipelines—the biggest rule I’ve learned is simple:

Signal always beats volume.

Instead of spraying 100 generic resumes, the engineers and professionals winning today are targeting verified live pipelines where hiring teams are actively reviewing candidates.

To give back to this community and support anyone currently in transition or #OpenToWork:

I am offering a complimentary Live Opportunity & ATS Match:

1. Drop your target role (e.g., "Operations Manager", "HR Generalist", "Data Analyst", "AI Engineer") in the comments below, or send me a DM.
2. I will run your profile across our verified live remote hiring index.
3. I will privately share 3 verified, active remote openings tailored to your background.

No catch. No fluff. Just real, verified signal to help you land your next role faster.

What role are you targeting right now? Let's connect."""


def publish_post(client, lane: T.Lane) -> bool:
    lane.log("--- Navigating to LinkedIn Feed ---")
    client.call_tool("browser_navigate", {"url": "https://www.linkedin.com/feed/"})
    time.sleep(6)

    page = T.read_page(client)
    wall = lane.wall(page["body"], page["title"])
    if wall:
        lane.log(f"Login/Captcha wall encountered: {wall}")
        return False

    # 1. Click "Start a post" button
    lane.log("Clicking 'Start a post' trigger button...")
    click_res = client._js("""
    (() => {
        const el = document.querySelector('div[aria-label="Start a post"]') || 
                   document.querySelector('#draft-text-replaceable-component') ||
                   Array.from(document.querySelectorAll('div, p, button')).find(e => (e.innerText||'').trim() === 'Start a post');
        if (el) {
            el.click();
            return { ok: true, clicked: el.tagName, aria: el.getAttribute('aria-label') };
        }
        return { ok: false, error: 'post_trigger_not_found' };
    })()
    """)
    lane.log(f"Trigger click result: {click_res}")
    time.sleep(4)

    # 2. Inject Post text into editor
    paragraphs = POST_TEXT.split("\n\n")
    inject_res = client._js(f"""
    (() => {{
        const editor = document.querySelector('div.ql-editor[contenteditable="true"]') || 
                       document.querySelector('div[role="textbox"][contenteditable="true"]');
        if (!editor) return {{ ok: false, error: 'editor_not_found' }};

        editor.focus();
        editor.innerHTML = '';
        const paras = {json.dumps(paragraphs)};
        paras.forEach(text => {{
            const p = document.createElement('p');
            p.innerText = text;
            editor.appendChild(p);
        }});

        editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
        editor.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return {{ ok: true, len: editor.innerText.length }};
    }})()
    """)
    lane.log(f"Text injection result: {inject_res}")
    time.sleep(2)

    # 3. Rule 1: Pre-post typed screenshot receipt
    ts = time.strftime("%Y%m%d_%H%M%S")
    shot_typed = lane.shot(client, f"post-typed-double-edge-{ts}")
    lane.log(f"PRE-POST SCREENSHOT RECEIPT: {shot_typed}")

    # 4. Click Publish/Post Button
    lane.log("Clicking Post/Publish button...")
    publish_res = client._js("""
    (() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const sendBtn = btns.find(b => {
            const t = (b.innerText || '').trim();
            return t === 'Post' || t === 'Publish' || b.classList.contains('share-actions__primary-action');
        });
        if (!sendBtn) return { ok: false, error: 'publish_button_not_found' };
        if (sendBtn.disabled) return { ok: false, error: 'publish_button_disabled' };
        sendBtn.click();
        return { ok: true, clicked: true };
    })()
    """)
    lane.log(f"Publish click result: {publish_res}")
    time.sleep(5)

    # 5. Rule 1: Post-publish screenshot receipt
    shot_published = lane.shot(client, f"post-published-double-edge-{ts}")
    lane.log(f"POST-PUBLISH SCREENSHOT RECEIPT: {shot_published}")

    lane.row(
        source="https://www.linkedin.com/feed/",
        role="Post Lead Magnet",
        company="LinkedIn Community",
        score=100,
        step="post_double_edge_gift",
        status=T.APPLIED,
        receipt=str(shot_published) if shot_published else "none",
        note="Double-Edged Sword Option 1 Post published (Zero pricing, free match hook)"
    )
    return True


def main():
    lane = T.Lane("linkedin", "lead_magnet_post")
    with T.session(lane) as client:
        publish_post(client, lane)
        lane.summary()


if __name__ == "__main__":
    main()
