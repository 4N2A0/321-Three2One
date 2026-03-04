import json
import os
import random
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, abort


def load_puzzles(puzzles_path: str) -> list[dict]:
    with open(puzzles_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_app(puzzles: list[dict]) -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    categories = sorted(set(p["category"] for p in puzzles))

    @app.route("/", methods=["GET", "POST"])
    def index():
        """
        Default behavior:
        - Start immediately in Random mode (no category page).
        - If user submits the category form (POST), go to that category.
        - If user explicitly wants the category chooser page: /?choose=1
        """
        if request.method == "POST":
            category = request.form.get("category", "Random")
            return redirect(url_for("play", category=category))

        if request.args.get("choose") == "1":
            return render_template("index.html", categories=categories)

        return redirect(url_for("play", category="Random"))

    @app.route("/play/<category>")
    def play(category: str):
        """
        Single-page game:
        - Render one HTML page
        - Embed puzzles (filtered by category) as JSON
        - JS handles reveal/next/restart instantly without navigation
        """
        if category == "Random":
            puzzles_in_category = puzzles[:]  # all puzzles
        else:
            puzzles_in_category = [p for p in puzzles if p["category"] == category]

        if not puzzles_in_category:
            abort(404, description=f"No puzzles found in category: {category}")

        return render_template(
            "play.html",
            categories=categories,
            category=category,
            puzzles=puzzles_in_category,
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
