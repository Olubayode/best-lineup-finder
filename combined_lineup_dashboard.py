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

df = load_data()

st.title("🏏 OU Softball Lineup Optimization App")
page = st.sidebar.radio("Select a tool:", ["🔐 Best Lineup Finder (Lock 1 Player)", "🧢 Manual Lineup Selector"])

# Best Lineup Finder - Lock 1 Player
if page == "🔐 Best Lineup Finder (Lock 1 Player)":
    st.header("🔐 Best Lineup Finder - Lock 1 Player")

    locked_player = st.selectbox("Select a player to lock in the lineup:", df["Player"].unique())

    locked_df = df[df["Player"] == locked_player]
    remaining_df = df[df["Player"] != locked_player]

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
        scores = df[df["Player"].isin(names)][["Player", "Estimated Runs"]].sort_values("Estimated Runs", ascending=False)
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

# Manual Lineup Selector
elif page == "🧢 Manual Lineup Selector":
    st.header("🧢 Manual Lineup Selector - Pick Any 9 Players")

    selected_players = st.multiselect("Select 9 players to create a lineup:", df["Player"].tolist(), max_selections=9)

    if len(selected_players) < 9:
        st.warning("Please select exactly 9 players.")
    elif len(selected_players) > 9:
        st.error("Too many players selected. Please choose exactly 9.")
    else:
        selected_df = df[df["Player"].isin(selected_players)].sort_values("Estimated Runs", ascending=False).reset_index(drop=True)
        total_estimated_runs = selected_df["Estimated Runs"].sum()

        st.success(f"✅ Total Estimated Runs for Selected Lineup: {total_estimated_runs:.3f}")

        st.dataframe(selected_df[["Player", "OBP", "SLG", "Estimated Runs"]])

        fig = go.Figure(go.Bar(
            x=selected_df["Player"],
            y=selected_df["Estimated Runs"],
            marker_color=px.colors.qualitative.Vivid,
            text=selected_df["Estimated Runs"],
            textposition="outside"
        ))
        fig.update_layout(title="Run Contribution by Player", xaxis_title="Player", yaxis_title="Estimated Runs")
        st.plotly_chart(fig)

        st.markdown("### 🧾 Visual Lineup Card")
        for i, row in selected_df.iterrows():
            with st.container():
                st.markdown(f"**{i+1}. {row['Player']}**")
                st.markdown(f"- OBP: `{row['OBP']:.3f}`  |  SLG: `{row['SLG']:.3f}`  |  Estimated Runs: `{row['Estimated Runs']:.3f}`")
                st.markdown("---")
