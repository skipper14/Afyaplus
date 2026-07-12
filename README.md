# AfyaPlus Triage Engine

## Overview
This project implements a production-style Python inference engine for the AfyaPlus triage workflow. It uses a cloud-first pathway with OpenAI and a local fallback pathway with Ollama so the system can continue operating when network conditions degrade.

## Architecture
- Cloud pathway: OpenAI GPT-4o-mini with strict JSON mode and a 4.0s timeout.
- Local pathway: Ollama running `llama3.2` for offline fallback.
- Output contract: the pipeline returns a JSON object matching the AfyaPlus schema.

## Prompt Engineering Iterations
### Variant 1: Baseline
- Simple instructional prompt.
- Helpful, but lacked strong guardrails.

### Variant 2: Structured Output Focus
- Explicitly requested a JSON object and blocked markdown.
- Improved schema adherence.

### Variant 3: Guardrailed Production Prompt
- Added role-based identity.
- Forced internal reasoning steps without revealing the chain of thought.
- Added defensive rules to eliminate conversational fluff and unsupported medical claims.

## Why the Guardrails Matter
The AfyaPlus backend requires machine-readable input. Without strict rules, the model may add prose, make unsupported medical claims, or return invalid wrappers. The final prompt prevents these failure modes by restricting output to a single valid JSON object.

## Baseline Performance Comparison

| Path | Tool | Approx. latency | Notes |
| --- | --- | ---: | --- |
| Cloud | OpenAI GPT-4o-mini | ~1-3s when key is valid | Fast but depends on network and authentication |
| Local | Ollama + llama3.2 | ~8-12s | Reliable fallback, but slower and less deterministic |

## How to Run
```bash
python3 app.py "I have had severe chest pain for 20 minutes and I feel short of breath."
```

## Sample Outputs
1. Cloud success path: valid JSON returned from the OpenAI route.
2. Cloud failure path: the script prints a cloud error and falls back to Ollama.
3. Local fallback path: Ollama returns a valid JSON object for the same message.
