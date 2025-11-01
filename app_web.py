import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ================== DATABASE CONNECTION ==================
conn = sqlite3.connect('hospital.db', check_same_thread=False)
cursor = conn.cursor()

# ================== PAGE SETTINGS ==================
st.set_page_config(page_title="Integrated Patient Care Management Platform", page_icon="🏥", layout="wide")
st.title("🏥 Integrated Patient Care Management Platform")

# ================== GLOBAL STYLE: CENTER ALIGN TABLES ==================
st.markdown("""
<style>
/* Center align text and numbers in tables */
[data-testid="stDataFrame"] div[role="cell"],
[data-testid="stDataFrame"] div[role="columnheader"] {
    justify-content: center !important;
    text-align: center !important;
}

/* Make text color white for dark mode */
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
    color: white !important;
}

/* Remove scrollbars */
[data-testid="stDataFrame"] div[data-testid="stHorizontalBlock"] {
    overflow-x: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ================== FETCH TABLES ==================
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
all_tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']

# Emojis for better UI
emoji_map = {
    "Patient": "🧍",
    "Employee": "💼",
    "Doctor": "👨‍⚕️",
    "Nurse": "👩‍⚕️",
    "Receptionist": "💁‍♀️",
    "Room": "🏥",
    "Medicine": "💊",
    "Equipment": "⚙️",
    "Record": "📋",
    "Assigned": "🧩",
    "Attends": "🤝",
    "Maintains": "🗂️",
    "Governs": "🩺",
    "BilledFor": "💰"
}

# Sidebar menu
menu = ["🏠 Home", "📊 View Database"] + [f"{emoji_map.get(t, '📦')} {t}" for t in all_tables]
choice = st.sidebar.selectbox("Select Option", menu)

# ================== HOME PAGE ==================
if choice == "🏠 Home":
  st.markdown("""
### 👋 Welcome to the Integrated Patient Care Management Platform  

This system is designed to streamline hospital operations by integrating patient, staff, and resource management into one smart interface.  

#### 💡 Key Features:
- 🧍 **Patient Management** — Register new patients, record demographics, admission, and discharge details.  
- 👨‍⚕️ **Doctor & Staff Management** — Maintain detailed records of doctors, nurses, and receptionists with their roles and responsibilities.  
- 🏥 **Room & Facility Management** — Track room assignments, nurse supervision, and equipment maintenance.  
- 💊 **Pharmacy & Equipment Tracking** — Manage medicines, medical supplies, and hospital inventory efficiently.  
- 📋 **Medical Records** — Maintain treatment history, prescriptions, and ongoing medical records for each patient.  
- 💰 **Billing & Financials** — Generate and link bills for medicines, treatments, and room usage.  
- 📊 **Database Insights** — View, search, and analyze real-time hospital data dynamically.  

> 🩺 A one-stop platform for complete hospital information management and patient care optimization.
""", unsafe_allow_html=True)


# ================== VIEW DATABASE PAGE ==================
elif choice == "📊 View Database":
    st.subheader("📊 Dynamic Database Viewer")

    selected_table = st.selectbox("Select Table to View", all_tables)

    # Load data
    df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)

    # 🔍 Search / Filter
    search = st.text_input("🔍 Search in this table")
    if search:
        df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
        st.dataframe(
    df_filtered.style.set_properties(**{'text-align': 'center'}),
    height=300,
    use_container_width=False,
    hide_index=True
)

        st.caption(f"Showing {len(df_filtered)} matching record(s)")
    else:
        st.dataframe(
    df.style.set_properties(**{'text-align': 'center'}),
    height=300,          # 👈 limits table height
    use_container_width=False,  # 👈 prevents full-width stretch
    hide_index=True
)

        st.caption(f"Showing all {len(df)} record(s)")
        

# ================== DYNAMIC TABLE FORMS ==================
else:
    table_name = choice.split(" ", 1)[1]
    st.subheader(f"{choice} — Add New Record")

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    input_data = {}
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        is_pk = col[5] == 1

        if not is_pk:
            # Special handling for known fields
            if col_name.lower() in ["sex", "gender"]:
                input_data[col_name] = st.selectbox(f"{col_name}", ["Male", "Female", "Other"])
            elif col_name.lower() in ["dateadmitted", "datedischarged"]:
                date_val = st.date_input(f"{col_name}")
                input_data[col_name] = date_val.strftime("%Y-%m-%d")
            elif "INT" in col_type:
                input_data[col_name] = st.number_input(f"{col_name}", step=1)
            elif "REAL" in col_type or "FLOAT" in col_type:
                input_data[col_name] = st.number_input(f"{col_name}", format="%.2f")
            else:
                input_data[col_name] = st.text_input(f"{col_name}")

    # Add record button
    if st.button(f"Add Record to {table_name}"):
        if input_data:
            cols_str = ", ".join(input_data.keys())
            placeholders = ", ".join(["?"] * len(input_data))
            values = tuple(str(v) if isinstance(v, datetime) else v for v in input_data.values())

            try:
                cursor.execute(f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})", values)
                conn.commit()
                st.success(f"✅ Record added successfully to {table_name}!")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

        # Show updated table (index hidden)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        st.markdown("---")
        st.dataframe(df.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
