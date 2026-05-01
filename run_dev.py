"""
Local development server – serves both Flask API and static frontend.
Run: python run_dev.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
from flask_cors import CORS
from api.index import app as api_app

# Mount static files
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")

@api_app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")

@api_app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(PUBLIC_DIR, path)

if __name__ == "__main__":
    print("\n  Wumpus World Logic Agent")
    print("  --------------------------")
    print("  Local: http://127.0.0.1:5000\n")
    api_app.run(debug=True, port=5000)
