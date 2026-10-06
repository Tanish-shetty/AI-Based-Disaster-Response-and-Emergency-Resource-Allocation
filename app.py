"""Streamlit demonstration: run with python -m streamlit run app.py."""
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.config import ROOT, LABELS, FEATURES
from src.prediction import load_bundle
from src.ethical_simulation import SCENARIOS, run_scenario
from src.explainability import explain_record
from src.accountability import AuditStore, REVIEWERS, AUTHORITIES, readiness_score, clean_json
from src.resource_allocation import DEFAULT_BUDGET
from src.governance import MATRIX, PRINCIPLES, FRAMEWORK, STAKEHOLDERS
from src.evaluation import disparity_table
from src.preprocessing import validate_features
from src.ui import inject_styles, hero, section, styled_chart, queue_card, decision_flow, selectable_map, area_profile, timeline, COLORS

st.set_page_config(page_title="Flood Response | Accountability Lab", page_icon="⚖️", layout="wide")
inject_styles()

@st.cache_resource
def bundles():
    return load_bundle(), load_bundle(True)

@st.cache_data
def explanations(inputs, model_version, _bundle):
    return {row.area_id: explain_record(inputs.loc[[index]], _bundle) for index, row in inputs.iterrows()}

try:
    bundle, under_bundle = bundles()
except FileNotFoundError as error:
    st.error(str(error))
    st.code("python -m src.train")
    st.stop()

data = pd.read_csv(ROOT/"data/raw/demo_incident.csv")
st.sidebar.markdown('<div class="brand"><div class="brand-icon">◈</div><div><div class="brand-name">Accountability Lab</div><div class="brand-sub">FLOOD RESPONSE STUDY</div></div></div>',unsafe_allow_html=True)
st.sidebar.caption("EXPLORE THE DECISION CHAIN")
pages = ["Overview", "Disaster Scenario", "AI Priority Analysis", "Explainable AI", "Ethical Risk Simulator",
         "Human Review", "Accountability Audit", "Stakeholder Accountability", "Results & Findings", "Recommendations"]
page = st.sidebar.radio("Workspace", pages, key="workspace",label_visibility="collapsed")
st.sidebar.divider()
scenario = st.sidebar.selectbox("Data-quality scenario", SCENARIOS)
threshold = st.sidebar.slider("Mandatory review confidence threshold", .5, .95, .7, .05)
with st.sidebar.expander("Resource budget", expanded=False):
    budget = {r: int(st.number_input(r.replace("_", " ").title(), 0, 200, total, 1)) for r, total in DEFAULT_BUDGET.items()}
st.sidebar.markdown('<div class="sidebar-note"><b>Academic simulation</b><br>Reproducible seed 42. No actual citizen or patient data. Recommendations always require human authorization.</div>',unsafe_allow_html=True)

run = run_scenario(data, scenario, bundle, budget, threshold, under_bundle)
predictions, comparison = run["predictions"], run["comparison"]
active = run["bundle"]
exps = explanations(run["inputs"], active["metadata"]["model_version"], active)
store = AuditStore()
decision_ids = store.log_recommendations(predictions, run["inputs"], active, exps, scenario, budget, threshold)
all_records = store.records()
current_records = [r for r in all_records if r["decision_id"] in decision_ids]
finalized = all(r["final_decision"] is not None for r in current_records)
hero(page,scenario,finalized)
meta = bundle["metadata"]
selected_metrics = meta["test"][meta["model_name"]]
readiness = readiness_score({
    "Explainability": all(e["method"] == "SHAP" for e in exps.values()),
    "Human Oversight": finalized,
    "Auditability": store.verify_integrity() and len(current_records) == len(data),
    "Data Quality": run["inputs"][FEATURES].isna().sum().sum() == 0 and run["inputs"].sensor_reliability.ge(.7).all(),
    "Model Reliability": selected_metrics["classification_report"]["High"]["recall"] >= .8 and selected_metrics["classification_report"]["Critical"]["support"] >= 30,
    "Documentation": (ROOT/"reports/PROJECT_REPORT.md").exists(), "Monitoring": False})

table_columns = ["rank", "area_name", "priority_score", "prediction", "score_band", "confidence", *DEFAULT_BUDGET, "review_status"]

