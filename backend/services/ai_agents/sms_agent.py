# backend/services/ai_agents/sms_agent.py

import json
import httpx
from backend.core.config import settings
from backend.models.ai_models import AIResponse
from backend.parsers.sms_parser import parse_sms
from backend.services.ai_agents.categorization_agent import CategorizationAgent
from backend.utils.logger import logger


class SMSAgent:
    """
    Hybrid SMS Analyzer:
    • Uses AI provider only if API key exists
    • Auto-fallback to rule-based parser
    • Strict JSON cleaning
    • Returns validated dict (no eval anywhere)
    """

    def __init__(self):
        self.providers = {
            "groq": settings.GROQ_API_KEY,
            "openai": settings.OPENAI_API_KEY,
            "gemini": settings.GEMINI_API_KEY,
            "cohere": settings.COHERE_API_KEY
        }
        self.categorizer = CategorizationAgent()

    # =====================================================================
    # PUBLIC MAIN ENTRY
    # =====================================================================
    async def analyze_sms(self, sms_text: str) -> AIResponse:
        prompt = self._build_prompt(sms_text)

        # Try each AI provider
        for provider, api_key in self.providers.items():
            if not api_key:
                continue

            try:
                logger.info(f"Trying provider: {provider}")
                raw = await self._call_provider(provider, api_key, prompt)

                if not raw:
                    continue

                cleaned = self._clean_json(raw)

                if not cleaned or not self._valid_json(cleaned):
                    continue

                parsed = json.loads(cleaned)

                normalized = await self._normalize_result(parsed, sms_text)

                # return dict safely (NOT STRING)
                return AIResponse(
                    success=True,
                    provider=provider,
                    text=json.dumps(normalized)
                )

            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}")
                continue

        # =====================================================
        # FALLBACK → Rule-based, guaranteed path
        # =====================================================
        logger.info("AI unavailable → falling back to strict parser")

        try:
            parsed = parse_sms(sms_text)

            parsed["category"] = await self.categorizer.categorize_transaction(
                sms_text, parsed.get("amount", 0)
            )

            return AIResponse(
                success=True,
                provider="rule_based",
                text=json.dumps(parsed)
            )

        except Exception as e:
            logger.error(f"Fallback parse failed: {e}")
            return AIResponse(
                success=False,
                provider="error",
                text=json.dumps({
                    "txn_type": "Unknown",
                    "amount": 0,
                    "counterparty": "Unknown",
                    "category": "Miscellaneous",
                    "error": str(e)
                })
            )

    # =====================================================================
    # PROMPT
    # =====================================================================
    def _build_prompt(self, sms_text: str) -> str:
        return f"""
Extract bank transaction details from this SMS.

Return STRICT JSON ONLY with keys:

- "txn_type": "Credited" | "Debited" | "Unknown"
- "amount": number
- "counterparty": string
- "category": string

SMS: "{sms_text}"
"""

    # =====================================================================
    # CLEAN JSON
    # =====================================================================
    def _clean_json(self, text: str) -> str:
        if not text:
            return None

        cleaned = text.strip()

        # remove code fences if present
        cleaned = cleaned.replace("```json", "")
        cleaned = cleaned.replace("```", "")

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            return cleaned[start:end+1].strip()

        return None

    # =====================================================================
    # VALIDATE JSON
    # =====================================================================
    def _valid_json(self, text: str) -> bool:
        try:
            parsed = json.loads(text)
            required = ["txn_type", "amount", "counterparty", "category"]
            return all(k in parsed for k in required)
        except:
            return False

    # =====================================================================
    # NORMALIZE RESULT
    # =====================================================================
    async def _normalize_result(self, data: dict, sms_text: str) -> dict:

        # txn_type
        txn_type = data.get("txn_type", "").lower()
        if "credit" in txn_type:
            txn_type = "Credited"
        elif "debit" in txn_type:
            txn_type = "Debited"
        else:
            txn_type = "Unknown"

        # amount
        amount = data.get("amount", 0)
        if isinstance(amount, str):
            try:
                amount = float(amount.replace(",", "").replace("₹", ""))
            except:
                amount = 0

        # counterparty
        counterparty = data.get("counterparty") or "Unknown"

        # category via our own logic
        category = await self.categorizer.categorize_transaction(sms_text, amount)

        return {
            "txn_type": txn_type,
            "amount": amount,
            "counterparty": counterparty,
            "category": category
        }

    # =====================================================================
    # PROVIDER ROUTER
    # =====================================================================
    async def _call_provider(self, provider: str, api_key: str, prompt: str) -> str:
        if provider == "groq":
            return await self._call_groq(prompt, api_key)
        if provider == "openai":
            return await self._call_openai(prompt, api_key)
        if provider == "gemini":
            return await self._call_gemini(prompt, api_key)
        if provider == "cohere":
            return await self._call_cohere(prompt, api_key)
        return None

    # =====================================================================
    # GROQ API
    # =====================================================================
    async def _call_groq(self, prompt: str, api_key: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=18) as client:
                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                        "response_format": {"type": "json_object"}
                    }
                )
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None

    # =====================================================================
    # OPENAI (new 2024 API)
    # =====================================================================
    async def _call_openai(self, prompt: str, api_key: str) -> str:
        try:
            import openai
            openai.api_key = api_key

            res = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )

            return res["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None

    # =====================================================================
    # GEMINI
    # =====================================================================
    async def _call_gemini(self, prompt: str, api_key: str) -> str:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")

            res = await model.generate_content_async(prompt)
            return res.text

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None

    # =====================================================================
    # COHERE
    # =====================================================================
    async def _call_cohere(self, prompt: str, api_key: str) -> str:
        try:
            import cohere
            client = cohere.AsyncClient(api_key)

            res = await client.generate(
                prompt=prompt,
                model="command",
                max_tokens=150,
                temperature=0.1
            )

            return res.generations[0].text

        except Exception as e:
            logger.error(f"Cohere error: {e}")
            return None
