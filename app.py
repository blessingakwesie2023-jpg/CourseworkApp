import streamlit as st
import pandas as pd
import io
from database import fetch, execute

st.title("DriveSmart Motors Ltd")

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


def result_to_df(result):
    if isinstance(result, tuple) and len(result) == 2:
        cols, rows = result
        return pd.DataFrame(rows, columns=cols)
    return pd.DataFrame(result)


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

    use_case = st.sidebar.radio(
        "Choose Use Case",
        ["Add New Customer", "Manage Cars"]
    )

    # ------------------------------------------------
    # USE CASE: ADD NEW CUSTOMER
    # ------------------------------------------------
    if use_case == "Add New Customer":
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

    # ------------------------------------------------
    # USE CASE: MANAGE CARS (ADD / UPDATE / DELETE)
    # ------------------------------------------------
    elif use_case == "Manage Cars":
        st.header("Manage Cars")

        car_action = st.radio(
            "Choose Action",
            ["Add Car", "Update Car", "Delete Car"],
            horizontal=True
        )

        FUEL_TYPES = ["Petrol", "Diesel", "Hybrid", "Electric", "LPG"]
        TRANSMISSIONS = ["Manual", "Automatic"]
        STATUSES = ["Available", "Sold"]

        # --------------------------
        # ADD CAR
        # --------------------------
        if car_action == "Add Car":
            st.subheader("Add New Car")

            make = st.text_input("Make")
            model = st.text_input("Model")
            year = st.number_input("Year", min_value=1900, max_value=2100, step=1, value=2024)
            colour = st.text_input("Colour")
            mileage = st.number_input("Mileage", min_value=0, step=1, value=0)
            fuel_type = st.selectbox("Fuel Type", FUEL_TYPES)
            transmission = st.selectbox("Transmission", TRANSMISSIONS)
            price = st.number_input("Price (GBP)", min_value=0.0, step=100.0, value=0.0, format="%.2f")
            status = st.selectbox("Status", STATUSES)
            purchase_date = st.date_input("Purchase Date")

            if st.button("Add Car"):
                if not make or not model:
                    st.error("Make and Model are required.")
                else:
                    execute(
                        """
                        INSERT INTO Cars
                        (Make, Model, Year, Colour, Mileage, FuelType,
                         Transmission, Price, Status, PurchaseDate)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (make, model, int(year), colour, int(mileage), fuel_type,
                         transmission, float(price), status, str(purchase_date))
                    )
                    st.success(f"Car '{make} {model}' added successfully!")

        # --------------------------
        # UPDATE CAR
        # --------------------------
        elif car_action == "Update Car":
            st.subheader("Update Existing Car")

            cars_df = result_to_df(fetch("SELECT * FROM Cars ORDER BY CarID"))

            if cars_df.empty:
                st.info("No cars found in the database.")
            else:
                cars_df["Label"] = cars_df.apply(
                    lambda r: f"#{r['CarID']} - {r['Make']} {r['Model']} ({r['Year']})",
                    axis=1
                )
                selected_label = st.selectbox("Select Car to Update", cars_df["Label"])
                selected_row = cars_df[cars_df["Label"] == selected_label].iloc[0]
                car_id = int(selected_row["CarID"])

                make = st.text_input("Make", value=str(selected_row["Make"]))
                model = st.text_input("Model", value=str(selected_row["Model"]))
                year = st.number_input(
                    "Year", min_value=1900, max_value=2100, step=1,
                    value=int(selected_row["Year"])
                )
                colour = st.text_input("Colour", value=str(selected_row["Colour"]))
                mileage = st.number_input(
                    "Mileage", min_value=0, step=1, value=int(selected_row["Mileage"])
                )
                fuel_type = st.selectbox(
                    "Fuel Type", FUEL_TYPES,
                    index=FUEL_TYPES.index(selected_row["FuelType"])
                    if selected_row["FuelType"] in FUEL_TYPES else 0
                )
                transmission = st.selectbox(
                    "Transmission", TRANSMISSIONS,
                    index=TRANSMISSIONS.index(selected_row["Transmission"])
                    if selected_row["Transmission"] in TRANSMISSIONS else 0
                )
                price = st.number_input(
                    "Price (GBP)", min_value=0.0, step=100.0,
                    value=float(selected_row["Price"]), format="%.2f"
                )
                status = st.selectbox(
                    "Status", STATUSES,
                    index=STATUSES.index(selected_row["Status"])
                    if selected_row["Status"] in STATUSES else 0
                )
                purchase_date = st.date_input(
                    "Purchase Date", value=pd.to_datetime(selected_row["PurchaseDate"]).date()
                    if pd.notnull(selected_row.get("PurchaseDate")) else None
                )

                if st.button("Update Car"):
                    execute(
                        """
                        UPDATE Cars
                        SET Make = ?, Model = ?, Year = ?, Colour = ?, Mileage = ?,
                            FuelType = ?, Transmission = ?, Price = ?, Status = ?,
                            PurchaseDate = ?
                        WHERE CarID = ?
                        """,
                        (make, model, int(year), colour, int(mileage), fuel_type,
                         transmission, float(price), status, str(purchase_date), car_id)
                    )
                    st.success(f"Car #{car_id} updated successfully!")

        # --------------------------
        # DELETE CAR
        # --------------------------
        elif car_action == "Delete Car":
            st.subheader("Delete Car")

            cars_df = result_to_df(fetch("SELECT * FROM Cars ORDER BY CarID"))

            if cars_df.empty:
                st.info("No cars found in the database.")
            else:
                cars_df["Label"] = cars_df.apply(
                    lambda r: f"#{r['CarID']} - {r['Make']} {r['Model']} ({r['Year']})",
                    axis=1
                )
                selected_label = st.selectbox("Select Car to Delete", cars_df["Label"])
                selected_row = cars_df[cars_df["Label"] == selected_label].iloc[0]
                car_id = int(selected_row["CarID"])

                st.dataframe(selected_row.drop("Label").to_frame().T)

                confirm = st.checkbox(f"I confirm I want to delete Car #{car_id}")

                if st.button("Delete Car"):
                    if confirm:
                        execute("DELETE FROM Cars WHERE CarID = ?", (car_id,))
                        st.success(f"Car #{car_id} deleted successfully!")
                    else:
                        st.warning("Please tick the confirmation box before deleting.")

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
    df = result_to_df(result)

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
    df = result_to_df(result)

    st.dataframe(df)

    safe_name = query.replace(" ", "_").replace(",", "").replace("£", "")
    add_excel_download(df, filename=f"{safe_name}.xlsx", label=f"Download '{query}' as Excel")
