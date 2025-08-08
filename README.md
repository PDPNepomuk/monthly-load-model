# Monthly Electric Load Model — Streamlit App

This small Streamlit app generates an hourly electric load profile for a selected month using:
- operating hours
- selected weekdays
- base and peak load (kW)
- optional random variation

## Run locally

1. Install Python 3.8+ from https://www.python.org/ (if you don't have it).
2. Open a terminal (Command Prompt / PowerShell on Windows, Terminal on macOS/Linux).
3. (Optional) Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate     # macOS/Linux
   venv\Scripts\activate      # Windows PowerShell
   ```
4. Install requirements:
   ```
   pip install -r requirements.txt
   ```
5. Run the app:
   ```
   streamlit run streamlit_app.py
   ```

## Deploy to Streamlit Community Cloud (easy, free for public repos)

1. Create a GitHub account (https://github.com) if you don't have one.
2. Create a new repository and add these files (`streamlit_app.py`, `requirements.txt`, `README.md`) to the repository root.
3. Go to https://share.streamlit.io (Streamlit Community Cloud) and sign in with GitHub.
4. Click **Create app** and follow the prompts to select your repo, branch (usually `main`), and entrypoint (`streamlit_app.py`).
5. Click **Deploy**.

Streamlit expects a `requirements.txt` at the repo root listing the Python packages your app needs.

If you prefer, I can walk you through creating the GitHub repo and deploying step-by-step.
