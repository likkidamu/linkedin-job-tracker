import json
import logging
import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL

logger = logging.getLogger(__name__)


class ResumeTailor:
    """
    Uses Ollama (local LLM) to tailor a base resume to match a specific job description.
    Completely free — no API keys needed for the AI part.
    """

    def __init__(self, base_resume_path: str = "base_resume.json"):
        with open(base_resume_path, "r") as f:
            self.base_resume = json.load(f)

        self.api_url = f"{OLLAMA_BASE_URL}/api/generate"
        self.model = OLLAMA_MODEL

        # Verify Ollama is reachable
        try:
            resp = requests.get(OLLAMA_BASE_URL, timeout=5)
            logger.info(f"Ollama is running at {OLLAMA_BASE_URL}")
        except requests.ConnectionError:
            logger.warning(
                f"Ollama not reachable at {OLLAMA_BASE_URL}. "
                "Make sure Ollama is running: ollama serve"
            )

    def tailor_resume(self, job: dict) -> dict:
        """
        Takes a job dict and returns a tailored resume dict.

        The tailored resume has the same structure as base_resume.json
        but with content optimized for the specific job.
        """
        prompt = f"""You are an expert resume writer. Your task is to tailor the following
base resume to match a specific job posting.

RULES:
1. DO NOT fabricate experience, skills, or qualifications the candidate doesn't have.
2. DO rewrite bullet points to emphasize relevant experience using keywords from the job.
3. DO reorder skills to prioritize those mentioned in the job description.
4. DO adjust the summary to align with the role.
5. DO use action verbs and quantify achievements where possible.
6. Keep the resume concise — max 2 pages worth of content.

BASE RESUME:
{json.dumps(self.base_resume, indent=2)}

JOB POSTING:
Company: {job.get('company', 'Unknown')}
Title: {job.get('title', 'Unknown')}
Location: {job.get('location', 'Unknown')}
Description:
{job.get('description', 'No description available')[:3000]}

Return ONLY a valid JSON object with the same structure as the base resume,
but with tailored content. No markdown, no explanation — just the JSON."""

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 4096,
                    },
                },
                timeout=300,  # LLMs can take a while on CPU
            )
            response.raise_for_status()

            response_text = response.json().get("response", "").strip()

            # Handle potential markdown code blocks in response
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0].strip()

            tailored = json.loads(response_text)
            logger.info(f"Resume tailored for: {job.get('title')} at {job.get('company')}")
            return tailored

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            return self.base_resume
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            return self.base_resume
