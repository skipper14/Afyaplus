# Title: Improving Patient Message Triage

---

## Slide 1 — Title
Improving Patient Message Triage

Notes:
- 5-minute pitch: goal is reliable routing and triage support.
- Emphasize prototype scope (assist clinicians, not diagnose).

---

## Slide 2 — Problem
Patients send messy, free-text messages; backend needs machine-readable triage data.

Example messy message:
"My chest hurts a lot, been coughing, sometimes dizzy. What should I do?"

Notes:
- Explain variability in language, abbreviations, missing context.
- State impact: slow routing, mis-triage, extra clinician workload.

---

## Slide 3 — Desired Output
Structured triage payload (example JSON):
```
{
  "chief_complaint": "chest pain",
  "severity": "moderate",
  "symptoms": ["cough","dizziness"],
  "timeframe": "2 days",
  "recommended_action": "urgent evaluation"
}
```

Notes:
- Show how strict JSON enables deterministic downstream routing and analytics.

---

## Slide 4 — Solution Overview
A Python inference engine with:
- Structured prompt enforcing strict JSON
- Cloud-first inference (GPT-4o-mini)
- Local Ollama fallback when offline

Notes:
- Cloud model for strong reasoning; local for resilience and privacy.
- Engine validates and sanitizes JSON before sending to backend.

---

## Slide 5 — Architecture (high level)
1. Ingest message → 2. Structured prompt → 3. Model inference (cloud or local) → 4. JSON validator → 5. Route to backend

Notes:
- Mention retries, logging, and human-in-loop moderation for risky outputs.

---

## Slide 6 — Why these models?
- GPT-4o-mini (cloud): strong general reasoning and language understanding
- Ollama (local): works offline, reduces latency and dependency on network

Notes:
- Tradeoffs: cloud accuracy vs. local availability and control.

---

## Slide 7 — Operational Risks
- Network failures: fallback to local inference
- Hallucinated clinical facts: enforce JSON-only outputs and human oversight
- Privacy/compliance: log minimal PHI, use encryption and access controls

Notes:
- Emphasize mitigation: strict schema, validation, clinician review for high-risk items.

---

## Slide 8 — Demo / Prototype Scope
- Prototype purpose: routing & triage support, not autonomous diagnosis
- What works now: structured parsing, routing rules, fallback strategy
- What remains: rigorous clinical validation, monitoring, regulatory review

Notes:
- Be explicit about limitations and next validation steps.

---

## Slide 9 — Closing / Ask
- Prototype helps scale triage and reduce clinician load
- Ask: pilot deployment, clinician feedback, safety validation

Notes:
- End with a concise call-to-action and contact info.

---

## Appendix — Speaker cues (timing)
- 0:00–0:30 Title & problem
- 0:30–1:30 Solution & demo snippet
- 1:30–2:30 Architecture & model choice
- 2:30–3:30 Risks & mitigations
- 3:30–4:30 Prototype scope and next steps
- 4:30–5:00 Closing & Q/A
