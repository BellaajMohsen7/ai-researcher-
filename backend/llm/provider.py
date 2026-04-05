import json
import logging
from groq import Groq
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient
from config import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """LLM with automatic fallback: Groq -> Gemini -> HF"""

    def __init__(self):
        # Primary: Groq
        self.groq_client = None
        if settings.groq_api_key:
            self.groq_client = Groq(api_key=settings.groq_api_key)

        # Backup 1: Gemini (new google-genai SDK)
        self.gemini_client = None
        if settings.gemini_api_key:
            self.gemini_client = genai.Client(api_key=settings.gemini_api_key)

        # Backup 2: HuggingFace
        self.hf_client = None
        if settings.hf_api_token:
            self.hf_client = InferenceClient(token=settings.hf_api_token)

    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.3) -> str:
        """Try each provider in order until one works."""

        # --- Try Groq first ---
        if self.groq_client:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.groq_client.chat.completions.create(
                    model=settings.groq_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=4096,
                )
                logger.info("Used Groq successfully")
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Groq failed: {e}")

        # --- Try Gemini (new google-genai SDK) ---
        if self.gemini_client:
            try:
                full_prompt = ""
                if system_prompt:
                    full_prompt = f"System: {system_prompt}\n\n"
                full_prompt += prompt

                response = self.gemini_client.models.generate_content(
                    model=settings.gemini_model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=4096,
                    )
                )
                logger.info("Used Gemini successfully")
                return response.text
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")

        # --- Try HuggingFace ---
        if self.hf_client:
            try:
                sys_tag = "<" + "|system|" + ">"
                user_tag = "<" + "|user|" + ">"
                asst_tag = "<" + "|assistant|" + ">"
                full_prompt = ""
                if system_prompt:
                    full_prompt = f"{sys_tag}{system_prompt}"
                full_prompt += f"{user_tag}{prompt}{asst_tag}"

                response = self.hf_client.text_generation(
                    full_prompt,
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    max_new_tokens=4096,
                    temperature=temperature,
                )
                logger.info("Used HuggingFace successfully")
                return response
            except Exception as e:
                logger.warning(f"HuggingFace failed: {e}")

        raise RuntimeError("All LLM providers failed!")

    async def generate_json(self, prompt: str, system_prompt: str = "") -> dict:
        """Generate and parse JSON response."""
        json_system = (
            system_prompt
            + "\n\nYou MUST respond with valid JSON only. "
            "No markdown, no explanation, just JSON."
        )

        text = await self.generate(prompt, json_system, 0.1)
        # Clean potential markdown wrapping
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        return json.loads(text.strip())


# Singleton
llm = LLMProvider()
