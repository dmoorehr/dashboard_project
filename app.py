# Main Flask App: app.py
from flask import Flask, render_template, request, send_file
import os
from dashboard import generate_dashboard

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Generate dashboard
    dashboard_path = generate_dashboard(file_path)
    return send_file(dashboard_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
