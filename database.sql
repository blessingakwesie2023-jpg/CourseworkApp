PRAGMA foreign_keys = ON;

-- Create Staff table (created first since other tables reference it)
CREATE TABLE Staff (
    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    JobTitle VARCHAR(100),
    Phone VARCHAR(20),
    Email VARCHAR(150)
);

-- Create Cars table
CREATE TABLE Cars (
    CarID INTEGER PRIMARY KEY AUTOINCREMENT,
    Make VARCHAR(100) NOT NULL,
    Model VARCHAR(100) NOT NULL,
    Year INT CHECK (Year > 1980 AND Year <= 2100),
    Colour VARCHAR(50),
    Mileage DECIMAL(12, 2),
    FuelType VARCHAR(50),
    Transmission VARCHAR(50),
    Price DECIMAL(12, 2) CHECK (Price > 0),
    Status VARCHAR(50) CHECK (Status IN ('Available', 'Sold')),
    PurchaseDate DATE
);

-- Create the Customers table
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    City VARCHAR(100),
    Postcode VARCHAR(10),
    Phone VARCHAR(20),
    Email VARCHAR(150)
);

-- Create Sales table connecting Cars, Customers, Staff
CREATE TABLE Sales (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    CarID INT REFERENCES Cars(CarID) ON DELETE SET NULL,
    CustomerID INT REFERENCES Customers(CustomerID) ON DELETE SET NULL,
    StaffID INT REFERENCES Staff(StaffID) ON DELETE SET NULL,
    SaleDate DATE DEFAULT CURRENT_DATE,
    SalePrice DECIMAL(12, 2) CHECK (SalePrice > 0),
    PaymentMethod VARCHAR(50)
);

-- Create Services table
CREATE TABLE Services (
    ServiceID INTEGER PRIMARY KEY AUTOINCREMENT,
    CarID INT REFERENCES Cars(CarID) ON DELETE CASCADE,
    StaffID INT REFERENCES Staff(StaffID) ON DELETE SET NULL,
    ServiceDate DATE DEFAULT CURRENT_DATE,
    ServiceType VARCHAR(50),
    ServiceCost DECIMAL(12, 2) CHECK (ServiceCost >= 0),
    Notes TEXT
);

-- Insert Staff Data
INSERT INTO Staff (StaffID, FirstName, LastName, JobTitle, Phone, Email)
VALUES 
(1, 'Kenneth', 'Davis', 'Sales Manager', '+44 7759 388389', 'kenneth.davis@cardealer.co.uk'),
(2, 'Jessica', 'Anderson', 'Service Manager', '+44 7754 207473', 'jessica.anderson@cardealer.co.uk'),
(3, 'Carol', 'Mitchell', 'New Car Sales', '+44 7089 719176', 'carol.mitchell@cardealer.co.uk'),
(4, 'Margaret', 'Williams', 'Sales Manager', '+44 7095 329258', 'margaret.williams@cardealer.co.uk'),
(5, 'Joseph', 'Allen', 'Technician', '+44 7027 688508', 'joseph.allen@cardealer.co.uk'),
(6, 'Richard', 'Rivera', 'New Car Sales', '+44 7429 331148', 'richard.rivera@cardealer.co.uk'),
(7, 'Mark', 'Nguyen', 'Detailer', '+44 7828 106814', 'mark.nguyen@cardealer.co.uk'),
(8, 'David', 'Hall', 'Valeter', '+44 7348 391369', 'david.hall@cardealer.co.uk'),
(9, 'Elizabeth', 'Wilson', 'Parts Manager', '+44 7104 197251', 'elizabeth.wilson@cardealer.co.uk'),
(10, 'Matthew', 'Miller', 'Accountant', '+44 7867 460663', 'matthew.miller@cardealer.co.uk'),
(11, 'Joshua', 'Taylor', 'Sales Executive', '+44 7747 581741', 'joshua.taylor@cardealer.co.uk'),
(12, 'Paul', 'Davis', 'Receptionist', '+44 7080 678856', 'paul.davis@cardealer.co.uk'),
(13, 'Charles', 'Green', 'Technician', '+44 7906 479201', 'charles.green@cardealer.co.uk'),
(14, 'Andrew', 'Gonzalez', 'Senior Sales Executive', '+44 7046 793384', 'andrew.gonzalez@cardealer.co.uk'),
(15, 'Joseph', 'Jackson', 'Senior Sales Executive', '+44 7875 344098', 'joseph.jackson@cardealer.co.uk'),
(16, 'Michael', 'Harris', 'Detailer', '+44 7464 766563', 'michael.harris@cardealer.co.uk'),
(17, 'Lisa', 'Hernandez', 'Accountant', '+44 7363 319684', 'lisa.hernandez@cardealer.co.uk'),
(18, 'Kevin', 'Moore', 'Senior Sales Executive', '+44 7623 765822', 'kevin.moore@cardealer.co.uk'),
(19, 'David', 'Wright', 'Service Advisor', '+44 7167 584714', 'david.wright@cardealer.co.uk'),
(20, 'Matthew', 'Moore', 'New Car Sales', '+44 7224 817870', 'matthew.moore@cardealer.co.uk'),
(21, 'Christopher', 'Brown', 'Service Advisor', '+44 7841 133659', 'christopher.brown@cardealer.co.uk'),
(22, 'Christopher', 'Sanchez', 'Detailer', '+44 7067 321231', 'christopher.sanchez@cardealer.co.uk'),
(23, 'Andrew', 'Rivera', 'Parts Manager', '+44 7217 787277', 'andrew.rivera@cardealer.co.uk'),
(24, 'Ashley', 'Sanchez', 'Warranty Administrator', '+44 7146 377746', 'ashley.sanchez@cardealer.co.uk'),
(25, 'William', 'Thomas', 'New Car Sales', '+44 7551 375504', 'william.thomas@cardealer.co.uk');