def ranking_table(frame=None,selectable=False):
    frame = predictions if frame is None else frame
    config = {"priority_score":st.column_config.ProgressColumn("Priority score",min_value=0,max_value=100,format="%.1f"),
              "confidence":st.column_config.ProgressColumn("Class probability",min_value=0,max_value=1,format="%.2f"),
              "area_name":st.column_config.TextColumn("Area",width="medium"),"rank":st.column_config.NumberColumn("Rank",width="small")}
    if selectable:
        return st.dataframe(frame[table_columns],hide_index=True,width="stretch",column_config=config,
                            on_select="rerun",selection_mode="single-row",key="priority_table")
    st.dataframe(frame[table_columns],hide_index=True,width="stretch",column_config=config)

def score_chart(frame=None):
    frame = predictions if frame is None else frame
    fig = px.bar(frame,x="priority_score",y="area_name",color="score_band",orientation="h",
                 category_orders={"area_name":frame.area_name.tolist()[::-1],"score_band":LABELS},
                 color_discrete_map=COLORS,range_x=[0,100],labels={"priority_score":"Priority score (0–100)","area_name":""})
    st.plotly_chart(styled_chart(fig,430),width="stretch",config={"displaylogo":False})

def navigate(destination):
    st.session_state.workspace = destination

def download_csv(frame,label,filename):
    st.download_button(label,frame.to_csv(index=False),filename,"text/csv",width="stretch")

if page == "Overview":
    a,b,c,d = st.columns(4)
    a.metric("Affected areas",len(data),"One fictional flood incident",delta_color="off")
    b.metric("Rescue teams",budget["rescue_teams"],"Limited central resources",delta_color="off")
    c.metric("Mandatory review",int(predictions.mandatory_review.sum()),"Confidence + data-quality flags",delta_color="off")
    d.metric("Accountability readiness",f"{readiness['score']:.0f}/100","Project-defined checklist",delta_color="off")
    section("INCIDENT EXPLORER")
    left,right=st.columns([1.8,1],gap="large")
    with left:
        with st.container(border=True):
            st.subheader("A city under pressure")
            clicked=selectable_map(predictions,"overview_map")
            if clicked:
                area_profile(predictions.loc[predictions.area_id.eq(clicked)].iloc[0])
            else:
                st.caption("Select an area marker to reveal its score, flood conditions and recommended teams.")
    with right:
        section("PRIORITY QUEUE")
        for _,row in predictions.head(4).iterrows():
            queue_card(row)
        st.button("Explore the full ranking →",on_click=navigate,args=("AI Priority Analysis",),width="stretch",type="primary")
        st.button("Test imperfect data →",on_click=navigate,args=("Ethical Risk Simulator",),width="stretch")
        with st.container(border=True):
            st.markdown("**A recommendation is still pending**" if not finalized else "**Portfolio authorization recorded**")
            st.caption("The AI proposes assistance. A coordinator reviews evidence and a final authority authorizes the complete plan.")
            st.button("Open human review →",on_click=navigate,args=("Human Review",),width="stretch")
    section("THE ACCOUNTABILITY QUESTION")
    st.subheader("Who is answerable when AI recommends the wrong allocation?")
    st.write("A simulated flood affects twelve urban areas. Scarce teams, ambulances, supplies and shelter assistance must be distributed. An AI ranks need from imperfect observations, while a coordinator and final authority remain responsible for reviewing the plan.")
    decision_flow(finalized)
    st.write("The system records pending recommendations automatically. A final plan exists only after explicit human sign-off. Ethical, technical and organizational responsibility may be shared; this project does not determine legal liability.")
