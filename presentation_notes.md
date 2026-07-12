Slide 1 - Title: Improving Patient Message Triage

Improving Patient Message Triage


Slide 2 — Problem
Patients send messy, free-text messages; backend needs machine-readable triage data.

Example messy message:
Patients write in varied, informal ways—using colloquialisms, misspellings, shorthand (e.g., “CP” for chest pain), and incomplete timelines—so key details like onset, severity, and exact symptoms are often missing or ambiguous. 

That linguistic variability and lack of context make automated parsing brittle: systems either miss critical cues (causing under-triage) or over-call severity (creating unnecessary urgent workflows), and staff must manually follow up to clarify intent. The net effect is slower routing, increased clinician workload for triage review, and greater risk to timely, appropriate care unless messages are normalized and converted into a strict, machine-readable triage payload.

Slide 3 — Desired Output
Structured triage payload (example JSON):
```
{
  "chief_complaint": "chest pain",
  "severity": "moderate",
  "symptoms": ["cough","dizziness"],
  "timeframe": "2 days",
  "recommended_action": "urgent evaluation"
}
- Enforcing a strict schema (fields/types/enums) removes ambiguity so routing rules can deterministically map `severity` and `recommended_action` to destination queues and priority levels.  
- Consistent JSON enables straightforward aggregation and analytics—supporting trend detection, SLA monitoring, and auditable logs for safety and model-performance evaluation.

Slide 4 — Solution Overview
A Python inference engine with:
- Structured prompt enforcing strict JSON
- Cloud-first inference (GPT-4o-mini)
- Local Ollama fallback when offline

Leveraging a cloud-first model like GPT-4o-mini provides strong language understanding for correctly interpreting ambiguous or abbreviated patient messages, while a local Ollama fallback keeps the system operational during network outages and lowers latency and exposure of sensitive data.

The engine uses a structured prompt to force strict JSON, then applies schema validation, canonicalization (normalizing symptom labels, timeframes, and severity enums), and sanitization/redaction of PHI before sending results to the backend.

These layers together balance accuracy, availability, and privacy while ensuring downstream routing receives deterministic, auditable triage payloads.


Slide 5 — Architecture (high level)
1. Ingest message → 2. Structured prompt → 3. Model inference (cloud or local) → 4. JSON validator → 5. Route to backend

The pipeline includes robust operational controls: automated retries with exponential backoff and circuit-breakers handle transient model or network failures, while structured logging (request IDs, timestamps, confidence scores, and model provenance) creates an auditable trail for every inference.

Low-confidence or high-risk outputs are triaged to a human-in-loop workflow—flagged automatically, routed to clinicians for review, and annotated with the model’s rationale to speed verification.

Monitoring and alerts surface drift or spike patterns so you can tune prompts, update routing rules, or pause automation; fail-safe defaults (e.g., “recommend clinician review”) ensure patient safety when the system is uncertain.

