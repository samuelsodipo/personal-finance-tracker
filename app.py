import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

st.set_page_config(page_title="Finance Tracker", page_icon="💷", layout="wide")

# Database
conn = sqlite3.connect("finance.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL
)
""")
conn.commit()
# Sidebar navigation
st.sidebar.title("💷 Finance Tracker")
st.sidebar.write("Your personal finance dashboard")
st.sidebar.divider()

st.sidebar.subheader("Navigation")
st.sidebar.write("🏠 Dashboard")
st.sidebar.write("💳 Transactions")
st.sidebar.write("📊 Spending Analysis")

st.sidebar.divider()
st.sidebar.success("Database Connected")

st.title("💷 Personal Finance Tracker")
st.caption("Track your income, expenses and spending habits.")

# Add transaction
st.subheader("Add Transaction")

with st.form("transaction_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        description = st.text_input("Description")
        amount = st.number_input("Amount (£)", min_value=0.01, value=10.0)
        transaction_type = st.selectbox("Type", ["Expense", "Income"])

    with col2:
        transaction_date = st.date_input("Date", date.today())
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Shopping", "Bills",
             "Entertainment", "Salary", "Other"]
        )

    submitted = st.form_submit_button("Add Transaction", type="primary")

    if submitted:
        if not description.strip():
            st.error("Please enter a description.")
        else:
            conn.execute(
                """INSERT INTO transactions
                (date, description, category, type, amount)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    str(transaction_date),
                    description.strip(),
                    category,
                    transaction_type,
                    amount,
                ),
            )
            conn.commit()
            st.success("Transaction added successfully!")

# Load transactions
df = pd.read_sql_query(
    "SELECT * FROM transactions ORDER BY date DESC, id DESC",
    conn
)

income = df.loc[df["type"] == "Income", "amount"].sum()
expenses = df.loc[df["type"] == "Expense", "amount"].sum()
balance = income - expenses

st.divider()

# Dashboard
st.subheader("📊 Financial Overview")

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    with st.container(border=True):
        st.metric("💰 Total Income", f"£{income:,.2f}")

with col2:
    with st.container(border=True):
        st.metric("💸 Total Expenses", f"£{expenses:,.2f}")

with col3:
    with st.container(border=True):
        st.metric("💷 Available Balance", f"£{balance:,.2f}")
st.divider()

# Transactions
st.subheader("Transaction History")

if df.empty:
    st.info("No transactions yet. Add your first transaction above.")
else:
    st.dataframe(
        df[["date", "description", "category", "type", "amount"]],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Spending by Category")

    expense_df = df[df["type"] == "Expense"]

    if not expense_df.empty:
        spending = expense_df.groupby("category")["amount"].sum()
        st.bar_chart(spending)
    else:
        st.info("Add an expense to see your spending chart.")

    st.subheader("Delete Transaction")

    transaction_id = st.selectbox(
        "Select transaction to delete",
        df["id"].tolist(),
        format_func=lambda x: (
            f"{x} - "
            f"{df.loc[df['id'] == x, 'description'].iloc[0]}"
        ),
    )

    if st.button("Delete Selected Transaction"):
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,),
        )
        conn.commit()
        st.rerun()
# Monthly Spending Analysis
st.divider()
st.subheader("📅 Monthly Spending Analysis")

if not df.empty:
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")

    monthly_expenses = (
        df[df["type"] == "Expense"]
        .groupby("month")["amount"]
        .sum()
    )

    if not monthly_expenses.empty:
        st.line_chart(monthly_expenses)
    else:
        st.info("No expenses recorded yet.")
else:
    st.info("Add transactions to see monthly spending.")

conn.close()