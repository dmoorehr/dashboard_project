from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.layouts import column as bokeh_column
import pandas as pd
from math import pi

def generate_dashboard(file_path):
    # Load the uploaded file
    if file_path.endswith(".xlsx"):
        uploaded_data = pd.read_excel(file_path)
    elif file_path.endswith(".csv"):
        uploaded_data = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file type. Please upload an Excel (.xlsx) or CSV file.")

    # Example Pie Chart Data Preparation
    data = uploaded_data.groupby("Category").size().reset_index(name="Count")
    data["angle"] = data["Count"] / data["Count"].sum() * 2 * pi
    source = ColumnDataSource(data)

    # Example Pie Chart
    chart = figure(height=350, title="Example Pie Chart", toolbar_location=None)
    chart.wedge(
        x=0, y=0, radius=0.4, 
        start_angle="angle", end_angle="angle", 
        line_color="white", source=source
    )

    layout = bokeh_column(chart)
    script, div = components(layout)
    return script, div