elif page == "Disaster Scenario":
    st.subheader("DEMO-FLOOD-01 • twelve fictional areas")
    st.write("The complete-data baseline is a separately generated incident. True severity is a hidden simulator reference, excluded from model inputs.")
    category=st.multiselect("Area categories",sorted(data.area_category.unique()),default=sorted(data.area_category.unique()))
    visible=predictions.loc[predictions.area_category.isin(category)]
    if visible.empty:
        st.info("Select at least one area category to explore.")
    else:
        left,right=st.columns([1.7,1],gap="large")
        with left:
            clicked=selectable_map(visible,"disaster_map")
        with right:
            if clicked and clicked in visible.area_id.values:
                st.session_state["disaster_area"]=visible.loc[visible.area_id.eq(clicked),"area_name"].iloc[0]
            if st.session_state.get("disaster_area") not in visible.area_name.tolist():
                st.session_state["disaster_area"]=visible.area_name.iloc[0]
            selected=st.selectbox("Inspect an affected area",visible.area_name.tolist(),key="disaster_area")
            area_profile(visible.loc[visible.area_name.eq(selected)].iloc[0])
            st.markdown("**Central resource budget**")
            st.dataframe(pd.DataFrame([(r.replace("_"," ").title(),v) for r,v in budget.items()],columns=["Resource","Available"]),hide_index=True,width="stretch")
        observed,relationships=st.tabs(["Observed records","Risk relationships"])
        with observed:
            inputs=run["inputs"].loc[run["inputs"].area_id.isin(visible.area_id)]
            st.dataframe(inputs[["area_name","area_category",*FEATURES[:-1],"true_severity","priority_label"]],hide_index=True,width="stretch")
            download_csv(inputs,"Download observed records","observed_records.csv")
        with relationships:
            st.plotly_chart(styled_chart(px.scatter(visible,x="flood_level",y="vulnerable_population",size="population",color="area_category",hover_name="area_name",labels={"vulnerable_population":"Vulnerable population fraction","flood_level":"Flood depth (m)"})),width="stretch")
elif page == "AI Priority Analysis":
    st.subheader("Recommendations awaiting human authorization" if not finalized else "Reviewed portfolio • recommendation history retained")
    search_col,severity_col,review_col=st.columns([1.4,1.5,1])
    search=search_col.text_input("Search areas",placeholder="e.g. Riverside")
    severity=severity_col.multiselect("Priority bands",LABELS,default=LABELS)
    only_review=review_col.checkbox("Mandatory review only")
    visible=predictions.loc[predictions.area_name.str.contains(search,case=False,regex=False)&predictions.score_band.isin(severity)]
    if only_review:
        visible=visible.loc[visible.mandatory_review]
    if visible.empty:
        st.info("No areas match these filters. Adjust the search, bands or review filter.")
    else:
        ranks,allocation=st.tabs(["Rankings & area details","Resource distribution"])
        with ranks:
            event=ranking_table(visible,selectable=True)
            st.caption("Select a table row to inspect its recommendation and data-quality flags.")
            row=visible.iloc[event.selection.rows[0]] if event.selection.rows and event.selection.rows[0]<len(visible) else visible.iloc[0]
            with st.container(border=True):
                area_profile(row)
            score_chart(visible)
        with allocation:
            resource=st.selectbox("Resource to visualize",list(DEFAULT_BUDGET),format_func=lambda r:r.replace("_"," ").title())
            fig=px.bar(visible,x="area_name",y=resource,color="score_band",color_discrete_map=COLORS,labels={"area_name":"","score_band":"Priority"})
            st.plotly_chart(styled_chart(fig),width="stretch")
            st.caption(f"Across the full portfolio: {int(predictions[resource].sum())} of {budget[resource]} units recommended. Filtering affects this view only.")
        download_csv(visible[table_columns],"Download filtered recommendations","priority_recommendations.csv")
    st.write("Score = 20·P(Low) + 55·P(Medium) + 77·P(High) + 95·P(Critical). Confidence is the largest predicted class probability, not a guarantee of safety. Prediction (most probable class) and score band can differ.")
    st.write("Integer resource quotas are proportional to score. Largest fractional remainders receive remaining units; equal remainders follow rank then area ID. This deliberately simple policy has no logistics optimizer, minimum coverage guarantee or measured lives-saved estimate.")
    st.caption("All allocations are simulated. Low-confidence, incomplete or unreliable-sensor inputs receive mandatory-review flags; every portfolio still requires human sign-off.")
