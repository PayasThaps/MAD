import pandas as pd
import streamlit as st
import plotly.express as px

# Load data
def load_data():
    return pd.read_excel("Insight_Trek_Dataset_Round3.xlsx", sheet_name="Sales Data", engine="openpyxl")

data = load_data()

# App Title
st.title("Comprehensive Sales Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Options")
locations = st.sidebar.multiselect(
    "Select Locations:", options=data["Location"].unique(), default=data["Location"].unique()
)
events = st.sidebar.multiselect(
    "Select Event Types:", options=data["Event Type"].dropna().unique(), default=data["Event Type"].dropna().unique()
)

# Filter data
filtered_data = data.copy()
if locations:
    filtered_data = filtered_data[filtered_data["Location"].isin(locations)]
if events:
    filtered_data = filtered_data[filtered_data["Event Type"].isin(events)]

# Metrics Section
st.header("Key Metrics")
total_revenue = filtered_data["Revenue"].sum()
total_units_sold = filtered_data["UnitsSold"].sum()
num_transactions = len(filtered_data)

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Units Sold", f"{total_units_sold:,}")
col3.metric("Transactions", f"{num_transactions:,}")

# Revenue Trend Graph
st.subheader("Revenue Over Time")
revenue_trend = filtered_data.groupby("Date")["Revenue"].sum().reset_index()
fig_revenue = px.line(revenue_trend, x="Date", y="Revenue", title="Revenue Over Time", labels={"Date": "Date", "Revenue": "Revenue ($)"})
st.plotly_chart(fig_revenue, use_container_width=True)

# Event Impact Graph
st.subheader("Revenue by Event Type")
event_impact = filtered_data.groupby("Event Type")["Revenue"].sum().reset_index()
fig_event = px.bar(event_impact, x="Event Type", y="Revenue", title="Revenue by Event Type", text="Revenue", labels={"Event Type": "Event Type", "Revenue": "Revenue ($)"})
fig_event.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig_event, use_container_width=True)

# Location Performance Graph
st.subheader("Revenue by Location")
location_performance = filtered_data.groupby("Location")["Revenue"].sum().reset_index()
fig_location = px.bar(location_performance, x="Location", y="Revenue", title="Revenue by Location", text="Revenue", labels={"Location": "Location", "Revenue": "Revenue ($)"})
fig_location.update_traces(texttemplate='%{text:.2s}', textposition='outside')
st.plotly_chart(fig_location, use_container_width=True)

# Detailed Table View
st.subheader("Detailed Data View")
st.dataframe(filtered_data)

# Download Option
st.sidebar.header("Download Filtered Data")
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(filtered_data)
st.sidebar.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)

