import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=90000),
)


MODELS = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash", "gemini-3.1-flash-lite"]

CONFIG = types.GenerateContentConfig(temperature=0.2)


def ask_gemini(prompt: str) -> dict:
    last_error = None
    for model in MODELS:
        for attempt in range(3):
            try:
                print(f"Try: {model} (attempt {attempt + 1})")
                response = client.models.generate_content(
                    model=model, contents=prompt, config=CONFIG
                )
                text = response.text.strip()
                text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                return json.loads(text)
            except Exception as e:
                last_error = e
                print("Error:", repr(e)[:150])
                time.sleep(5 * (attempt + 1))
    raise last_error


# ---------- Activity 3.1: Construction Project Planning Logic ----------
def plan_construction_project(params: dict) -> dict:
    prompt = f"""
You are a senior construction cost estimator and project planner.
Use the parameters below and return ONLY valid JSON.

Parameters:
{json.dumps(params, indent=2)}

Return JSON with this exact structure:
{{
  "cost_estimate": {{
    "currency": "INR",
    "total_cost": number,
    "cost_per_sqft": number,
    "breakdown": {{
      "foundation_structure": number,
      "masonry_finishing": number,
      "electrical_plumbing": number,
      "labor": number,
      "contingency": number
    }}
  }},
  "materials": [
    {{"item": string, "quantity": string, "estimated_cost": number}}
  ],
  "schedule": [
    {{"phase": string, "duration_weeks": number, "tasks": [string]}}
  ],
  "risks": [string],
  "assumptions": [string]
}}
Use realistic local market rates for the given location.
"""
    return ask_gemini(prompt)


# ---------- Activity 3.2: Real Estate Valuation Engine ----------
def estimate_real_estate_value(params: dict, plan: dict) -> dict:
    construction_cost = plan["cost_estimate"]["total_cost"]
    prompt = f"""
You are a real estate valuation analyst.
Estimate the market value of this property after completion. Return ONLY valid JSON.

Property parameters:
{json.dumps(params, indent=2)}

Estimated construction cost: {construction_cost}

Return JSON with this exact structure:
{{
  "estimated_land_value": number,
  "estimated_market_value": number,
  "value_range": {{"low": number, "high": number}},
  "price_per_sqft": number,
  "roi_percent": number,
  "investment_verdict": "good" | "moderate" | "poor",
  "key_factors": [string],
  "reasoning": string
}}
Consider location, quality, area, and local market trends.
"""
    return ask_gemini(prompt)


def run_planning_and_valuation(params: dict) -> dict:
    plan = plan_construction_project(params)
    valuation = estimate_real_estate_value(params, plan)
    return {"plan": plan, "valuation": valuation}


if __name__ == "__main__":
    print("Script start hui")
    print("API key mili:", bool(os.getenv("GEMINI_API_KEY")))

    sample = {
        "location": "Indore, India",
        "built_up_area_sqft": 2000,
        "floors": 2,
        "quality": "standard",
        "project_type": "residential",
        "target_months": 10,
    }
    try:
        result = run_planning_and_valuation(sample)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("ERROR:", repr(e))