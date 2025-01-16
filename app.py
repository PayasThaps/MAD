import os
import pandas as pd
from flask import Flask, render_template, request
import plotly.express as px

# Function to load data
def load_data():
    excel_file_path = "Insight_Trek_Dataset_Round3.xlsx"  # Path to your Excel file

    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")

    try:
        data = pd.read_excel(excel_file_path, sheet_name="Sales Data", engine="openpyxl")
        return data
    except Exception as e:
        raise ValueError(f"Failed to load Excel file: {e}")

# Load dataset
data = load_data()

# Initialize Flask app
app = Flask(__name__)

# Utility functions
def generate_revenue_graph(filtered_data):
    revenue_trend = filtered_data.groupby("Date")[["Revenue", "UnitsSold"]].sum().reset_index()
    fig_revenue = px.line(
        revenue_trend,
        x="Date",
        y="Revenue",
        title="Revenue Over Time",
        labels={"Date": "Date", "Revenue": "Revenue"},
    )
    return fig_revenue.to_html(full_html=False)

def generate_event_graph(filtered_data):
    event_impact = filtered_data.groupby("Event Type")["Revenue"].sum().reset_index()
    fig_event = px.bar(
        event_impact,
        x="Event Type",
        y="Revenue",
        title="Revenue by Event Type",
        text="Revenue",
        labels={"Event Type": "Event Type", "Revenue": "Revenue"},
    )
    return fig_event.to_html(full_html=False)

def generate_location_graph(filtered_data):
    location_performance = filtered_data.groupby("Location")["Revenue"].sum().reset_index()
    fig_location = px.bar(
        location_performance,
        x="Location",
        y="Revenue",
        title="Revenue by Location",
        text="Revenue",
        labels={"Location": "Location", "Revenue": "Revenue"},
    )
    return fig_location.to_html(full_html=False)

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    # Filters
    selected_location = request.form.getlist("location")
    selected_event = request.form.getlist("event")

    # Apply filters to the data
    filtered_data = data.copy()
    if selected_location:
        filtered_data = filtered_data[filtered_data["Location"].isin(selected_location)]
    if selected_event:
        filtered_data = filtered_data[filtered_data["Event Type"].isin(selected_event)]

    if filtered_data.empty:
        return render_template(
            "index.html",
            locations=data["Location"].unique(),
            events=data["Event Type"].dropna().unique(),
            selected_location=selected_location,
            selected_event=selected_event,
            message="No data available for the selected filters.",
            revenue_graph="",
            event_graph="",
            location_graph="",
        )

    # Generate graphs
    revenue_graph = generate_revenue_graph(filtered_data)
    event_graph = generate_event_graph(filtered_data)
    location_graph = generate_location_graph(filtered_data)

    return render_template(
        "index.html",
        locations=data["Location"].unique(),
        events=data["Event Type"].dropna().unique(),
        selected_location=selected_location,
        selected_event=selected_event,
        message="",
        revenue_graph=revenue_graph,
        event_graph=event_graph,
        location_graph=location_graph,
    )

# Run the app
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT"))  # Use PORT environment variable or default to 5000
        app.run(host="0.0.0.0", port=port)
    except OSError as e:
        print(f"Port {port} is already in use. Trying a different port...")
        app.run(host="0.0.0.0", port=port + 1)
