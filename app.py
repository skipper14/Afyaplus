import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError
import httpx


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

DEFAULT_MESSAGE = (
    "I have had severe chest pain for 20 minutes and I feel short of breath."
)


def build_prompt(prompt_variant: str, patient_message: str) -> str:
    """Build a prompt for the chosen prompt engineering style."""
    if prompt_variant == "baseline":
        return (
            "You are an AfyaPlus triage assistant. "
            "Read the patient message and return only a JSON object with keys: "
            "is_critical_emergency, detected_symptoms, clinical_reasoning_summary, routing_destination."
        )

    if prompt_variant == "structured":
        return (
            "You are an AfyaPlus triage assistant. "
            "Use a concise, factual analysis. "
            "Output only JSON in this exact schema: "
            "{\"is_critical_emergency\": boolean, \"detected_symptoms\": [\"string\"], "
            "\"clinical_reasoning_summary\": \"string\", \"routing_destination\": \"string\"}. "
            "Do not add markdown, prose, or explanation outside the JSON object."
        )

    # Final prompt variant with role assignment, chain-of-thought instructions,
    # and strict guardrails against conversational fluff.
    return (
        "You are AfyaPlus Triage Engine, a calm, evidence-based routing assistant. "
        "Your job is to classify the patient's message into a strict JSON object for a downstream backend. "
        "Before generating the final answer, silently reason through the following steps internally: "
        "1) identify obvious symptoms, 2) decide if the case is a critical emergency, "
        "3) choose the most appropriate routing_destination, and 4) write a short clinical summary. "
        "Do not reveal the chain of thought. "
        "Rules: never add conversational fluff, never include introductory remarks, "
        "never mention uncertainty as a disclaimer, never invent medical facts, "
        "and never output markdown fences or plain text. "
        "Return only a single valid JSON object with the keys: "
        "is_critical_emergency, detected_symptoms, clinical_reasoning_summary, routing_destination. "
        f"Patient message: {patient_message}"
    )


def normalize_payload(raw_text: str) -> Dict[str, Any]:
    """Extract a JSON object from either plain JSON or fenced markdown output."""
    if not raw_text:
        return {}

    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return {}


def ensure_schema(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the output contains the required schema keys."""
    schema = {
        "is_critical_emergency": False,
        "detected_symptoms": [],
        "clinical_reasoning_summary": "No structured analysis available.",
        "routing_destination": "primary_care",
    }
    if not isinstance(payload, dict):
        return schema

    result = schema.copy()
    result["is_critical_emergency"] = bool(payload.get("is_critical_emergency", False))
    symptoms = payload.get("detected_symptoms") or []
    if isinstance(symptoms, list):
        result["detected_symptoms"] = [str(item) for item in symptoms if str(item).strip()]
    elif isinstance(symptoms, str):
        result["detected_symptoms"] = [symptoms]

    summary = payload.get("clinical_reasoning_summary")
    if isinstance(summary, str) and summary.strip():
        result["clinical_reasoning_summary"] = summary.strip()

    destination = payload.get("routing_destination")
    if isinstance(destination, str) and destination.strip():
        result["routing_destination"] = destination.strip()
    else:
        result["routing_destination"] = "primary_care"

    return result


def run_cloud_inference(patient_message: str, prompt: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    """Try the cloud path with a strict timeout and return a parsed payload if successful."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, None, "Cloud key missing"

    client = OpenAI(api_key=api_key)
    started = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": patient_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=300,
            timeout=4.0,
        )
        content = response.choices[0].message.content or "{}"
        elapsed = time.perf_counter() - started
        parsed = ensure_schema(normalize_payload(content))
        return parsed, elapsed, None
    except (httpx.TimeoutException, TimeoutError, AuthenticationError) as exc:
        elapsed = time.perf_counter() - started
        return None, elapsed, f"Cloud error: {exc}"
    except Exception as exc:  # pragma: no cover - broad guard for network issues
        elapsed = time.perf_counter() - started
        return None, elapsed, f"Cloud error: {exc}"


def run_local_inference(patient_message: str, prompt: str) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str]]:
    """Use Ollama locally as a fallback engine."""
    started = time.perf_counter()
    try:
        full_prompt = f"{prompt}\nPatient message: {patient_message}\nReturn only valid JSON."
        completed = subprocess.run(
            ["ollama", "run", "llama3.2", full_prompt],
            text=True,
            capture_output=True,
            timeout=20,
            check=True,
        )
        elapsed = time.perf_counter() - started
        parsed = ensure_schema(normalize_payload(completed.stdout))
        return parsed, elapsed, None
    except FileNotFoundError as exc:
        elapsed = time.perf_counter() - started
        return None, elapsed, f"Ollama CLI not found: {exc}"
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        return None, elapsed, f"Ollama timeout: {exc}"
    except subprocess.CalledProcessError as exc:
        elapsed = time.perf_counter() - started
        stderr = exc.stderr or ""
        return None, elapsed, f"Ollama failed: {stderr or exc}"
    except Exception as exc:
        elapsed = time.perf_counter() - started
        return None, elapsed, f"Ollama error: {exc}"


def main() -> None:
    patient_message = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else DEFAULT_MESSAGE
    prompt = build_prompt("guardrailed", patient_message)

    print("AfyaPlus triage engine starting...")
    print(f"Patient message: {patient_message}")

    cloud_result, cloud_elapsed, cloud_error = run_cloud_inference(patient_message, prompt)
    if cloud_result:
        print("Cloud path succeeded.")
        if cloud_elapsed is not None:
            print(f"Cloud latency: {cloud_elapsed:.2f}s")
        print("Parsed dictionary:")
        print(json.dumps(cloud_result, indent=2))
        print(f"Routing decision: {cloud_result['routing_destination']}")
        return

    print("Cloud path failed or timed out; falling back to local Ollama.")
    if cloud_error:
        print(cloud_error)
    local_result, local_elapsed, local_error = run_local_inference(patient_message, prompt)
    if local_result:
        if local_elapsed is not None:
            print(f"Local latency: {local_elapsed:.2f}s")
        print("Parsed dictionary:")
        print(json.dumps(local_result, indent=2))
        print(f"Routing decision: {local_result['routing_destination']}")
        return

    print(local_error or "No fallback response generated.")


if __name__ == "__main__":
    main()
