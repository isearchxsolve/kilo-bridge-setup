"""Bounded NVIDIA endpoint health/latency comparison for text and vision.

Reads the key from NVIDIA_API_KEY or the local OpenCode/Crush config. Never prints
the key. Writes only beside this script (the Downloads package), not to D:.
"""
import base64
import json
import os
import struct
import time
import urllib.error
import urllib.request
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "bench-nvidia-vision.json"
BASE = "https://integrate.api.nvidia.com/v1/chat/completions"
TIMEOUT = 15
MODELS = [
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "meta/llama-3.2-11b-vision-instruct",
]
TOOL_MODELS = [
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "meta/muse-glimmer-30b",
    "meta/llama-3.2-11b-vision-instruct",
]


def get_key():
    key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if key:
        return key
    path = Path(os.environ.get("CODEX_HOME", Path.home() / ".config"))
    candidates = [
        Path.home() / ".config" / "crush" / "crush.json",
        Path.home() / ".config" / "opencode" / "opencode.json",
        Path.home() / ".config" / "opencode" / "opencode.jsonc",
    ]
    for config in candidates:
        try:
            raw = config.read_text(encoding="utf-8")
            # OpenCode JSONC may contain comments; extract only the provider key
            # from strict JSON files and skip JSONC instead of printing its data.
            data = json.loads(raw)
            key = data.get("providers", {}).get("nvidiafree", {}).get("api_key", "")
            if key:
                return str(key).strip()
        except Exception:
            continue
    return ""


def png_two_bands():
    # 64x64 image: a clear red top half and blue bottom half.
    width = height = 64
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        color = (255, 0, 0) if y < height // 2 else (0, 0, 255)
        raw.extend(bytes(color) * width)

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload +
                struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n" +
           chunk(b"IHDR", struct.pack(">2I5B", width, height, 8, 2, 0, 0, 0)) +
           chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))
    return base64.b64encode(png).decode("ascii")


def request(model, image=None):
    if image is None:
        content = "Reply with exactly PONG."
    else:
        content = [
            {"type": "text", "text": "Name the colors in the top and bottom halves, exactly RED/BLUE."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image}},
        ]
    body = {"model": model, "messages": [{"role": "user", "content": content}],
            "max_tokens": 96, "temperature": 0, "stream": True,
            "reasoning_effort": "low"}
    if model == "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning":
        body["reasoning_budget"] = 0
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + KEY,
                 "Content-Type": "application/json",
                 "Accept": "text/event-stream"}, method="POST")
    start = time.perf_counter()
    first = None
    output = []
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status = response.status
            for raw in response:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                item = line[5:].strip()
                if item == "[DONE]":
                    break
                try:
                    event = json.loads(item)
                except json.JSONDecodeError:
                    continue
                if first is None:
                    first = (time.perf_counter() - start) * 1000
                choices = event.get("choices") or []
                if choices:
                    delta = choices[0].get("delta") or {}
                    text = delta.get("content")
                    if isinstance(text, str):
                        output.append(text)
        total = (time.perf_counter() - start) * 1000
        return {"http": status, "ttft_ms": round(first) if first is not None else None,
                "total_ms": round(total), "text": "".join(output).strip()[:160], "error": None}
    except urllib.error.HTTPError as exc:
        message = exc.read(600).decode("utf-8", errors="replace")
        return {"http": exc.code, "ttft_ms": None,
                "total_ms": round((time.perf_counter() - start) * 1000),
                "text": "", "error": message[:250]}
    except Exception as exc:
        return {"http": None, "ttft_ms": None,
                "total_ms": round((time.perf_counter() - start) * 1000),
                "text": "", "error": (type(exc).__name__ + ": " + str(exc))[:250]}


def request_tool(model):
    """Test whether the model emits a structured OpenAI function call."""
    body = {
        "model": model,
        "messages": [{"role": "user", "content": "Use the report function to report status ready."}],
        "tools": [{"type": "function", "function": {
            "name": "report", "description": "Return the requested status.",
            "parameters": {"type": "object", "properties": {
                "status": {"type": "string", "enum": ["ready"]}},
                "required": ["status"], "additionalProperties": False}}}],
        "tool_choice": {"type": "function", "function": {"name": "report"}},
        "max_tokens": 64, "temperature": 0, "stream": False,
    }
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + KEY,
                 "Content-Type": "application/json",
                 "Accept": "application/json"}, method="POST")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            payload = json.load(response)
        message = payload["choices"][0]["message"]
        calls = message.get("tool_calls") or []
        call = calls[0] if calls else {}
        fn = call.get("function") or {}
        return {"http": 200, "total_ms": round((time.perf_counter() - start) * 1000),
                "tool_call": fn.get("name") == "report", "name": fn.get("name"),
                "arguments": fn.get("arguments"), "error": None}
    except urllib.error.HTTPError as exc:
        return {"http": exc.code, "total_ms": round((time.perf_counter() - start) * 1000),
                "tool_call": False, "name": None, "arguments": None,
                "error": exc.read(600).decode("utf-8", errors="replace")[:250]}
    except Exception as exc:
        return {"http": None, "total_ms": round((time.perf_counter() - start) * 1000),
                "tool_call": False, "name": None, "arguments": None,
                "error": (type(exc).__name__ + ": " + str(exc))[:250]}


KEY = get_key()
if not KEY:
    raise SystemExit("No NVIDIA API key found in NVIDIA_API_KEY or local provider config.")

print("NVIDIA endpoint probe: one short text + one vision request per model; timeout=15s", flush=True)
print("MODEL | TEXT(total/first ms, reply) | VISION(total/first ms, reply) | HTTP/errors", flush=True)
image = png_two_bands()
try:
    results = json.loads(OUTPUT.read_text(encoding="utf-8"))
except Exception:
    results = []
already_tested = {
    row.get("model") for row in results
    if row.get("text", {}).get("http") == 200 and row.get("vision", {}).get("http") == 200
    and row.get("vision", {}).get("text")
    and (row.get("model") not in TOOL_MODELS or row.get("tool", {}).get("tool_call"))
}
for model in MODELS:
    if model in already_tested:
        continue
    text_result = request(model)
    vision_result = request(model, image)
    tool_result = request_tool(model) if model in TOOL_MODELS else None
    result = {"model": model, "text": text_result, "vision": vision_result, "tool": tool_result}
    results.append(result)
    OUTPUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    checks = [text_result, vision_result] + ([tool_result] if tool_result else [])
    errors = "; ".join(x["error"][:90] for x in checks if x and x["error"])
    print("%s | %s/%s %s | %s/%s %s | tool=%s@%sms | %s" % (
        model, text_result["total_ms"], text_result["ttft_ms"], text_result["text"][:36],
        vision_result["total_ms"], vision_result["ttft_ms"], vision_result["text"][:36],
        tool_result["tool_call"] if tool_result else "n/a",
        tool_result["total_ms"] if tool_result else "n/a",
        errors or "HTTP 200"), flush=True)
print("Saved: " + str(OUTPUT), flush=True)