-- Insert Customers Data
INSERT INTO Customers (CustomerID, FirstName, LastName, Address, City, Postcode, Phone, Email)
VALUES 
(1, 'Melissa', 'Nguyen', '110 Maple Drive', 'Kilmarnock', 'EH54 6AA', '+44 7224 245051', 'melissa.nguyen66@gmail.com'),
(2, 'Ashley', 'Garcia', '194 High Street', 'Dundee', 'IV1 1AA', '+44 7642 267753', 'ashley.garcia88@gmail.com'),
(3, 'Margaret', 'Hill', '17 Oak Avenue', 'Kilmarnock', 'ML6 1AA', '+44 7479 654816', 'margaret.hill33@gmail.com'),
(4, 'Emily', 'Smith', '175 Victoria Road', 'Dundee', 'M1 1AA', '+44 7906 663054', 'emily.smith97@gmail.com'),
(5, 'Sarah', 'Adams', '88 High Street', 'Paisley', 'KA7 1AA', '+44 7161 575763', 'sarah.adams1@gmail.com'),
(6, 'George', 'Campbell', '68 Maple Drive', 'Bristol', 'FK8 1AA', '+44 7519 211579', 'george.campbell81@gmail.com'),
(7, 'Karen', 'Green', '130 Maple Drive', 'Perth', 'IV1 1AA', '+44 7382 899550', 'karen.green21@gmail.com'),
(8, 'Paul', 'King', '236 High Street', 'Airdrie', 'G74 1AA', '+44 7500 120422', 'paul.king15@gmail.com'),
(9, 'Lisa', 'Martin', '62 High Street', 'Cumbernauld', 'PA15 1AA', '+44 7969 182582', 'lisa.martin11@gmail.com'),
(10, 'George', 'Young', '209 High Street', 'Bristol', 'ML5 1AA', '+44 7784 231869', 'george.young17@gmail.com'),
(11, 'Kevin', 'Walker', '243 Maple Drive', 'Stirling', 'ML3 6AA', '+44 7540 736059', 'kevin.walker55@gmail.com'),
(12, 'Susan', 'Wright', '194 Victoria Road', 'Liverpool', 'PH1 1AA', '+44 7730 426858', 'susan.wright52@gmail.com'),
(13, 'Kevin', 'Adams', '96 Oak Avenue', 'Motherwell', 'DG1 1AA', '+44 7123 359947', 'kevin.adams29@gmail.com'),
(14, 'Robert', 'Perez', '6 Maple Drive', 'Coatbridge', 'G67 2BB', '+44 7602 330914', 'robert.perez1@gmail.com'),
(15, 'Robert', 'Rivera', '162 High Street', 'Cumbernauld', 'AB10 1AA', '+44 7927 132938', 'robert.rivera43@gmail.com'),
(16, 'Robert', 'Allen', '61 Church Lane', 'Manchester', 'FK1 1AA', '+44 7219 665427', 'robert.allen17@gmail.com'),
(17, 'George', 'Torres', '148 Oak Avenue', 'Cumbernauld', 'S1 1AA', '+44 7484 946721', 'george.torres53@gmail.com'),
(18, 'Richard', 'Miller', '25 Victoria Road', 'Ayr', 'EH54 6AA', '+44 7433 531071', 'richard.miller60@gmail.com'),
(19, 'George', 'Brown', '173 Victoria Road', 'Birmingham', 'DD1 1AA', '+44 7062 522179', 'george.brown94@gmail.com'),
(20, 'Nancy', 'Miller', '64 Main Road', 'Perth', 'ML5 1AA', '+44 7459 246991', 'nancy.miller55@gmail.com'),
(21, 'Barbara', 'Moore', '119 Main Road', 'Aberdeen', 'DG1 1AA', '+44 7827 997546', 'barbara.moore71@gmail.com'),
(22, 'Michael', 'Brown', '167 Maple Drive', 'Glasgow', 'AB10 1AA', '+44 7948 890170', 'michael.brown31@gmail.com'),
(23, 'David', 'Clark', '125 Oak Avenue', 'Perth', 'KA1 1AA', '+44 7924 161483', 'david.clark22@gmail.com'),
(24, 'Matthew', 'Smith', '100 Church Lane', 'Sheffield', 'S1 1AA', '+44 7465 399105', 'matthew.smith55@gmail.com'),
(25, 'Brian', 'Campbell', '201 Maple Drive', 'Manchester', 'L1 1AA', '+44 7498 262316', 'brian.campbell25@gmail.com');

