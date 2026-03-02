# ✈️ AI Travel Planner

An AI-powered travel planner that creates detailed day-by-day trip itineraries with **real-time hotel price comparison** across Booking.com, TripAdvisor, and Airbnb — powered by Brightdata MCP web scraping and Claude AI.

## What it does

Type a prompt like:
> "Plan a 4-day trip to Rome for $1000"

And get back a complete travel plan including:

- 🏨 **3 hotel options side-by-side** — real prices compared from Booking.com, TripAdvisor, and Airbnb
- 📅 **Day-by-day itinerary** — morning, afternoon, and evening activities
- 🗺️ **Top sightseeing spots** with entry fees and tips
- 💰 **Full budget breakdown** — hotel, food, transport, attractions
- 💡 **Money-saving tips** specific to your destination

## Hotel Comparison Feature

The app searches 3 platforms in real time and shows them side by side:

| Platform | Badge | Label |
|----------|-------|-------|
| Booking.com | 🔵 Blue | ⭐ Best Value |
| TripAdvisor | 🟢 Green | 🏅 Top Rated |
| Airbnb | 🔴 Red | 🏠 Local Experience |

Each card shows: hotel name, price per night, rating, number of reviews, key features, and total cost for the trip.

## Tech Stack

- **Backend**: Python + Flask
- **AI Brain**: Anthropic Claude API (`claude-sonnet-4-6`)
- **Web Scraping**: Brightdata MCP (`search_engine`, `scrape_as_markdown`)
- **Frontend**: HTML + CSS + JavaScript (no frameworks)

## Requirements

- Python 3.10+
- Node.js 18+ (required for Brightdata MCP server)
- Anthropic API key
- Brightdata API token

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/olgalitvinets-png/travel-planner.git
cd travel-planner
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Create a `.env` file (copy from `.env.example`):
```
ANTHROPIC_API_KEY=your_anthropic_api_key
BRIGHTDATA_API_TOKEN=your_brightdata_api_token
```

### 4. Run the app
```bash
python app.py
```

Open your browser at **http://localhost:5000**

### 5. Test Brightdata connection
Visit **http://localhost:5000/test-brightdata** to verify Brightdata MCP is connected.

## Example

**Prompt:** `Plan a 4-day trip to Rome for $1000`

**Output:**
- 3 hotel options: Hotel Navona ($75/night on Booking.com) vs Hotel Campo de' Fiori ($90/night on TripAdvisor) vs Trastevere apartment ($65/night on Airbnb)
- 4-day itinerary: Colosseum, Vatican, Borghese Gallery, Pantheon
- Budget breakdown: Hotel $300 · Attractions $120 · Food $280 · Transport $60 · **Total $760**

## License

MIT License — free to use and modify.
