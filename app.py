import os
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Function to load data
def load_data():
    excel_file_path = "Insight_Trek_Dataset_Round3.xlsx"  # Path to your .xlsx file

    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")

    try:
        data = pd.read_excel(excel_file_path, sheet_name="Sales Data", engine="openpyxl")
        print("Excel data loaded successfully.")
        return data
    except Exception as e:
        raise ValueError(f"Failed to load Excel file: {e}")

# Load dataset
try:
    data = load_data()
except Exception as e:
    print(f"Error loading data: {e}")
    data = pd.DataFrame()  # Fallback to an empty DataFrame if data loading fails

# Initialize Dash app
app = Dash(__name__)
app.title = "Comprehensive Dash App for Render"

# Layout of the app
app.layout = html.Div([
    html.H1("Comprehensive Dash App", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Location:"),
        dcc.Dropdown(
            id="location-filter",
            options=[{"label": loc, "value": loc} for loc in data["Location"].unique()] if not data.empty else [],
            value=data["Location"].unique() if not data.empty else [],
            multi=True
        ),
    ], style={"marginBottom": "20px"}),

    html.Div([
        html.Label("Select Event Type:"),
        dcc.Dropdown(
            id="event-filter",
            options=[{"label": event, "value": event} for event in data["Event Type"].unique()] if not data.empty else [],
            value=data["Event Type"].unique() if not data.empty else [],
            multi=True
        ),
    ], style={"marginBottom": "20px"}),

    # Graphs Section
    html.Div([
        dcc.Graph(id="revenue-trend"),
        dcc.Graph(id="event-impact"),
    ])
])

# Callbacks
@app.callback(
    [
        Output("revenue-trend", "figure"),
        Output("event-impact", "figure"),
    ],
    [
        Input("location-filter", "value"),
        Input("event-filter", "value"),
    ]
)
def update_dashboard(selected_location, selected_event):
    if data.empty:
        return go.Figure(), go.Figure()

    # Filter data based on selections
    filtered_data = data[
        (data["Location"].isin(selected_location)) &
        (data["Event Type"].isin(selected_event))
    ]

    # Revenue Trend
    revenue_trend = filtered_data.groupby("Date")[["Revenue", "UnitsSold"]].sum().reset_index()
    revenue_trend_fig = px.line(
        revenue_trend,
        x="Date",
        y=["Revenue", "UnitsSold"],
        title="Revenue and Units Sold Over Time"
    )

    # Event Impact
    event_impact = filtered_data.groupby("Event Type")["Revenue"].sum().reset_index()
    event_impact_fig = px.bar(
        event_impact,
        x="Event Type",
        y="Revenue",
        title="Revenue by Event Type",
        text="Revenue"
    )

    return revenue_trend_fig, event_impact_fig

# Main entry point
if __name__ == "__main__":
    # Bind the app to the PORT environment variable, or use a default port (e.g., 4000)
    port = int(os.environ.get("PORT", 4000))
    app.run_server(host="0.0.0.0", port=port)
