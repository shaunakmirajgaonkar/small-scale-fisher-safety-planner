from fisherguard_engine import score_trips, score_trip_scenario
import pandas as pd

def test_score_bounds():
    df=pd.DataFrame([{
        'trip_id':'T1','trip_name':'Test','location':'Harbor','latitude':18.5,'longitude':73.8,'trip_date':'2026-08-19',
        'weather_risk_index':80,'sea_condition_index':75,'boat_condition_score':70,'distance_from_shore_km':10,
        'communication_coverage_pct':60,'fuel_availability_pct':80,'engine_condition_score':75,'lifejacket_readiness_pct':90,'crew_experience_years':5
    }])
    s=score_trips(df)
    assert 0 <= s.risk_score.iloc[0] <= 100

def test_scenario_returns_number():
    assert isinstance(score_trip_scenario(40,40,80,80,90,95,5,85),float)
