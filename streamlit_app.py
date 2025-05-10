import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Employee Absence Cost Analysis", layout="wide")

# --- Utility & Caching ---
@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    # Ensure advanced columns exist with defaults
    advanced_cols = {
        'training_hours': 0.0,
        'skill_multiplier': 1.0,
        'delay_penalty': 0.0,
        'rework_pct': 0.0,
        'hr_overhead_hrs': 0.0,
        'seasonal_factor': 1.0,
        'compliance_cost': 0.0,
        'benefits_loading': 0.0
    }
    for col, default in advanced_cols.items():
        if col not in df.columns:
            df[col] = default
    return df

@st.cache_data
def calculate_cost(params, adv_params):
    # Base components
    direct = params['hourly_rate'] * params['hours_per_absence']
    mgr_hr = (params['manager_weekly_salary'] / params['weekly_hours']
              if params['weekly_hours'] > 0 else 0.0)
    manager = mgr_hr * params['manager_time_hours'] * params['num_managers']
    overtime = params['overtime_rate'] * params['overtime_hours']
    productivity = ((params['hourly_rate'] * params['weekly_hours']) *
                    (params['productivity_loss_pct'] / 100))
    equipment = params['idle_equipment_rate'] * params['idle_hours']
    total = direct + manager + overtime + productivity + equipment

    # Advanced adjustments
    skill_adj = total * (adv_params['skill_multiplier'] - 1)
    training_cost = adv_params['training_hours'] * params['hourly_rate']
    delay_cost = adv_params['delay_penalty'] * params['hours_per_absence']
    rework_cost = total * (adv_params['rework_pct'] / 100)
    hr_overhead_cost = adv_params['hr_overhead_hrs'] * mgr_hr
    seasonal_cost = total * (adv_params['seasonal_factor'] - 1)
    compliance = adv_params['compliance_cost']
    benefits_cost = total * (adv_params['benefits_loading'] / 100)

    # Sum advanced
    total_adv = (total + skill_adj + training_cost + delay_cost +
                 rework_cost + hr_overhead_cost)
    total_adv = total_adv * adv_params['seasonal_factor'] + compliance + benefits_cost

    # Overhead and annualize
    total_overhead = total_adv * (1 + params['overhead_pct'] / 100)
    annualized = total_overhead * params['absences_per_year']

    return {
        'Total per Absence': total_overhead,
        'Annualized Cost': annualized,
        'Direct Cost': direct,
        'Manager Cost': manager,
        'Overtime Cost': overtime,
        'Productivity Loss': productivity,
        'Equipment Idle': equipment,
        'Skill Adj': skill_adj,
        'Training Cost': training_cost,
        'Delay Cost': delay_cost,
        'Rework Cost': rework_cost,
        'HR Overhead': hr_overhead_cost,
        'Seasonal Cost': seasonal_cost,
        'Compliance Cost': compliance,
        'Benefits Cost': benefits_cost
    }

# --- Sidebar Inputs ---
mode = st.sidebar.radio("Mode", ["Single", "Batch"], index=0)

with st.sidebar.expander("Defaults"):
    default_weekly_hours = st.number_input("Default Weekly Hours", 40.0, min_value=0.0)
    overhead_pct = st.number_input("Overhead Multiplier (%)", 0.0, min_value=0.0)

with st.sidebar.expander("Employee Details"):
    if mode == "Single":
        name = st.text_input("Employee Name", "Adam Waller")
        emp_type = st.radio("Employment Type", ["Hourly", "Salaried"], index=0)
        if emp_type == "Hourly":
            hourly_rate = st.number_input("Hourly Rate ($/hr)", 35.29, min_value=0.0)
            weekly_hours = st.number_input("Scheduled Hours/Week", default_weekly_hours, min_value=0.0)
        else:
            weekly_salary = st.number_input("Weekly Salary ($)", 2000.0, min_value=0.0)
            weekly_hours = st.number_input("Scheduled Hours/Week", default_weekly_hours, min_value=0.0)
            hourly_rate = (weekly_salary / weekly_hours) if weekly_hours > 0 else 0.0

with st.sidebar.expander("Absence Pattern"):
    absences_per_year = st.number_input("Absences per Year", 6, min_value=0)
    hours_per_absence = st.number_input("Hours Missed/Absence", default_weekly_hours/5, min_value=0.0)

with st.sidebar.expander("Management Impact"):
    num_managers = st.number_input("Managers Affected", 3, min_value=0)
    manager_weekly_salary = st.number_input("Mgr Weekly Salary ($)", 2000.0, min_value=0.0)
    manager_time_hours = st.number_input("Mgr Time/Absence (hrs)", 1.0, min_value=0.0)

with st.sidebar.expander("Additional Costs"):
    overtime_rate = st.number_input("Overtime Rate ($/hr)", 0.0, min_value=0.0)
    overtime_hours = st.number_input("OT Hours/Absence", 0.0, min_value=0.0)
    productivity_loss_pct = st.number_input("Prod Loss (%)", 10.0, min_value=0.0, max_value=100.0)
    idle_equipment_rate = st.number_input("Idle Equip Rate ($/hr)", 0.0, min_value=0.0)
    idle_hours = st.number_input("Idle Hours/Absence", 0.0, min_value=0.0)

