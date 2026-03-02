from flask import Flask, render_template, request, jsonify
from travel_agent import create_travel_plan, test_brightdata_mcp

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json()
    user_prompt = data.get("prompt", "").strip()

    if not user_prompt:
        return jsonify({"error": "Please enter a travel request."}), 400

    try:
        plan_html = create_travel_plan(user_prompt)
        return jsonify({"plan": plan_html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test-brightdata")
def test_brightdata():
    result = test_brightdata_mcp()
    color = "green" if result.startswith("✅") else "red"
    return f"<h2 style='color:{color}'>{result}</h2>"


if __name__ == "__main__":
    print("=" * 50)
    print("  AI Travel Planner is running!")
    print("  Open your browser and go to:")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, host="0.0.0.0", port=5000)
