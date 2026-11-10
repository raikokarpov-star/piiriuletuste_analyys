
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------
# LEHE SEADISTUSED
# ---------------------------------

st.set_page_config(
    page_title="Piiriületuste prognoos",
    page_icon="📈",
    layout="wide"
)

st.title("Eesti piiriületuste prognoos")
st.caption("Riiklik prognoos ja ajalooliste tulemuste võrdlus")

# ---------------------------------
# ANDMETE LAADIMINE
# ---------------------------------

@st.cache_data
def lae_piirangute_andmed():
    return pd.read_parquet("piiripunktide_kuud.parquet")


@st.cache_data
def lae_andmed():
    return pd.read_parquet("piiriuletused.parquet")


piirangud = lae_piirangute_andmed()
df = lae_andmed()

piirangud["Kuupäev"] = pd.to_datetime(
    piirangud["Kuupäev"]
)

# ---------------------------------
# PIIRANGUTE ALGUSKUUPÄEVADE LEIDMINE
# ---------------------------------

tunnused = {
    "Ajutine_piirikontroll": "Ajutine piirikontroll",
    "Narva_soidukipiirangu_osakaal": "Narva sõidukipiirang",
    "Saatse_automaatse_süsteemi_osakaal": "Saatse automaatne süsteem",
    "Narva_ABC_süsteemi_osakaal": "Narva ABC-süsteem",
    "Tallinna_ABC_süsteemi_osakaal": "Tallinna ABC-süsteem"
}

algused = []

for piiripunkt, grupp in piirangud.groupby("Piiripunkt"):

    grupp = grupp.sort_values("Kuupäev")

    for tunnus in tunnused:

        aktiivne = grupp[tunnus] > 0

        algus = aktiivne & ~aktiivne.shift(
            1,
            fill_value=False
        )

        for _, rida in grupp[algus].iterrows():
            algused.append({
                "Kuupäev": rida["Kuupäev"],
                "Piiripunkt": piiripunkt,
                "Tunnus": tunnus
            })


algused_df = pd.DataFrame(algused)

# ---------------------------------
# VALGA PIIRIPUNKTIDE KOONDAMINE
# ---------------------------------

algused_df.loc[
    algused_df["Piiripunkt"].isin([
        "Valga-1 piiripunkt",
        "Valga-2 piiripunkt",
        "Valga-3 piiripunkt"
    ]),
    "Piiripunkt"
] = "Valga-1–3 piiripunkt"

algused_df = algused_df.drop_duplicates(
    subset=["Kuupäev", "Piiripunkt", "Tunnus"]
)




# ---------------------------------
# PROGNOOSID
# ---------------------------------

prognoos = pd.DataFrame({
    "Kuupäev": pd.date_range(
        "2026-11-01",
        "2027-12-01",
        freq="MS"
    ),
    "A7": [
        55214, 53773,
        55406, 41287, 54791, 56276, 58346, 59995,
        70231, 74723, 59020, 64134, 49862, 48975
    ],
    "A9": [
        61387, 57223,
        56234, 40227, 52558, 54841, 51308, 54398,
        63494, 68550, 52933, 61903, 47214, 43050
    ]
})

# ---------------------------------
# AJALOOLISED ANDMED
# ---------------------------------

df["Piiriületuse kpv"] = pd.to_datetime(
    df["Piiriületuse kpv"]
)

ajalugu = df[
    df["Piiripunkti tüüp"].isin(
        ["Maismaapiir", "Õhupiir"]
    )
    & (df["Piiriületuse kpv"] < "2026-11-01")
].copy()

ajalugu = (
    ajalugu
    .groupby(["aasta", "kuu"])
    .size()
    .reset_index(name="Tegelik")
)

ajalugu["Kuupäev"] = pd.to_datetime(
    dict(
        year=ajalugu["aasta"],
        month=ajalugu["kuu"],
        day=1
    )
)

# ---------------------------------
# PROGNOOSI JA AJALOO GRAAFIK
# ---------------------------------

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=ajalugu["Kuupäev"],
    y=ajalugu["Tegelik"],
    name="Tegelik",
    mode="lines",
    line=dict(color="black", width=2)
))

fig.add_trace(go.Scatter(
    x=prognoos["Kuupäev"],
    y=prognoos["A7"],
    name="A7 – SARIMAX",
    mode="lines",
    line=dict(color="#178939", width=2, dash="dash")
))

fig.add_trace(go.Scatter(
    x=prognoos["Kuupäev"],
    y=prognoos["A9"],
    name="A9 – lineaarne trend",
    mode="lines",
    line=dict(color="#E69532", width=2, dash="dot")
))

fig.add_vline(
    x=pd.Timestamp("2026-11-01").timestamp() * 1000,
    line_dash="dash",
    line_color="grey"
)

fig.update_layout(
    title="Tegelikud piiriületused ja riiklik prognoos",
    xaxis_title="Aasta",
    yaxis_title="Piiriületuste arv",
    hovermode="x unified",
    template="plotly_white",
    width=1050,
    height=580,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    xaxis=dict(
        range=["2021-01-01", "2027-12-31"],
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True,
        showgrid=False
    ),
    yaxis=dict(
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True,
        showgrid=True,
        gridcolor="lightgrey"
    )
)

# ---------------------------------
# SÜNDMUSTE LISAMINE PROGNOOSIGRAAFIKULE
# ---------------------------------

nimetused = {
    "Ajutine_piirikontroll": "Ajutine piirikontroll",
    "Narva_soidukipiirangu_osakaal": "Narva sõidukipiirang",
    "Saatse_automaatse_süsteemi_osakaal": "Saatse automaatne süsteem",
    "Narva_ABC_süsteemi_osakaal": "Narva ABC-süsteem",
    "Tallinna_ABC_süsteemi_osakaal": "Tallinna ABC-süsteem"
}

for i, (_, rida) in enumerate(algused_df.iterrows()):

    if rida["Piiripunkt"] == "Saatse piiripunkt":
        y_asukoht = 0.85

    elif rida["Piiripunkt"] == "Valga-1–3 piiripunkt":
        y_asukoht = 0.45

    else:
        y_asukoht = 0.75 - (i % 3) * 0.13

    fig.add_annotation(
        x=rida["Kuupäev"],
        y=y_asukoht,
        xref="x",
        yref="paper",
        text=(
            f"↓ {nimetused[rida['Tunnus']]}<br>"
            f"{rida['Piiripunkt'].replace(' piiripunkt', '')}"
        ),
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#178939",
        ax=0,
        ay=-35,
        font=dict(size=10, color="black"),
        bgcolor="rgba(255, 255, 255, 0.35)",
        bordercolor="#178939",
        borderwidth=1,
        borderpad=4
    )

    fig.add_annotation(
        x=rida["Kuupäev"],
        y=y_asukoht,
        xref="x",
        yref="paper",
        text=(
            f"↓ {nimetused[rida['Tunnus']]}<br>"
            f"{rida['Piiripunkt'].replace(' piiripunkt', '')}"
        ),
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#178939",
        ax=0,
        ay=-35,
        font=dict(size=10, color="black"),
        bgcolor="rgba(255, 255, 255, 0.35)",
        bordercolor="#178939",
        borderwidth=1,
        borderpad=4
    )

# ---------------------------------
# GRAAFIKU KUVAMINE
# ---------------------------------

st.plotly_chart(
    fig,
    use_container_width=True
)
