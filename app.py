# Directory Structure
# dashboard_project/
# ├── app.py                 # Main Flask app file
# ├── dashboard.py           # Dashboard generation logic
# ├── requirements.txt       # List of Python dependencies
# ├── uploads/              # Directory for uploaded files
# └── templates/            # HTML templates
#     └── index.html          # Upload page

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

# Dashboard Logic: dashboard.py
import pandas as pd
from bokeh.models import ColumnDataSource, CustomJS, Select, DataTable, TableColumn
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column as bokeh_column, row as bokeh_row
from bokeh.transform import cumsum
from math import pi
from datetime import datetime
import os

def generate_dashboard(file_path):
    # Load the uploaded file
    if file_path.endswith(".xlsx"):
        uploaded_data = pd.read_excel(file_path)
    elif file_path.endswith(".csv"):
        uploaded_data = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file type. Please upload an Excel (.xlsx) or CSV file.")

    # Filter out terminated employees
    uploaded_data = uploaded_data[uploaded_data['Termination Date'].isna()]

    # Custom color palette
    custom_palette = ["#332288", "#117733", "#44AA99", "#88CCEE", "#DDCC77", "#CC6677", "#AA4499", "#882255"]

    # Prepare pie chart data
    def prepare_pie_data(data, group_column, palette):
        counts = data.groupby(group_column).size().reset_index(name="Count")
        counts["angle"] = counts["Count"] / counts["Count"].sum() * 2 * pi
        counts["percentage"] = counts["Count"] / counts["Count"].sum() * 100
        counts["color"] = palette[: len(counts)]
        return counts

    gender_data = prepare_pie_data(uploaded_data, "Gender Code", custom_palette)
    gender_source = ColumnDataSource(gender_data)

    # Create pie chart
    def create_pie_chart(source, title, group_column):
        chart = figure(
            title=title,
            height=250,
            sizing_mode="stretch_width",
            tools="tap,pan,wheel_zoom,reset,save",
            tooltips=f"@{{{group_column}}}: @Count (@percentage{{0.2f}}%)",
            x_range=(-0.5, 1.0),
        )
        chart.wedge(
            x=0,
            y=1,
            radius=0.4,
            start_angle=cumsum("angle", include_zero=True),
            end_angle=cumsum("angle"),
            line_color="white",
            fill_color="color",
            legend_field=group_column,
            source=source,
        )
        return chart

    pie_chart_gender = create_pie_chart(gender_source, "Gender Distribution", "Gender Code")

    # Layout
    layout = bokeh_column(
        pie_chart_gender,
        sizing_mode="stretch_width",
    )

    # Save the dashboard
    base_filename = "People_Analytics_Dashboard"
    current_date = datetime.now().strftime("%m_%d_%Y")
    output_filename = os.path.join("uploads", f"{base_filename}_{current_date}.html")
    output_file(output_filename)
    save(layout)

    return output_filename

# HTML Template: templates/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard File Upload</title>
</head>
<body>
    <h1>Upload Your File</h1>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <button type="submit">Generate Dashboard</button>
    </form>
</body>
</html>

# Python Dependencies: requirements.txt
bokeh
flask
pandas
