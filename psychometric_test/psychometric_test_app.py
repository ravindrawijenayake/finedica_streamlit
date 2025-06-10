from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# === CONFIG DATABASE ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///responses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === DEFINE MODEL ===
class PsychometricResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    scores = db.Column(db.JSON)
    dominant_belief = db.Column(db.String(100))

# === QUESTIONS & DESCRIPTIONS ===
questions = {
    "Money Resentment": [...],  # shortened for brevity
    "Financial Fantasists": [...],
    "Money Prestige": [...],
    "Money Anxiety": [...]
}

descriptions = {
    "Money Resentment": "Money Resenters may also believe...",
    "Financial Fantasists": "Financial Fantasists believe...",
    "Money Prestige": "Money Prestige seekers...",
    "Money Anxiety": "Money Anxious are alert..."
}

# === ROUTES ===
@app.route('/psychometric-test')
def show_form():
    return render_template('psychometric_test.html', questions=questions)

@app.route('/submit-psychometric', methods=['POST'])
def submit_form():
    scores = {cat: 0 for cat in questions}
    for category, qs in questions.items():
        for idx, _ in enumerate(qs):
            key = f"{category}_{idx}"
            value = int(request.form.get(key, 0))
            scores[category] += value

    top_category = max(scores, key=scores.get)

    # Save to DB
    response = PsychometricResponse(
        scores=scores,
        dominant_belief=top_category
    )
    db.session.add(response)
    db.session.commit()

    return render_template(
        "result.html",
        top_category=top_category,
        scores=scores,
        description=descriptions[top_category]
    )

if __name__ == '__main__':
    app.run(debug=True)

