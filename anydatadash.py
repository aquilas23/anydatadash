import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# Streamlit configuration
st.set_page_config(page_title="General Dataset Analysis", page_icon=":bar_chart:", layout="wide")

# Title and header
st.title(":bar_chart: General Dataset Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# File upload handling
fl = st.file_uploader(":file_folder: Upload a dataset", type=(["csv", "txt", "xlsx", "xls"]))
if fl is not None:
    df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    st.stop()

# Clean column names
df.columns = df.columns.str.strip()

# Sidebar for dynamic filter creation based on categorical columns
st.sidebar.header("Choose your filters:")

# Identifying column types
numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
date_cols = df.select_dtypes(include=['datetime64', 'object']).columns.tolist()

# Filter for categorical columns
filters = {}
for col in categorical_cols:
    unique_values = df[col].unique()
    selected_values = st.sidebar.multiselect(f"Select values for {col}", unique_values)
    if selected_values:
        filters[col] = selected_values

# Applying filters
df_filtered = df.copy()
for col, values in filters.items():
    df_filtered = df_filtered[df_filtered[col].isin(values)]

# Show summary statistics for numerical columns
if numerical_cols:
    with st.expander("Numerical Column Statistics"):
        st.write(df_filtered[numerical_cols].describe().transpose())

# Dynamic visualizations for numerical columns
if numerical_cols:
    # Correlation matrix
    st.subheader("Correlation Matrix")
    corr = df_filtered[numerical_cols].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)

    # Scatter plot for two numerical variables
    st.subheader("Scatter Plot between Two Numerical Variables")
    num_col_x = st.selectbox("Select X-axis", numerical_cols)
    num_col_y = st.selectbox("Select Y-axis", numerical_cols, index=1)
    size_col = st.selectbox("Select Size variable", [None] + numerical_cols, index=0)
    fig_scatter = px.scatter(df_filtered, x=num_col_x, y=num_col_y, size=size_col if size_col else None)
    st.plotly_chart(fig_scatter, use_container_width=True)

# Visualizations for categorical columns
if categorical_cols and numerical_cols:
    st.subheader("Bar Chart of Categorical Variables with a Numerical Value")
    cat_col = st.selectbox("Select Categorical Variable", categorical_cols)
    num_col = st.selectbox("Select Numerical Variable", numerical_cols)

    grouped_df = df_filtered.groupby(cat_col, as_index=False)[num_col].mean()
    fig_bar = px.bar(grouped_df, x=cat_col, y=num_col, text=[f'${x:,.2f}' for x in grouped_df[num_col]])
    st.plotly_chart(fig_bar, use_container_width=True)

# Pie chart for categorical distribution
if categorical_cols:
    st.subheader("Pie Chart for Categorical Variables")
    pie_col = st.selectbox("Select a Categorical Variable for Pie Chart", categorical_cols)
    pie_data = df_filtered[pie_col].value_counts().reset_index()
    pie_data.columns = [pie_col, 'count']
    fig_pie = px.pie(pie_data, values='count', names=pie_col, title=f"Distribution of {pie_col}")
    st.plotly_chart(fig_pie, use_container_width=True)

# Time series analysis (if date columns are present)
for col in date_cols:
    try:
        df_filtered[col] = pd.to_datetime(df_filtered[col], errors='coerce')
    except:
        continue

if date_cols:
    valid_date_cols = [col for col in date_cols if pd.api.types.is_datetime64_any_dtype(df_filtered[col])]
    if valid_date_cols:
        st.subheader("Time Series Analysis")
        date_col = st.selectbox("Select Date Column", valid_date_cols)
        num_col_for_ts = st.selectbox("Select Numerical Column for Time Series", numerical_cols)

        df_filtered['year_month'] = df_filtered[date_col].dt.to_period("M")
        ts_data = df_filtered.groupby("year_month")[num_col_for_ts].mean().reset_index()

        fig_ts = px.line(ts_data, x='year_month', y=num_col_for_ts, title=f"{num_col_for_ts} Over Time")
        st.plotly_chart(fig_ts, use_container_width=True)

# Download the filtered dataset
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button('Download Filtered Data', data=csv, file_name="Filtered_Data.csv", mime='text/csv')
