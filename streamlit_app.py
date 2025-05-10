import streamlit as st
import pandas as pd

st.set_page_config(page_title="Employee Absence Cost Analysis", layout="wide")

st.title("Employee Absence Cost Analysis")

# --- Sidebar: Default Settings ---
st.sidebar.header("Defaults")
default_weekly_hours = st.sidebar.number_input(
    label="Default Weekly Hours",
    value=40.0,
    min_value=0.0,
    format="%.1f"
)

# --- Sidebar: Profile Management ---
st.sidebar.header("Employee Profiles")
profile_mode = st.sidebar.radio(
    label="Profile Mode",
    options=["Single", "Batch"],
    index=0
)

# Initialize session state for profiles
if "profiles" not in st.session_state:
    st.session_state["profiles"] = []

# Batch Mode: upload CSV
df_profiles = None
if profile_mode == "Batch":
    uploaded_file = st.sidebar.file_uploader(
        label="Upload Profiles CSV",
        type=["csv"]
    )
    if uploaded_file:
        try:
            df_profiles = pd.read_csv(uploaded_file)
            st.sidebar.success("Profiles loaded from CSV.")
        except Exception as e:
            st.sidebar.error(f"Error loading CSV: {e}")
else:
    # Single Mode: input form + save
    name = st.sidebar.text_input(
        label="Employee Name",
        value="Adam Waller"
    )
    employment_type = st.sidebar.radio(
        label="Employment Type",
        options=["Hourly", "Salaried"],
        index=0
    )

    if employment_type == "Hourly":
        hourly_rate = st.sidebar.number_input(
            label="Hourly Wage ($/hr)",
            value=35.29,
            min_value=0.0,
            format="%.2f"
        )
        weekly_hours = st.sidebar.number_input(
            label="Scheduled Hours per Week",
            value=default_weekly_hours,
            min_value=0.0,
            format="%.1f"
        )
    else:
        weekly_salary = st.sidebar.number_input(
            label="Weekly Salary ($)",
            value=2000.0,
            min_value=0.0,
            format="%.2f"
        )
        weekly_hours = st.sidebar.number_input(
            label="Scheduled Hours per Week",
            value=default_weekly_hours,
            min_value=0.0,
            format="%.1f"
        )
        hourly_rate = weekly_salary / weekly_hours if weekly_hours > 0 else 0.0

    absences_per_year = st.sidebar.number_input(
        label="Average Absences per Year",
        value=6,
        min_value=0
    )
    hours_per_absence = st.sidebar.number_input(
        label="Hours Missed per Absence",
        value=(weekly_hours / 5 if weekly_hours > 0 else 0.0),
        min_value=0.0,
        format="%.1f"
    )

    num_managers = st.sidebar.number_input(
        label="Number of Managers Affected",
        value=3,
        min_value=0
    )
    manager_weekly_salary = st.sidebar.number_input(
        label="Manager Weekly Salary ($)",
        value=2000.0,
        min_value=0.0,
        format="%.2f"
    )
    manager_time_hours = st.sidebar.number_input(
        label="Manager Time per Absence (hrs)",
        value=1.0,
        min_value=0.0,
        format="%.1f"
    )

    overtime_rate = st.sidebar.number_input(
        label="Overtime/Backfill Rate ($/hr)",
        value=0.0,
        min_value=0.0,
        format="%.2f"
    )
    overtime_hours = st.sidebar.number_input(
        label="OT Hours per Absence",
        value=0.0,
        min_value=0.0,
        format="%.1f"
    )
    productivity_loss_pct = st.sidebar.number_input(
        label="Estimated Productivity Loss (%)",
        value=10.0,
        min_value=0.0,
        max_value=100.0,
        format="%.1f"
    )

    role_criticality = st.sidebar.selectbox(
        label="Role Criticality",
        options=["Low", "Medium", "High"]
    )

    if st.sidebar.button("Add Profile"):
        st.session_state["profiles"].append({
            "employee_name": name,
            "hourly_rate": hourly_rate,
            "weekly_hours": weekly_hours,
            "absences_per_year": absences_per_year,
            "hours_per_absence": hours_per_absence,
            "num_managers": num_managers,
            "manager_weekly_salary": manager_weekly_salary,
            "manager_time_hours": manager_time_hours,
            "overtime_rate": overtime_rate,
            "overtime_hours": overtime_hours,
            "productivity_loss_pct": productivity_loss_pct,
            "role_criticality": role_criticality,
            "employment_type": employment_type
        })
        st.sidebar.success(f"Profile '{name}' added.")

    if st.session_state["profiles"]:
        idx = st.sidebar.selectbox(
            label="Select Profile",
            options=list(range(len(st.session_state["profiles"]))),
            format_func=lambda i: st.session_state["profiles"][i]["employee_name"]
        )
        profile = st.session_state["profiles"][idx]
        (name, hourly_rate, weekly_hours,
         absences_per_year, hours_per_absence,
         num_managers, manager_weekly_salary,
         manager_time_hours, overtime_rate,
         overtime_hours, productivity_loss_pct,
         role_criticality, employment_type) = (
            profile["employee_name"],
            profile["hourly_rate"],
            profile["weekly_hours"],
            profile["absences_per_year"],
            profile["hours_per_absence"],
            profile["num_managers"],
            profile["manager_weekly_salary"],
            profile["manager_time_hours"],
            profile["overtime_rate"],
            profile["overtime_hours"],
            profile["productivity_loss_pct"],
            profile["role_criticality"],
            profile["employment_type"]
        )

