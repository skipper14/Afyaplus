# 5-Minute Presentation Outline

1. Problem statement: patients send messy messages, but the backend needs machine-readable triage data.
2. Solution overview: a Python inference engine that uses a structured prompt, strict JSON outputs, cloud-first inference, and local Ollama fallback.
3. Why this model choice is appropriate: cloud GPT-4o-mini gives strong general reasoning; local Ollama supports resilience when connectivity is unstable.
4. Operational risks: network failures, hallucinated clinical facts, and the need for human oversight.
5. Closing: the prototype is suitable for routing and triage support, not autonomous diagnosis.
