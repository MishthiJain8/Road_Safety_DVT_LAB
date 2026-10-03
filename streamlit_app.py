import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Road Accident & Traffic Safety Analytics", page_icon="🚦", layout="wide")

DATA_FILE = Path(__file__).with_name("bad-drivers.csv")
SOURCE_URL = "https://raw.githubusercontent.com/fivethirtyeight/data/master/bad-drivers/bad-drivers.csv"
REPO_URL = "https://github.com/fivethirtyeight/data/tree/master/bad-drivers"

@st.cache_data
def load_data():
    d = pd.read_csv(DATA_FILE)
    d = d.rename(columns={
        "Number of drivers involved in fatal collisions per billion miles": "Fatal collision rate",
        "Percentage Of Drivers Involved In Fatal Collisions Who Were Speeding": "Speeding %",
        "Percentage Of Drivers Involved In Fatal Collisions Who Were Alcohol-Impaired": "Alcohol-impaired %",
        "Percentage Of Drivers Involved In Fatal Collisions Who Were Not Distracted": "Not distracted %",
        "Percentage Of Drivers Involved In Fatal Collisions Who Had Not Been Involved In Any Previous Accidents": "No previous accidents %",
        "Car Insurance Premiums ($)": "Insurance premium ($)",
        "Losses incurred by insurance companies for collisions per insured driver ($)": "Insurance losses ($)",
    })

    codes = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE',
        'District of Columbia':'DC','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA',
        'Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN',
        'Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
        'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI',
        'South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA',
        'West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'
    }
    regions = {
        'CT':'Northeast','ME':'Northeast','MA':'Northeast','NH':'Northeast','RI':'Northeast','VT':'Northeast','NJ':'Northeast','NY':'Northeast','PA':'Northeast',
        'IL':'Midwest','IN':'Midwest','MI':'Midwest','OH':'Midwest','WI':'Midwest','IA':'Midwest','KS':'Midwest','MN':'Midwest','MO':'Midwest','NE':'Midwest','ND':'Midwest','SD':'Midwest',
        'DE':'South','FL':'South','GA':'South','MD':'South','NC':'South','SC':'South','VA':'South','DC':'South','WV':'South','AL':'South','KY':'South','MS':'South','TN':'South','AR':'South','LA':'South','OK':'South','TX':'South',
        'AZ':'West','CO':'West','ID':'West','MT':'West','NV':'West','NM':'West','UT':'West','WY':'West','AK':'West','CA':'West','HI':'West','OR':'West','WA':'West'
    }
    d["Code"] = d["State"].map(codes)
    d["Region"] = d["Code"].map(regions)
    return d

df = load_data()

st.title("Road Accident & Traffic Safety Analytics")
st.write("**Data Detective Challenge – Group 1**")
st.caption("CCP7005 Data Visualization Techniques | B.Tech. Cyber Security | Semester VII | Session 2026–27")

with st.expander("Group members", expanded=False):
    st.write("1 – Arya Bhangadia")
    st.write("18 – Harshvardhan Tendulka")
    st.write("36 – Mishthi Jain")
    st.write("54 – Shreya Mishra")

st.markdown(
    "**Objective:** To compare road-safety patterns across U.S. states and study how fatal-collision rates relate to speeding, "
    "alcohol impairment and insurance variables."
)

with st.sidebar:
    st.header("Filters")
    all_regions = sorted(df["Region"].dropna().unique())
    selected_regions = st.multiselect("Region", all_regions, default=all_regions)
    min_rate, max_rate = float(df["Fatal collision rate"].min()), float(df["Fatal collision rate"].max())
    selected_rate = st.slider("Fatal collision rate", min_rate, max_rate, (min_rate, max_rate), step=0.1)
    state_search = st.text_input("Search state", placeholder="Example: Texas")
    st.divider()
    st.caption("Use these controls during the presentation to show that the dashboard is interactive.")

filtered = df[
    df["Region"].isin(selected_regions)
    & df["Fatal collision rate"].between(selected_rate[0], selected_rate[1])
].copy()
if state_search.strip():
    filtered = filtered[filtered["State"].str.contains(state_search.strip(), case=False, na=False)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("States shown", len(filtered))
c2.metric("Average fatal-collision rate", f"{filtered['Fatal collision rate'].mean():.1f}" if len(filtered) else "–")
if len(filtered):
    max_row = filtered.loc[filtered["Fatal collision rate"].idxmax()]
    c3.metric("Highest state", max_row["State"], f"{max_row['Fatal collision rate']:.1f}")
    c4.metric("Median rate", f"{filtered['Fatal collision rate'].median():.1f}")
else:
    c3.metric("Highest state", "–")
    c4.metric("Median rate", "–")

st.subheader("Q1. How does the fatal-collision rate vary geographically?")
fig_map = px.choropleth(
    filtered,
    locations="Code",
    locationmode="USA-states",
    color="Fatal collision rate",
    scope="usa",
    hover_name="State",
    hover_data={"Code": False, "Region": True, "Fatal collision rate": ":.1f"},
    color_continuous_scale="Reds",
    labels={"Fatal collision rate": "Fatal-collision rate"},
)
fig_map.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=430)
st.plotly_chart(fig_map, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Q2. Which states have the highest rates?")
    top = filtered.nlargest(min(10, len(filtered)), "Fatal collision rate").sort_values("Fatal collision rate") if len(filtered) else filtered
    fig_bar = px.bar(
        top, x="Fatal collision rate", y="State", orientation="h",
        labels={"Fatal collision rate": "Drivers in fatal collisions per billion miles"},
    )
    fig_bar.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with right:
    st.subheader("Q3. Is alcohol impairment related to the fatal-collision rate?")
    fig_scatter = px.scatter(
        filtered, x="Alcohol-impaired %", y="Fatal collision rate", color="Region",
        hover_name="State", labels={"Alcohol-impaired %": "Alcohol-impaired drivers (%)"},
    )
    if len(filtered) >= 2 and filtered["Alcohol-impaired %"].nunique() > 1:
        x = filtered["Alcohol-impaired %"].to_numpy(dtype=float)
        y = filtered["Fatal collision rate"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 100)
        fig_scatter.add_trace(go.Scatter(x=xs, y=slope*xs+intercept, mode="lines", name="Trend line", line=dict(dash="dash")))
    fig_scatter.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_scatter, use_container_width=True)

