# ✈️ AI Travel Planner

An AI-powered travel planner that creates detailed day-by-day trip itineraries with real hotel prices, attractions, and budget breakdowns.

Built with **Claude AI** + **Brightdata** web scraping.

![Travel Planner Demo](https://placehold.co/800x400?text=AI+Travel+Planner)

## What it does

Type a prompt like:
> "Plan a 4-day trip to Rome for $1000"

And get back a complete travel plan including:
- 🏨 Hotel recommendations with real prices
- 📅 Day-by-day itinerary
- 🗺️ Top sightseeing spots with entry fees
- 💰 Full budget breakdown
- 💡 Money-saving tips

## Tech Stack

- **Backend**: Python + Flask
- **AI Brain**: Anthropic Claude API (claude-sonnet-4-6)
- **Web Scraping**: Brightdata SERP API
- **Frontend**: HTML + CSS + JavaScript

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/travel-planner.git
cd travel-planner
```

### 2. Install dependencies
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

## Example Output

**Prompt:** "Plan a 4-day trip to Rome for $1000"

The app returns:
- Hotel: Hotel Navona (€65/night, 8.2/10 rating)
- Day 1: Colosseum, Roman Forum, Trastevere dinner
- Day 2: Vatican Museums, St. Peter's Basilica
- Day 3: Borghese Gallery, Spanish Steps, Trevi Fountain
- Day 4: Pantheon, Campo de' Fiori market
- Total estimated cost: $920

## License

MIT License — free to use and modify.