# --- Cost Calculation Function ---
def calculate_cost(
    hourly_rate, weekly_hours, absences_per_year, hours_per_absence,
    num_managers, manager_weekly_salary, manager_time_hours,
    overtime_rate, overtime_hours, productivity_loss_pct
):
    direct_cost = hourly_rate * hours_per_absence
    manager_hourly_rate = manager_weekly_salary / weekly_hours if weekly_hours > 0 else 0.0
    manager_cost = manager_hourly_rate * manager_time_hours * num_managers
    overtime_cost = overtime_rate * overtime_hours
    productivity_loss_cost = (hourly_rate * weekly_hours) * (productivity_loss_pct / 100)
    total_per_incident = direct_cost + manager_cost + overtime_cost + productivity_loss_cost
    annualized_cost = total_per_incident * absences_per_year
    return {
        "Direct Cost (Wages)": direct_cost,
        "Manager Response Cost": manager_cost,
        "Overtime/Backfill Cost": overtime_cost,
        "Productivity Loss Cost": productivity_loss_cost,
        "Total Cost per Absence": total_per_incident,
        "Annualized Cost": annualized_cost
    }

# --- Main Display & Logic ---
if profile_mode == "Batch" and df_profiles is not None:
    results = []
    for _, row in df_profiles.iterrows():
        cost_dict = calculate_cost(
            row.get("hourly_rate", 0),
            row.get("weekly_hours", default_weekly_hours),
            row.get("absences_per_year", 0),
            row.get("hours_per_absence", 0),
            row.get("num_managers", 0),
            row.get("manager_weekly_salary", 0),
            row.get("manager_time_hours", 0),
            row.get("overtime_rate", 0),
            row.get("overtime_hours", 0),
            row.get("productivity_loss_pct", 0)
        )
        cost_dict["Employee Name"] = row.get("employee_name", "")
        results.append(cost_dict)
    df_results = pd.DataFrame(results)
    st.header("Batch Analysis Results")
    st.dataframe(df_results)

    csv = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name="absence_cost_batch.csv",
        mime="text/csv"
    )

elif profile_mode == "Single":
    st.header(f"Cost Analysis for {name}")
    cost = calculate_cost(
        hourly_rate, weekly_hours, absences_per_year, hours_per_absence,
        num_managers, manager_weekly_salary, manager_time_hours,
        overtime_rate, overtime_hours, productivity_loss_pct
    )
    df = pd.DataFrame(
        list(cost.items()), columns=["Component", "Amount ($)"]
    )
    st.table(df)
    st.write("### Cost Breakdown Chart")
    st.bar_chart(df.set_index("Component")["Amount ($)"])

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv,
        file_name=f"absence_cost_{name.replace(' ', '_')}.csv",
        mime="text/csv"
    )

    suggestions_map = {
        "High": [
            "Implement cross-training for backup support",
            "Maintain on-call backup staff",
            "Develop a formal absence-coverage protocol"
        ],
        "Medium": [
            "Encourage periodic knowledge sharing sessions",
            "Create a flexible shift swap system"
        ],
        "Low": [
            "Reassign tasks temporarily to peers",
            "Monitor absence trend for future planning"
        ]
    }
    st.write("---")
    st.subheader("Mitigation Suggestions")
    for item in suggestions_map.get(role_criticality, []):
        st.write(f"- {item}")

# --- Notes ---
st.write("---")
st.write("**Notes:**")
st.write("- Adjust inputs in the sidebar to refine your analysis.")
st.write("- For batch mode, ensure your CSV headers match the expected field names.")
