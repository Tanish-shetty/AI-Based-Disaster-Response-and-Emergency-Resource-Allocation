"""Presentation helpers for the interactive accountability dashboard."""
from html import escape
import numpy as np
import plotly.graph_objects as go
import streamlit as st

COLORS = {"Low": "#399a8f", "Medium": "#dcac48", "High": "#ed8855", "Critical": "#d85470"}
PAGE_COPY = {
    "Overview": ("Every recommendation. A human decision.", "Explore how imperfect data changes who receives help, and follow the evidence behind every allocation."),
    "Disaster Scenario": ("Explore the affected areas", "Inspect flood conditions, community vulnerability and the observations available to the model."),
    "AI Priority Analysis": ("From model output to resource priorities", "Filter the queue, inspect an area and explore how scarce assistance is distributed."),
    "Explainable AI": ("Look inside the recommendation", "See which observations support a prediction, and distinguish model confidence from evidence quality."),
    "Ethical Risk Simulator": ("Small data changes. Consequential decisions.", "Compare the complete-data baseline with imperfect observations and investigate who gains or loses assistance."),
    "Human Review": ("Evidence first. Authorization next.", "Review the entire portfolio, redistribute resources and preserve the reasons behind your decision."),
    "Accountability Audit": ("Follow the decision trail", "Search the journal and reconstruct the path from observed data to an authorized allocation."),
    "Stakeholder Accountability": ("Responsibility is shared", "Investigate duties across the decision chain using retained evidence, without automatically assigning blame."),
    "Results & Findings": ("Measure performance. Examine the gaps.", "Compare evaluated models and see why aggregate accuracy cannot stand in for severe-case reliability."),
    "Recommendations": ("Build accountability into the process", "Connect twelve practical safeguards to data, models, human oversight and post-incident review.")}

def inject_styles():
    st.markdown("""<style>
    :root {--navy:#102d3a;--teal:#0c9385;--muted:#71818b;--line:#e1e8ec}
    .stApp {background:#f4f7f9}
    .block-container {max-width:1540px;padding:1.8rem 2.6rem 2rem}
    h1,h2,h3 {font-family:'Segoe UI',sans-serif;letter-spacing:-.035em;color:#173341}
    h3 {font-size:1.25rem!important;font-weight:650!important}
    [data-testid='stHeader'] {background:rgba(244,247,249,.92)}
    [data-testid='stSidebar'] {background:#102d3a;border-right:0}
    [data-testid='stSidebar'] * {color:#dce8ed}
    [data-testid='stSidebar'] [data-baseweb='select'] * {color:#173341}
    [data-testid='stSidebar'] input {color:#173341!important}
    [data-testid='stSidebar'] [data-baseweb='input'] {background:#f3f7f8}
    [data-testid='stSidebar'] [data-testid='stExpander'] {border-color:#35505c}
    [data-testid='stSidebar'] hr {border-color:#35505c}
    [data-testid='stSidebar'] [data-testid='stRadio'] label {padding:.28rem .35rem;border-radius:6px;transition:background .15s}
    [data-testid='stSidebar'] [data-testid='stRadio'] label:hover {background:#24424e}
    [data-testid='stMetric'] {padding:18px 20px;background:#fff;border:1px solid var(--line);border-radius:13px;box-shadow:0 3px 12px #19313d04}
    [data-testid='stMetricLabel'] {color:#6c7c86;font-size:.84rem}
    [data-testid='stMetricValue'] {font-weight:650;color:#173341}
    [data-testid='stVerticalBlockBorderWrapper']>div {border-radius:14px!important}
    [data-testid='stDataFrame'],[data-testid='stDataEditor'] {border-radius:10px;overflow:hidden}
    .stButton>button,.stDownloadButton>button {border-radius:9px;min-height:42px;font-weight:600}
    .stTabs [data-baseweb='tab-list'] {gap:22px;border-bottom:1px solid var(--line)}
    .stTabs [data-baseweb='tab'] {background:transparent;font-weight:600}
    .hero {background:linear-gradient(120deg,#11313e 0%,#1b4853 62%,#176557 100%);border-radius:18px;padding:28px 32px;margin-bottom:22px;position:relative;overflow:hidden}
    .hero:after {content:'';position:absolute;width:240px;height:240px;border:38px solid #ffffff07;border-radius:50%;right:-65px;top:-105px;pointer-events:none}
    .hero-eyebrow {display:flex;align-items:center;gap:10px;color:#91c8c2;font-size:.72rem;letter-spacing:.15em;font-weight:700;text-transform:uppercase;margin-bottom:16px}
    .hero h1 {color:#fff;font-size:2.1rem;line-height:1.2;margin:0 0 12px;font-weight:650;max-width:850px}
    .hero p {color:#bacfd5;font-size:.92rem;line-height:1.7;max-width:790px;margin:0 0 20px}
    .hero-meta {display:flex;gap:9px;flex-wrap:wrap}
    .pill {display:inline-block;font-size:.73rem;padding:6px 11px;border-radius:6px;background:#ffffff12;color:#d7e8eb;border:1px solid #ffffff18}
    .pill-teal {background:#2bbb981c;color:#9de3cf;border-color:#56cbae45}
    .brand {display:flex;gap:12px;align-items:center;padding:4px 0 12px}
    .brand-icon {background:#18a68f;border-radius:11px;color:white!important;font-size:23px;display:grid;place-items:center;width:43px;height:43px}
    .brand-name {font-size:1.05rem;font-weight:750;letter-spacing:-.025em;color:#fff!important}
    .brand-sub {font-size:.69rem;color:#90afb9!important;margin-top:4px;letter-spacing:.05em}
    .sidebar-note {padding:12px;background:#ffffff08;border:1px solid #ffffff12;border-radius:9px;font-size:.74rem;line-height:1.6;color:#b4cbd1!important;margin-top:20px}
    .section-label {font-size:.69rem;letter-spacing:.16em;color:#6f8794;font-weight:700;text-transform:uppercase;margin:16px 0 7px}
    .queue-card {background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:9px;display:flex;align-items:center;gap:12px}
    .queue-rank {background:#eef4f5;border-radius:8px;width:32px;height:32px;display:grid;place-items:center;font-weight:700;color:#66808b;font-size:.85rem}
    .queue-name {font-size:.89rem;font-weight:650;color:#193743}
    .queue-detail {font-size:.74rem;color:#778892;margin-top:3px}
    .queue-score {margin-left:auto;font-size:1.2rem;font-weight:700;color:#173d49}
    .mini-badge {font-size:.64rem;padding:3px 7px;border-radius:4px;background:#fff1de;color:#9b6224;margin-left:7px;white-space:nowrap}
    .flow {display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 8px}
    .flow-step {flex:1;min-width:115px;border:1px solid var(--line);border-radius:9px;background:#fff;padding:13px}
    .flow-number {font-size:.65rem;color:#0c9385;font-weight:750;letter-spacing:.1em}
    .flow-title {font-size:.83rem;color:#264551;font-weight:600;margin-top:6px}
    .trail {border-left:2px solid #d6e3e7;margin-left:7px;padding:0 0 22px 20px;position:relative}
    .trail:before {content:'';width:10px;height:10px;border-radius:50%;position:absolute;left:-6px;top:5px;background:#13a18d;border:2px solid #f4f7f9}
    .trail-title {font-size:.87rem;font-weight:650;color:#254754}
    .trail-text {font-size:.78rem;color:#7a8d96;line-height:1.6;margin-top:5px}
    .safeguard {padding:18px;border-radius:12px;background:#fff;border:1px solid var(--line);min-height:150px;margin:6px 0}
    .safeguard .num {font-size:.69rem;font-weight:750;color:#0c9385;letter-spacing:.12em}
    .safeguard h4 {font-size:.94rem;margin:10px 0;color:#214451}
    .safeguard p {font-size:.78rem;line-height:1.6;color:#74868f}
    @media(max-width:760px){.block-container{padding:1rem}.hero{padding:22px}.hero h1{font-size:1.65rem}}
    </style>""",unsafe_allow_html=True)

