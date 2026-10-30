from datetime import datetime, timezone

from google.adk.tools import ToolContext

from emissions import (
    calculate_travel_emissions,
    calculate_electricity_emissions,
    calculate_ac_emissions,
)


def _save_activity(result: dict, description: str, tool_context: ToolContext):
    """Save a successfully calculated activity to the current ADK session."""

    activities = list(tool_context.state.get("activities", []))

    activity = {
        "description": description,
        "category": result["category"],
        "emissions_kg_co2e": result["emissions_kg_co2e"],
        "logged_at": datetime.now(timezone.utc).isoformat(),
        "calculation": result,
    }

    activities.append(activity)

    # ADK tracks this change and saves it to the session.
    tool_context.state["activities"] = activities

    return activity


def record_travel_activity(
    mode: str,
    km: float,
    tool_context: ToolContext
) -> dict:
    """Calculate travel emissions and save the activity to the user's session."""

    result = calculate_travel_emissions(mode, km)

    activity = _save_activity(
        result,
        f"Travelled {km} km by {mode}",
        tool_context
    )

    return {
        "status": "success",
        "message": "Travel activity calculated and saved.",
        "activity": activity,
    }


def record_electricity_activity(
    kwh: float,
    tool_context: ToolContext
) -> dict:
    """Calculate electricity emissions and save the activity."""

    result = calculate_electricity_emissions(kwh)

    activity = _save_activity(
        result,
        f"Used {kwh} kWh of electricity",
        tool_context
    )

    return {
        "status": "success",
        "message": "Electricity activity calculated and saved.",
        "activity": activity,
    }


def record_ac_activity(
    hours: float,
    power_kw: float,
    tool_context: ToolContext
) -> dict:
    """Calculate AC electricity emissions and save the activity."""

    result = calculate_ac_emissions(hours, power_kw)

    activity = _save_activity(
        result,
        f"Used an AC rated at {power_kw} kW for {hours} hours",
        tool_context
    )

    return {
        "status": "success",
        "message": "AC activity calculated and saved.",
        "activity": activity,
    }


def get_carbon_summary(tool_context: ToolContext) -> dict:
    """Retrieve saved activities and calculate the session's carbon total."""

    activities = tool_context.state.get("activities", [])

    if not activities:
        return {
            "status": "success",
            "activity_count": 0,
            "total_emissions_kg_co2e": 0,
            "message": "No activities have been recorded in this session yet."
        }

    total = sum(
        item["emissions_kg_co2e"]
        for item in activities
    )

    breakdown = {}

    for item in activities:
        category = item["category"]

        breakdown[category] = (
            breakdown.get(category, 0)
            + item["emissions_kg_co2e"]
        )

    return {
        "status": "success",
        "activity_count": len(activities),
        "total_emissions_kg_co2e": round(total, 4),
        "category_breakdown": {
            key: round(value, 4)
            for key, value in breakdown.items()
        },
        "activities": activities,
    }