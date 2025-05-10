import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Employee Absence Cost Analysis", layout="wide")

# --- Sidebar: Mode Selection ---
mode = st.sidebar.radio(
    label="Mode", options=["Single", "Batch"], index=0,
    help="Select single-employee analysis or batch analysis via CSV"
)

# --- Sidebar Inputs ---
with st.sidebar.expander("Defaults"):
    default_weekly_hours = st.number_input(
        label="Default Weekly Hours",
        value=40.0,
        min_value=0.0,
        format="%.1f",
        help="Standard work hours per week for an employee"
    )
    overhead_pct = st.number_input(
        label="Overhead Multiplier (%)",
        value=0.0,
        min_value=0.0,
        max_value=100.0,
        format="%.1f",
        help="Additional overhead or inflation percentage to apply to total costs"
    )

with st.sidebar.expander("Employee Details"):
    if mode == "Single":
        name = st.text_input(
            label="Employee Name", value="Adam Waller",
            help="Name of the employee to analyze"
        )
        employment_type = st.radio(
            label="Employment Type", options=["Hourly", "Salaried"], index=0,
            help="Choose if the employee is paid hourly or salaried"
        )
        if employment_type == "Hourly":
            hourly_rate = st.number_input(
                label="Hourly Wage ($/hr)", value=35.29, min_value=0.0, format="%.2f",
                help="Hourly wage cost to the company"
            )
            weekly_hours = st.number_input(
                label="Scheduled Hours per Week", value=default_weekly_hours, min_value=0.0, format="%.1f",
                help="Number of hours scheduled per week"
            )
        else:
            weekly_salary = st.number_input(
                label="Weekly Salary ($)", value=2000.0, min_value=0.0, format="%.2f",
                help="Total weekly salary cost to the company"
            )
            weekly_hours = st.number_input(
                label="Scheduled Hours per Week", value=default_weekly_hours, min_value=0.0, format="%.1f",
                help="Number of hours scheduled per week"
            )
            hourly_rate = weekly_salary / weekly_hours if weekly_hours > 0 else 0.0

with st.sidebar.expander("Absence Pattern"):
    absences_per_year = st.number_input(
        label="Average Absences per Year", value=6, min_value=0,
        help="Historical average of unplanned absences per year"
    )
    hours_per_absence = st.number_input(
        label="Hours Missed per Absence", value=(weekly_hours/5), min_value=0.0, format="%.1f",
        help="Typical hours missed when absent"
    )

with st.sidebar.expander("Management Impact"):
    num_managers = st.number_input(
        label="Managers Affected", value=3, min_value=0,
        help="Number of managers who respond to an absence"
    )
    manager_weekly_salary = st.number_input(
        label="Manager Weekly Salary ($)", value=2000.0, min_value=0.0, format="%.2f",
        help="Weekly salary cost per manager"
    )
    manager_time_hours = st.number_input(
        label="Manager Time per Absence (hrs)", value=1.0, min_value=0.0, format="%.1f",
        help="Hours managers spend adjusting workflows"
    )

with st.sidebar.expander("Additional Costs"):
    overtime_rate = st.number_input(
        label="Overtime/Backfill Rate ($/hr)", value=0.0, min_value=0.0, format="%.2f",
        help="Hourly rate for overtime or replacement workers"
    )
    overtime_hours = st.number_input(
        label="OT Hours per Absence", value=0.0, min_value=0.0, format="%.1f",
        help="Overtime hours incurred due to absence"
    )
    productivity_loss_pct = st.number_input(
        label="Productivity Loss (%)", value=10.0, min_value=0.0, max_value=100.0, format="%.1f",
        help="Estimated percent productivity lost"
    )
    idle_equipment_rate = st.number_input(
        label="Idle Equipment Cost Rate ($/hr)", value=0.0, min_value=0.0, format="%.2f",
        help="Hourly cost of equipment idling"
    )
    idle_hours = st.number_input(
        label="Equipment Downtime per Absence (hrs)", value=0.0, min_value=0.0, format="%.1f",
        help="Hours equipment is idle due to site shutdown"
    )

