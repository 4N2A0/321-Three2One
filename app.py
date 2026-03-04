import json
import os
import random
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, abort, session


def load_puzzles(puzzles_path: str) -> list[dict]:
    with open(puzzles_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_app(puzzles: list[dict]) -> Flask:
    app = Flask(__name__)

    # Required for Flask sessions (used for non-repeating Random order)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    categories = sorted(set(p["category"] for p in puzzles))

    @app.route("/", methods=["GET", "POST"])
    def index():
        # POST from category switcher -> start chosen category
        if request.method == "POST":
            category = request.form.get("category", "Random")
            return redirect(url_for("game", category=category, idx=0, reveal=0))

        # Optional category-selection page
        if request.args.get("choose") == "1":
            return render_template("index.html", categories=categories)

        # Default behaviour: start game immediately in Random mode
        return redirect(url_for("game", category="Random", idx=0, reveal=0))

    @app.route("/game/<category>/<int:idx>/<int:reveal>")
    def game(category: str, idx: int, reveal: int):
        puzzles_in_category = puzzles if category == "Random" else [p for p in puzzles if p["category"] == category]
        if not puzzles_in_category:
            abort(404, description=f"No puzzles found in category: {category}")

        reset = request.args.get("reset") == "1"

        # Random: shuffle once, cycle through all before repeating
        if category == "Random":
            key = "order_random"
            if reset or key not in session or len(session[key]) != len(puzzles_in_category):
                order = list(range(len(puzzles_in_category)))
                random.shuffle(order)
                session[key] = order

            order = session[key]
            current_pos = idx % len(order)
            puzzle = puzzles_in_category[order[current_pos]]

            is_last = (current_pos == len(order) - 1)
            next_idx = 0 if is_last else (current_pos + 1)
        else:
            current_pos = idx % len(puzzles_in_category)
            puzzle = puzzles_in_category[current_pos]

            is_last = (current_pos == len(puzzles_in_category) - 1)
            next_idx = 0 if is_last else (current_pos + 1)

        return render_template(
            "game.html",
            puzzle=puzzle,
            category=category,
            categories=categories,
            current_idx=current_pos,
            next_idx=next_idx,
            is_last=is_last,
            reveal=bool(reveal),
        )

    return app


def create_app() -> Flask:
    puzzles_path = Path(__file__).with_name("puzzles.json")
    puzzles = load_puzzles(puzzles_path)
    return build_app(puzzles)


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
