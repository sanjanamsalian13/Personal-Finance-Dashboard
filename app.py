from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("💰 Personal Finance Dashboard")
st.write("Analyze your income and expenses easily!")

# --------------------------------------------------
# Upload CSV
# --------------------------------------------------
base_dir = Path(__file__).resolve().parent
default_csv_path = base_dir / "transactions.csv"

uploaded_file = st.file_uploader(
    "Upload your transactions CSV",
    type="csv"
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    if not default_csv_path.exists():
        st.error(f"❌ Default CSV not found at {default_csv_path}")
        st.stop()
    df = pd.read_csv(default_csv_path)

# Convert numeric values safely
try:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
except KeyError:
    st.error("❌ CSV must contain an Amount column.")
    st.stop()

# --------------------------------------------------
# Validate CSV
# --------------------------------------------------
required_columns = [
    "Date",
    "Description",
    "Amount",
    "Category",
    "Type"
]

if not all(column in df.columns for column in required_columns):
    st.error("❌ Invalid CSV format.")
    st.stop()

# --------------------------------------------------
# Sidebar Filters
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

selected_type = st.sidebar.selectbox(
    "Transaction Type",
    ["All"] + list(df["Type"].unique())
)

selected_category = st.sidebar.selectbox(
    "Category",
    ["All"] + list(df["Category"].unique())
)

search = st.sidebar.text_input(
    "Search Description"
)



# --------------------------------------------------
# Apply Filters
# --------------------------------------------------
filtered_df = df.copy()

if selected_type != "All":
    filtered_df = filtered_df[
        filtered_df["Type"] == selected_type
    ]

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]

if search:
    filtered_df = filtered_df[
        filtered_df["Description"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# --------------------------------------------------
# Download Button
# --------------------------------------------------
st.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="transactions.csv",
    mime="text/csv"
)

# --------------------------------------------------
# Display Data
# --------------------------------------------------
st.subheader("📋 Transaction Details")

st.dataframe(filtered_df, width="stretch")

# --------------------------------------------------
# Financial Summary
# --------------------------------------------------
total_income = filtered_df[
    filtered_df["Type"] == "Income"
]["Amount"].sum()

total_expense = abs(
    filtered_df[
        filtered_df["Type"] == "Expense"
    ]["Amount"].sum()
)

net_savings = total_income - total_expense

st.subheader("📊 Financial Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💵 Total Income",
        f"₹{total_income:,.2f}"
    )

with col2:
    st.metric(
        "💸 Total Expense",
        f"₹{total_expense:,.2f}"
    )

with col3:
    st.metric(
        "💰 Net Savings",
        f"₹{net_savings:,.2f}"
    )


expense_df = filtered_df[
    filtered_df["Type"] == "Expense"
].copy()

if not expense_df.empty:
    expense_df["Amount"] = expense_df["Amount"].abs()
    expense_df["Date"] = pd.to_datetime(expense_df["Date"], errors="coerce")
else:
    expense_df = pd.DataFrame(columns=["Amount", "Date", "Category", "Description"])

# --------------------------------------------------
# Quick Financial Insights
# --------------------------------------------------

st.subheader("📌 Quick Financial Insights")

total_transactions = len(filtered_df)

if not expense_df.empty:
    highest_expense = expense_df.loc[expense_df["Amount"].idxmax()]
    highest_category = (
        expense_df.groupby("Category")["Amount"]
        .sum()
        .idxmax()
    )
    average_expense = expense_df["Amount"].mean()
else:
    highest_expense = None
    highest_category = "N/A"
    average_expense = 0.0

savings_rate = (
    (net_savings / total_income) * 100
    if total_income > 0 else 0
)

col1, col2 = st.columns(2)

with col1:
    st.info(f"📄 Total Transactions: {total_transactions}")
    if highest_expense is not None:
        st.info(
            f"💸 Highest Expense: {highest_expense['Description']} (₹{highest_expense['Amount']:,.2f})"
        )
    else:
        st.info("💸 Highest Expense: No expense records for the current filters")
    st.info(f"📂 Highest Spending Category: {highest_category}")

with col2:
    st.info(f"📊 Average Expense: ₹{average_expense:,.2f}")
    st.info(f"💰 Savings Rate: {savings_rate:.2f}%")


# --------------------------------------------------
# Expense Data
# --------------------------------------------------
# Reuse the expense_df prepared above for charts and summaries.

# --------------------------------------------------
# Pie Chart
# --------------------------------------------------
st.subheader("🥧 Expense Distribution")

if not expense_df.empty:
    pie_chart = px.pie(
        expense_df,
        values="Amount",
        names="Category",
        title="Expense Distribution"
    )

    st.plotly_chart(
        pie_chart,
        width="stretch"
    )
else:
    st.info("No expense data available for the current filters.")

# --------------------------------------------------
# Expense by Category
# --------------------------------------------------
st.subheader("📂 Expenses by Category")

if not expense_df.empty:
    category_expense = (
        expense_df
        .groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    st.dataframe(
        category_expense,
        width="stretch"
    )

    bar_chart = px.bar(
        category_expense,
        x="Category",
        y="Amount",
        color="Category",
        title="Expenses by Category"
    )

    st.plotly_chart(
        bar_chart,
        width="stretch"
    )
else:
    st.info("No category expense data available for the current filters.")

# --------------------------------------------------
# Daily Spending Trend
# --------------------------------------------------
st.subheader("📈 Daily Spending Trend")

if not expense_df.empty:
    daily_expense = (
        expense_df
        .groupby("Date")["Amount"]
        .sum()
        .reset_index()
    )

    line_chart = px.line(
        daily_expense,
        x="Date",
        y="Amount",
        markers=True,
        title="Daily Spending Trend"
    )

    st.plotly_chart(
        line_chart,
        width="stretch"
    )
else:
    st.info("No daily spending trend data available for the current filters.")

# --------------------------------------------------
# Monthly Expense Summary
# --------------------------------------------------
if not expense_df.empty:
    expense_df["Month"] = (
        expense_df["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_expense = (
        expense_df
        .groupby("Month")["Amount"]
        .sum()
        .reset_index()
    )

    st.subheader("📅 Monthly Expense Summary")

    st.dataframe(
        monthly_expense,
        width="stretch"
    )
else:
    st.subheader("📅 Monthly Expense Summary")
    st.info("No monthly expense data available for the current filters.")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("---")
st.caption("Built using ❤️ Python • Pandas • Plotly • Streamlit")