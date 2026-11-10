from flask import Flask, request, jsonify, render_template
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))

print("Static folder:", app.static_folder)
print("Exists:", Path(app.static_folder).exists())
print("Files:", list(Path(app.static_folder).glob("*")))

@app.route("/test")
def test():
    return jsonify({"message": "Working!"})

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        return jsonify({"success": True, "data": data})
    return jsonify({"message": "API running"})

@app.route("/")
def index():
    return render_template("data-collection.html")

@app.route("/data-collection")
def data_collection():
    return render_template("data-collection.html")


@app.route("/data-review")
def data_review():
    return render_template("data-review.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)