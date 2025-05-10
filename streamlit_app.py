import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Employee Absence Cost Analysis", layout="wide")

# --- Sidebar: Mode Selection ---
mode = st.sidebar.radio(
    label="Mode", options=["Single", "Batch"], index=0,
    help="Select single-employee analysis or batch analysis via CSV"
)

# --- Sidebar Inputs ---
with st.sidebar.expander("Defaults"):
    default_weekly_hours = st.number_input(
        label="Default Weekly Hours", value=40.0, min_value=0.0, format="%.1f",
        help="Standard work hours per week for an employee"
    )
    overhead_pct = st.number_input(
        label="Overhead Multiplier (%)", value=0.0, min_value=0.0, max_value=100.0, format="%.1f",
        help="Additional overhead percentage to apply to total costs"
    )

with st.sidebar.expander("Employee Details"):
    if mode == "Single":
        name = st.text_input(label="Employee Name", value="Adam Waller", help="Employee to analyze")
        employment_type = st.radio(
            label="Employment Type", options=["Hourly","Salaried"], index=0,
            help="How the employee is compensated"
        )
        if employment_type == "Hourly":
            hourly_rate = st.number_input(
                label="Hourly Rate ($/hr)", value=35.29, min_value=0.0, format="%.2f",
                help="Cost per hour"
            )
            weekly_hours = st.number_input(
                label="Scheduled Hours/Week", value=default_weekly_hours, min_value=0.0, format="%.1f",
                help="Typical weekly hours"
            )
        else:
            weekly_salary = st.number_input(
                label="Weekly Salary ($)", value=2000.0, min_value=0.0, format="%.2f",
                help="Cost per week"
            )
            weekly_hours = st.number_input(
                label="Scheduled Hours/Week", value=default_weekly_hours, min_value=0.0, format="%.1f",
                help="Typical weekly hours"
            )
            hourly_rate = weekly_salary/weekly_hours if weekly_hours>0 else 0.0

with st.sidebar.expander("Absence Pattern"):
    absences_per_year = st.number_input(
        label="Absences per Year", value=6, min_value=0,
        help="Historical unplanned absences per year"
    )
    hours_per_absence = st.number_input(
        label="Hours Missed/Absence", value=(weekly_hours/5), min_value=0.0, format="%.1f",
        help="Hours lost per absence"
    )

with st.sidebar.expander("Management Impact"):
    num_managers = st.number_input(
        label="Managers Affected", value=3, min_value=0,
        help="Managers covering the absence"
    )
    manager_weekly_salary = st.number_input(
        label="Mgr Weekly Salary ($)", value=2000.0, min_value=0.0, format="%.2f",
        help="Cost per manager per week"
    )
    manager_time_hours = st.number_input(
        label="Mgr Time/Absence (hrs)", value=1.0, min_value=0.0, format="%.1f",
        help="Hours each manager spends"
    )

with st.sidebar.expander("Additional Costs"):
    overtime_rate = st.number_input(
        label="Overtime Rate ($/hr)", value=0.0, min_value=0.0, format="%.2f",
        help="Backfill hourly cost"
    )
    overtime_hours = st.number_input(
        label="OT Hours/Absence", value=0.0, min_value=0.0, format="%.1f",
        help="Overtime hours needed"
    )
    productivity_loss_pct = st.number_input(
        label="Prod Loss (%)", value=10.0, min_value=0.0, max_value=100.0, format="%.1f",
        help="Estimated productivity loss"
    )
    idle_equipment_rate = st.number_input(
        label="Idle Equip Rate ($/hr)", value=0.0, min_value=0.0, format="%.2f",
        help="Cost of idle equipment"
    )
    idle_hours = st.number_input(
        label="Idle Hours/Absence", value=0.0, min_value=0.0, format="%.1f",
        help="Equipment downtime hours"
    )

role_criticality = st.selectbox(label="Role Criticality", options=["Low","Medium","High"],
    help="Role's operational importance"
)

# CSV Loading
df_profiles=None
if mode=="Batch":
    uploaded=st.sidebar.file_uploader("Upload profiles CSV",type=["csv"])
    @st.cache_data
    def load_csv(f): return pd.read_csv(f)
    if uploaded: df_profiles=load_csv(uploaded)

# Cost functions
@st.cache_data
def calculate_cost(
    hourly_rate, weekly_hours, absences_per_year, hours_per_absence,
    num_managers, manager_weekly_salary, manager_time_hours,
    overtime_rate, overtime_hours, productivity_loss_pct,
    idle_equipment_rate, idle_hours, overhead_pct
):
    direct=hourly_rate*hours_per_absence
    mgr_hr=manager_weekly_salary/weekly_hours if weekly_hours>0 else 0
    mgr_cost=mgr_hr*manager_time_hours*num_managers
    ot_cost=overtime_rate*overtime_hours
    prod_cost=(hourly_rate*weekly_hours)*(productivity_loss_pct/100)
    eq_cost=idle_equipment_rate*idle_hours
    total=direct+mgr_cost+ot_cost+prod_cost+eq_cost
    total_overhead=total*(1+overhead_pct/100)
    annual=total_overhead*absences_per_year
    return {
        "Total per Absence":total_overhead,
        "Annualized Cost":annual,
        "Direct Cost":direct,
        "Manager Cost":mgr_cost,
        "Overtime Cost":ot_cost,
        "Prod Loss Cost":prod_cost,
        "Equip Idle Cost":eq_cost
    }

st.header("Employee Absence Cost Analysis")

if mode=="Single":
    cost=calculate_cost(
        hourly_rate,weekly_hours,absences_per_year,hours_per_absence,
        num_managers,manager_weekly_salary,manager_time_hours,
        overtime_rate,overtime_hours,productivity_loss_pct,
        idle_equipment_rate,idle_hours,overhead_pct
    )
    c1,c2=st.columns(2)
    c1.metric("Cost/Absence",f"${cost['Total per Absence']:.2f}")
    c2.metric("Annual Cost",f"${cost['Annualized Cost']:.2f}")
    df=pd.DataFrame(cost.items(),columns=["Component","Amount"])
    st.dataframe(df)
    fig=px.pie(df,names='Component',values='Amount',title='Cost Breakdown')
    st.plotly_chart(fig)
    st.bar_chart(df.set_index('Component')['Amount'])
    csv=df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV",csv,file_name=f"{name}_cost.csv")
elif mode=="Batch" and df_profiles is not None:
    results=[]
    for _,r in df_profiles.iterrows():
        c=calculate_cost(
            r.hourly_rate,r.weekly_hours,r.absences_per_year,r.hours_per_absence,
            r.num_managers,r.manager_weekly_salary,r.manager_time_hours,
            r.overtime_rate,r.overtime_hours,r.productivity_loss_pct,
            r.idle_equipment_rate,r.idle_hours,overhead_pct
        )
        c['Employee']=r.employee_name
        results.append(c)
    dfb=pd.DataFrame(results)
    b1,b2=st.columns(2)
    b1.metric("Avg Cost/Absence",f"${dfb['Total per Absence'].mean():.2f}")
    b2.metric("Total Annual Cost",f"${dfb['Annualized Cost'].sum():.2f}")
    st.dataframe(dfb)
    st.bar_chart(dfb.set_index('Employee')['Total per Absence'])
    csvb=dfb.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV",csvb,file_name='batch_costs.csv')
