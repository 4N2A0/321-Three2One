from flask import Flask, render_template, request, redirect, url_for
import json, random

app = Flask(__name__)

# Load puzzles from JSON file
with open('puzzles.json', 'r', encoding='utf-8') as f:
    PUZZLES = json.load(f)

CATEGORIES = sorted(set(p['category'] for p in PUZZLES))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        category = request.form.get('category')
        return redirect(url_for('game', category=category, idx=0, reveal=0))
    return render_template('index.html', categories=CATEGORIES)

@app.route('/game/<category>/<int:idx>/<int:reveal>')
def game(category, idx, reveal):
    # Filter puzzles by category (or random if 'Random')
    puzzles = PUZZLES if category == 'Random' else [p for p in PUZZLES if p['category'] == category]
    if not puzzles:
        return "No puzzles in this category.", 404

    puzzle = puzzles[idx % len(puzzles)]
    next_idx = (idx + 1) % len(puzzles)
    return render_template(
        'game.html',
        puzzle=puzzle,
        category=category,
        idx=next_idx,
        reveal=bool(reveal)
    )

if __name__ == '__main__':
    app.run(debug=True)