import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1oKRoX6fYVy9xJ1l0irr37s6O6YTMbUWIqXcvbyGjUNE/export?format=csv"
    df = pd.read_csv(url)
    df['Received Date'] = pd.to_datetime(df['Received Date'])  # Ensure date format
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range", [df['Received Date'].min(), df['Received Date'].max()])
selected_category = st.sidebar.multiselect("Select Categories", df['Category'].unique())
selected_partner = st.sidebar.multiselect("Select Partner", df['Received From'].unique())

# Filter data
filtered_df = df[
    (df['Received Date'] >= pd.to_datetime(date_range[0])) &
    (df['Received Date'] <= pd.to_datetime(date_range[1]))
]

if selected_category:
    filtered_df = filtered_df[filtered_df['Category'].isin(selected_category)]
if selected_partner:
    filtered_df = filtered_df[filtered_df['Received From'].isin(selected_partner)]

# Summary Statistics
current_year = pd.to_datetime("today").year
current_month = pd.to_datetime("today").month
cases_this_year = df[df['Received Date'].dt.year == current_year]
cases_this_month = cases_this_year[cases_this_year['Received Date'].dt.month == current_month]

st.title("Legal Cases Dashboard 📊")
st.subheader(f"Total Cases This Month: {len(cases_this_month)} | Total Cases This Year: {len(cases_this_year)}")

# Annual Target Progress
target_cases = st.sidebar.number_input("Set Annual Target", min_value=0, value=2000)
progress = len(cases_this_year) / target_cases * 100
st.progress(progress / 100)
st.write(f"Progress toward target: **{progress:.2f}%**")

# Cases by Partner
cases_by_partner = filtered_df.groupby("Received From").size().reset_index(name="Count")
fig_partner = px.bar(cases_by_partner, x="Received From", y="Count", title="Cases by Partner", color="Count")
st.plotly_chart(fig_partner)

# Cases by Category
cases_by_category = filtered_df.groupby("Category").size().reset_index(name="Count")
fig_category = px.pie(cases_by_category, names="Category", values="Count", title="Cases by Category")
st.plotly_chart(fig_category)

# Comparison with Last Year
previous_year_cases = df[df['Received Date'].dt.year == (current_year - 1)]
current_vs_last = pd.DataFrame({
    "Year": ["Last Year", "This Year"],
    "Cases": [len(previous_year_cases), len(cases_this_year)]
})

fig_comparison = px.bar(current_vs_last, x="Year", y="Cases", title="Current Year vs Last Year Cases", color="Cases")
st.plotly_chart(fig_comparison)

# Monthly Trends
df['Month-Year'] = df['Received Date'].dt.to_period('M')
cases_trend = df.groupby("Month-Year").size().reset_index(name="Count")
cases_trend["Month-Year"] = cases_trend["Month-Year"].astype(str)

fig_trend = px.line(cases_trend, x="Month-Year", y="Count", title="Monthly Cases Trend", markers=True)
st.plotly_chart(fig_trend)

st.write("### Filtered Data")
st.dataframe(filtered_df)