-- Insert Cars Data
INSERT INTO Cars (CarID, Make, Model, Year, Colour, Mileage, FuelType, Transmission, Price, Status, PurchaseDate)
VALUES 
(1, 'Honda', 'Civic', 2021, 'Black', 18979, 'Hybrid', 'Manual', 10505.69, 'Sold', '2024-06-02'),
(2, 'Hyundai', 'i30', 2020, 'Black', 136124, 'Petrol', 'Manual', 11240.85, 'Sold', '2023-04-10'),
(3, 'Volkswagen', 'Golf', 2024, 'White', 67543, 'Petrol', 'Manual', 25269, 'Sold', '2024-09-19'),
(4, 'Kia', 'Ceed', 2023, 'Red', 56545, 'Hybrid', 'Manual', 19124.58, 'Sold', '2023-06-14'),
(5, 'Honda', 'CR-V', 2025, 'Blue', 22016, 'Petrol', 'Automatic', 33346.37, 'Sold', '2024-08-29'),
(6, 'BMW', '3 Series', 2019, 'Orange', 58877, 'Hybrid', 'Manual', 45830.38, 'Sold', '2023-04-11'),
(7, 'Volkswagen', 'Golf', 2023, 'Red', 44352, 'Electric', 'Automatic', 32967.11, 'Sold', '2025-05-06'),
(8, 'Kia', 'Ceed', 2018, 'Orange', 81480, 'Petrol', 'Manual', 19078.64, 'Sold', '2023-05-20'),
(9, 'Renault', 'Captur', 2020, 'Red', 76860, 'Diesel', 'Automatic', 16643.89, 'Sold', '2024-11-10'),
(10, 'Volkswagen', 'Passat', 2025, 'Red', 16316, 'Petrol', 'Automatic', 41673.92, 'Sold', '2023-03-17'),
(11, 'Toyota', 'Corolla', 2023, 'Silver', 71670, 'Diesel', 'Automatic', 30567.22, 'Sold', '2024-04-12'),
(12, 'Renault', 'Captur', 2018, 'White', 22724, 'Diesel', 'Manual', 41883.8, 'Sold', '2024-09-18'),
(13, 'Renault', 'Captur', 2020, 'Green', 36409, 'Petrol', 'Automatic', 23086.06, 'Sold', '2025-04-25'),
(14, 'Toyota', 'Camry', 2023, 'Grey', 68412, 'Petrol', 'Automatic', 39704.65, 'Sold', '2024-03-22'),
(15, 'Mercedes-Benz', 'C-Class', 2021, 'Silver', 49413, 'Electric', 'Manual', 15674.43, 'Sold', '2024-01-06'),
(16, 'Hyundai', 'Tucson', 2021, 'Red', 44732, 'Petrol', 'Automatic', 43386.67, 'Sold', '2024-05-26'),
(17, 'Audi', 'Q5', 2021, 'Yellow', 94660, 'Hybrid', 'Manual', 17416.94, 'Sold', '2024-12-06'),
(18, 'Audi', 'A4', 2024, 'Blue', 76034, 'Petrol', 'Automatic', 22545.85, 'Sold', '2024-07-05'),
(19, 'Tesla', 'Model Y', 2023, 'Black', 33236, 'Hybrid', 'Manual', 31723.59, 'Sold', '2023-10-29'),
(20, 'Toyota', 'Camry', 2019, 'Brown', 116918, 'Hybrid', 'Automatic', 25955.76, 'Sold', '2024-07-07'),
(21, 'BMW', '5 Series', 2024, 'Brown', 52828, 'Hybrid', 'Manual', 36851.41, 'Available', '2023-02-01'),
(22, 'Kia', 'Ceed', 2021, 'Blue', 116062, 'Petrol', 'Automatic', 33426.22, 'Available', '2024-12-10'),
(23, 'BMW', '5 Series', 2022, 'Orange', 84077, 'Electric', 'Automatic', 24596.02, 'Available', '2023-11-29'),
(24, 'Renault', 'Captur', 2020, 'Grey', 113217, 'Electric', 'Manual', 33120.6, 'Available', '2023-12-05'),
(25, 'Tesla', 'Model Y', 2018, 'Red', 78212, 'Diesel', 'Automatic', 39930.35, 'Available', '2024-10-13');

