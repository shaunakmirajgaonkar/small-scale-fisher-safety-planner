from pathlib import Path
import pandas as pd
from fisherguard_engine import score_trips, validate_columns, REQUIRED, HISTORY_REQUIRED

base = Path(__file__).parent
df = pd.read_csv(base/'data/sample_trip_metrics.csv')
h = pd.read_csv(base/'data/sample_trip_history.csv')
missing = validate_columns(df, REQUIRED)
missing_h = validate_columns(h, HISTORY_REQUIRED)
assert not missing, missing
assert not missing_h, missing_h
assert h['trip_id'].nunique() <= len(h)
scored = score_trips(df)
assert scored['risk_score'].between(0,100).all()
assert len(scored) == len(df)
print('PASS: FisherGuard small-scale fisher safety screening')
print(f'Trips: {len(scored)}')
print(f'History rows: {len(h)}')
print(f'Risk range: {scored.risk_score.min():.1f}–{scored.risk_score.max():.1f}')
print(f'High/Critical: {(scored.risk_level.isin(["High","Critical"])).sum()}')
