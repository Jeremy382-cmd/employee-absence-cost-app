# Employee Absence Cost Analysis App

This Streamlit app calculates the true cost of unplanned employee absences, including direct wages, management response, overtime/backfill, productivity loss, and equipment idle costs—with an optional overhead multiplier.

## Files in this repo

- `streamlit_app.py`: Main Streamlit application.
- `requirements.txt`: Lists dependencies (`streamlit`, `pandas`, `plotly`).
- `example_profiles.csv`: Sample CSV for batch analysis.
- `README.md`: Project overview and setup instructions.
- `.gitignore`: Common ignores for Python and virtual environments.

## Setup & Usage

1. **Clone repo**  
2. **Create virtual environment & activate**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```  
3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```  
4. **Run locally**  
   ```bash
   streamlit run streamlit_app.py
   ```  
5. **Deploy on Streamlit Cloud**  
   - Push to GitHub  
   - In Streamlit Cloud: New app → select repo → `streamlit_app.py`  

