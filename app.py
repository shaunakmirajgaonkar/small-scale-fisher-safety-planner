from pathlib import Path
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fisherguard_engine import score_trips, validate_columns, REQUIRED, HISTORY_REQUIRED, score_trip_scenario

BASE = Path(__file__).parent
st.set_page_config(page_title='FisherGuard', page_icon='⚓', layout='wide', initial_sidebar_state='expanded')


def svg_data_uri(text):
    return 'data:image/svg+xml;base64,' + base64.b64encode(text.encode()).decode()

LOGO = '''<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><circle cx="48" cy="48" r="44" fill="#e7f6ff"/><path d="M20 54c10-10 21-10 31 0s21 10 25 0" fill="none" stroke="#0a84d8" stroke-width="5" stroke-linecap="round"/><path d="M32 44l11-19 24 35" fill="none" stroke="#12a879" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="34" cy="70" r="4" fill="#ffb51b"/></svg>'''

st.markdown('''<style>
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.block-container{padding-top:1.3rem;padding-bottom:2rem;max-width:1480px}
.hero{background:linear-gradient(135deg,#eef9ff 0%,#f4fffb 55%,#fffaf0 100%);border:1px solid #d6ebf7;border-radius:26px;padding:24px 28px;margin-bottom:18px;box-shadow:0 10px 30px rgba(22,95,135,.08)}
.hero-title{font-size:2.65rem;font-weight:800;color:#123c6d;line-height:1.08;margin:0}
.hero-sub{font-size:1.05rem;color:#557595;margin:.45rem 0 0}
.badge{display:inline-block;padding:.42rem .7rem;border-radius:999px;margin-right:.35rem;margin-top:.8rem;background:#fff;border:1px solid #d9eaf3;color:#21557d;font-size:.84rem;font-weight:650}
.card{background:#fff;border:1px solid #dbeaf3;border-radius:18px;padding:18px 18px 16px;box-shadow:0 7px 22px rgba(28,86,122,.06);height:100%}
.kpi-label{color:#66809a;font-weight:700;font-size:.84rem;text-transform:uppercase;letter-spacing:.04em}.kpi-value{font-size:2rem;font-weight:800;color:#123f74;margin-top:.25rem}.kpi-note{color:#4f8b72;margin-top:.3rem;font-size:.9rem}
.small-note{color:#63809b;font-size:.9rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#f4fbff 0%,#eef7fb 100%);border-right:1px solid #d8eaf4}
</style>''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'<img src="{svg_data_uri(LOGO)}" width="72"/>', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#123f74;margin:.1rem 0 0">FisherGuard</h2><div style="color:#6a8298">Small-Scale Fisher Safety Planner</div>', unsafe_allow_html=True)
    page = st.radio('Navigate', ['Dashboard','Risk Analysis','Trip Planner','Location Explorer','Historical Trends','Scenario Simulator','Data Upload','Reports'])
    st.divider(); st.markdown('**LOCAL PROCESSING**'); st.caption('CSV • Pandas • NumPy • Plotly'); st.caption('No external APIs required.')

trips = pd.read_csv(BASE/'data/sample_trip_metrics.csv')
history = pd.read_csv(BASE/'data/sample_trip_history.csv')
scored = score_trips(trips)

st.markdown(f'''<div class="hero"><div style="display:grid;grid-template-columns:88px minmax(0,1fr) 230px;gap:22px;align-items:center"><div><img src="{svg_data_uri(LOGO)}" width="82"/></div><div><div class="hero-title">Small-Scale Fisher Safety Planner</div><div class="hero-sub">Estimate fishing-trip risk using weather, sea conditions, boat condition, location, communication coverage and fuel availability.</div><span class="badge">100% Local</span><span class="badge">Explainable Risk</span><span class="badge">Safety Planning</span></div><div style="background:#ffffffcc;border:1px solid #d7eadf;border-radius:16px;padding:14px 16px;color:#1f654d;font-weight:700">Safer Trips • Better Decisions<br><span style="font-weight:500;font-size:.86rem;color:#648675">No remote services required</span></div></div></div>''', unsafe_allow_html=True)

if page == 'Dashboard':
    total=len(scored); high=int(scored.risk_level.eq('High').sum()); crit=int(scored.risk_level.eq('Critical').sum()); low=int(scored.risk_level.eq('Low').sum()); mod=int(scored.risk_level.eq('Moderate').sum())
    cols=st.columns(5)
    vals=[('Total Trips',total,'Locally assessed'),('High Risk Trips',high,'Review before departure'),('Low Risk Trips',low,'Lower screening pressure'),('Moderate Risk Trips',mod,'Continue monitoring'),('Critical Risk Trips',crit,'Immediate review')]
    for c,(lab,val,note) in zip(cols,vals):
        c.markdown(f'<div class="card"><div class="kpi-label">{lab}</div><div class="kpi-value">{val}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)
    st.write('')
    a,b,c=st.columns([1.2,1.2,1])
    with a:
        st.markdown('<div class="card"><h3>Risk Level Distribution</h3>',unsafe_allow_html=True)
        fig=px.pie(scored,names='risk_level',hole=.58,color='risk_level',color_discrete_map={'Low':'#36b37e','Moderate':'#ffbf2f','High':'#ff7a45','Critical':'#e64a5b'})
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10),showlegend=True)
        st.plotly_chart(fig,width="stretch"); st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><h3>Weather vs Sea Conditions</h3>',unsafe_allow_html=True)
        fig=px.scatter(scored,x='weather_risk_index',y='sea_condition_index',size='risk_score',color='risk_level',hover_name='location',color_discrete_map={'Low':'#36b37e','Moderate':'#ffbf2f','High':'#ff7a45','Critical':'#e64a5b'})
        st.plotly_chart(fig,width="stretch"); st.markdown('</div>',unsafe_allow_html=True)
    with c:
        st.markdown('<div class="card"><h3>Top Risk Fishing Areas</h3>',unsafe_allow_html=True)
        st.dataframe(scored[['location','risk_score','risk_level','primary_driver']].sort_values('risk_score',ascending=False).head(6),hide_index=True,width="stretch")
        st.markdown('</div>',unsafe_allow_html=True)
    d,e=st.columns([1.25,1])
    with d:
        st.markdown('<div class="card"><h3>Risk Factors Contribution</h3>',unsafe_allow_html=True)
        factors=pd.DataFrame({'factor':['Sea Conditions','Weather','Boat Condition','Location & Distance','Communication','Fuel','Engine','Safety Readiness'],'contribution':[24,22,14,10,10,8,6,4]})
        fig=px.bar(factors.sort_values('contribution'),x='contribution',y='factor',orientation='h',text='contribution')
        fig.update_traces(texttemplate='%{text}%'); st.plotly_chart(fig,width="stretch"); st.markdown('</div>',unsafe_allow_html=True)
    with e:
        st.markdown('<div class="card"><h3>Priority Trips</h3>',unsafe_allow_html=True)
        st.dataframe(scored.sort_values('risk_score',ascending=False)[['trip_name','location','trip_date','risk_score','risk_level']].head(8),hide_index=True,width="stretch")
        st.markdown('</div>',unsafe_allow_html=True)

elif page == 'Risk Analysis':
    selected=st.selectbox('Select trip',scored['trip_name'].tolist())
    row=scored[scored.trip_name==selected].iloc[0]
    st.markdown(f'### {selected} — {row.location}')
    st.metric('Risk score',f"{row.risk_score:.1f}/100",row.risk_level)
    comp=pd.DataFrame({'Factor':['Weather','Sea Conditions','Boat Condition','Distance','Communication','Fuel','Engine','Safety Readiness'],'Pressure':[row.weather_risk_index,row.sea_condition_index,100-row.boat_condition_score,min(100,row.distance_from_shore_km/1.5),100-row.communication_coverage_pct,100-row.fuel_availability_pct,100-row.engine_condition_score,100-row.lifejacket_readiness_pct]})
    st.plotly_chart(px.bar(comp.sort_values('Pressure'),x='Pressure',y='Factor',orientation='h',text_auto='.0f'),width="stretch")
    st.dataframe(pd.DataFrame([row]),hide_index=True,width="stretch")

elif page == 'Trip Planner':
    st.markdown('### Trip Planner')
    st.write('Select a trip and review the pre-departure screening indicators.')
    selected=st.selectbox('Trip',scored['trip_name'].tolist(),key='planner')
    row=scored[scored.trip_name==selected].iloc[0]
    c1,c2,c3=st.columns(3)
    c1.metric('Risk',f'{row.risk_score:.1f}',row.risk_level)
    c2.metric('Distance',f"{row.distance_from_shore_km:.1f} km")
    c3.metric('Communication',f"{row.communication_coverage_pct:.0f}%")
    st.warning('Use this as a planning aid. Confirm current conditions, equipment readiness, communications, fuel, local advisories and professional safety procedures before departure.')

elif page == 'Location Explorer':
    st.markdown('### Location Explorer')
    grp=scored.groupby('location',as_index=False).agg(risk_score=('risk_score','mean'),trips=('trip_id','count'))
    st.dataframe(grp.sort_values('risk_score',ascending=False),hide_index=True,width="stretch")
    st.plotly_chart(px.bar(grp.sort_values('risk_score'),x='risk_score',y='location',orientation='h',color='risk_score',color_continuous_scale='Blues'),width="stretch")

elif page == 'Historical Trends':
    h=history.copy(); h['period']=pd.to_datetime(h['period']); h['risk_score']=pd.to_numeric(h['risk_score'],errors='coerce')
    st.plotly_chart(px.line(h.sort_values('period'),x='period',y='risk_score',color='trip_id',markers=True),width="stretch")
    st.dataframe(h.sort_values('period',ascending=False).head(30),hide_index=True,width="stretch")

elif page == 'Scenario Simulator':
    st.markdown('### Scenario Simulator')
    c1,c2=st.columns(2)
    with c1:
        weather=st.slider('Weather risk index',0.0,100.0,55.0,1.0)
        sea=st.slider('Sea condition index',0.0,100.0,60.0,1.0)
        boat=st.slider('Boat condition score',0.0,100.0,75.0,1.0)
        distance=st.slider('Distance from shore (km)',0.0,30.0,8.0,0.5)
    with c2:
        comm=st.slider('Communication coverage (%)',0.0,100.0,70.0,1.0)
        fuel=st.slider('Fuel availability (%)',0.0,100.0,80.0,1.0)
        life=st.slider('Lifejacket readiness (%)',0.0,100.0,90.0,1.0)
        engine=st.slider('Engine condition score',0.0,100.0,78.0,1.0)
    score=score_trip_scenario(weather,sea,boat,comm,fuel,life,distance,engine)
    level='Low' if score<25 else 'Moderate' if score<50 else 'High' if score<75 else 'Critical'
    st.success(f'Estimated screening score: **{score:.1f}/100 — {level}**')

elif page == 'Data Upload':
    st.markdown('### Local Data Upload')
    up1=st.file_uploader('Upload trip metrics CSV',type=['csv'])
    up2=st.file_uploader('Upload risk history CSV',type=['csv'])
    if up1:
        d=pd.read_csv(up1); missing=validate_columns(d,REQUIRED)
        if missing: st.error('Missing columns: '+', '.join(missing))
        else:
            s=score_trips(d); st.success(f'Loaded {len(s)} trips successfully.'); st.dataframe(s,width="stretch")
    if up2:
        d=pd.read_csv(up2); missing=validate_columns(d,HISTORY_REQUIRED)
        if missing: st.error('Missing columns: '+', '.join(missing))
        else: st.success(f'Loaded {len(d)} history rows successfully.')

elif page == 'Reports':
    st.markdown('### Reports')
    st.download_button('Download scored trip report',scored.to_csv(index=False).encode(),'fisherguard_scored_trips.csv','text/csv')
    priority=scored[scored.risk_level.isin(['High','Critical'])].sort_values('risk_score',ascending=False)
    st.download_button('Download priority review queue',priority.to_csv(index=False).encode(),'fisherguard_priority_review.csv','text/csv')
    st.dataframe(priority[['trip_name','location','trip_date','risk_score','risk_level','primary_driver']],hide_index=True,width="stretch")

st.markdown('<div class="small-note" style="margin-top:24px">FisherGuard is a screening and planning aid. It does not certify seaworthiness, weather safety, navigation safety, or trip suitability.</div>',unsafe_allow_html=True)
