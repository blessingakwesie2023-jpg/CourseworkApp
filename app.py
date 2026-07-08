import streamlit as st
import pandas as pd
import io
from database import fetch, execute

st.title("Car Dealership Database Management System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Run Use Cases", "View Tables", "Run Queries"]
)


# ----------------------------
# HELPER: Excel download button
# ----------------------------
def add_excel_download(df, filename="report.xlsx", label="Download as Excel"):
    if df.empty:
        return
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    buffer.seek(0)
    st.download_button(
        label=label,
        data=buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ----------------------------
# RUN USE CASES
# ----------------------------
if menu == "Run Use Cases":
    st.header("Add New Customer")

    first = st.text_input("First Name")
    last = st.text_input("Last Name")
    address = st.text_input("Address")
    city = st.text_input("City")
    postcode = st.text_input("Postcode")
    phone = st.text_input("Phone")
    email = st.text_input("Email")

    if st.button("Add Customer"):
        execute(
            """
            INSERT INTO Customers
            (FirstName, LastName, Address, City, Postcode, Phone, Email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (first, last, address, city, postcode, phone, email)
        )
        st.success("Customer added successfully!")

# ----------------------------
# VIEW TABLES
# ----------------------------
elif menu == "View Tables":

    st.header("View Tables")

    table = st.selectbox(
        "Choose Table",
        [
            "Cars",
            "Customers",
            "Staff",
            "Sales",
            "Services"
        ]
    )

    result = fetch(f"SELECT * FROM {table}")

    if isinstance(result, tuple) and len(result) == 2:
        cols, rows = result
        df = pd.DataFrame(rows, columns=cols)
    else:
        df = pd.DataFrame(result)

    st.dataframe(df)

    add_excel_download(df, filename=f"{table}.xlsx", label=f"Download {table} as Excel")

# ----------------------------
# RUN QUERIES
# ----------------------------
elif menu == "Run Queries":

    st.header("Common Queries")

    query = st.selectbox(
        "Choose Query",
        [
            "All Cars",
            "Available Cars",
            "Sold Cars",
            "Customers",
            "Sales History",
            "Services",
            "Cars Over £30,000",
            "Automatic Cars",
            "Hybrid Cars",
            "Sales with Customer Names"
        ]
    )

    if query == "All Cars":
        result = fetch("SELECT * FROM Cars")

    elif query == "Available Cars":
        result = fetch(
            "SELECT * FROM Cars WHERE Status='Available'"
        )

    elif query == "Sold Cars":
        result = fetch(
            "SELECT * FROM Cars WHERE Status='Sold'"
        )

    elif query == "Customers":
        result = fetch(
            "SELECT * FROM Customers"
        )

    elif query == "Sales History":
        result = fetch(
            "SELECT * FROM Sales"
        )

    elif query == "Services":
        result = fetch(
            "SELECT * FROM Services"
        )

    elif query == "Cars Over £30,000":
        result = fetch(
            "SELECT * FROM Cars WHERE Price > 30000"
        )

    elif query == "Automatic Cars":
        result = fetch(
            "SELECT * FROM Cars WHERE Transmission='Automatic'"
        )

    elif query == "Hybrid Cars":
        result = fetch(
            "SELECT * FROM Cars WHERE FuelType='Hybrid'"
        )

    elif query == "Sales with Customer Names":
        result = fetch(
            """
            SELECT
                Sales.SaleID,
                Customers.FirstName,
                Customers.LastName,
                Cars.Make,
                Cars.Model,
                Sales.SalePrice,
                Sales.SaleDate
            FROM Sales
            JOIN Customers
                ON Sales.CustomerID = Customers.CustomerID
            JOIN Cars
                ON Sales.CarID = Cars.CarID
            """
        )

    if isinstance(result, tuple) and len(result) == 2:
        cols, rows = result
        df = pd.DataFrame(rows, columns=cols)
    else:
        df = pd.DataFrame(result)

    st.dataframe(df)

    safe_name = query.replace(" ", "_").replace(",", "").replace("£", "")
    add_excel_download(df, filename=f"{safe_name}.xlsx", label=f"Download '{query}' as Excel")