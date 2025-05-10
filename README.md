# Employee Absence Cost Analysis App

A Streamlit application to calculate the **true cost** of unplanned employee absences. It factors in direct wages, management response time, overtime/backfill, productivity losses, equipment idle costs, and an optional overhead multiplier. Supports both single-employee analysis and batch processing via CSV.

---

## 🚀 Features

- **Single-Mode Analysis**  
  - Enter one employee’s details and absence parameters.  
  - Instantly view:
    - **Cost per Absence**  
    - **Annualized Cost**  
    - Breakdown table of cost components  
    - Interactive Pie & Bar charts  
  - Download results as a CSV file.

- **Batch-Mode Analysis**  
  - Upload a CSV of multiple employee profiles.  
  - Automatically compute:
    - Average cost per absence across all employees  
    - Total annual cost  
    - Per-employee cost comparisons  
  - Download aggregated results as a CSV file.

- **Customizable Inputs**  
  - Default weekly hours and overhead/inflation percentage  
  - Hourly or salaried pay structures  
  - Management team size and response time  
  - Overtime/backfill rates  
  - Productivity loss percentage  
  - Equipment idle rates and downtime

- **Performance & Usability**  
  - Input sections organized in collapsible sidebar panels  
  - Key metrics surfaced via `st.metric` cards  
  - Caching of cost calculations and CSV loading for responsiveness  
  - Uses Plotly Express for dynamic pie charts

---

## 📂 Repository Structure

```
.
├── streamlit_app.py         # Main Streamlit application
├── requirements.txt         # Python dependencies
├── example_profiles.csv     # Sample data for batch mode
├── README.md                # This file
└── .gitignore               # Git ignore rules
```

---

## 🔧 Installation & Local Usage

1. **Clone the repository**  
   ```bash
   git clone https://github.com/<your-username>/employee-absence-cost-app.git
   cd employee-absence-cost-app
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the app**  
   ```bash
   streamlit run streamlit_app.py
   ```
   The app will open at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Cloud

1. **Push to GitHub**  
   ```bash
   git add .
   git commit -m "Add Streamlit absence cost app"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**  
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)  
   - Select **New app** → **Deploy from GitHub**  
   - Choose your repository and branch, with `streamlit_app.py` as the main file.

---

## 📊 CSV Example Format

Use `example_profiles.csv`:

| employee_name | hourly_rate | weekly_hours | absences_per_year | hours_per_absence | num_managers | manager_weekly_salary | manager_time_hours | overtime_rate | overtime_hours | productivity_loss_pct | idle_equipment_rate | idle_hours |
|---------------|-------------|--------------|-------------------|-------------------|--------------|-----------------------|--------------------|---------------|----------------|-----------------------|---------------------|------------|
| Adam Waller   | 35.29       | 44           | 6                 | 8.8               | 3            | 2000                  | 1                  | 0             | 0              | 10                    | 0                   | 0          |

---

## 🤝 Contributing

1. Fork, create a branch, implement changes, and open a PR.  
2. Ensure code is clean and documented.

---

## 📜 License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built with ❤️ using Streamlit and Plotly.*  