elif page == "Explainable AI":
    selected = st.selectbox("Area to explain", predictions.area_name.tolist())
    row = predictions.loc[predictions.area_name.eq(selected)].iloc[0]
    explanation = exps[row.area_id]
    a,b,c = st.columns(3)
    a.metric("Predicted class", row.prediction)
    b.metric("Priority score", f"{row.priority_score:.2f}")
    c.metric("Class probability", f"{row.confidence:.1%}")
    st.write(f"{explanation['method']} contributions in **{explanation['units']}**. Positive values support the selected predicted class; negative values oppose it. They do not directly describe priority-score points.")
    contributions,probabilities,observations=st.tabs(["Feature contributions","Class probabilities","Observed data"])
    with contributions:
        count_col,direction_col=st.columns(2)
        count=count_col.slider("Number of features",5,len(explanation["features"]),min(10,len(explanation["features"])))
        direction=direction_col.selectbox("Contribution direction",["All contributions","Positive only","Negative only"])
        feature_table=explanation["features"]
        if direction == "Positive only":
            feature_table=feature_table.loc[feature_table.contribution>0]
        elif direction == "Negative only":
            feature_table=feature_table.loc[feature_table.contribution<0]
        feature_table=feature_table.head(count)
        st.plotly_chart(styled_chart(px.bar(feature_table.sort_values("contribution"),x="contribution",y="feature",orientation="h",color="contribution",color_continuous_scale=[[0,"#e69872"],[.5,"#dbe8e6"],[1,"#118e81"]]),430),width="stretch")
        with st.expander("Inspect all computed contributions"):
            st.dataframe(explanation["features"],hide_index=True,width="stretch")
        download_csv(explanation["features"],"Download this explanation","area_explanation.csv")
    with probabilities:
        source=run["inputs"].loc[run["inputs"].area_id.eq(row.area_id)]
        p=active["pipeline"].predict_proba(validate_features(source))[0]
        frame=pd.DataFrame({"Class":active["pipeline"].classes_,"Probability":p})
        st.plotly_chart(styled_chart(px.bar(frame,x="Class",y="Probability",color="Class",color_discrete_map=COLORS,range_y=[0,1],category_orders={"Class":LABELS})),width="stretch")
        st.caption("These are the model's uncalibrated probabilities. The priority score averages all four class anchors.")
    with observations:
        source=run["inputs"].loc[run["inputs"].area_id.eq(row.area_id),FEATURES].T.reset_index()
        source.columns=["Feature","Observed value"]
        source["Observed value"]=source["Observed value"].map(lambda v:"Missing — pipeline imputes" if pd.isna(v) else str(v))
        st.dataframe(source,hide_index=True,width="stretch")
    if explanation["method"] == "SHAP":
        st.caption(f"Base {explanation['base_value']:.5f} + all contributions = {explanation['reconstructed_output']:.5f}; model output = {explanation['explained_output']:.5f}.")
    st.info(explanation["warning"])