role_criticality = st.selectbox(
    label="Role Criticality", options=["Low","Medium","High"],
    help="Criticality of employee role to site operations"
)

# Load CSV with caching
df_profiles = None
if mode == "Batch":
    uploaded = st.sidebar.file_uploader("Upload Profiles CSV for Batch Analysis", type=["csv"])
    @st.cache_data
    def load_csv(file):
        return pd.read_csv(file)
    if uploaded:
        df_profiles = load_csv(uploaded)

# Cost function and overhead application
def apply_overhead(cost, pct):
    return cost * (1 + pct/100)

@st.cache_data
def calculate_cost(
    hourly_rate, weekly_hours, absences_per_year, hours_per_absence,
    num_managers, manager_weekly_salary, manager_time_hours,
    overtime_rate, overtime_hours, productivity_loss_pct,
    idle_equipment_rate, idle_hours, overhead_pct
):
    direct_cost = hourly_rate * hours_per_absence
    manager_hourly_rate = manager_weekly_salary / weekly_hours if weekly_hours > 0 else 0.0
    manager_cost = manager_hourly_rate * manager_time_hours * num_managers
    overtime_cost = overtime_rate * overtime_hours
    productivity_loss_cost = (hourly_rate*weekly_hours)*(productivity_loss_pct/100)
    equipment_idle_cost = idle_equipment_rate * idle_hours
    total = direct_cost + manager_cost + overtime_cost + productivity_loss_cost + equipment_idle_cost
    total_overhead = apply_overhead(total, overhead_pct)
    annualized = total_overhead * absences_per_year
    return {
        "Total per Absence": total_overhead,
        "Annualized Cost": annualized,
        "Direct Cost": direct_cost,
        "Manager Cost": manager_cost,
        "Overtime Cost": overtime_cost,
        "Productivity Loss Cost": productivity_loss_cost,
        "Equipment Idle Cost": equipment_idle_cost
    }

st.header("Employee Absence Cost Analysis")

if mode == "Single":
    cost = calculate_cost(
        hourly_rate, weekly_hours, absences_per_year, hours_per_absence,
        num_managers, manager_weekly_salary, manager_time_hours,
        overtime_rate, overtime_hours, productivity_loss_pct,
        idle_equipment_rate, idle_hours, overhead_pct
    )
    # KPI metrics
    k1, k2 = st.columns(2)
    k1.metric("Cost per Absence", f"${cost['Total per Absence']:.2f}")
    k2.metric("Annualized Cost", f"${cost['Annualized Cost']:.2f}")
    # Results table & charts
    df = pd.DataFrame({"Component": list(cost.keys()), "Amount": list(cost.values())})
    st.dataframe(df)
    # Pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(df['Amount'], labels=df['Component'], autopct='%1.1f%%')
    ax1.axis('equal')
    st.pyplot(fig1)
    # Bar chart
    st.bar_chart(df.set_index('Component')['Amount'])
    # CSV export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Single Result as CSV", data=csv, file_name=f"{name}_cost.csv")

elif mode == "Batch" and df_profiles is not None:
    results = []
    for _, row in df_profiles.iterrows():
        c = calculate_cost(
            row['hourly_rate'], row['weekly_hours'], row['absences_per_year'], row['hours_per_absence'],
            row['num_managers'], row['manager_weekly_salary'], row['manager_time_hours'],
            row['overtime_rate'], row['overtime_hours'], row['productivity_loss_pct'],
            row['idle_equipment_rate'], row['idle_hours'], overhead_pct
        )
        c['Employee'] = row['employee_name']
        results.append(c)
    dfb = pd.DataFrame(results)
    # Batch KPIs
    b1, b2 = st.columns(2)
    b1.metric("Avg Cost per Absence", f"${dfb['Total per Absence'].mean():.2f}")
    b2.metric("Total Annualized Cost", f"${dfb['Annualized Cost'].sum():.2f}")
    st.dataframe(dfb)
    # Bar chart per employee
    st.bar_chart(dfb.set_index('Employee')['Total per Absence'])
    # Download
    csvb = dfb.to_csv(index=False).encode('utf-8')
    st.download_button("Download Batch Results as CSV", data=csvb, file_name="batch_costs.csv")