left2, right2 = st.columns(2)
with left2:
    st.subheader("Q4. How do regions compare?")
    fig_box = px.box(filtered, x="Region", y="Fatal collision rate", points="all", hover_name="State")
    fig_box.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

with right2:
    st.subheader("Q5. Which numerical variables move together?")
    numeric_cols = [
        "Fatal collision rate", "Speeding %", "Alcohol-impaired %", "Not distracted %",
        "No previous accidents %", "Insurance premium ($)", "Insurance losses ($)"
    ]
    corr = filtered[numeric_cols].corr().round(2) if len(filtered) >= 2 else df[numeric_cols].corr().round(2)
    fig_heat = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        zmin=-1, zmax=1, colorscale="RdBu", text=corr.values, texttemplate="%{text}",
        colorbar=dict(title="r")
    ))
    fig_heat.update_layout(height=430, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_heat, use_container_width=True)

st.divider()
st.header("Major findings")
full_corr_alcohol = df["Fatal collision rate"].corr(df["Alcohol-impaired %"])
full_corr_speeding = df["Fatal collision rate"].corr(df["Speeding %"])
findings = [
    "North Dakota and South Carolina have the highest fatal-collision rate in the dataset (23.9 drivers per billion miles).",
    "District of Columbia has the lowest value (5.9), followed by Massachusetts (8.2).",
    f"Alcohol-impaired percentage has only a weak positive correlation with the fatal-collision rate (r = {full_corr_alcohol:.2f}); this does not prove causation.",
    f"Speeding percentage has almost no linear correlation with the total fatal-collision rate in this small state-level dataset (r = {full_corr_speeding:.2f}).",
    "Insurance premium/loss values do not directly follow the fatal-collision ranking, showing that insurance cost is affected by more than one factor.",
]
for i, item in enumerate(findings, 1):
    st.write(f"{i}. {item}")

st.header("Actionable recommendations")
st.write("1. States with high fatal-collision rates should be prioritized for road-safety review and targeted enforcement.")
st.write("2. Alcohol-impaired driving should be monitored as one risk factor, but decisions should not be based on a single correlation.")
st.write("3. Combine crash data with road type, weather, seat-belt use, time and vehicle data for stronger future analysis.")

st.header("Wrong Visualization Challenge")
st.write("**Question selected:** Which states have the highest fatal-collision rates?")
wc1, wc2 = st.columns(2)
wrong_top = df.nlargest(8, "Fatal collision rate")
with wc1:
    st.write("**Correct: sorted bar chart**")
    correct = px.bar(wrong_top.sort_values("Fatal collision rate"), x="Fatal collision rate", y="State", orientation="h")
    correct.update_layout(height=390, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(correct, use_container_width=True)
with wc2:
    st.write("**Wrong: pie chart**")
    wrong = px.pie(wrong_top, values="Fatal collision rate", names="State")
    wrong.update_layout(height=390, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(wrong, use_container_width=True)
st.info("The bar chart is appropriate because it compares state values on a common scale. The pie chart is misleading because these rates are not parts of one total, so the slices do not represent a meaningful whole.")

st.header("AI as a Critic")
st.write("**Visualization reviewed:** Alcohol-impaired % vs fatal-collision rate scatter plot")
st.write("**AI recommendation:** Add a trend line, make state names available on hover, and avoid saying that alcohol percentage causes the total fatal-collision rate.")
st.write("**Team decision:** PARTIALLY ACCEPTED")
st.write("**Team justification:** We accepted the trend line and hover labels because they improve interpretation. We also changed our wording to 'relationship' instead of 'cause'. We kept region colors because they help us compare broad geographical groups during the presentation.")

st.header("Dataset discovery summary")
st.write("**Records:** 51 | **Original attributes:** 8")
st.write("**Numerical variables:** fatal-collision rate, four driver percentages, insurance premium and insurance loss")
st.write("**Categorical/geographical variable:** State. We added state code and U.S. region only for visualization/filtering.")
st.write(f"**Missing values:** {int(df.isna().sum().sum())} | **Duplicate rows:** {int(df.duplicated().sum())}")
st.write("**Temporal variable:** Not available in this dataset. This is a state-level cross-sectional dataset.")

with st.expander("Dataset source and raw data", expanded=False):
    st.markdown(f"**FiveThirtyEight data repository:** {REPO_URL}")
    st.markdown(f"**Raw CSV:** {SOURCE_URL}")
    st.dataframe(df.drop(columns=["Code", "Region"]), use_container_width=True, hide_index=True)
    st.download_button("Download dataset used in this dashboard", DATA_FILE.read_bytes(), file_name="bad-drivers.csv", mime="text/csv")

st.caption("Prepared by Group 1 for the Data Detective Challenge. Dataset values are used for educational analysis; correlations are descriptive and do not establish causation.")
