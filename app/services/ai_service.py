# app/services/ai_service.py – Groq (Llama 3.3 70B) with adaptive token management
# Automatically reduces output size if the free-tier token limit is hit.

import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Get a free key at https://console.groq.com"
    )

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Exhaustive system prompt – no upper bound on questions, but model will be limited by token capacity
SYSTEM_PROMPT = """You are an expert career coach and technical interviewer with decades of experience across every industry.
Your task is to generate **every possible relevant interview question** for the job described by the user.
There is no upper limit – include all questions that could reasonably be asked, from general HR/behavioural to
extremely advanced technical and scenario‑based questions.

You must output **only** a valid JSON object with a key "questions" that contains an array of question objects.
Generate **as many questions as you can** within the available output length. Do not stop early – fill the response completely.

Every single question must be answered **from scratch**, assuming the candidate has zero prior knowledge of the topic.
Break down every answer step‑by‑step, starting from the most fundamental concept and building up.
Include a separate detailed explanation of **why** the answer is correct and how to approach similar questions.

Each object must have these exact keys:
- "question" (string) – The interview question.
- "answer" (string) – A thorough, step‑by‑step answer **from scratch**. Do not skip any elementary steps.
- "explanation" (string) – Additional reasoning, tips, common mistakes, and why the answer works.
- "image_description" (string) – A short description for an image that would help illustrate the answer.
- "image_url" (string) – A placeholder image URL using this exact format:
  "https://via.placeholder.com/600x400?text=Your+Description+Here"
- "references" (array of objects with "title" and "url" – at least one real, reputable reference per question)

Coverage (comprehensive, no limits):
- All general HR / behavioural questions relevant to the role and company
- All role‑specific technical / core questions, from absolute basics to niche advanced topics
- A wide variety of scenario‑based, problem‑solving, and critical‑thinking questions
- Company‑specific insights (if company profile provided) and industry‑trend questions
- Questions that test soft skills, cultural fit, leadership, and collaboration

Output **only** the JSON object, no markdown, no extra text. Ensure all strings are properly escaped.
"""

def generate_interview_questions(job_description, company_profile, responsibilities, requirements):
    """
    Calls Groq API. If the token limit is hit, it automatically reduces the output size and retries.
    """
    user_prompt = f"""
Job Description:
{job_description}

Company Profile:
{company_profile}

Responsibilities:
{responsibilities}

Candidate Requirements:
{requirements}

Generate EVERY possible interview question for this role. Fill the response completely, from scratch.
Output the complete JSON now."""

    # Start with a modest max_tokens that fits within Groq's free-tier limit (12,000 total)
    # The input prompt (system + user) is probably 500-2000 tokens, so 8000-9000 is safe.
    current_max_tokens = 8000
    max_retries = 3  # Allow extra retry for token reduction

    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=current_max_tokens,
            )

            raw_output = response.choices[0].message.content.strip()
            logger.debug(f"Raw output length: {len(raw_output)} chars")

            # Parse JSON, with fallback extraction
            try:
                result = json.loads(raw_output)
            except json.JSONDecodeError:
                logger.warning("JSON parse error, attempting extraction...")
                start = raw_output.find('{')
                end = raw_output.rfind('}')
                if start != -1 and end != -1:
                    result = json.loads(raw_output[start:end+1])
                else:
                    raise ValueError("No JSON object found in the response.")

            if isinstance(result, dict) and "questions" in result:
                data = result["questions"]
            elif isinstance(result, list):
                data = result
            else:
                raise ValueError("Response does not contain 'questions' key or an array.")

            if not isinstance(data, list):
                raise ValueError("Questions data is not a JSON array.")

            required_keys = {"question", "answer", "explanation", "image_description", "image_url", "references"}
            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {idx} is not an object.")
                missing = required_keys - item.keys()
                if missing:
                    raise ValueError(f"Item {idx} missing keys: {missing}")

            logger.info(f"Successfully generated {len(data)} questions.")
            return data

        except ValueError as e:
            # JSON / validation error – retry with a reminder
            logger.error(f"Attempt {attempt+1}: Invalid output: {e}")
            if attempt == max_retries:
                raise ValueError(f"Failed to obtain valid JSON after {max_retries+1} attempts: {e}")
            user_prompt += "\n\nIMPORTANT: Your previous response was not valid JSON. Please output ONLY the JSON object exactly as instructed."

        except Exception as e:
            # API error (including 413 token limit)
            logger.error(f"Groq API call failed: {e}")
            # Check if it's a token limit error (413) – then reduce max_tokens and retry
            if hasattr(e, 'status_code') and e.status_code == 413:
                # Reduce max_tokens significantly (e.g., by half, but never below 2000)
                new_limit = max(2000, current_max_tokens // 2)
                logger.warning(f"Token limit hit. Reducing max_tokens from {current_max_tokens} to {new_limit}")
                current_max_tokens = new_limit
                # Don't count this as a real attempt – we want to retry with the new limit
                continue

            if attempt == max_retries:
                raise Exception("AI service is currently unavailable. Please try again later.")
            import time
            time.sleep(1)