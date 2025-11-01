import mysql.connector

# ================== CONNECT TO MYSQL DATABASE ==================
conn = mysql.connector.connect(
    host="bukqxhgtpvn4hogiklcv-mysql.services.clever-cloud.com",
        user="uq1cmnqukpjg7gpa",
        password="odV2Yp3EwqIaUFpx64vN",
        database="bukqxhgtpvn4hogiklcv",
        port=3306
)
cursor = conn.cursor()
print("✅ Connected to MySQL successfully!")

# ================== CREATE DATABASE ==================
cursor.execute("CREATE DATABASE IF NOT EXISTS hospital_db")
cursor.execute("USE hospital_db")

# ================== CREATE TABLES ==================

# ---- Employee (Super class) ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Employee (
    empID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sex VARCHAR(10),
    contactNo VARCHAR(20),
    qualification VARCHAR(100),
    experience INT,
    salary FLOAT
)
""")

# ---- Doctor (ISA Employee) ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Doctor (
    doctorID INT AUTO_INCREMENT PRIMARY KEY,
    empID INT,
    doctorType ENUM('Visiting','Permanent','Trainee'),
    FOREIGN KEY (empID) REFERENCES Employee(empID)
)
""")

# ---- Nurse ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Nurse (
    nurseID INT AUTO_INCREMENT PRIMARY KEY,
    empID INT,
    appointment VARCHAR(100),
    FOREIGN KEY (empID) REFERENCES Employee(empID)
)
""")

# ---- Receptionist ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Receptionist (
    recID INT AUTO_INCREMENT PRIMARY KEY,
    empID INT,
    FOREIGN KEY (empID) REFERENCES Employee(empID)
)
""")

# ---- Room ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Room (
    roomID INT AUTO_INCREMENT PRIMARY KEY,
    roomType VARCHAR(50),
    description VARCHAR(255),
    extension VARCHAR(50)
)
""")

# ---- Medicine ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Medicine (
    medCode INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description VARCHAR(255),
    price FLOAT
)
""")

# ---- Equipment ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Equipment (
    equipCode INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255),
    price FLOAT
)
""")

# ---- Patient ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Patient (
    patientID INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    sex VARCHAR(10),
    age INT,
    contactNo VARCHAR(20),
    dateAdmitted DATE,
    dateDischarged DATE
)
""")

# ---- Record ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Record (
    recordNo INT AUTO_INCREMENT PRIMARY KEY,
    patientID INT,
    recordInfo VARCHAR(255),
    appointment VARCHAR(100),
    FOREIGN KEY (patientID) REFERENCES Patient(patientID)
)
""")

# ---- Relationship Tables ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS Assigned (
    assignID INT AUTO_INCREMENT PRIMARY KEY,
    patientID INT,
    roomID INT,
    FOREIGN KEY (patientID) REFERENCES Patient(patientID),
    FOREIGN KEY (roomID) REFERENCES Room(roomID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Attends (
    attendID INT AUTO_INCREMENT PRIMARY KEY,
    patientID INT,
    doctorID INT,
    FOREIGN KEY (patientID) REFERENCES Patient(patientID),
    FOREIGN KEY (doctorID) REFERENCES Doctor(doctorID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Maintains (
    maintainID INT AUTO_INCREMENT PRIMARY KEY,
    recID INT,
    recordNo INT,
    FOREIGN KEY (recID) REFERENCES Receptionist(recID),
    FOREIGN KEY (recordNo) REFERENCES Record(recordNo)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Governs (
    governID INT AUTO_INCREMENT PRIMARY KEY,
    nurseID INT,
    roomID INT,
    FOREIGN KEY (nurseID) REFERENCES Nurse(nurseID),
    FOREIGN KEY (roomID) REFERENCES Room(roomID)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS BilledFor (
    billID INT AUTO_INCREMENT PRIMARY KEY,
    patientID INT,
    medicineID INT,
    equipmentID INT,
    treatment VARCHAR(255),
    totalAmount FLOAT,
    FOREIGN KEY (patientID) REFERENCES Patient(patientID),
    FOREIGN KEY (medicineID) REFERENCES Medicine(medCode),
    FOREIGN KEY (equipmentID) REFERENCES Equipment(equipCode)
)
""")

conn.commit()
print("✅ All MySQL tables created successfully in 'hospital_db'!")
conn.close()
print("🚪 Connection closed.")