-- Insert Sales Data
INSERT INTO Sales (SaleID, CarID, CustomerID, StaffID, SaleDate, SalePrice, PaymentMethod)
VALUES 
(1, 1, 21, 11, '2024-10-04', 9990.12, 'Credit Card'),
(2, 2, 17, 16, '2023-05-28', 10860, 'Finance'),
(3, 3, 17, 22, '2025-03-05', 24342.85, 'Cash'),
(4, 4, 25, 8, '2023-12-08', 18010.18, 'Credit Card'),
(5, 5, 5, 1, '2024-09-14', 31250.18, 'Bank Transfer'),
(6, 6, 20, 25, '2023-05-04', 43624.98, 'Lease'),
(7, 7, 7, 23, '2025-08-17', 31470.61, 'Credit Card'),
(8, 8, 5, 21, '2023-05-26', 18744.5, 'Cash'),
(9, 9, 25, 14, '2025-01-10', 15517.3, 'Lease'),
(10, 10, 15, 2, '2023-08-11', 39066.96, 'Cash'),
(11, 11, 15, 5, '2024-08-13', 29550.26, 'Lease'),
(12, 12, 20, 11, '2025-01-14', 40329.31, 'Lease'),
(13, 13, 14, 18, '2025-08-22', 22689.09, 'Bank Transfer'),
(14, 14, 15, 9, '2024-05-29', 38862.53, 'Finance'),
(15, 15, 25, 25, '2024-05-23', 14952.18, 'Credit Card'),
(16, 16, 9, 15, '2024-06-19', 42082.82, 'Credit Card'),
(17, 17, 9, 11, '2025-03-02', 17112.35, 'Cash'),
(18, 18, 5, 5, '2024-09-07', 21346.69, 'Credit Card'),
(19, 19, 23, 7, '2023-11-19', 30106.98, 'Finance'),
(20, 20, 18, 15, '2024-10-26', 23992.43, 'Bank Transfer');