def hero(page,scenario,finalized):
    title,description = PAGE_COPY[page]
    st.markdown(f"""<div class="hero"><div class="hero-eyebrow">◈ FLOOD RESPONSE / ACCOUNTABILITY LAB</div>
    <h1>{escape(title)}</h1><p>{escape(description)}</p><div class="hero-meta">
    <span class="pill pill-teal">ACADEMIC SIMULATION</span><span class="pill">DEMO-FLOOD-01</span>
    <span class="pill">{escape(scenario)}</span><span class="pill">{'Portfolio authorized' if finalized else 'Human authorization pending'}</span>
    </div></div>""",unsafe_allow_html=True)
    st.caption("Simulation only — not for real emergency decision-making. All areas, data and resource allocations are synthetic.")

def section(label):
    st.markdown(f'<div class="section-label">{escape(label)}</div>',unsafe_allow_html=True)

def styled_chart(fig,height=380):
    fig.update_layout(template="plotly_white",height=height,font=dict(family="Segoe UI, sans-serif",color="#607780",size=12),
                      paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=15,r=15,t=25,b=30),legend=dict(orientation="h",y=1.12,x=0),
                      hoverlabel=dict(bgcolor="#173c49",font_color="white"),colorway=["#0e9788","#ecad62","#628db5","#cc6c86"])
    fig.update_xaxes(gridcolor="#e8eef1",zerolinecolor="#d7e4e8")
    fig.update_yaxes(gridcolor="#e8eef1",zerolinecolor="#d7e4e8")
    return fig

def queue_card(row):
    badge = '<span class="mini-badge">REVIEW</span>' if row.mandatory_review else ""
    st.markdown(f'<div class="queue-card"><div class="queue-rank">{int(row["rank"]):02d}</div><div><div class="queue-name">{escape(row.area_name)}{badge}</div><div class="queue-detail">{escape(row.score_band)} · {row.confidence:.0%} class probability</div></div><div class="queue-score">{row.priority_score:.1f}</div></div>',unsafe_allow_html=True)

