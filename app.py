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
# CONSTANTS
# ----------------------------
FUEL_TYPES = ["Petrol", "Diesel", "Hybrid", "Electric", "LPG"]
TRANSMISSIONS = ["Manual", "Automatic"]
STATUSES = ["Available", "Sold"]


# ----------------------------
# CUSTOMER CRUD SECTION
# ----------------------------
def manage_customers():
    st.subheader("Manage Customers")

    customer_action = st.radio(
        "Choose Action",
        ["Add Customer", "Update Customer", "Delete Customer"],
        horizontal=True,
        key="customer_action"
    )

    # --------------------------
    # ADD CUSTOMER
    # --------------------------
    if customer_action == "Add Customer":
        first = st.text_input("First Name", key="add_cust_first")
        last = st.text_input("Last Name", key="add_cust_last")
        address = st.text_input("Address", key="add_cust_address")
        city = st.text_input("City", key="add_cust_city")
        postcode = st.text_input("Postcode", key="add_cust_postcode")
        phone = st.text_input("Phone", key="add_cust_phone")
        email = st.text_input("Email", key="add_cust_email")

        if st.button("Add Customer", key="add_cust_btn"):
            if not first or not last:
                st.error("First Name and Last Name are required.")
            else:
                execute(
                    """
                    INSERT INTO Customers
                    (FirstName, LastName, Address, City, Postcode, Phone, Email)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (first, last, address, city, postcode, phone, email)
                )
                st.success(f"Customer '{first} {last}' added successfully!")

    # --------------------------
    # UPDATE CUSTOMER
    # --------------------------
    elif customer_action == "Update Customer":
        customers_df = result_to_df(fetch("SELECT * FROM Customers ORDER BY CustomerID"))

        if customers_df.empty:
            st.info("No customers found in the database.")
        else:
            customers_df["Label"] = customers_df.apply(
                lambda r: f"#{r['CustomerID']} - {r['FirstName']} {r['LastName']}",
                axis=1
            )
            selected_label = st.selectbox(
                "Select Customer to Update", customers_df["Label"], key="update_cust_select"
            )
            selected_row = customers_df[customers_df["Label"] == selected_label].iloc[0]
            customer_id = int(selected_row["CustomerID"])

            first = st.text_input("First Name", value=str(selected_row["FirstName"]), key="upd_cust_first")
            last = st.text_input("Last Name", value=str(selected_row["LastName"]), key="upd_cust_last")
            address = st.text_input("Address", value=str(selected_row["Address"]), key="upd_cust_address")
            city = st.text_input("City", value=str(selected_row["City"]), key="upd_cust_city")
            postcode = st.text_input("Postcode", value=str(selected_row["Postcode"]), key="upd_cust_postcode")
            phone = st.text_input("Phone", value=str(selected_row["Phone"]), key="upd_cust_phone")
            email = st.text_input("Email", value=str(selected_row["Email"]), key="upd_cust_email")

            if st.button("Update Customer", key="update_cust_btn"):
                execute(
                    """
                    UPDATE Customers
                    SET FirstName = ?, LastName = ?, Address = ?, City = ?,
                        Postcode = ?, Phone = ?, Email = ?
                    WHERE CustomerID = ?
                    """,
                    (first, last, address, city, postcode, phone, email, customer_id)
                )
                st.success(f"Customer #{customer_id} updated successfully!")

    # --------------------------
    # DELETE CUSTOMER
    # --------------------------
    elif customer_action == "Delete Customer":
        customers_df = result_to_df(fetch("SELECT * FROM Customers ORDER BY CustomerID"))

        if customers_df.empty:
            st.info("No customers found in the database.")
        else:
            customers_df["Label"] = customers_df.apply(
                lambda r: f"#{r['CustomerID']} - {r['FirstName']} {r['LastName']}",
                axis=1
            )
            selected_label = st.selectbox(
                "Select Customer to Delete", customers_df["Label"], key="delete_cust_select"
            )
            selected_row = customers_df[customers_df["Label"] == selected_label].iloc[0]
            customer_id = int(selected_row["CustomerID"])

            st.dataframe(selected_row.drop("Label").to_frame().T)

            confirm = st.checkbox(
                f"I confirm I want to delete Customer #{customer_id}", key="delete_cust_confirm"
            )

            if st.button("Delete Customer", key="delete_cust_btn"):
                if confirm:
                    execute("DELETE FROM Customers WHERE CustomerID = ?", (customer_id,))
                    st.success(f"Customer #{customer_id} deleted successfully!")
                else:
                    st.warning("Please tick the confirmation box before deleting.")


# ----------------------------
# CAR CRUD SECTION
# ----------------------------
def manage_cars():
    st.subheader("Manage Cars")

    car_action = st.radio(
        "Choose Action",
        ["Add Car", "Update Car", "Delete Car"],
        horizontal=True,
        key="car_action"
    )

    # --------------------------
    # ADD CAR
    # --------------------------
    if car_action == "Add Car":
        make = st.text_input("Make", key="add_car_make")
        model = st.text_input("Model", key="add_car_model")
        year = st.number_input(
            "Year", min_value=1900, max_value=2100, step=1, value=2024, key="add_car_year"
        )
        colour = st.text_input("Colour", key="add_car_colour")
        mileage = st.number_input("Mileage", min_value=0, step=1, value=0, key="add_car_mileage")
        fuel_type = st.selectbox("Fuel Type", FUEL_TYPES, key="add_car_fuel")
        transmission = st.selectbox("Transmission", TRANSMISSIONS, key="add_car_trans")
        price = st.number_input(
            "Price (GBP)", min_value=0.0, step=100.0, value=0.0, format="%.2f", key="add_car_price"
        )
        status = st.selectbox("Status", STATUSES, key="add_car_status")
        purchase_date = st.date_input("Purchase Date", key="add_car_pdate")

        if st.button("Add Car", key="add_car_btn"):
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
        cars_df = result_to_df(fetch("SELECT * FROM Cars ORDER BY CarID"))

        if cars_df.empty:
            st.info("No cars found in the database.")
        else:
            cars_df["Label"] = cars_df.apply(
                lambda r: f"#{r['CarID']} - {r['Make']} {r['Model']} ({r['Year']})",
                axis=1
            )
            selected_label = st.selectbox(
                "Select Car to Update", cars_df["Label"], key="update_car_select"
            )
            selected_row = cars_df[cars_df["Label"] == selected_label].iloc[0]
            car_id = int(selected_row["CarID"])

            make = st.text_input("Make", value=str(selected_row["Make"]), key="upd_car_make")
            model = st.text_input("Model", value=str(selected_row["Model"]), key="upd_car_model")
            year = st.number_input(
                "Year", min_value=1900, max_value=2100, step=1,
                value=int(selected_row["Year"]), key="upd_car_year"
            )
            colour = st.text_input("Colour", value=str(selected_row["Colour"]), key="upd_car_colour")
            mileage = st.number_input(
                "Mileage", min_value=0, step=1, value=int(selected_row["Mileage"]), key="upd_car_mileage"
            )
            fuel_type = st.selectbox(
                "Fuel Type", FUEL_TYPES,
                index=FUEL_TYPES.index(selected_row["FuelType"])
                if selected_row["FuelType"] in FUEL_TYPES else 0,
                key="upd_car_fuel"
            )
            transmission = st.selectbox(
                "Transmission", TRANSMISSIONS,
                index=TRANSMISSIONS.index(selected_row["Transmission"])
                if selected_row["Transmission"] in TRANSMISSIONS else 0,
                key="upd_car_trans"
            )
            price = st.number_input(
                "Price (GBP)", min_value=0.0, step=100.0,
                value=float(selected_row["Price"]), format="%.2f", key="upd_car_price"
            )
            status = st.selectbox(
                "Status", STATUSES,
                index=STATUSES.index(selected_row["Status"])
                if selected_row["Status"] in STATUSES else 0,
                key="upd_car_status"
            )
            purchase_date = st.date_input(
                "Purchase Date",
                value=pd.to_datetime(selected_row["PurchaseDate"]).date()
                if pd.notnull(selected_row.get("PurchaseDate")) else None,
                key="upd_car_pdate"
            )

            if st.button("Update Car", key="update_car_btn"):
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
        cars_df = result_to_df(fetch("SELECT * FROM Cars ORDER BY CarID"))

        if cars_df.empty:
            st.info("No cars found in the database.")
        else:
            cars_df["Label"] = cars_df.apply(
                lambda r: f"#{r['CarID']} - {r['Make']} {r['Model']} ({r['Year']})",
                axis=1
            )
            selected_label = st.selectbox(
                "Select Car to Delete", cars_df["Label"], key="delete_car_select"
            )
            selected_row = cars_df[cars_df["Label"] == selected_label].iloc[0]
            car_id = int(selected_row["CarID"])

            st.dataframe(selected_row.drop("Label").to_frame().T)

            confirm = st.checkbox(
                f"I confirm I want to delete Car #{car_id}", key="delete_car_confirm"
            )

            if st.button("Delete Car", key="delete_car_btn"):
                if confirm:
                    execute("DELETE FROM Cars WHERE CarID = ?", (car_id,))
                    st.success(f"Car #{car_id} deleted successfully!")
                else:
                    st.warning("Please tick the confirmation box before deleting.")


# ----------------------------
# RUN USE CASES
# ----------------------------
if menu == "Run Use Cases":

    st.header("Run Use Cases")
    st.caption("Manage customers and cars independently — both support add, update, and delete.")

    tab_customers, tab_cars = st.tabs(["Customer Details", "Car Details"])

    with tab_customers:
        manage_customers()

    with tab_cars:
        manage_cars()

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
