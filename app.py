from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# In-memory session storage
user_sessions = {}

# Define follow-up questions
FOLLOWUP_QUESTIONS = [
    "Which country or region are you referring to?",
    "Do you want results from a specific time period (e.g. last year, last 6 months)?",
    "Are you looking for a specific company or general category?",
    "Should pricing or availability be considered in your results?"
]

@app.route('/ask', methods=['POST'])
def ask():
    user_id = request.json.get('sessionId', 'default')
    user_input = request.json.get('message', '')
    search_type = request.json.get('searchType', 'normal')

    user_sessions[user_id] = {
        'searchType': search_type,
        'initialQuery': user_input,
        'followupIndex': 0,
        'followupAnswers': [],
        'applyFilters': False  # For Boolean option
    }

    if search_type == 'boolean':
        # Ask if they want to apply filters
        return jsonify({
            "followups": ["Would you like to apply filters for Boolean Search? (yes/no)"],
            "skip": False
        })

    # Normal search: start standard follow-up questions
    return jsonify({"followups": [FOLLOWUP_QUESTIONS[0]], "skip": False})

@app.route('/followup', methods=['POST'])
def followup():
    data = request.json
    user_id = data.get('sessionId', 'default')
    answer = data.get('answer', '').strip().lower()

    session = user_sessions.get(user_id)
    if not session:
        return jsonify({"error": "Invalid session."}), 400

    # Boolean path decision
    if session['searchType'] == 'boolean' and session['followupIndex'] == 0:
        if answer in ['yes', 'y']:
            session['applyFilters'] = True
            session['followupAnswers'] = []
            session['followupIndex'] = 0
            return jsonify({"next": FOLLOWUP_QUESTIONS[0]})
        else:
            return jsonify({"done": True})

    # Store answer and move to next
    session['followupAnswers'].append(answer)
    session['followupIndex'] += 1

    if session['followupIndex'] < len(FOLLOWUP_QUESTIONS):
        return jsonify({"next": FOLLOWUP_QUESTIONS[session['followupIndex']]})
    else:
        return jsonify({"done": True})

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    user_id = data.get('sessionId', 'default')
    session = user_sessions.get(user_id)
    time.sleep(2)

    if not session:
        return jsonify({"summary": "Session expired or invalid.", "link": "#"})

    summary_lines = [f"Search query: {session['initialQuery']}"]

    if session['followupAnswers']:
        for idx, ans in enumerate(session['followupAnswers']):
            summary_lines.append(f"→ {FOLLOWUP_QUESTIONS[idx]}: {ans}")

    result_summary = "\n".join(summary_lines)

    result_link = (
        "https://example.com/boolean-results" if session['searchType'] == 'boolean'
        else "https://example.com/normal-results"
    )

    return jsonify({
        "summary": result_summary,
        "link": result_link
    })

@app.route('/')
def home():
    return "Proxy AI Assistant v3 with dual-mode follow-up is running."

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
