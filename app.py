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
# QUERY DEFINITIONS
# ----------------------------
QUERIES = {

    "Cars Available for Sale": """
    SELECT
        c.CarID,
        c.Make,
        c.Model,
        c.Year,
        c.Colour,
        c.Mileage,
        c.FuelType,
        c.Transmission,
        ROUND(c.Price, 2) AS ListPrice_GBP
    FROM Cars c
    WHERE c.Status = 'Available'
    ORDER BY c.Price DESC;
    """,

    "Sales by Date": """
    SELECT
        s.SaleID,
        s.SaleDate,
        c.Make || ' ' || c.Model AS Vehicle,
        ROUND(s.SalePrice, 2) AS SalePrice_GBP,
        s.PaymentMethod,
        st.FirstName || ' ' || st.LastName AS SalesStaff
    FROM Sales s
    JOIN Cars c ON s.CarID = c.CarID
    JOIN Staff st ON s.StaffID = st.StaffID
    WHERE s.SaleDate BETWEEN '2024-01-01' AND '2024-12-31'
    ORDER BY s.SaleDate;
    """,

    "Sales by Staff Member": """
    SELECT
        st.StaffID,
        st.FirstName || ' ' || st.LastName AS StaffMember,
        st.JobTitle,
        COUNT(s.SaleID) AS TotalSales,
        ROUND(SUM(s.SalePrice), 2) AS TotalRevenue_GBP,
        ROUND(AVG(s.SalePrice), 2) AS AvgSalePrice_GBP,
        ROUND(MAX(s.SalePrice), 2) AS HighestSale_GBP
    FROM Staff st
    LEFT JOIN Sales s ON st.StaffID = s.StaffID
    GROUP BY st.StaffID, st.FirstName, st.LastName, st.JobTitle
    HAVING COUNT(s.SaleID) > 0
    ORDER BY TotalRevenue_GBP DESC;
    """,

    "Total Sales Revenue": """
    SELECT
        COUNT(SaleID) AS TotalTransactions,
        ROUND(SUM(SalePrice), 2) AS GrandTotalRevenue_GBP,
        ROUND(AVG(SalePrice), 2) AS AverageSalePrice_GBP,
        ROUND(MIN(SalePrice), 2) AS LowestSale_GBP,
        ROUND(MAX(SalePrice), 2) AS HighestSale_GBP
    FROM Sales;
    """,

    "Number of Cars Sold": """
    SELECT
        COUNT(*) AS TotalCarsSold
    FROM Cars
    WHERE Status = 'Sold';
    """,

    "Number of Cars by Fuel Type": """
    SELECT
        FuelType,
        COUNT(*) AS NumberOfCars
    FROM Cars
    GROUP BY FuelType
    ORDER BY NumberOfCars DESC;
    """,

    "Number of Sales by Payment Method": """
    SELECT
        PaymentMethod,
        COUNT(*) AS NumberOfSales,
        ROUND(SUM(SalePrice), 2) AS TotalRevenue_GBP
    FROM Sales
    GROUP BY PaymentMethod
    ORDER BY NumberOfSales DESC;
    """,

    "Cars with Upcoming Services": """
    SELECT
        sv.ServiceID,
        sv.ServiceDate,
        c.Make || ' ' || c.Model || ' (' || c.Year || ')' AS Vehicle,
        c.CarID,
        sv.ServiceType,
        ROUND(sv.ServiceCost, 2) AS EstimatedCost_GBP,
        st.FirstName || ' ' || st.LastName AS AssignedTechnician,
        julianday(sv.ServiceDate) - julianday(DATE('now')) AS DaysUntilService
    FROM Services sv
    JOIN Cars c ON sv.CarID = c.CarID
    JOIN Staff st ON sv.StaffID = st.StaffID
    WHERE sv.ServiceDate > DATE('now')
    ORDER BY sv.ServiceDate ASC;
    """,

    "Cars with Past Services": """
    SELECT
        sv.ServiceID,
        sv.ServiceDate,
        c.Make || ' ' || c.Model || ' (' || c.Year || ')' AS Vehicle,
        c.CarID,
        sv.ServiceType,
        ROUND(sv.ServiceCost, 2) AS Cost_GBP,
        st.FirstName || ' ' || st.LastName AS Technician,
        sv.Notes
    FROM Services sv
    JOIN Cars c ON sv.CarID = c.CarID
    JOIN Staff st ON sv.StaffID = st.StaffID
    WHERE sv.ServiceDate <= DATE('now')
    ORDER BY sv.ServiceDate DESC;
    """,

    "Customer Purchase Histories": """
    SELECT
        cu.CustomerID,
        cu.FirstName || ' ' || cu.LastName AS CustomerName,
        cu.City,
        cu.Email,
        COUNT(s.SaleID) AS TotalPurchases,
        ROUND(SUM(s.SalePrice), 2) AS TotalSpent_GBP,
        MIN(s.SaleDate) AS FirstPurchase,
        MAX(s.SaleDate) AS MostRecentPurchase,
        GROUP_CONCAT(c.Make || ' ' || c.Model, ' | ') AS VehiclesBought
    FROM Customers cu
    LEFT JOIN Sales s ON cu.CustomerID = s.CustomerID
    LEFT JOIN Cars c ON s.CarID = c.CarID
    GROUP BY cu.CustomerID
    ORDER BY TotalSpent_GBP DESC;
    """
}


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
        list(QUERIES.keys())
    )

    result = fetch(QUERIES[query])

    if isinstance(result, tuple) and len(result) == 2:
        cols, rows = result
        df = pd.DataFrame(rows, columns=cols)
    else:
        df = pd.DataFrame(result)

    st.dataframe(df)

    safe_name = query.replace(" ", "_").replace(",", "").replace("£", "")
    add_excel_download(df, filename=f"{safe_name}.xlsx", label=f"Download '{query}' as Excel")