elif page == "Ethical Risk Simulator":
    st.subheader(scenario)
    st.write("Change the sidebar scenario to rerun the model and allocation. Ground-truth need is held constant; only observations and, for underrepresentation, the deliberately reduced-training model change.")
    a,b,c,d = st.columns(4)
    indicators = run["indicators"]
    a.metric("Mean absolute score change", f"{indicators['mean_absolute_score_change']:.2f}")
    b.metric("Areas changing rank", indicators["changed_ranks"])
    c.metric("Rescue units reassigned", indicators["rescue_units_reassigned"])
    d.metric("Missed high-severity areas", indicators["missed_high_severity_areas"])
    scores_tab,resource_tab,groups_tab=st.tabs(["Priority & ranking changes","Resource transfers","Group diagnostics"])
    with scores_tab:
        mode=st.radio("Comparison view",["Before & after","Score change","Rank movement"],horizontal=True)
        changed_only=st.checkbox("Show changed areas only")
        visible=comparison.loc[comparison.priority_score_change.abs()>1e-8] if changed_only else comparison
        if visible.empty:
            st.info("No score changes in this condition. Select a different scenario to explore its effect.")
        elif mode == "Before & after":
            long=visible.melt(id_vars=["area_name"],value_vars=["priority_score_baseline","priority_score"],var_name="Condition",value_name="Score")
            long["Condition"]=long.Condition.map({"priority_score_baseline":"Complete-data baseline","priority_score":"Active scenario"})
            st.plotly_chart(styled_chart(px.bar(long,x="area_name",y="Score",color="Condition",barmode="group",range_y=[0,100])),width="stretch")
        else:
            field="priority_score_change" if mode == "Score change" else "rank_change"
            fig=px.bar(visible.sort_values(field),x=field,y="area_name",orientation="h",color=field,color_continuous_scale=[[0,"#d97668"],[.5,"#e6eef0"],[1,"#139686"]],labels={"area_name":"",field:"Score change" if field=="priority_score_change" else "Rank movement (+ = worse)"})
            st.plotly_chart(styled_chart(fig,430),width="stretch")
        st.dataframe(visible[["area_name","priority_score_baseline","priority_score","priority_score_change","rank_baseline","rank","rank_change"]],hide_index=True,width="stretch")
    with resource_tab:
        resource=st.selectbox("Compare resource",list(DEFAULT_BUDGET),format_func=lambda r:r.replace("_"," ").title())
        long=comparison.melt(id_vars="area_name",value_vars=[resource+"_baseline",resource],var_name="Condition",value_name="Units")
        long["Condition"]=long.Condition.map({resource+"_baseline":"Baseline",resource:"Active scenario"})
        st.plotly_chart(styled_chart(px.bar(long,x="area_name",y="Units",color="Condition",barmode="group")),width="stretch")
        st.dataframe(comparison[["area_name",resource+"_baseline",resource,resource+"_change"]],hide_index=True,width="stretch")
    with groups_tab:
        st.dataframe(disparity_table(data,predictions),hide_index=True,width="stretch")
    download_csv(comparison,"Download the complete scenario comparison","scenario_comparison.csv")
    worst = comparison.loc[comparison.priority_score_change.idxmin()]
    st.info(f"{worst.area_name}: {worst.priority_score_change:+.2f} score points and {int(worst.rank_change):+d} ranking places versus baseline. A positive rank change means a worse position. Potential harms are unmet assistance and delayed response, not measured casualties.")
    st.caption("Twelve-area group differences are descriptive only. Underrepresentation combines reduced peripheral training coverage with missing/underreported peripheral input; it cannot isolate a causal training effect.")
