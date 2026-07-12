# AfyaPlus Triage Inference Engine

This repository contains a production-style Python prototype for the AfyaPlus medical sorting pipeline. It accepts a patient message, applies a defensive prompt, tries a cloud GPT-4o-mini pathway first, automatically falls back to a local Ollama request when the cloud path fails or times out, and finally uses a safe rule-based fallback if both inference services are unavailable.

## What the script does

- Accepts a patient message from the command line or uses a built-in sample message.
- Uses a strict prompt that instructs the model to return only JSON.
- Enforces a native JSON response shape using the OpenAI-compatible JSON mode payload.
- Wraps network calls in explicit timeout and exception handling.
- Prints a parsed Python dictionary and a one-line routing decision.

## Prompt engineering iterations

### Iteration 1: Basic extraction prompt
- The first version asked the model to classify the message and return a JSON object.
- Limitation: it was too open-ended and occasionally produced conversational text.

### Iteration 2: Structured schema prompt
- The second version explicitly named the required keys and described the expected JSON shape.
- Limitation: the format could still drift when the model was not forced into JSON mode.

### Iteration 3: Role-based, chain-of-thought, and guardrails
- The final version gives the model a clear operational identity as an AfyaPlus triage officer.
- It forces a step-by-step reasoning path before a final answer.
- Guardrails block fluff, invented medical facts, and unverified calculations.
- This version is the most reliable for downstream automation.

## Baseline performance notes

The current lab environment did not have a configured OpenAI API key or a usable Ollama model endpoint during validation, so the script exercised its safety fallback path.

| Path | Status in this environment | Observed latency |
| --- | --- | ---: |
| Cloud GPT-4o-mini | Not available because OPENAI_API_KEY was unset | Not measured |
| Local Ollama | Endpoint returned 404 for the default model route | Not measured |
| Rule-based fallback | Active and successful | ~0.000s |

## How to run

```bash
python app.py "I have sudden chest pain and I am having trouble breathing."
```

## Expected output shape

```json
{
  "is_critical_emergency": true,
  "detected_symptoms": ["acute discomfort", "respiratory distress"],
  "clinical_reasoning_summary": "The message includes high-risk symptoms that warrant immediate emergency evaluation.",
  "routing_destination": "emergency_room"
}
```

## Notes on operational risk

- The local fallback is intentionally conservative and should be treated as a safety net rather than a replacement for validated clinical decision support.
- The system is suitable for intake triage and routing, not for autonomous diagnosis.
