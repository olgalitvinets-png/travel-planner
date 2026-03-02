import asyncio
import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
BRIGHTDATA_TOKEN = os.getenv("BRIGHTDATA_API_TOKEN")


# --- System prompt: Claude returns JSON ---

SYSTEM_PROMPT = """You are an expert travel planner. Always respond with ONLY valid JSON — no markdown, no explanation, just the JSON object.

You have access to Brightdata tools: search_engine, scrape_as_markdown. Use them to find REAL current data:
1. Call search_engine to search "hotels in [city] booking.com prices 2025" — pick one hotel for Booking.com card.
2. Call search_engine to search "best hotels in [city] tripadvisor rating 2025" — pick one hotel for TripAdvisor card.
3. Call search_engine to search "airbnb apartment [city] per night 2025" — pick one for Airbnb card.
4. Call search_engine to search "top tourist attractions [city] entry fee 2025".
5. Call search_engine to search "average meal price [city] tourist restaurant 2025".
6. Return the complete JSON below with ALL fields filled from real search results.

CRITICAL: The "hotels" object MUST contain exactly 3 entries with DIFFERENT names and prices:
- "booking": a hotel from Booking.com
- "tripadvisor": a hotel from TripAdvisor
- "airbnb": an apartment from Airbnb

Return this exact JSON structure:

{
  "destination": "city name",
  "days": 4,
  "budget": 1000,
  "estimated_cost": 920,
  "hotels": {
    "booking": {
      "name": "actual hotel name",
      "price_per_night": 75,
      "total": 300,
      "rating": 8.4,
      "reviews": 1240,
      "features": ["Free cancellation", "Breakfast included", "City center"],
      "label": "Best Value"
    },
    "tripadvisor": {
      "name": "different hotel name",
      "price_per_night": 90,
      "total": 360,
      "rating": 9.1,
      "reviews": 876,
      "features": ["Travellers Choice Award", "Rooftop terrace", "Near main sights"],
      "label": "Top Rated"
    },
    "airbnb": {
      "name": "apartment or property name",
      "price_per_night": 65,
      "total": 260,
      "rating": 4.8,
      "reviews": 312,
      "features": ["Entire apartment", "Full kitchen", "Local neighborhood"],
      "label": "Local Experience"
    }
  },
  "itinerary": [
    {
      "day": 1,
      "title": "Arrival & First Exploration",
      "morning": "Arrive and check in — $0",
      "afternoon": "Visit main landmark — $20",
      "evening": "Dinner at local restaurant — $25",
      "day_total": 45
    }
  ],
  "budget_breakdown": {
    "hotel": 300,
    "attractions": 120,
    "food": 280,
    "transport": 60,
    "total": 760
  },
  "tips": [
    "Book tickets online in advance to avoid queues",
    "Use public transport instead of taxis",
    "Eat at local markets for cheaper meals"
  ]
}"""


# --- HTML renderer (converts JSON to HTML cards) ---

def render_html(data: dict) -> str:
    hotels = data.get("hotels", {})

    def hotel_card(platform: str, info: dict, highlight: bool) -> str:
        label_icon = "⭐" if highlight else ("🏅" if platform == "tripadvisor" else "🏠")
        platform_display = "TripAdvisor" if platform == "tripadvisor" else platform.capitalize()
        rating_scale = "5" if platform == "airbnb" else "10"
        highlight_class = " best-value" if highlight else ""
        features_html = "".join(f"<li>{f}</li>" for f in info.get("features", []))
        return f"""
        <div class="hotel-card{highlight_class}">
          <div class="platform-badge {platform}">{platform_display}</div>
          <div class="card-label">{label_icon} {info.get('label', '')}</div>
          <h3>{info.get('name', '')}</h3>
          <div class="hotel-price">${info.get('price_per_night', 0)} <span>/ night</span></div>
          <div class="hotel-rating">⭐ {info.get('rating', '')}/{rating_scale} · {info.get('reviews', '')} reviews</div>
          <ul class="hotel-features">{features_html}</ul>
          <div class="hotel-total">${info.get('total', 0)} total for {data.get('days', '')} nights</div>
        </div>"""

    hotel_html = (
        hotel_card("booking", hotels.get("booking", {}), highlight=True) +
        hotel_card("tripadvisor", hotels.get("tripadvisor", {}), highlight=False) +
        hotel_card("airbnb", hotels.get("airbnb", {}), highlight=False)
    )

    itinerary_html = ""
    for day in data.get("itinerary", []):
        itinerary_html += f"""
        <div class="day">
          <h3>Day {day.get('day')} — {day.get('title', '')}</h3>
          <ul>
            <li>🌅 Morning: {day.get('morning', '')}</li>
            <li>🌞 Afternoon: {day.get('afternoon', '')}</li>
            <li>🌙 Evening: {day.get('evening', '')}</li>
          </ul>
          <p class="day-cost">Day {day.get('day')} total: ~${day.get('day_total', '')}</p>
        </div>"""

    bd = data.get("budget_breakdown", {})
    tips_html = "".join(f"<li>{t}</li>" for t in data.get("tips", []))

    return f"""
    <div class="plan">
      <div class="summary-box">
        <h2>Trip Summary</h2>
        <p><strong>Destination:</strong> {data.get('destination', '')}</p>
        <p><strong>Duration:</strong> {data.get('days', '')} days</p>
        <p><strong>Total Budget:</strong> ${data.get('budget', '')}</p>
        <p><strong>Estimated Cost:</strong> ${data.get('estimated_cost', '')}</p>
      </div>

      <div class="hotel-comparison">
        <h2>🏨 Hotel Options — Price Comparison</h2>
        <div class="hotel-cards">{hotel_html}</div>
        <p class="hotel-note">💡 The itinerary uses the <strong>Best Value</strong> option. Swap to any option — just adjust the budget.</p>
      </div>

      <div class="itinerary">
        <h2>📅 Day-by-Day Itinerary</h2>
        {itinerary_html}
      </div>

      <div class="budget-breakdown">
        <h2>💰 Budget Breakdown</h2>
        <table>
          <tr><td>Hotel ({data.get('days', '')} nights)</td><td>${bd.get('hotel', '')}</td></tr>
          <tr><td>Attractions & Entry Fees</td><td>${bd.get('attractions', '')}</td></tr>
          <tr><td>Food & Drinks</td><td>${bd.get('food', '')}</td></tr>
          <tr><td>Local Transport</td><td>${bd.get('transport', '')}</td></tr>
          <tr class="total-row"><td><strong>TOTAL</strong></td><td><strong>${bd.get('total', '')}</strong></td></tr>
        </table>
      </div>

      <div class="tips">
        <h2>💡 Money-Saving Tips</h2>
        <ul>{tips_html}</ul>
      </div>
    </div>"""


