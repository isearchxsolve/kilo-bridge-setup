# NVIDIA vision model probe

**Date:** 2026-10-07 (local time)  
**Purpose:** Compare response speed and basic vision/tool-call suitability for the employment mission.  
**Method:** One short text and synthetic 64×64 red/blue image prompt per attempt, streamed through NVIDIA's OpenAI-compatible endpoint. These are spot checks, not a load test or a statistically reliable latency benchmark.

## Findings

| Model | Latest text result | Latest vision result | Tool call | Readout |
|---|---:|---:|---|---|
| `meta/llama-3.2-11b-vision-instruct` | 573 ms first token / 604 ms total | 876 ms first token / 1,124 ms total; correctly identified red above blue | HTTP 200, 1,035 ms; response arguments contained a `<|python_tag|>` prefix | Fastest successful end-to-end spot check. Vision worked. Validate OpenCode's handling of its tool-call argument format during real use. |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | 700 ms first token / 737 ms total; `PONG` | 1,199 ms first token / 1,295 ms total; correctly identified `RED, BLUE` | Valid JSON tool arguments in 2,684 ms on one attempt; a later request hit HTTP 503, worker capacity `16/16` | Best-balanced agent choice in this probe: vision worked and the successful tool call was clean. It was slower than Llama on vision and showed transient capacity pressure. |
| `z-ai/glm-5.3-flash` | timed out at about 35.5 s | timed out at about 35.3 s | not reached | Matches the reported stalling in this probe. This does not prove a current NVIDIA-wide outage. |
| `deepseek-ai/deepseek-v4.1-flash` | timed out at about 15.3 s | timed out at about 15.3 s | not reached | Inconclusive because this was a bounded 15-second attempt. |
| `meta/muse-glimmer-30b` | later attempts: 1,380 ms first token / 1,910 ms total, no visible text | later attempts: 1,780 ms first token / 2,625 ms total, no visible text | 4,181 ms; no usable tool call | Not selected for the mission. |

The first Nemotron attempt used an unsupported `clear_thinking` parameter and returned HTTP 400; subsequent results used the supported request shape. Some earlier rows in `bench-nvidia-vision.json` are failed or superseded attempts; the table reports the latest relevant readings, not averages.

## Recommendation

Keep Nemotron Nano Omni as the mission's default where reliable structured tool calls matter most. Llama 3.2 11B Vision is the faster vision-capable fallback and successfully called a tool in the API probe, but its arguments included a model-specific prefix; OpenCode/browser-MCP compatibility needs observation in the mission before calling it the safer default. A read-only OpenCode smoke call with Llama did invoke `browser_list_tabs`, but the connected browser returned zero tabs, so it did not establish live portal readiness.

The GLM and DeepSeek timeouts plus Nemotron's one 503 indicate provider/model capacity or endpoint variability can affect response time. The probe did not establish a general NVIDIA outage; no authoritative outage status was confirmed during this run.

## References

- [NVIDIA GLM-5.3-Flash model card](https://build.nvidia.com/z-ai/glm-5-3-flash/modelcard)
- [NVIDIA Nemotron-3-Nano-Omni model card](https://build.nvidia.com/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning)
- [NVIDIA Llama 3.2 11B Vision model card](https://build.nvidia.com/meta/llama-3.2-11b-vision-instruct)
- [NVIDIA Muse Glimmer model card](https://build.nvidia.com/meta/muse-glimmer-30b)
