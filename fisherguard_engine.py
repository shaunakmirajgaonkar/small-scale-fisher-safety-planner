from __future__ import annotations

import pandas as pd
import numpy as np

REQUIRED = [
    'trip_id','trip_name','location','latitude','longitude','trip_date',
    'weather_risk_index','sea_condition_index','boat_condition_score',
    'distance_from_shore_km','communication_coverage_pct','fuel_availability_pct',
    'engine_condition_score','lifejacket_readiness_pct','crew_experience_years'
]
HISTORY_REQUIRED = ['trip_id','period','risk_score','weather_risk_index','sea_condition_index']


def validate_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    return [c for c in required if c not in df.columns]


def clamp(v: pd.Series | float, lo=0.0, hi=100.0):
    return np.clip(v, lo, hi)


def score_trips(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in REQUIRED:
        if c in ['trip_id','trip_name','location','trip_date']:
            continue
        out[c] = pd.to_numeric(out[c], errors='coerce').fillna(0)
    weather = clamp(out['weather_risk_index'])
    sea = clamp(out['sea_condition_index'])
    boat = 100 - clamp(out['boat_condition_score'])
    distance = clamp(out['distance_from_shore_km'] / 1.5)
    comm = 100 - clamp(out['communication_coverage_pct'])
    fuel = 100 - clamp(out['fuel_availability_pct'])
    engine = 100 - clamp(out['engine_condition_score'])
    safety = 100 - clamp(out['lifejacket_readiness_pct'])
    experience = clamp(100 - out['crew_experience_years'] * 8)
    score = (
        weather*0.22 + sea*0.24 + boat*0.14 + distance*0.10 + comm*0.10 +
        fuel*0.08 + engine*0.06 + safety*0.04 + experience*0.02
    )
    out['risk_score'] = clamp(score).round(1)
    out['risk_level'] = pd.cut(
        out['risk_score'], bins=[-0.01,24.99,49.99,74.99,100],
        labels=['Low','Moderate','High','Critical']
    ).astype(str)
    out['primary_driver'] = pd.Series(np.select(
        [weather >= sea, sea >= weather, boat >= 60, comm >= 60, engine >= 60],
        ['Weather','Sea Conditions','Boat Condition','Communication','Engine Condition'],
        default='Fuel / Safety Readiness'
    ), index=out.index)
    return out


def score_trip_scenario(weather, sea, boat_condition, communication, fuel, lifejacket, distance_km, engine):
    row = pd.DataFrame([{
        'trip_id':'SCENARIO', 'trip_name':'Scenario', 'location':'Scenario', 'latitude':0.0, 'longitude':0.0, 'trip_date':'2026-01-01',
        'weather_risk_index': weather,
        'sea_condition_index': sea,
        'boat_condition_score': boat_condition,
        'distance_from_shore_km': distance_km,
        'communication_coverage_pct': communication,
        'fuel_availability_pct': fuel,
        'engine_condition_score': engine,
        'lifejacket_readiness_pct': lifejacket,
        'crew_experience_years': 5,
    }])
    return float(score_trips(row)['risk_score'].iloc[0])