# --- MCP + Claude agent ---

async def _run_agent_with_mcp(user_prompt: str) -> str:
    """Connect to Brightdata MCP server, give its tools to Claude, run the agent loop."""

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@brightdata/mcp"],
        env={**os.environ, "API_TOKEN": BRIGHTDATA_TOKEN},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get all tools Brightdata MCP exposes
            mcp_tools_response = await session.list_tools()
            print(f"[Brightdata MCP] Available tools: {[t.name for t in mcp_tools_response.tools]}")

            # Convert MCP tool format → Anthropic tool format
            anthropic_tools = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema,
                }
                for tool in mcp_tools_response.tools
            ]

            messages = [{"role": "user", "content": user_prompt}]

            # Agentic loop
            while True:
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=8096,
                    system=SYSTEM_PROMPT,
                    tools=anthropic_tools,
                    messages=messages,
                )

                if response.stop_reason == "end_turn":
                    for block in response.content:
                        if hasattr(block, "text"):
                            text = block.text.strip()
                            # Extract JSON from anywhere in the response
                            # Claude sometimes adds explanation text before/after the JSON block
                            json_text = None
                            if "```" in text:
                                # Find content between ``` fences
                                parts = text.split("```")
                                for part in parts:
                                    candidate = part.strip()
                                    if candidate.startswith("json"):
                                        candidate = candidate[4:].strip()
                                    if candidate.startswith("{"):
                                        json_text = candidate
                                        break
                            elif "{" in text:
                                # No fences — find the first { to last }
                                start = text.index("{")
                                end = text.rindex("}") + 1
                                json_text = text[start:end]

                            if json_text:
                                try:
                                    data = json.loads(json_text)
                                    return render_html(data)
                                except json.JSONDecodeError as e:
                                    print(f"[JSON error] {e}")
                                    print(f"[JSON raw] {json_text[:500]}")
                                    return f"<div class='error-box'>Could not parse plan. Please try again.</div>"
                            else:
                                print(f"[No JSON found] Raw text: {text[:400]}")
                                return "<div class='error-box'>No travel plan found in response. Please try again.</div>"
                    return "<p>No response received.</p>"

                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"[Brightdata MCP] Calling tool: {block.name} with {block.input}")
                            mcp_result = await session.call_tool(block.name, block.input)
                            # Extract text from MCP result
                            result_text = ""
                            for content_block in mcp_result.content:
                                if hasattr(content_block, "text"):
                                    result_text += content_block.text
                            print(f"[Brightdata MCP] Result preview: {result_text[:200]}")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_text or "No data returned.",
                            })

                    messages.append({"role": "user", "content": tool_results})
                else:
                    for block in response.content:
                        if hasattr(block, "text"):
                            return block.text
                    return "<p>Unexpected response.</p>"


def create_travel_plan(user_prompt: str) -> str:
    """Entry point called by Flask. Runs the async MCP agent."""
    return asyncio.run(_run_agent_with_mcp(user_prompt))


# --- Simple test function for /test-brightdata route ---

async def _test_brightdata_async() -> str:
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@brightdata/mcp"],
        env={**os.environ, "API_TOKEN": BRIGHTDATA_TOKEN},
    )
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = [t.name for t in tools.tools]
                return f"✅ Brightdata MCP connected! Tools available: {', '.join(names)}"
    except Exception as e:
        return f"❌ MCP connection failed: {e}"


def test_brightdata_mcp() -> str:
    return asyncio.run(_test_brightdata_async())