def decision_flow(finalized=False):
    steps = ["Observe data", "AI recommendation", "Explain & inspect", "Human review", "Authorize & audit"]
    st.markdown('<div class="flow">'+"".join(f'<div class="flow-step"><div class="flow-number">0{i}</div><div class="flow-title">{title}</div></div>' for i,title in enumerate(steps,1))+"</div>",unsafe_allow_html=True)

def area_map(predictions):
    """Fictional layout for visual exploration. Coordinates are never ML features."""
    coordinates = {"AREA-01":(3.2,3.8),"AREA-02":(4.5,6.3),"AREA-03":(2.4,5.4),"AREA-04":(7.1,4.5),
                   "AREA-05":(7.2,7),"AREA-06":(3,1.7),"AREA-07":(3.5,8),"AREA-08":(5.4,4.5),
                   "AREA-09":(1.2,3),"AREA-10":(6.4,2.4),"AREA-11":(8.1,2),"AREA-12":(8.6,8.4)}
    fig = go.Figure()
    # A conceptual river and street grid provide orientation, not real geography.
    fig.add_shape(type="path",path="M 4.6,10 Q 3.6,8 4.9,6 Q 6.2,4 5.2,2 Q 4.7,1 5.8,0",line=dict(color="#a8d9e3",width=33),layer="below")
    for pos in [1,2.7,4.4,6.1,7.8,9.5]:
        fig.add_shape(type="line",x0=0,x1=10,y0=pos,y1=pos,line=dict(color="#e0e9ed",width=2),layer="below")
        fig.add_shape(type="line",x0=pos,x1=pos,y0=0,y1=10,line=dict(color="#e0e9ed",width=2),layer="below")
    for _,row in predictions.iterrows():
        x,y = coordinates[row.area_id]
        fig.add_trace(go.Scatter(x=[x],y=[y],mode="markers+text",name=row.area_name,text=[row.area_name],
            textposition="top center",textfont=dict(size=11,color="#344f5c"),
            marker=dict(size=15+row.priority_score/5,color=COLORS[row.score_band],opacity=.9,line=dict(width=3,color="white")),
            customdata=[[row.area_id,row.priority_score,row.confidence,int(row.rescue_teams)]],
            hovertemplate="<b>"+escape(row.area_name)+"</b><br>Score: %{customdata[1]:.1f}<br>Confidence: %{customdata[2]:.0%}<br>Rescue teams: %{customdata[3]}<extra></extra>"))
    styled_chart(fig,420)
    fig.update_layout(showlegend=False,clickmode="event+select",dragmode="pan",plot_bgcolor="#edf4f5",margin=dict(l=5,r=5,t=10,b=5))
    fig.update_xaxes(visible=False,range=[0,10],fixedrange=False)
    fig.update_yaxes(visible=False,range=[0,10],scaleanchor="x",scaleratio=1)
    return fig

def selectable_map(predictions,key):
    event = st.plotly_chart(area_map(predictions),key=key,on_select="rerun",selection_mode="points",width="stretch",config={"displaylogo":False,"scrollZoom":False})
    st.caption("Fictional city schematic · marker size reflects priority · color indicates score band. Click an area to inspect it; positions are illustrative.")
    if event and event.selection.points:
        custom = event.selection.points[-1].get("customdata")
        if custom:
            return custom[0]
    return None

def area_profile(row):
    st.markdown(f"**{row.area_name}** · {row.area_category}")
    a,b,c=st.columns(3)
    a.metric("Priority",f"{row.priority_score:.1f}")
    b.metric("Flood depth",f"{row.flood_level:.2f} m")
    c.metric("Class probability",f"{row.confidence:.0%}")
    st.progress(float(row.priority_score)/100,text=f"{row.score_band} priority · rank {int(row['rank'])} of 12")
    if row.mandatory_review:
        st.warning("Mandatory human review: confidence or data-quality threshold triggered.")
    st.caption(f"{int(row.population):,} residents (synthetic) · {int(row.rescue_teams)} recommended rescue teams")

def timeline(record):
    stages=[("Observation retained",f"{record['input_record_identifier']} · dataset {record['dataset_version']}"),
            ("Recommendation generated",f"{record['prediction']} · score {record['priority_score']:.2f} · {record['confidence']:.0%} confidence"),
            ("Explanation captured",f"{record['explanation_method']} · {record['explanation_units']}"),
            ("Human review",f"{record['human_decision']} · {record['human_reviewer'] or 'Awaiting coordinator'}"),
            ("Final authority",record['responsible_authority'] or "Pending authorization; no final allocation")]
    for title,detail in stages:
        st.markdown(f'<div class="trail"><div class="trail-title">{escape(title)}</div><div class="trail-text">{escape(detail)}</div></div>',unsafe_allow_html=True)