with st.sidebar.expander("Advanced Information"):
    absence_reason = st.selectbox("Absence Reason", ["Illness", "Personal", "No-Show", "Other"])
    training_hours = st.number_input("Replacement Training Time (hrs)", 0.0, min_value=0.0)
    skill_multiplier = st.slider("Skill Level Multiplier", 1.0, 2.0, 1.0, 0.1)
    delay_penalty = st.number_input("Project Delay Penalty ($/hr)", 0.0, min_value=0.0)
    rework_pct = st.number_input("Rework Rate (%)", 0.0, min_value=0.0, max_value=100.0)
    hr_overhead_hrs = st.number_input("Administrative Overhead (hrs)", 0.0, min_value=0.0)
    seasonal_factor = st.number_input("Seasonal Adjustment Factor", 1.0, min_value=0.1, max_value=2.0)
    compliance_cost = st.number_input("Regulatory/Compliance Cost ($)", 0.0, min_value=0.0)
    benefits_loading = st.number_input("Benefit Loading (%)", 0.0, min_value=0.0, max_value=100.0)

# Load CSV for Batch Mode
df_profiles = None
if mode == "Batch":
    uploaded = st.sidebar.file_uploader("Upload profiles CSV", type=["csv"])
    if uploaded:
        df_profiles = load_csv(uploaded)

# Main Header
st.header("Employee Absence Cost Analysis")

if mode == "Single":
    base_params = {
        'hourly_rate': hourly_rate,
        'weekly_hours': weekly_hours,
        'absences_per_year': absences_per_year,
        'hours_per_absence': hours_per_absence,
        'num_managers': num_managers,
        'manager_weekly_salary': manager_weekly_salary,
        'manager_time_hours': manager_time_hours,
        'overtime_rate': overtime_rate,
        'overtime_hours': overtime_hours,
        'productivity_loss_pct': productivity_loss_pct,
        'idle_equipment_rate': idle_equipment_rate,
        'idle_hours': idle_hours,
        'overhead_pct': overhead_pct
    }
    adv_params = {
        'training_hours': training_hours,
        'skill_multiplier': skill_multiplier,
        'delay_penalty': delay_penalty,
        'rework_pct': rework_pct,
        'hr_overhead_hrs': hr_overhead_hrs,
        'seasonal_factor': seasonal_factor,
        'compliance_cost': compliance_cost,
        'benefits_loading': benefits_loading
    }

    st.subheader(f"Employee: {name}")
    cost = calculate_cost(base_params, adv_params)
    c1, c2 = st.columns(2)
    c1.metric("Cost per Absence", f"${cost['Total per Absence']:.2f}")
    c2.metric("Annualized Cost", f"${cost['Annualized Cost']:.2f}")

    df = pd.DataFrame(cost.items(), columns=["Component","Amount"])
    st.dataframe(df)

    # Pie: Top 6 with 'Other'
    df_sorted = df.sort_values(by='Amount', ascending=False)
    top_n = 6
    top_df = df_sorted.head(top_n).copy()
    if len(df_sorted) > top_n:
        other_sum = df_sorted['Amount'].iloc[top_n:].sum()
        top_df = pd.concat([top_df, pd.DataFrame([{'Component':'Other','Amount':other_sum}])],
                            ignore_index=True)
    fig = px.pie(top_df, names='Component', values='Amount', title='Cost Breakdown')
    st.plotly_chart(fig)

    st.bar_chart(df.set_index('Component')['Amount'])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, file_name=f"{name}_cost.csv")

elif mode == "Batch" and df_profiles is not None:
    results = []
    for _, r in df_profiles.iterrows():
        base = {
            'hourly_rate': r.hourly_rate,
            'weekly_hours': r.weekly_hours,
            'absences_per_year': r.absences_per_year,
            'hours_per_absence': r.hours_per_absence,
            'num_managers': r.num_managers,
            'manager_weekly_salary': r.manager_weekly_salary,
            'manager_time_hours': r.manager_time_hours,
            'overtime_rate': r.overtime_rate,
            'overtime_hours': r.overtime_hours,
            'productivity_loss_pct': r.productivity_loss_pct,
            'idle_equipment_rate': r.idle_equipment_rate,
            'idle_hours': r.idle_hours,
            'overhead_pct': overhead_pct
        }
        adv = {col: r[col] for col in [
            'training_hours','skill_multiplier','delay_penalty','rework_pct',
            'hr_overhead_hrs','seasonal_factor','compliance_cost','benefits_loading'
        ]}
        c = calculate_cost(base, adv)
        c['Employee'] = r.employee_name
        results.append(c)

    dfb = pd.DataFrame(results)
    b1, b2 = st.columns(2)
    b1.metric("Avg Cost/Absence", f"${dfb['Total per Absence'].mean():.2f}")
    b2.metric("Total Annualized Cost", f"${dfb['Annualized Cost'].sum():.2f}")
    st.dataframe(dfb)
    st.bar_chart(dfb.set_index('Employee')['Total per Absence'])
    csvb = dfb.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csvb, file_name='batch_costs.csv')
'''

with open('/mnt/data/streamlit_app_corrected.py', 'w') as f:
    f.write(fixed_code)

'/mnt/data/streamlit_app_corrected.py'
