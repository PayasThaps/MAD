import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import zipfile
import os

# Function to load data from a compressed .zip file
def load_data():
    # Path to the zip file
    zip_file_path = "Insight_Trek_Dataset_Round3_compressed.zip"
    extracted_file_path = "Insight_Trek_Dataset_Round3.xlsx"

    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall()  # Extracts the contents of the zip file

    # Check if the extracted file exists
    if not os.path.exists(extracted_file_path):
        raise FileNotFoundError(f"Expected file {extracted_file_path} not found after extraction.")

    # Load the Excel file
    try:
        data = pd.read_excel(extracted_file_path, sheet_name="Sales Data", engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Failed to load Excel file: {e}")

    return data

# Load the dataset
data = load_data()

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Mood Analytics Dashboard (MAD)"

# App layout
app.layout = html.Div([
    html.H1("Mood Analytics Dashboard (MAD)", style={"textAlign": "center"}),

    # Filters
    html.Div([
        html.Label("Select Location:"),
        dcc.Dropdown(
            id="location-filter",
            options=[{"label": loc, "value": loc} for loc in data["Location"].unique()],
            value=data["Location"].unique(),
            multi=True
        ),
        html.Label("Select Event Type:"),
        dcc.Dropdown(
            id="event-filter",
            options=[{"label": event, "value": event} for event in data["Event Type"].dropna().unique()],
            value=data["Event Type"].dropna().unique(),
            multi=True
        ),
        html.Label("Select Economic Sentiment:"),
        dcc.Dropdown(
            id="sentiment-filter",
            options=[{"label": sentiment, "value": sentiment} for sentiment in data["Economic Sentiment"].unique()],
            value=data["Economic Sentiment"].unique(),
            multi=True
        )
    ], style={"marginBottom": "20px"}),

    # Graphs
    dcc.Graph(id="revenue-units-trend"),
    dcc.Graph(id="event-type-impact"),
    dcc.Graph(id="competitor-discounts"),
    dcc.Graph(id="sentiment-analysis"),
    dcc.Graph(id="category-performance"),
])

# Callbacks
@app.callback(
    Output("revenue-units-trend", "figure"),
    Output("event-type-impact", "figure"),
    Output("competitor-discounts", "figure"),
    Output("sentiment-analysis", "figure"),
    Output("category-performance", "figure"),
    Input("location-filter", "value"),
    Input("event-filter", "value"),
    Input("sentiment-filter", "value"),
)
def update_dashboard(selected_location, selected_event, selected_sentiment):
    # Filter data based on selections
    filtered_data = data[
        (data["Location"].isin(selected_location)) &
        (data["Event Type"].isin(selected_event)) &
        (data["Economic Sentiment"].isin(selected_sentiment))
    ]

    # Revenue and Units Sold Trends
    revenue_trend = filtered_data.groupby("Date")["Revenue"].sum().reset_index()
    units_trend = filtered_data.groupby("Date")["UnitsSold"].sum().reset_index()

    combined_fig = px.line()
    combined_fig.add_scatter(x=revenue_trend["Date"], y=revenue_trend["Revenue"], mode="lines+markers", name="Revenue")
    combined_fig.add_scatter(x=units_trend["Date"], y=units_trend["UnitsSold"], mode="lines+markers", name="Units Sold")
    combined_fig.update_layout(title="Revenue and Units Sold Trends")

    # Event Type Impact
    event_impact = filtered_data.groupby("Event Type")["Revenue"].sum().reset_index()
    event_fig = px.bar(event_impact, x="Event Type", y="Revenue", title="Event Type Impact on Revenue", text="Revenue")

    # Competitor Discounts
    discount_impact = filtered_data.groupby("Competitor Discount")["Revenue"].sum().reset_index()
    discount_fig = px.pie(discount_impact, names="Competitor Discount", values="Revenue", title="Revenue by Competitor Discount")

    # Sentiment Analysis
    sentiment_impact = filtered_data.groupby("Economic Sentiment")["Revenue"].sum().reset_index()
    sentiment_fig = px.bar(sentiment_impact, x="Economic Sentiment", y="Revenue", title="Revenue by Economic Sentiment", text="Revenue")

    # Category Performance
    category_performance = filtered_data.groupby("CategoryID")["Revenue"].sum().reset_index()
    category_fig = px.bar(category_performance, x="CategoryID", y="Revenue", title="Revenue by Category", text="Revenue")

    return combined_fig, event_fig, discount_fig, sentiment_fig, category_fig

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
