# Employee Absence Cost Analysis App

This Streamlit app calculates the true cost of unplanned employee absences, including direct wages, management response, overtime/backfill, productivity loss, and equipment idle costs, with an optional overhead multiplier.

## Files

- `streamlit_app.py`: Main Streamlit application.
- `requirements.txt`: Python dependencies.
- `example_profiles.csv`: Sample CSV for batch analysis.

## Usage

### Local

1. Clone this repo.
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud

1. Push this repo to GitHub.
2. On Streamlit Cloud, choose “Deploy from GitHub” and select this repo.
3. Set the main file to `streamlit_app.py`.

