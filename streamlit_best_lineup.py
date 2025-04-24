
import streamlit as st
import pandas as pd
import itertools
import plotly.express as px
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_csv("Interactive Stats - Stats .csv")
    df = df[df["Player"].str.lower() != "team"]
    df["Player"] = df["Player"].str.strip()
    df["OBP"] = pd.to_numeric(df["OBP"], errors="coerce")
    df["SLG"] = pd.to_numeric(df["SLG"], errors="coerce")
    df = df.dropna(subset=["OBP", "SLG"])
    df["Estimated Runs"] = (df["OBP"] + df["SLG"]) / 2
    return df

overall_df = load_data()

st.title("🔁 Best Lineup Finder - Lock 1 Player")

locked_player = st.selectbox("Select a player to lock in the lineup:", overall_df["Player"].unique())

locked_df = overall_df[overall_df["Player"] == locked_player]
remaining_df = overall_df[overall_df["Player"] != locked_player]

combos = list(itertools.combinations(remaining_df["Player"], 8))
locked_score = locked_df["Estimated Runs"].values[0]

best_lineups = []
for combo in combos:
    combo_score = remaining_df[remaining_df["Player"].isin(combo)]["Estimated Runs"].sum()
    best_lineups.append((combo, combo_score + locked_score))

top_lineups = sorted(best_lineups, key=lambda x: x[1], reverse=True)[:5]

final_df = pd.DataFrame([
    {"Lineup": ", ".join([locked_player] + list(combo)), "Total Estimated Runs": total}
    for combo, total in top_lineups
])

st.subheader("Top 5 Lineups Including: " + locked_player)
st.dataframe(final_df)

for i, row in final_df.iterrows():
    names = row["Lineup"].split(", ")
    scores = overall_df[overall_df["Player"].isin(names)][["Player", "Estimated Runs"]].sort_values("Estimated Runs", ascending=False)
    fig = go.Figure(go.Bar(
        x=scores["Player"],
        y=scores["Estimated Runs"],
        marker_color=px.colors.qualitative.Set3,
        text=scores["Estimated Runs"],
        textposition="outside"
    ))
    fig.update_layout(title=f"Run Contribution Breakdown (Lineup #{i+1})",
                      xaxis_title="Player", yaxis_title="Estimated Runs", height=400)
    st.plotly_chart(fig)
