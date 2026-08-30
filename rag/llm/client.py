import os
from typing import Optional
from dotenv import load_dotenv

# Automatically load .env file if present
load_dotenv()

class LLMClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.api_type = None
        self.client = None

        # Check for Gemini API key
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=gemini_key)
                self.api_type = "gemini"
            except Exception as e:
                print(f"[LLMClient] Gemini Client init failed: {e}")
        elif openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
                self.api_type = "openai"
            except Exception as e:
                print(f"[LLMClient] OpenAI Client init failed: {e}")

        if not self.api_type:
            print("[LLMClient] No API keys found or initialization failed. Using grounded local engine mode.")

    def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        if self.api_type == "gemini" and self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=f"{system_prompt}\n\n{user_prompt}"
                )
                return response.text
            except Exception as e:
                print(f"[LLMClient] Gemini API call failed: {e}")

        elif self.api_type == "openai" and self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[LLMClient] OpenAI API call failed: {e}")

        return None
