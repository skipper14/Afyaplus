# Sample outputs

## Scenario 1: High-risk emergency message

Command:

```bash
python app.py "I have sudden chest pain and I am having trouble breathing."
```

Observed output:

```json
{
  "is_critical_emergency": true,
  "detected_symptoms": [
    "acute discomfort",
    "respiratory distress"
  ],
  "clinical_reasoning_summary": "The message includes high-risk symptoms that warrant immediate emergency evaluation.",
  "routing_destination": "emergency_room"
}
```

## Scenario 2: Routine symptom message

Command:

```bash
python app.py "I have a mild headache and sore throat."
```

Observed output:

```json
{
  "is_critical_emergency": false,
  "detected_symptoms": [
    "mild infection symptoms"
  ],
  "clinical_reasoning_summary": "The message contains signs of urgent care needs and was handled with a safe offline fallback.",
  "routing_destination": "urgent_care"
}
```

## Scenario 3: Cloud failure fallback path

Observed behavior during validation:

```text
Cloud request failed: OPENAI_API_KEY is not set. Falling back to local Ollama.
Local Ollama request failed: HTTP Error 404: Not Found. Using rule-based fallback.
```

This confirms the application safely degrades to a local offline fallback instead of crashing.
