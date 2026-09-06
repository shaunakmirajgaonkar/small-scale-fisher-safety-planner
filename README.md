# FisherGuard — Small-Scale Fisher Safety Planner

Privacy-conscious, local-first fishing-trip risk screening and planning dashboard.

## Run
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 validate_project.py
python3 -m pytest -q
python3 run.py
