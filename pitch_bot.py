import os
from fastapi import FastAPI, Form
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# Load the pitch samples once at startup
with open("sample_pitches.txt", "r", encoding="utf-8") as f:
    sample = f.read().strip()

def generate_prompt(data: dict) -> str:
    header = f"""
You are a world-class startup pitch strategist trusted by top-tier venture capital firms to help founders craft pitches that are crisp, credible, and investor-ready.

Your job is to read the detailed information provided by the founder and generate a compelling, structured pitch. The pitch should cover the full spectrum of what VCs want to hear, including: the problem, solution, market, product, traction, business model, team, competition, financials, and future vision.

**Guidelines:**
- Make the pitch persuasive and visionary, yet grounded in logic and realistic strategy.
- Use clear section headers (like a pitch deck structure).
- Use confident, founder-style language (no passive tone or robotic output).
- Focus on clarity, differentiation, and strong narrative.
- Avoid generic or vague language—be specific and memorable.

Some of the best pitches from where you can take references on how to write a pitch: are:
{sample}
these are just refernces. The pitch has to be in First person perspective as if the founder is gonna speak it in front of the VCs.
Dont give any sections. just a perfect pitch.

dont give any html and also no introduction like here is a pitch.
just give a deliverable ready pitch.

Below is the information shared by the founder:
"""

    founder_data = ""
    for key, value in data.items():
        if value:
            section_title = key.replace('_', ' ').title()
            founder_data += f"\n### {section_title}:\n{value.strip()}\n"

    closing = "\nNow, using the information above, generate a powerful, investor-grade startup pitch ready to be delivered to VCs.\n"
    return header.strip() + founder_data + closing


@app.post("/generate-pitch")
async def generate_pitch_form(
    core_business_info: str = Form(...),
    company_basics: Optional[str] = Form(None),
    problem_solution: Optional[str] = Form(None),
    market_analysis: Optional[str] = Form(None),
    market_size_opportunity: Optional[str] = Form(None),
    competition: Optional[str] = Form(None),
    financial_metrics: Optional[str] = Form(None),
    historical_financials: Optional[str] = Form(None),
    customer_metrics: Optional[str] = Form(None),
    unit_economics: Optional[str] = Form(None),
    financial_projections: Optional[str] = Form(None),
    revenue_forecasts: Optional[str] = Form(None),
    expense_projections: Optional[str] = Form(None),
    business_model: Optional[str] = Form(None),
    revenue_streams: Optional[str] = Form(None),
    operations: Optional[str] = Form(None),
    team_info: Optional[str] = Form(None),
    founding_team: Optional[str] = Form(None),
    key_personnel: Optional[str] = Form(None),
    traction_validation: Optional[str] = Form(None),
    product_development: Optional[str] = Form(None),
    market_validation: Optional[str] = Form(None),
    business_traction: Optional[str] = Form(None),
    investment_details: Optional[str] = Form(None),
    funding_history: Optional[str] = Form(None),
    current_fundraising: Optional[str] = Form(None),
    future_planning: Optional[str] = Form(None),
    operational_metrics: Optional[str] = Form(None),
    kpis: Optional[str] = Form(None),
    risk_factors: Optional[str] = Form(None),
    additional_context: Optional[str] = Form(None),
    personal_story: Optional[str] = Form(None),
    supporting_materials: Optional[str] = Form(None),
):
    data = {
        "core_business_info": core_business_info,
        "company_basics": company_basics,
        "problem_solution": problem_solution,
        "market_analysis": market_analysis,
        "market_size_opportunity": market_size_opportunity,
        "competition": competition,
        "financial_metrics": financial_metrics,
        "historical_financials": historical_financials,
        "customer_metrics": customer_metrics,
        "unit_economics": unit_economics,
        "financial_projections": financial_projections,
        "revenue_forecasts": revenue_forecasts,
        "expense_projections": expense_projections,
        "business_model": business_model,
        "revenue_streams": revenue_streams,
        "operations": operations,
        "team_info": team_info,
        "founding_team": founding_team,
        "key_personnel": key_personnel,
        "traction_validation": traction_validation,
        "product_development": product_development,
        "market_validation": market_validation,
        "business_traction": business_traction,
        "investment_details": investment_details,
        "funding_history": funding_history,
        "current_fundraising": current_fundraising,
        "future_planning": future_planning,
        "operational_metrics": operational_metrics,
        "kpis": kpis,
        "risk_factors": risk_factors,
        "additional_context": additional_context,
        "personal_story": personal_story,
        "supporting_materials": supporting_materials
    }

    prompt = generate_prompt(data)

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a VC pitch expert helping startups write strong, fundable pitches."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024
    )

    pitch_text = response.choices[0].message.content.strip()
    return {"pitch": pitch_text}