elif page == "Human Review":
    st.subheader("Coordinator review and final authority sign-off")
    decision_flow(finalized)
    with st.expander("Inspect the model ranking and mandatory-review flags"):
        ranking_table()
    if finalized:
        st.success("This complete portfolio has been finalized. The audit page preserves the recommendation and final plan.")
        st.dataframe(pd.DataFrame([{**{"area_id":r["area_id"], "decision":r["human_decision"]}, **r["final_decision"]} for r in current_records]), hide_index=True)
    else:
        portfolio_id = current_records[0]["portfolio_id"]
        original=predictions[["area_id","area_name",*DEFAULT_BUDGET]].reset_index(drop=True)
        draft_key="draft_plan_"+portfolio_id
        epoch_key="editor_epoch_"+portfolio_id
        epoch=st.session_state.get(epoch_key,0)
        editor_key="final_plan_"+portfolio_id+(f"_{epoch}" if epoch else "")
        draft=st.session_state.get(draft_key,original).copy()
        section("1 / REVIEW AND REDISTRIBUTE")
        st.caption("Edit the portfolio directly or transfer a resource between two areas. Your final plan must remain within every budget.")
        with st.expander("Quick resource transfer",expanded=True):
            from_col,to_col,resource_col,amount_col=st.columns([1.25,1.25,1.1,.65])
            names=dict(zip(original.area_id,original.area_name))
            donor=from_col.selectbox("Transfer from",original.area_id.tolist(),format_func=lambda value:names[value],key="transfer_donor_"+portfolio_id)
            recipient=to_col.selectbox("Transfer to",original.area_id.tolist(),index=min(1,len(original)-1),format_func=lambda value:names[value],key="transfer_recipient_"+portfolio_id)
            resource=resource_col.selectbox("Resource",list(DEFAULT_BUDGET),format_func=lambda value:value.replace("_"," ").title(),key="transfer_resource_"+portfolio_id)
            amount=int(amount_col.number_input("Units",min_value=1,max_value=max(1,budget[resource]),value=1,step=1,key="transfer_amount_"+portfolio_id))
            transfer_col,reset_col=st.columns(2)
            if transfer_col.button("Apply transfer",width="stretch"):
                edits=st.session_state.get(editor_key,{"edited_rows":{},"added_rows":[],"deleted_rows":[]})
                transfer_plan=draft.copy()
                for row_index,changes in edits["edited_rows"].items():
                    for field,value in changes.items():
                        if field in DEFAULT_BUDGET:
                            transfer_plan.loc[int(row_index),field]=value
                donor_index=int(original.index[original.area_id.eq(donor)][0])
                recipient_index=int(original.index[original.area_id.eq(recipient)][0])
                donor_count=transfer_plan.loc[donor_index,resource]
                recipient_count=transfer_plan.loc[recipient_index,resource]
                if donor == recipient:
                    st.error("Choose two different areas for a transfer.")
                elif pd.isna(donor_count) or pd.isna(recipient_count) or donor_count<amount:
                    st.error("The selected area does not have enough units in the edited plan.")
                elif float(donor_count)!=int(donor_count) or float(recipient_count)!=int(recipient_count):
                    st.error("Use whole-number resource counts before applying a transfer.")
                elif recipient_count+amount>budget[resource]:
                    st.error("The resulting area allocation would exceed the resource budget.")
                else:
                    transfer_plan.loc[donor_index,resource]=int(donor_count)-amount
                    transfer_plan.loc[recipient_index,resource]=int(recipient_count)+amount
                    draft=transfer_plan
                    st.session_state[draft_key]=draft
                    epoch+=1
                    st.session_state[epoch_key]=epoch
                    editor_key="final_plan_"+portfolio_id+f"_{epoch}"
                    st.success(f"Transferred {amount} {resource.replace('_',' ')} from {names[donor]} to {names[recipient]}. Add the reason before authorization.")
            if reset_col.button("Restore AI proposal",width="stretch"):
                draft=original.copy()
                st.session_state[draft_key]=draft
                epoch+=1
                st.session_state[epoch_key]=epoch
                editor_key="final_plan_"+portfolio_id+f"_{epoch}"
        edited=st.data_editor(draft,key=editor_key,disabled=["area_id","area_name"],hide_index=True,num_rows="fixed",width="stretch",
            column_config={r:st.column_config.NumberColumn(r.replace("_"," ").title(),min_value=0,max_value=budget[r],step=1) for r in DEFAULT_BUDGET})
        totals=edited[list(DEFAULT_BUDGET)].sum()
        for column,(resource,total) in zip(st.columns(4),budget.items()):
            used=int(totals[resource])
            column.metric(resource.replace("_"," ").title(),f"{used} / {total}",f"{total-used} units remaining",delta_color="normal")
        section("2 / RECORD YOUR JUSTIFICATION")
        with st.form("review_form_"+portfolio_id):
            review_col,authority_col=st.columns(2)
            reviewer = review_col.selectbox("Synthetic human reviewer", REVIEWERS)
            authority = authority_col.selectbox("Synthetic responsible authority", AUTHORITIES)
            reason = st.text_area("Override reason (required for changed allocations; use simulated evidence only)")
            checked = st.checkbox("I reviewed the evidence and all mandatory-review flags, and authorize this simulated final plan.")
            submitted = st.form_submit_button("Authorize reviewed portfolio", type="primary")
        if submitted:
            if not checked:
                st.error("Explicit evidence review and authorization are required.")
            else:
                try:
                    allocations = {}
                    for _, item in edited.iterrows():
                        values = {r:item[r] for r in DEFAULT_BUDGET}
                        if any(pd.isna(v) or float(v) != int(v) for v in values.values()):
                            raise ValueError("Resource counts must be whole numbers.")
                        allocations[item.area_id] = {r:int(v) for r,v in values.items()}
                    store.review_portfolio(decision_ids, allocations, reviewer, authority, reason)
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
elif page == "Accountability Audit":
    st.subheader("Traceable recommendations and final decisions")
    st.success("Local event-chain integrity verified") if store.verify_integrity() else st.error("Audit integrity check failed")
    scope = st.checkbox("Only the current portfolio", value=True)
    records = current_records if scope else all_records
    first,second,third=st.columns(3)
    first.metric("Recorded recommendations",len(records))
    second.metric("Authorized decisions",sum(r["final_decision"] is not None for r in records))
    third.metric("Human overrides",sum(r["human_override"] for r in records))
    search_col,status_col=st.columns([2,1])
    search=search_col.text_input("Search the audit",placeholder="Area, decision ID, reviewer or override reason")
    status=status_col.selectbox("Decision status",["All decisions","Pending","Accept","Override"])
    records=[r for r in records if (status=="All decisions" or r["human_decision"]==status) and search.lower() in " ".join(str(r.get(k) or "") for k in ["area_id","decision_id","human_reviewer","override_reason"]).lower()]
    if not records:
        st.info("No audit entries match these filters.")
    else:
        summary_columns=["area_id","prediction","priority_score","confidence","human_decision","human_reviewer","responsible_authority","timestamp"]
        st.dataframe(pd.DataFrame(records)[summary_columns],hide_index=True,width="stretch")
        st.download_button("Export filtered audit JSON",json.dumps(clean_json(records),indent=2),"accountability_audit.json","application/json",width="stretch")
        selected=st.selectbox("Inspect decision",[r["decision_id"] for r in records],format_func=lambda value:value[-7:]+" · "+value[:12])
        record=next(r for r in records if r["decision_id"]==selected)
        trail_col,evidence_col=st.columns([1,1.7],gap="large")
        with trail_col:
            section("DECISION TIMELINE")
            timeline(record)
        with evidence_col:
            section("RETAINED EVIDENCE")
            recommendation_tab,input_tab,raw_tab=st.tabs(["Recommendation & review","Input snapshot","Full record"])
            with recommendation_tab:
                plan=pd.DataFrame([record["ai_recommendation"],record["final_decision"] or {}],index=["AI recommendation","Final authorized decision"]).T
                st.dataframe(plan,width="stretch")
                if record["override_reason"]:
                    st.info(record["override_reason"])
                st.dataframe(pd.DataFrame(record["top_explanation_features"]),hide_index=True,width="stretch")
                st.caption(f"Model {record['model_version']} · dataset {record['dataset_version']}")
            with input_tab:
                st.json(record["input_snapshot"])
            with raw_tab:
                st.json(record)
    st.caption("Append-only recommendation and review events; input snapshots and hashes preserve provenance. Local hash checking detects changes, but does not protect against an administrator rewriting the database. Synthetic aliases are not authentication.")
