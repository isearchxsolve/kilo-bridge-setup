import sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T
import lane_two_edged_sword as TES

lane = T.Lane("linkedin", "subhamay_pitch")
with T.session(lane) as c:
    lane.log("Navigating to Subhamay profile...")
    c.call_tool("browser_navigate", {"url": "https://www.linkedin.com/in/subhamay-namata-55451512a/"})
    time.sleep(6)
    
    # Check for direct compose link or click Message button
    compose_info = c._js("""
    (() => {
        // 1. Direct link
        const a = document.querySelector('a[href*="/messaging/compose/"]');
        if (a) return { type: 'link', href: a.href };
        
        // 2. Message button
        const btns = Array.from(document.querySelectorAll('button'));
        const msgBtn = btns.find(b => b.innerText.trim() === 'Message' || b.getAttribute('aria-label')?.includes('Message Subhamay'));
        if (msgBtn) {
            msgBtn.click();
            return { type: 'clicked_button' };
        }
        return { type: 'none' };
    })()
    """)
    lane.log(f"Profile message control: {compose_info}")
    time.sleep(4)
    
    # Check if chat window opened or what URL we are on
    page = T.read_page(c)
    lane.log(f"Current URL: {page['url']}")
    
    # Extract recipient id from URL or compose container
    recipient_id = c._js("""
    (() => {
        const u = window.location.href;
        const m = u.match(/recipient=([^&]+)/);
        if (m) return m[1];
        // Check active compose box
        const form = document.querySelector('form.msg-form');
        if (form) {
            const hidden = form.querySelector('input[name="recipientId"]');
            if (hidden) return hidden.value;
        }
        return null;
    })()
    """)
    lane.log(f"Detected Recipient ID: {recipient_id}")
    
    if not recipient_id:
        # If chat window opened as a dock overlay:
        lane.log("Inspecting docked chat window...")
        box_exists = c._js("!!document.querySelector('div.msg-form__contenteditable')")
        lane.log(f"Docked compose box exists: {box_exists}")
        if box_exists:
            # We can deliver directly to the open compose box!
            jobs = TES.find_matched_jobs(["hr operations", "people operations", "workday", "hr generalist"], limit=3)
            pitch = TES.build_pitch_message("Subhamay", "HR Operations, People Services, and Workday HRMS", jobs)
            paragraphs = pitch.split("\n\n")
            
            c._js(f"""
            (() => {{
                const box = document.querySelector('div.msg-form__contenteditable[contenteditable="true"]');
                box.focus();
                box.innerHTML = '';
                const paras = {TES.json.dumps(paragraphs)};
                paras.forEach(text => {{
                    const p = document.createElement('p');
                    p.innerText = text;
                    box.appendChild(p);
                }});
                box.dispatchEvent(new Event('input', {{ bubbles: true }}));
                box.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }})()
            """)
            time.sleep(1)
            
            ts = time.strftime("%Y%m%d_%H%M%S")
            shot_typed = lane.shot(c, f"two-edge-typed-subhamay_namata-{ts}")
            lane.log(f"PRE-SEND RECEIPT: {shot_typed}")
            
            # Click send
            send_res = c._js("""
            (() => {
                const sendBtn = document.querySelector('button.msg-form__send-button');
                if (sendBtn && !sendBtn.disabled) {
                    sendBtn.click();
                    return { ok: true };
                }
                return { ok: false, disabled: sendBtn ? sendBtn.disabled : true };
            })()
            """)
            lane.log(f"Send result: {send_res}")
            time.sleep(3)
            
            shot_sent = lane.shot(c, f"two-edge-sent-subhamay_namata-{ts}")
            lane.log(f"POST-SEND FINAL RECEIPT: {shot_sent}")
            
            lane.row(
                source="https://www.linkedin.com/in/subhamay-namata-55451512a/",
                role="1st-Degree Pitch",
                company="Subhamay Namata",
                score=len(jobs),
                step="two_edged_sword_delivery",
                status=T.APPLIED,
                receipt=str(shot_sent) if shot_sent else "none",
                note=f"Delivered gift with {len(jobs)} roles and 2 packages"
            )
    else:
        # Deliver via standard TES module
        TES.deliver_two_edged_sword_pitch(
            client=c,
            lane=lane,
            recipient_id=recipient_id,
            name="Subhamay Namata",
            domain_summary="HR Operations, People Services, and Workday HRMS",
            keywords=["hr operations", "people operations", "workday", "hr generalist"]
        )

lane.summary()
print("Subhamay sweep completed!")
