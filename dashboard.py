import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
def load_data():
    df = pd.read_csv("C:\Users\10b11\OneDrive\Desktop\Python dashboard\marketing_campaign_dataset.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Acquisition_Cost"] = df["Acquisition_Cost"].str.replace("$", "").str.replace(",", "").astype(float)
    return df

df = load_data()

st.set_page_config(page_title="Marketing Campaign Dashboard", layout="wide")
st.title("📊 Marketing Campaign Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Data")
company = st.sidebar.multiselect("Select Company", df["Company"].unique())
campaign_type = st.sidebar.multiselect("Select Campaign Type", df["Campaign_Type"].unique())
channel = st.sidebar.multiselect("Select Channel", df["Channel_Used"].unique())
location = st.sidebar.multiselect("Select Location", df["Location"].unique())

filtered_df = df.copy()
if company:
    filtered_df = filtered_df[filtered_df["Company"].isin(company)]
if campaign_type:
    filtered_df = filtered_df[filtered_df["Campaign_Type"].isin(campaign_type)]
if channel:
    filtered_df = filtered_df[filtered_df["Channel_Used"].isin(channel)]
if location:
    filtered_df = filtered_df[filtered_df["Location"].isin(location)]

# KPIs
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Conversion Rate", f"{filtered_df['Conversion_Rate'].mean():.2%}")
with col2:
    st.metric("Avg ROI", f"{filtered_df['ROI'].mean():.2f}")
with col3:
    st.metric("Total Clicks", f"{filtered_df['Clicks'].sum():,}")
with col4:
    st.metric("Total Impressions", f"{filtered_df['Impressions'].sum():,}")

# Charts
st.subheader("Visualizations")
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(filtered_df.groupby("Channel_Used")["Conversion_Rate"].mean().reset_index(),
                  x="Channel_Used", y="Conversion_Rate", title="Avg Conversion Rate by Channel")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(filtered_df.groupby("Campaign_Type")["ROI"].mean().reset_index(),
                  x="Campaign_Type", y="ROI", title="Avg ROI by Campaign Type")
    st.plotly_chart(fig2, use_container_width=True)

# Time series
fig3 = px.line(filtered_df.groupby("Date")["Conversion_Rate"].mean().reset_index(),
               x="Date", y="Conversion_Rate", title="Conversion Rate Over Time")
st.plotly_chart(fig3, use_container_width=True)

# Show data table
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)
  
