from pathlib import Path
from flask import Flask, render_template, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)

@app.get("/")
def dashboard():
    return render_template("dashboard.html")

@app.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(BASE_DIR / "assets", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