-- Insert Services Data
INSERT INTO Services (ServiceID, CarID, StaffID, ServiceDate, ServiceType, ServiceCost, Notes)
VALUES 
(1, 13, 25, '2025-08-31', 'Coolant Flush', 80.26, 'Customer satisfied with service quality.'),
(2, 16, 1, '2025-01-05', 'Battery Replacement', 1405.02, 'Customer satisfied with service quality.'),
(3, 18, 24, '2025-07-23', 'Transmission Service', 1133.87, 'Full inspection passed. All systems operational.'),
(4, 16, 8, '2024-10-16', 'Spark Plug Replacement', 921.58, 'Customer satisfied with service quality.'),
(5, 11, 22, '2025-02-28', 'Coolant Flush', 342.91, 'Additional recommendation: brake pads due in 3 months.'),
(6, 5, 20, '2025-07-10', 'Oil Change', 1682.01, 'Routine maintenance completed successfully.'),
(7, 3, 21, '2025-03-24', 'Brake Replacement', 1609.67, 'Replaced worn components. Advised follow-up in 6 months.'),
(8, 2, 9, '2025-02-02', 'Air Filter Change', 427.05, 'Performed as per manufacturer schedule.'),
(9, 11, 25, '2025-02-02', 'Battery Replacement', 1402.38, 'Customer satisfied with service quality.'),
(10, 9, 3, '2025-05-06', 'Oil Change', 1396.99, 'Routine maintenance completed successfully.'),
(11, 12, 8, '2025-11-06', 'Full Service', 1455.13, 'Routine maintenance completed successfully.'),
(12, 25, 1, '2024-09-20', 'Tyre Replacement', 1559.81, 'Replaced worn components. Advised follow-up in 6 months.'),
(13, 8, 5, '2025-05-09', 'MOT Test', 251.47, 'Full inspection passed. All systems operational.'),
(14, 15, 23, '2024-09-29', 'Transmission Service', 710.86, 'Customer reported unusual noise; issue resolved.'),
(15, 25, 6, '2024-11-24', 'Full Service', 1089.53, 'Minor oil leak fixed. No further issues detected.'),
(16, 19, 22, '2025-01-29', 'Spark Plug Replacement', 1744.35, 'Full inspection passed. All systems operational.'),
(17, 3, 19, '2025-10-14', 'Tyre Replacement', 228.93, 'Minor oil leak fixed. No further issues detected.'),
(18, 22, 20, '2024-05-13', 'Transmission Service', 1820.84, 'Routine maintenance completed successfully.'),
(19, 12, 18, '2025-03-24', 'MOT Test', 713.88, 'Performed as per manufacturer schedule.'),
(20, 1, 14, '2025-05-26', 'Full Service', 827.51, 'Performed as per manufacturer schedule.'),
(21, 21, 15, '2024-06-15', 'Spark Plug Replacement', 362.93, 'Minor oil leak fixed. No further issues detected.'),
(22, 20, 18, '2025-05-20', 'Timing Belt Service', 831.21, 'Performed as per manufacturer schedule.'),
(23, 11, 8, '2024-04-08', 'Battery Replacement', 1636.34, 'Full inspection passed. All systems operational.'),
(24, 25, 15, '2025-08-16', 'Wheel Alignment', 1251.08, 'Performed as per manufacturer schedule.'),
(25, 1, 16, '2024-12-08', 'Brake Replacement', 925.03, 'Performed as per manufacturer schedule.');

-- Additional Services Data (2026 entries)
INSERT INTO Services (ServiceID, CarID, StaffID, ServiceDate, ServiceType, ServiceCost, Notes)
VALUES 
(26, 21, 8, '2026-08-15', 'Coolant Flush', 80.26, 'Customer satisfied with service quality.'), 
(27, 23, 19, '2026-09-01', 'Battery Replacement', 1405.02, 'Customer satisfied with service quality.'), 
(28, 24, 22, '2026-10-07', 'Transmission Service', 1133.87, 'Full inspection passed. All systems operational.'), 
(29, 25, 15, '2026-11-12', 'Spark Plug Replacement', 921.58, 'Customer satisfied with service quality.'), 
(30, 20, 17, '2026-12-20', 'Oil Change', 1682.01, 'Routine maintenance completed successfully.'), 
(31, 19, 14, '2026-08-25', 'Air Filter Change', 427.05, 'Performed as per manufacturer schedule.'), 
(32, 22, 16, '2026-09-29', 'Battery Replacement', 1402.38, 'Customer satisfied with service quality.'), 
(33, 23, 5, '2026-10-14', 'Oil Change', 1396.99, 'Routine maintenance completed successfully.'), 
(34, 24, 21, '2026-11-28', 'Full Service', 1455.13, 'Routine maintenance completed successfully.'), 
(35, 25, 7, '2026-12-19', 'Spark Plug Replacement', 1744.35, 'Customer reported unusual noise; issue resolved.');