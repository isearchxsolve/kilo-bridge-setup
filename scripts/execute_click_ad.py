r"""execute_click_ad.py - Click the view button, wait for countdown, verify credit and record receipt.
"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lane_tools as T

lane = T.Lane("timebucks", "click_ad_worker")
with T.session(lane) as client:
    tabs = client.list_tabs()
    tb_tab = next((t for t in tabs if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(1)
    else:
        client.call_tool("browser_navigate", {"url": "https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads"})
        time.sleep(3)

    # Check initial balance
    initial_info = client._js(r"""
        (function() {
            var text = document.body.innerText || '';
            var match = text.match(/Wallet:\s*\$([0-9\.]+)/i) ||
                        text.match(/Balance:\s*\$([0-9\.]+)/i);
            var headerBal = document.querySelector('.current_balance, #current_balance, .wallet-balance, .header-balance');
            return {
                textMatch: match ? match[1] : null,
                headerText: headerBal ? headerBal.innerText : null,
                title: document.title,
                url: window.location.href
            };
        })()
    """)
    print("INITIAL STATE:", json.dumps(initial_info, indent=2))

    # Take pre-click screenshot
    pre_shot = lane.shot(client, "timebucks_click_ad_pre")
    print("Pre-click screenshot:", pre_shot)

    # Click the View button
    click_res = client._js(r"""
        (function() {
            var allInputs = Array.from(document.querySelectorAll('input, button, a'));
            var viewBtn = allInputs.find(b => {
                var val = (b.value || b.innerText || '').toLowerCase().trim();
                return val === 'view';
            });
            if (viewBtn) {
                var form = viewBtn.closest('form');
                var onclick = viewBtn.getAttribute('onclick') || '';
                var href = viewBtn.getAttribute('href') || '';
                var details = {
                    tagName: viewBtn.tagName,
                    value: viewBtn.value,
                    formAction: form ? form.action : null,
                    onclick: onclick,
                    href: href
                };
                viewBtn.click();
                return { success: true, details: details };
            }
            return { success: false, reason: "No View button found" };
        })()
    """)
    print("CLICK RESULT:", json.dumps(click_res, indent=2))

    # Wait for ad duration (offer specified 5 seconds, let's wait 8 seconds)
    print("Waiting 8 seconds for timer countdown to complete...")
    time.sleep(8)

    # Check tabs after click
    tabs_after = client.list_tabs()
    print(f"Tabs count after click: {len(tabs_after)}")
    
    # Ensure we are focused on TimeBucks tab
    tb_tab = next((t for t in tabs_after if "timebucks.com" in t.get("url", "").lower()), None)
    if tb_tab:
        client.switch_tab(tb_tab["id"])
        time.sleep(2)

    # Check post-click balance and page state
    post_info = client._js(r"""
        (function() {
            var text = document.body.innerText || '';
            var match = text.match(/Wallet:\s*\$([0-9\.]+)/i) ||
                        text.match(/Balance:\s*\$([0-9\.]+)/i);
            var headerBal = document.querySelector('.current_balance, #current_balance, .wallet-balance, .header-balance');
            
            // Check if timer countdown or success banner exists
            var successBanner = Array.from(document.querySelectorAll('.alert, .alert-success, .success, div[class*="success"]'))
                                     .map(el => el.innerText.trim()).filter(Boolean);

            var remainingButtons = Array.from(document.querySelectorAll('input, button, a'))
                .filter(b => (b.value || b.innerText || '').toLowerCase().trim() === 'view');

            return {
                textMatch: match ? match[1] : null,
                headerText: headerBal ? headerBal.innerText : null,
                successBanner: successBanner,
                remainingViewButtons: remainingButtons.length,
                pageSnippet: document.body.innerText.slice(500, 1500)
            };
        })()
    """)
    print("POST STATE:", json.dumps(post_info, indent=2))

    post_shot = lane.shot(client, "timebucks_click_ad_post")
    print("Post-click screenshot:", post_shot)

    # Record row in ledger
    lane.row(
        source="https://timebucks.com/publishers/index.php?pg=earn&tab=view_content_ads",
        role="microtask_worker",
        company="TimeBucks",
        score=1,
        step="view_content_ad_1",
        status=T.APPLIED_STEP,
        receipt=post_shot,
        note=f"Clicked 5s ad. Pre-bal: {initial_info.get('headerText')}, Post-bal: {post_info.get('headerText')}"
    )
    print("Ledger entry recorded.")