elif page == "Stakeholder Accountability":
    st.subheader("Shared responsibilities, evidence before blame")
    selected_stakeholder=st.selectbox("Explore a stakeholder's duties",["All stakeholders",*STAKEHOLDERS])
    visible=MATRIX if selected_stakeholder=="All stakeholders" else MATRIX.loc[MATRIX["Stakeholder(s)"].str.contains(selected_stakeholder,regex=False)]
    st.dataframe(visible, hide_index=True, width="stretch")
    for stakeholder, responsibility in STAKEHOLDERS.items():
        with st.expander(stakeholder):
            st.write(responsibility)
    st.dataframe(PRINCIPLES, hide_index=True, width="stretch")
    st.info("Ethical accountability means giving reasons and accepting scrutiny. Technical responsibility concerns engineering work. Organizational responsibility concerns deployment, resources and governance. Legal liability requires applicable law and facts; this academic framework does not determine it.")
elif page == "Results & Findings":
    st.subheader("Measured results from actual execution")
    metrics = pd.DataFrame([{ "model":name, **{k:v for k,v in m.items() if isinstance(v,(int,float))}} for name,m in meta["test"].items()])
    metric=st.selectbox("Compare models by",["f1_macro","accuracy","recall_macro","precision_macro","roc_auc_ovr_macro"],format_func=lambda value:value.replace("_"," ").title())
    st.plotly_chart(styled_chart(px.bar(metrics,x="model",y=metric,color="model",range_y=[0,1],text_auto=".3f",labels={"model":"",metric:metric.replace("_"," ").title()}),290),width="stretch")
    with st.expander("Full measured model metrics"):
        st.dataframe(metrics, hide_index=True, width="stretch")
    st.write(f"Selected model: **{meta['model_name']}**, using validation macro F1. Dataset split: {meta['split_counts']}. Entire incidents stay within one split.")
    confusion_col,recall_col=st.columns(2)
    with confusion_col:
        section("WHERE THE MODEL GETS IT WRONG")
        st.plotly_chart(styled_chart(px.imshow(selected_metrics["confusion_matrix"],x=LABELS,y=LABELS,text_auto=True,color_continuous_scale="Teal",labels={"x":"Predicted","y":"True","color":"Count"}),350),width="stretch")
    with recall_col:
        section("RECALL ACROSS SEVERITY CLASSES")
        class_frame=pd.DataFrame([{"Class":label,"Recall":selected_metrics["classification_report"][label]["recall"],"Test examples":int(selected_metrics["classification_report"][label]["support"])} for label in LABELS])
        st.plotly_chart(styled_chart(px.bar(class_frame,x="Class",y="Recall",color="Class",color_discrete_map=COLORS,range_y=[0,1],hover_data=["Test examples"],text_auto=".0%"),350),width="stretch")
    st.warning(f"High-class test recall is {selected_metrics['classification_report']['High']['recall']:.1%}; Critical test support is only {int(selected_metrics['classification_report']['Critical']['support'])}. Overall accuracy hides consequential errors. Confidence probabilities are not independently calibrated.")
    result_path = ROOT/"reports/scenario_summary.csv"
    if result_path.exists():
        st.dataframe(pd.read_csv(result_path), hide_index=True, width="stretch")
        st.caption("Saved experiments use the default resource budgets and 70% confidence threshold. Live scenario pages use the current sidebar settings.")
    st.metric(readiness["label"], f"{readiness['score']:.1f}/100")
    dimensions=pd.DataFrame(readiness["dimensions"].items(),columns=["Dimension","Checklist points"])
    st.plotly_chart(styled_chart(px.bar(dimensions,y="Dimension",x="Checklist points",orientation="h",range_x=[0,100],color="Checklist points",color_continuous_scale=[[0,"#e0a48e"],[1,"#109482"]]),300),width="stretch")
    st.caption("Equal-weight binary checklist; a project-defined measure, not an international or legal standard. Human Oversight requires current portfolio sign-off. Reliability requires High recall ≥80% and Critical test support ≥30; Monitoring remains zero because sustained deployment monitoring is absent. Data Quality checks missing values and sensor reliability, and cannot detect every stale observation.")
