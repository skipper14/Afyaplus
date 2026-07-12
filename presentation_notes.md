# 5-Minute Presentation Notes

## Slide 1 - Problem
AfyaPlus receives unstructured patient messages that cannot be sent directly to backend systems. The system needs a machine-readable triage result that can be routed safely.

## Slide 2 - Solution
We built a Python inference engine that tries OpenAI first, then automatically falls back to Ollama when the cloud path fails or times out. The app uses defensive prompting and enforces a JSON schema.

## Slide 3 - Why the Model Choice Makes Sense
OpenAI provides fast cloud inference, while Ollama gives a local fallback for resilience. In production, having both improves continuity during outages.

## Slide 4 - Risks and Constraints
- Cloud inference depends on valid API credentials and network connectivity.
- Local Ollama is slower but more resilient.
- The system should never return free-form prose to the backend.

## Slide 5 - Demo Summary
The script accepts a patient message, runs the cloud trial, falls back to local inference if necessary, parses a JSON object, and prints the routing decision.
