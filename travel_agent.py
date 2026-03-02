import os
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
BRIGHTDATA_TOKEN = os.getenv("BRIGHTDATA_API_TOKEN")

# --- Brightdata scraping functions ---

def brightdata_search(query: str) -> str:
    """Search the web using Brightdata SERP API and return results as text."""
    if not BRIGHTDATA_TOKEN:
        return "Brightdata not configured, using AI knowledge."
    try:
        response = requests.get(
            "https://api.brightdata.com/serp",
            headers={"Authorization": f"Bearer {BRIGHTDATA_TOKEN}"},
            params={"q": query, "engine": "google", "gl": "us", "hl": "en"},
            timeout=30,
        )
        if response.status_code == 200:
            data = response.json()
            # Extract useful text from organic results
            results = []
            for item in data.get("organic", [])[:5]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                results.append(f"- {title}: {snippet} ({link})")
            return "\n".join(results) if results else "No results found."
        else:
            return f"Brightdata API returned status {response.status_code}. Using AI knowledge instead."
    except Exception as e:
        return f"Search error: {str(e)}. Using AI knowledge instead."


def brightdata_scrape(url: str) -> str:
    """Scrape a specific URL using Brightdata Web Unlocker."""
    if not BRIGHTDATA_TOKEN:
        return "Brightdata not configured."
    try:
        response = requests.post(
            "https://api.brightdata.com/request",
            headers={
                "Authorization": f"Bearer {BRIGHTDATA_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"url": url, "format": "raw"},
            timeout=45,
        )
        if response.status_code == 200:
            # Return first 3000 chars to avoid overwhelming Claude
            return response.text[:3000]
        else:
            return f"Scrape returned status {response.status_code}."
    except Exception as e:
        return f"Scrape error: {str(e)}."


# --- Tool definitions that Claude can call ---

TOOLS = [
    {
        "name": "search_hotels",
        "description": (
            "Search for hotels in a city with prices and ratings. "
            "Use this to find accommodation options within the traveler's budget."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Rome"},
                "max_price_per_night": {
                    "type": "number",
                    "description": "Maximum budget per night in USD",
                },
                "num_nights": {
                    "type": "integer",
                    "description": "Number of nights to stay",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "search_attractions",
        "description": (
            "Search for tourist attractions, sightseeing spots, and landmarks in a city. "
            "Returns names, entry fees, ratings, and recommended visit duration."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "search_restaurants_and_food",
        "description": (
            "Search for typical restaurant prices and food costs in a city. "
            "Returns average meal prices for budget, mid-range, and upscale options."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "search_transport",
        "description": (
            "Search for local transport costs in a city: metro/bus day passes, "
            "taxi prices, and airport transfer costs."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        },
    },
]


def handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute the tool Claude requested and return the result."""
    city = tool_input.get("city", "")

    if tool_name == "search_hotels":
        price = tool_input.get("max_price_per_night", "")
        nights = tool_input.get("num_nights", "")
        query = f"best hotels in {city} under ${price} per night site:booking.com OR site:hotels.com 2024 2025 prices ratings"
        return brightdata_search(query)

    elif tool_name == "search_attractions":
        query = f"top tourist attractions sightseeing {city} entry fee cost tickets 2024 2025"
        return brightdata_search(query)

    elif tool_name == "search_restaurants_and_food":
        query = f"average restaurant meal prices {city} budget food cost per day tourist 2024"
        return brightdata_search(query)

    elif tool_name == "search_transport":
        query = f"public transport cost {city} metro bus day pass taxi airport transfer price 2024"
        return brightdata_search(query)

    return "Unknown tool."


# --- Main travel planning agent ---

SYSTEM_PROMPT = """You are an expert travel planner. Your job is to create detailed, realistic,
day-by-day travel itineraries based on the traveler's destination, duration, and budget.

When given a travel request:
1. Use your tools to search for REAL current data on hotels, attractions, restaurants, and transport.
2. Calculate costs carefully to stay within the stated budget.
3. Create a complete, practical day-by-day itinerary.

Your final response must be in this exact HTML structure (no markdown, pure HTML):

<div class="plan">
  <div class="summary-box">
    <h2>Trip Summary</h2>
    <p><strong>Destination:</strong> [city]</p>
    <p><strong>Duration:</strong> [X days]</p>
    <p><strong>Total Budget:</strong> $[amount]</p>
    <p><strong>Estimated Cost:</strong> $[amount]</p>
  </div>

  <div class="hotel-section">
    <h2>🏨 Recommended Hotel</h2>
    <p><strong>Name:</strong> [hotel name]</p>
    <p><strong>Price:</strong> $[X] per night × [N] nights = $[total]</p>
    <p><strong>Rating:</strong> [rating]/10</p>
    <p><strong>Why chosen:</strong> [reason]</p>
  </div>

  <div class="itinerary">
    <h2>📅 Day-by-Day Itinerary</h2>
    [For each day:]
    <div class="day">
      <h3>Day [N] — [Theme/Title]</h3>
      <ul>
        <li>🌅 Morning: [activity] — $[cost]</li>
        <li>🌞 Afternoon: [activity] — $[cost]</li>
        <li>🌙 Evening: [activity + dinner] — $[cost]</li>
      </ul>
      <p class="day-cost">Day [N] total: ~$[amount]</p>
    </div>
  </div>

  <div class="budget-breakdown">
    <h2>💰 Budget Breakdown</h2>
    <table>
      <tr><td>Hotel ([N] nights)</td><td>$[amount]</td></tr>
      <tr><td>Attractions & Entry Fees</td><td>$[amount]</td></tr>
      <tr><td>Food & Drinks</td><td>$[amount]</td></tr>
      <tr><td>Local Transport</td><td>$[amount]</td></tr>
      <tr class="total-row"><td><strong>TOTAL</strong></td><td><strong>$[amount]</strong></td></tr>
    </table>
  </div>

  <div class="tips">
    <h2>💡 Money-Saving Tips</h2>
    <ul>
      <li>[tip 1]</li>
      <li>[tip 2]</li>
      <li>[tip 3]</li>
    </ul>
  </div>
</div>

Always be realistic with prices. If you don't have exact data, use reasonable estimates based on your knowledge."""


def create_travel_plan(user_prompt: str) -> str:
    """
    Run the travel planning agent with tool use.
    Returns HTML string of the complete travel plan.
    """
    messages = [{"role": "user", "content": user_prompt}]

    # Agentic loop: Claude calls tools until it has enough data
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # If Claude is done (no more tool calls), return final text
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "<p>Could not generate plan. Please try again.</p>"

        # Claude wants to use tools — execute them and feed results back
        if response.stop_reason == "tool_use":
            # Add Claude's response (with tool calls) to message history
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = handle_tool_call(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed tool results back to Claude
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason — return whatever we have
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "<p>Unexpected response. Please try again.</p>"
