import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import os

def load_data():
    """
    Load data from the Excel file.
    Returns:
        pd.DataFrame: DataFrame containing the data from the Excel file.
    """
    excel_file_path = "Insight_Trek_Dataset_Round3.xlsx"  # Path to your .xlsx file

    # Check if the file exists
    if not os.path.exists(excel_file_path):
        raise FileNotFoundError(f"Excel file not found: {excel_file_path}")

    # Attempt to load the Excel file
    try:
        data = pd.read_excel(excel_file_path, sheet_name="Sales Data", engine="openpyxl")
    except Exception as e:
        raise ValueError(f"Failed to load Excel file: {e}")

    print("Excel data loaded successfully.")
    return data

# Load the dataset
data = load_data()

# Initialize Dash app
app = Dash(__name__)
app.title = "Advanced Data Analysis Dashboard"

# App layout
app.layout = html.Div([
    html.H1("Advanced Data Analysis Dashboard", style={"textAlign": "center"}),

    # Filters Section
    html.Div([
        html.Div([
            html.Label("Select Location:"),
            dcc.Dropdown(
                id="location-filter",
                options=[{"label": loc, "value": loc} for loc in data["Location"].unique()],
                value=data["Location"].unique(),
                multi=True
            ),
        ], style={"width": "30%", "display": "inline-block", "marginRight": "5%"}),

        html.Div([
            html.Label("Select Event Type:"),
            dcc.Dropdown(
                id="event-filter",
                options=[{"label": event, "value": event} for event in data["Event Type"].dropna().unique()],
                value=data["Event Type"].dropna().unique(),
                multi=True
            ),
        ], style={"width": "30%", "display": "inline-block"}),

        html.Div([
            html.Label("Select Economic Sentiment:"),
            dcc.Dropdown(
                id="sentiment-filter",
                options=[{"label": sentiment, "value": sentiment} for sentiment in data["Economic Sentiment"].unique()],
                value=data["Economic Sentiment"].unique(),
                multi=True
            ),
        ], style={"width": "30%", "display": "inline-block", "marginLeft": "5%"}),
    ], style={"marginBottom": "20px"}),

    # Summary Table
    html.Div([
        html.H4("Summary Table"),
        dcc.Graph(id="summary-table")
    ], style={"marginBottom": "30px"}),

    # Graphs Section
    html.Div([
        dcc.Graph(id="revenue-trend"),
        dcc.Graph(id="event-impact"),
        dcc.Graph(id="sentiment-impact"),
        dcc.Graph(id="category-performance"),
    ])
])

# Callbacks
@app.callback(
    [
        Output("summary-table", "figure"),
        Output("revenue-trend", "figure"),
        Output("event-impact", "figure"),
        Output("sentiment-impact", "figure"),
        Output("category-performance", "figure"),
    ],
    [
        Input("location-filter", "value"),
        Input("event-filter", "value"),
        Input("sentiment-filter", "value"),
    ]
)
def update_dashboard(selected_location, selected_event, selected_sentiment):
    # Filter data based on selections
    filtered_data = data[
        (data["Location"].isin(selected_location)) &
        (data["Event Type"].isin(selected_event)) &
        (data["Economic Sentiment"].isin(selected_sentiment))
    ]

    # Summary Table
    summary = filtered_data.groupby("Event Type").agg(
        Total_Revenue=("Revenue", "sum"),
        Avg_Units_Sold=("UnitsSold", "mean"),
        Event_Count=("Event Type", "count")
    ).reset_index()

    summary_table_fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(summary.columns), align="center"),
            cells=dict(values=[summary[col] for col in summary.columns], align="center")
        )]
    )

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

    # Sentiment Impact
    sentiment_impact = filtered_data.groupby("Economic Sentiment")["Revenue"].sum().reset_index()
    sentiment_impact_fig = px.bar(
        sentiment_impact,
        x="Economic Sentiment",
        y="Revenue",
        title="Revenue by Economic Sentiment",
        text="Revenue"
    )

    # Category Performance
    category_performance = filtered_data.groupby("CategoryID")["Revenue"].sum().reset_index()
    category_performance_fig = px.bar(
        category_performance,
        x="CategoryID",
        y="Revenue",
        title="Revenue by Category",
        text="Revenue"
    )

    return summary_table_fig, revenue_trend_fig, event_impact_fig, sentiment_impact_fig, category_performance_fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