elif page == "Recommendations":
    st.subheader("AI Disaster Response Accountability Framework")
    from html import escape
    descriptions=["Retain source identifiers, collection context and dataset versions.","Check completeness, plausible ranges and evidence freshness.","Publish intended use, class errors and known limitations.","Link every recommendation to the model release that generated it.","Expose actual feature contributions and their units.","Escalate uncertainty while requiring sign-off for every plan.","Provide local evidence, time and authority to challenge advice.","Require a reason and conserve budgets when changing allocations.","Preserve the observation, advice, review and final authority.","Reconstruct the chain and investigate failures using evidence.","Assign owners for drift checks, incident response and suspension.","Document shared duties across all six stakeholder roles."]
    stage=st.segmented_control("Explore safeguards by stage",["All safeguards","Data & model","Human decision","Audit & governance"],default="All safeguards")
    ranges={"All safeguards":range(12),"Data & model":range(5),"Human decision":range(5,8),"Audit & governance":range(8,12)}
    columns=st.columns(3)
    for offset,index in enumerate(ranges[stage or "All safeguards"]):
        with columns[offset%3]:
            st.markdown(f'<div class="safeguard"><div class="num">SAFEGUARD {index+1:02d}</div><h4>{escape(FRAMEWORK[index])}</h4><p>{escape(descriptions[index])}</p></div>',unsafe_allow_html=True)
    with st.expander("View the complete framework flow"):
        st.graphviz_chart('digraph {rankdir=LR;node [shape=box,style=rounded]; '+" -> ".join('"'+s+'"' for s in FRAMEWORK)+';}')
    st.write("Verify timestamps and field reports, inspect uncertainty, require meaningful human review, preserve model/input provenance, test underserved areas, and conduct post-incident scrutiny. Before any operational use, replace synthetic data with governed representative evidence and validate logistics, security, reliability and organizational procedures.")
    st.info("The proposed framework supports responsibility attribution through evidence. It does not certify safety, decide legal liability or prove that any stakeholder caused real harm.")

st.divider()
st.caption(f"Active model: {active['metadata']['model_name']} | {active['metadata']['model_version']} | {meta['dataset_version']} | Scenario: {scenario}")
