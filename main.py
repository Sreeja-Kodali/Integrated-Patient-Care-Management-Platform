import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ========================= DATABASE CONNECTION =========================
def get_connection():
    return sqlite3.connect("hospital.db")

# ========================= PAGE CONFIG =========================
st.set_page_config(
    page_title="🏥 Hospital Management System",
    page_icon=None,
    layout="wide"
)

# ========================= REMOVE STREAMLIT ICON =========================
st.markdown("""
    <head>
        <link rel="shortcut icon" href="data:image/x-icon;," type="image/x-icon">
    </head>
""", unsafe_allow_html=True)

# ========================= TITLE =========================
st.markdown("""
    <h2 style='text-align:center; color:white; margin-top:0;'>
        🏥 Integrated Patient Care Management Platform
    </h2>
    <hr>
""", unsafe_allow_html=True)

# ========================= TAB NAVIGATION =========================
tab1, tab2 = st.tabs(["🧩 Add / Manage Data", "📊 View Database"])

# ========================= AUTO-DETECT TABLES =========================
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [t[0] for t in cursor.fetchall()]

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

# ========================= TAB 1: ADD / MANAGE DATA =========================
with tab1:
    st.subheader("🧩 Add / Manage Data")

    if tables:
        table_choice = st.selectbox("Choose a Table", [f"{emoji_map.get(t, '')} {t}" for t in tables])
        table_name = table_choice.split(" ", 1)[-1]

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        st.markdown(f"### ✍️ Add Record to **{table_name}** Table")

        if columns:
            inputs = {}
            for col in columns:
                col_name = col[1]
                col_type = (col[2] or "").upper()

                # Skip auto-increment primary key fields
                if col[5] == 1 or col_name.lower().endswith("id"):
                    continue

                # ---- Custom Inputs ----
                if col_name.lower() in ["sex", "gender"]:
                    inputs[col_name] = st.selectbox(f"Select {col_name}", ["Male", "Female", "Other"])
                elif col_name.lower() in ["dateadmitted", "datedischarged"]:
                    date_val = st.date_input(f"Select {col_name}")
                    inputs[col_name] = date_val.strftime("%Y-%m-%d")
                elif "INT" in col_type:
                    inputs[col_name] = st.number_input(f"{col_name}", step=1)
                elif "REAL" in col_type or "FLOAT" in col_type:
                    inputs[col_name] = st.number_input(f"{col_name}", format="%.2f")
                else:
                    inputs[col_name] = st.text_input(f"Enter {col_name}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Add Record"):
                    if not any(inputs.values()):
                        st.warning("⚠️ Please enter at least one field before adding.")
                    else:
                        placeholders = ", ".join(["?"] * len(inputs))
                        cols = ", ".join(inputs.keys())
                        values = list(inputs.values())
                        try:
                            cursor.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", values)
                            conn.commit()
                            st.success(f"✅ Record added successfully to {table_name}!")
                        except Exception as e:
                            st.error(f"⚠️ Error inserting into {table_name}: {e}")

            with col2:
                if st.button(f"🗑️ Clear All Records in {table_name}"):
                    cursor.execute(f"DELETE FROM {table_name}")
                    conn.commit()
                    st.warning(f"⚠️ All records deleted from {table_name}")

    else:
        st.error("No tables found in database. Please run main.py first!")

# ========================= TAB 2: VIEW DATABASE =========================
with tab2:
    st.subheader("📊 View Database")

    if tables:
        st.markdown("### 📋 Total Records in Each Table")
        summary_data = []
        for t in tables:
            try:
                count = pd.read_sql_query(f"SELECT COUNT(*) AS c FROM {t}", conn)["c"][0]
                summary_data.append({"Table": f"{emoji_map.get(t, '')} {t}", "Total Records": count})
            except Exception:
                pass

        if summary_data:
            df_summary = pd.DataFrame(summary_data)

            # ✅ Center align all table cells and prevent scroll
            st.markdown("""
                <style>
                    .dataframe td, .dataframe th {
                        text-align: center !important;
                        vertical-align: middle !important;
                        color: white !important;
                    }
                    th {
                        background-color: #0B5345 !important;
                        font-weight: bold;
                        text-align: center !important;
                    }
                    [data-testid="stDataFrame"] div[data-testid="stHorizontalBlock"] {
                        overflow-x: hidden !important;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.dataframe(df_summary, use_container_width=True, hide_index=True)

        st.markdown("---")

        view_choice = st.selectbox(
            "Select Table to View",
            [f"{emoji_map.get(t, '')} {t}" for t in tables],
            key="view"
        )
        view_table = view_choice.split(" ", 1)[-1]

        try:
            df = pd.read_sql_query(f"SELECT * FROM {view_table}", conn)
            search = st.text_input("🔍 Search records by keyword")
            if search:
                df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.success(f"✅ Showing {len(df)} record(s) from {view_table}")
        except Exception as e:
            st.error(f"⚠️ Could not fetch data: {e}")

    else:
        st.error("No tables found in database.")

conn.close()
