"""
Flask application for the picture‑link guessing game.

This app serves a simple game where users choose a category and are
presented with a set of image clues. Players reveal the answer and
explanations for each clue. The game does not require any user
accounts or typing input, keeping gameplay frictionless.

The puzzles are defined in a separate JSON file (puzzles.json).
Images referenced in the puzzles should reside in the static/images
directory. See puzzles.json for the data format.

To run locally:
    pip install -r requirements.txt
    python app.py

The app is intended for deployment on platforms like Render or
Fly.io. See README.md for deployment instructions.
"""

import json
import os
import random
from pathlib import Path

from flask import Flask, render_template, redirect, url_for, request, abort


def load_puzzles(puzzles_path: str) -> list[dict]:
    """Load puzzles from a JSON file.

    Args:
        puzzles_path: Path to the JSON file containing puzzle definitions.

    Returns:
        A list of puzzle dictionaries.

    Raises:
        FileNotFoundError: if the file does not exist.
        json.JSONDecodeError: if the file contents are invalid JSON.
    """
    with open(puzzles_path, "r", encoding="utf-8") as f:
        puzzles = json.load(f)
    return puzzles


def build_app(puzzles: list[dict]) -> Flask:
    """Create the Flask application and register routes.

    Args:
        puzzles: List of puzzle dictionaries loaded from puzzles.json.

    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__)

    # Derive category list from puzzles
    categories = sorted(set(p["category"] for p in puzzles))

    @app.route("/", methods=["GET", "POST"])
    def index():
        """Landing page with category selection.

        Handles GET to display the form and POST to redirect to the game.
        """
        if request.method == "POST":
            category = request.form.get("category", "Random")
            # Start with index 0; reveal flag false
            return redirect(url_for("game", category=category, idx=0, reveal=0))
        return render_template("index.html", categories=categories)

    @app.route("/game/<category>/<int:idx>/<int:reveal>")
    def game(category: str, idx: int, reveal: int):
        """Serve a puzzle page.

        Args:
            category: Name of the category or 'Random' for any.
            idx: Index of the puzzle within the category list.
            reveal: 0 (do not show answer) or 1 (show answer).

        Returns:
            Rendered HTML page.
        """
        # Filter puzzles by selected category or use all if 'Random'
        if category == "Random":
            puzzles_in_category = puzzles
        else:
            puzzles_in_category = [p for p in puzzles if p["category"] == category]
        if not puzzles_in_category:
            abort(404, description=f"No puzzles found in category: {category}")

        # Normalize index within available puzzles
        puzzle = puzzles_in_category[idx % len(puzzles_in_category)]
        next_idx = (idx + 1) % len(puzzles_in_category)

        return render_template(
            "game.html",
            puzzle=puzzle,
            category=category,
            idx=next_idx,
            reveal=bool(reveal),
        )

    return app


def create_app() -> Flask:
    """Factory for the Flask app used by deployment servers.

    Reads puzzles.json from the application directory and constructs
    the Flask app.
    """
    puzzles_path = Path(__file__).with_name("puzzles.json")
    puzzles = load_puzzles(puzzles_path)
    return build_app(puzzles)


# Instantiate the app at the module level so that Gunicorn can discover it.
# When running with a production server like `gunicorn app:app`, this variable
# will be used. The `create_app` factory can still be used for testing or
# other frameworks.
app = create_app()


if __name__ == "__main__":
    # For local development only. Use a production server like gunicorn in deployment.
    # Determine port from environment (e.g., when running on Render)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)