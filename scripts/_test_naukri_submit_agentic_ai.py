"""test_naukri_submit_agentic_ai.py - apply to Agentic AI Architect role."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lane_tools as T

lane = T.Lane("naukri", "apply agentic ai architect")
title = "Agentic AI Architect | LLMs, RAG & Autonomous Agents_XP: 10+_Hyderabad"
company = "Tata Consultancy Services"
url = "https://www.naukri.com/job-listings-agentic-ai-architect-llms-rag-autonomous-agents-xp-10-hyderabad-tata-consultancy-services-hyderabad-10-to-20-years-280926031876"

with T.session(lane) as client:
    client.call_tool("browser_navigate", {"url": url})
    time.sleep(8)
    
    # Click apply button if drawer not open
    client._js('''(() => {
        const c = document.querySelector(".chatbot_MessageContainer");
        if (!c) {
            const btn = document.querySelector("#apply-button, button.apply-button");
            if (btn) btn.click();
        }
    })()''')
    time.sleep(5)
    
    seen = set()
    success = False
    
    for turn in range(1, 8):
        rq = T.read_recruiter_question(client)
        print(f"Round {turn}: Question = {rq}")
        if not rq or rq in seen:
            break
            
        ans = T.answer_from_resume(rq)
        print(f"Round {turn}: Answer = {ans}")
        if not ans:
            shot = lane.shot(client, "48-agentic-ai-blocked-" + time.strftime("%H%M%S"))
            lane.row(url[:70], title[:70], company, 4, "recruiter question", T.BLOCKED,
                     str(shot) if shot else "none", "UNANSWERABLE: " + rq[:100])
            print("BLOCKED:", rq)
            break
            
        seen.add(rq)
        res = T.answer_and_save(client, rq, ans)
        print(f"Round {turn}: Save result = {res}")
        time.sleep(5)
        
        page = T.read_page(client)
        low = page["body"].lower()
        if any(s in low for s in ["application submitted", "successfully applied", "applied successfully", "application sent"]):
            success = True
            break
            
    c_check = client._js('document.querySelector(".chatbot_MessageContainer") ? "open" : "closed"')
    print("Chatbot status:", c_check)
    
    shot = lane.shot(client, "49-agentic-ai-result-" + time.strftime("%Y%m%d-%H%M%S"))
    if success or c_check == "closed":
        lane.row(url[:70], title[:70], company, 4, "application submitted", T.APPLIED,
                 str(shot) if shot else "none", "portal confirmed: success text or panel closed")
        print("APPLIED SUCCESSFUL!")
    else:
        lane.row(url[:70], title[:70], company, 4, "apply flow", T.BLOCKED,
                 str(shot) if shot else "none", "not confirmed")
        print("Apply not confirmed.")
        
    lane.summary()
