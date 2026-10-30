import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

from activity_tools import (
    record_travel_activity,
    record_electricity_activity,
    record_ac_activity,
    get_carbon_summary,
)


# Load API key from backend/.env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env")


root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="carbon_coach",

    description=(
        "An AI assistant that helps users track "
        "and reduce their carbon footprint."
    ),

    instruction="""
    You are Carbon Coach, an AI-powered environmental assistant.

    Your responsibilities:
    1. Understand users' daily activities.
    2. Calculate their carbon emissions.
    3. Record successfully calculated activities.
    4. Retrieve their recorded activities.
    5. Explain their carbon footprint.
    6. Suggest practical ways to reduce emissions.

    TOOL RULES:
    - Use record_travel_activity for travel.
    - Use record_electricity_activity for electricity usage.
    - Use record_ac_activity for air conditioner usage.
    - Use get_carbon_summary when users ask for their total
      or want to review their recorded activities.
    - Do not claim an activity was saved unless the tool
      confirms successful recording.
    - Do not invent or estimate missing activity data.
    - Ask follow-up questions if required information is missing.
    - Never calculate emissions mentally.
    - Explain results in kg CO2e.

    MEMORY RULES:
    - Use the activity summary tool to retrieve recorded activities.
    - Remember that recorded activities belong to the current session.
    - Do not claim that session data is permanently stored.

    Be friendly, clear, and helpful.
    """,

    tools=[
        record_travel_activity,
        record_electricity_activity,
        record_ac_activity,
        get_carbon_summary,
    ],
)