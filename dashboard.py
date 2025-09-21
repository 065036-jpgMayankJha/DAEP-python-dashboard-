import pandas as pd
import streamlit as st
import plotly.express as px
import io

# ======================
# Load dataset
# ======================
@st.cache_data
def load_data():
    # Try multiple file path options
    file_paths = [
        "marketing_campaign_dataset.csv"
    ]
    
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            st.success(f"✅ Data loaded successfully from: {file_path}")
            return df
        except FileNotFoundError:
            continue
    
    # If no file found, show error
    st.error("❌ CSV file not found. Please ensure 'marketing_campaign_dataset.csv' is in the correct location.")
    st.info("For deployment, place the CSV file in the same directory as your app.py")
    st.stop()

df = load_data()
df.columns = df.columns.str.strip()

# ======================
# Streamlit setup
# ======================
st.set_page_config(page_title="Marketing Dashboard", layout="wide")
st.title("📊 Marketing Campaign KPI Dashboard")
st.markdown("---")

# ======================
# Sidebar Filters
# ======================
st.sidebar.header("🔎 Filters")

# Campaign Type filter
campaign_filter = st.sidebar.multiselect(
    "Select Campaign Type",
    df["Campaign_Type"].unique(),
    default=list(df["Campaign_Type"].unique())
)

# Channel filter
channel_filter = st.sidebar.multiselect(
    "Select Channel",
    df["Channel_Used"].unique(),
    default=list(df["Channel_Used"].unique())
)

# Company filter
company_filter = st.sidebar.multiselect(
    "Select Company",
    df["Company"].unique(),
    default=list(df["Company"].unique())
)

# Apply filters
filtered_df = df[
    (df["Campaign_Type"].isin(campaign_filter)) &
    (df["Channel_Used"].isin(channel_filter)) &
    (df["Company"].isin(company_filter))
]

if filtered_df.empty:
    st.warning("No data matches your current filters. Please adjust your selections.")
    st.stop()

# ======================
# Summary KPIs
# ======================
st.markdown("### 📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

# Clean acquisition cost data
filtered_df['Acquisition_Cost_Numeric'] = filtered_df['Acquisition_Cost'].str.replace('$', '').str.replace(',', '').astype(float)

with col1:
    avg_conversion = filtered_df['Conversion_Rate'].mean()
    st.metric(
        "Avg Conversion Rate", 
        f"{avg_conversion:.1%}",
        delta=f"{(avg_conversion - df['Conversion_Rate'].mean()):.1%}"
    )

with col2:
    avg_roi = filtered_df['ROI'].mean()
    st.metric(
        "Average ROI", 
        f"{avg_roi:.2f}x",
        delta=f"{(avg_roi - df['ROI'].mean()):.2f}"
    )

with col3:
    total_clicks = filtered_df['Clicks'].sum()
    st.metric("Total Clicks", f"{total_clicks:,}")

with col4:
    avg_cost = filtered_df['Acquisition_Cost_Numeric'].mean()
    st.metric("Avg Acquisition Cost", f"${avg_cost:,.0f}")

st.markdown("---")

# ======================
# Charts Layout
# ======================

# Row 1: Two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🎯 Conversion Rate by Campaign Type")
    conv_by_type = filtered_df.groupby("Campaign_Type")["Conversion_Rate"].mean().reset_index()
    fig1 = px.bar(
        conv_by_type,
        x="Campaign_Type", 
        y="Conversion_Rate", 
        color="Campaign_Type",
        text="Conversion_Rate",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=""
    )
    fig1.update_traces(texttemplate='%{text:.1%}', textposition="outside")
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### 💰 Average ROI by Channel")
    roi_by_channel = filtered_df.groupby('Channel_Used')['ROI'].mean().sort_values(ascending=False).reset_index()
    fig2 = px.bar(
        roi_by_channel,
        x='Channel_Used',
        y='ROI',
        color='Channel_Used',
        text='ROI',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title=""
    )
    fig2.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig2.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Full width treemap
st.markdown("#### 🏢 Campaign Performance by Company")
fig3 = px.treemap(
    filtered_df,
    path=['Company', 'Campaign_Type'],
    values='Clicks',
    color='ROI',
    color_continuous_scale='RdYlGn',
    title=""
)
fig3.update_layout(height=500)
st.plotly_chart(fig3, use_container_width=True)

# Row 3: Two columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🎪 Target Audience Distribution")
    fig4 = px.pie(
        filtered_df, 
        names='Target_Audience', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title=""
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.markdown("#### 📈 ROI vs Acquisition Cost")
    fig5 = px.scatter(
        filtered_df, 
        x="Acquisition_Cost_Numeric", 
        y="ROI",
        color="Campaign_Type", 
        size="Conversion_Rate",
        hover_data=["Company", "Channel_Used"],
        size_max=40,
        title=""
    )
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)

# Row 4: Time series if date column exists
try:
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors="coerce")
    if not filtered_df["Date"].isnull().all():
        st.markdown("#### 📅 Engagement Score Trend")
        fig6 = px.line(
            filtered_df.sort_values("Date"), 
            x="Date", 
            y="Engagement_Score",
            color="Campaign_Type", 
            markers=True,
            title=""
        )
        fig6.update_layout(height=400)
        st.plotly_chart(fig6, use_container_width=True)
except:
    pass

# ======================
# Data Table
# ======================
st.markdown("---")
st.markdown("#### 📋 Campaign Details")
st.dataframe(
    filtered_df[['Campaign_ID', 'Company', 'Campaign_Type', 'Channel_Used', 
                'Conversion_Rate', 'ROI', 'Clicks', 'Impressions']],
    use_container_width=True
)
