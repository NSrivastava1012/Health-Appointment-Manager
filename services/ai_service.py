import json
import ollama


# ============================================================
# PRE-VISIT AI SUMMARY
# ============================================================

def generate_previsit_summary(symptoms):

    prompt = f"""
You are an assistant supporting a doctor before a patient appointment.

Analyze ONLY the patient's self-reported symptoms.

Patient symptoms:
{symptoms}

Create a concise pre-visit summary.

Rules:
- Do not diagnose the patient.
- Do not recommend medication.
- Do not invent symptoms.
- Use only information provided by the patient.
- If duration is not mentioned, write "Not specified".
- Urgency must be exactly one of:
  Routine, Soon, Urgent
- Provide exactly 3 suggested questions for the doctor.

Return ONLY valid JSON:

{{
    "chief_complaint": "string",
    "key_symptoms": ["string"],
    "duration": "string",
    "urgency": "Routine",
    "suggested_questions": [
        "string",
        "string",
        "string"
    ]
}}
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response["message"]["content"]

    # Remove markdown code fences
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)


# ============================================================
# POST-VISIT AI SUMMARY
# ============================================================

def generate_postvisit_summary(
    diagnosis,
    post_visit_notes,
    prescription,
    follow_up_instructions
):

    prompt = f"""
You are an assistant helping convert a doctor's post-visit
information into a simple, patient-friendly summary.

Use ONLY the information provided by the doctor.

Doctor's diagnosis:
{diagnosis or "Not provided"}

Doctor's post-visit notes:
{post_visit_notes or "Not provided"}

Prescription:
{prescription or "Not provided"}

Follow-up instructions:
{follow_up_instructions or "Not provided"}

Create a clear and easy-to-understand summary for the patient.

Rules:
- Use ONLY the information provided by the doctor.
- Do not add information.
- Do not create a new diagnosis.
- Do not recommend additional medicines.
- Do not change medicine names.
- Do not change dosage.
- Do not change frequency.
- Do not change medication instructions.
- Do not contradict the doctor's instructions.
- Do not make medical assumptions.
- Explain medical terminology in simple language where possible.
- If a field is empty or not provided, do not invent information.
- Keep the summary concise.
- Write directly for the patient.
- Do not include statements such as "consult another doctor"
  unless the doctor explicitly included such an instruction.
- Do not mention that you are an AI.

Return ONLY valid JSON:

{{
    "summary": "string"
}}
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    text = response["message"]["content"]

    # Remove markdown code fences
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    result = json.loads(text)

    return result.get(
        "summary",
        "Post-visit summary could not be generated."
    )