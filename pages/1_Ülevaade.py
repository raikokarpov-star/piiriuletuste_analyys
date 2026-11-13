
import streamlit as st
import pandas as pd
import io
import time
import numpy as np
import psutil

from utils import filtri_tingimused


def kuva_malukasuts():
    protsess = psutil.Process()
    malumaht = protsess.memory_info().rss / (1024 ** 2)

    st.info(f"RAM kasutus: {malumaht:.1f} MB")


# ---------------------------------
# LEHE SEADISTUSED
# ---------------------------------

st.title("Eesti piiriületuste dünaamiline analüüs 2021–2027")


# ---------------------------------
# ANDMETE LAADIMINE
# ---------------------------------

df = st.session_state["andmed_df"]

catboost_detailne_prognoos = st.session_state["catboost_df"]

# ---------------------------------
# ÜHISED FILTRID APP.PY-ST
# ---------------------------------

piiri_tyyp = st.session_state["piiri_tyyp"]
valitud_punktid = st.session_state["valitud_punktid"]
valitud_aastad = st.session_state["valitud_aastad"]
valitud_kuud = st.session_state["valitud_kuud"]
valitud_kodakondsused = st.session_state["valitud_kodakondsused"]
valitud_vanuseruhmad = st.session_state["valitud_vanuseruhmad"]
valitud_riikide_grupid = st.session_state["valitud_riikide_grupid"]


st.subheader("Mälu diagnostika")
kuva_malukasuts()


# ---------------------------------
# RIIKLIKUD PROGNOOSID: A7 JA A9
# ---------------------------------

prognoosi_andmed = pd.DataFrame({
    "Kuupäev": pd.date_range(
        start="2026-11-01",
        end="2027-12-01",
        freq="MS"
    ),
    "Prognoos_A7": [
        55214, 53773,
        55406, 41287, 54791, 56276, 58346, 59995,
        70231, 74723, 59020, 64134, 49862, 48975
    ],
    "Prognoos_A9": [
        61387, 57223,
        56234, 40227, 52558, 54841, 51308, 54398,
        63494, 68550, 52933, 61903, 47214, 43050
    ]
})

prognoosi_andmed["aasta"] = prognoosi_andmed["Kuupäev"].dt.year
prognoosi_andmed["kuu"] = prognoosi_andmed["Kuupäev"].dt.month

# ---------------------------------
# FILTRID
# ---------------------------------


# ---------------------------------
# ANDMETE FILTREERIMINE
# ---------------------------------

    
algusaeg = time.perf_counter()

filtreeritud = filtri_tingimused(df)

prognoos_filtreeritud = filtri_tingimused(
    catboost_detailne_prognoos
)

filtreerimise_aeg = time.perf_counter() - algusaeg

st.caption(
    f"Andmete filtreerimine: {filtreerimise_aeg:.3f} sekundit"
)

# ---------------------------------
# TULEMUSED
# ---------------------------------

st.subheader("Ülevaade")

col1, col2, col3, col4, col5, col6 = st.columns(6)

tegelik_arv = len(filtreeritud)

prognoos_a7_arv = prognoos_filtreeritud[
    "Prognoos_kategooria_A7"
].sum()

prognoos_a9_arv = prognoos_filtreeritud[
    "Prognoos_kategooria_A9"
].sum()

koguarv_a7 = tegelik_arv + prognoos_a7_arv
koguarv_a9 = tegelik_arv + prognoos_a9_arv

muutus_a7 = prognoos_a7_arv / tegelik_arv * 100
muutus_a9 = prognoos_a9_arv / tegelik_arv * 100

# Tegeliku piiriületuste arvu muutus
aastate_kaupa = (
    filtreeritud.groupby("aasta")
    .size()
    .sort_index()
)

if len(aastate_kaupa) >= 2:
    esimene = aastate_kaupa.iloc[0]
    viimane = aastate_kaupa.iloc[-1]
    muutus = (viimane - esimene) / esimene * 100
else:
    muutus = None

with col1:
    st.metric(
        "Piiriületuste arv (tegelik)",
        f"{tegelik_arv:,.0f}".replace(",", " ")
    )

with col2:
    varv = (
        "#21a366" if muutus > 0
        else "#e53935" if muutus < 0
        else "inherit"
    ) if muutus is not None else "inherit"

    vaartus = (
        f"{muutus:+.1f}%"
        if muutus is not None
        else "–"
    )

    st.markdown(
        f"""
        <div>
            <div style="font-size:14px; color:inherit;">
                Tegelik muutus (%)
            </div>
            <div style="
                font-size:28px;
                font-weight:600;
                color:{varv};
            ">
                {vaartus}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.metric(
        "Prognoos (A7)",
        f"{koguarv_a7:,.0f}".replace(",", " "),
        delta=f"+{muutus_a7:.1f}%"
    )

with col4:
    st.metric(
        "Prognoos (A9)",
        f"{koguarv_a9:,.0f}".replace(",", " "),
        delta=f"+{muutus_a9:.1f}%"
    )

with col5:
    st.metric(
        "Valitud piiripunkte",
        len(valitud_punktid)
    )

with col6:
    st.metric(
        "Valitud aastaid",
        len(valitud_aastad)
    )

st.write("Filtreeritud andmestiku mõõtmed:", filtreeritud.shape)

st.write("RAM pärast filtreerimist:")
kuva_malukasuts()

# ---------------------------------
# AJALINE ANALÜÜS
# ---------------------------------

st.divider()


st.subheader("Piiriületuste muutumine ajas vs piiripunktidega + masinõppepõhised prognoosid (november 2026 – detsember 2027)")

# ---------------------------------
# TEGELIKUD ANDMED
# ---------------------------------

graafiku_andmed = (
    filtreeritud[
        (filtreeritud["aasta"] < 2026)
        | (
            (filtreeritud["aasta"] == 2026)
            & (filtreeritud["kuu"] <= 10)
        )
    ]
    .groupby(
        ["aasta", "kuu", "Piiripunkt"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

graafiku_andmed["Kuupäev"] = pd.to_datetime(
    graafiku_andmed["aasta"].astype(str)
    + "-"
    + graafiku_andmed["kuu"].astype(str)
    + "-01"
)

graafiku_andmed["Stsenaarium"] = "Tegelik"

# ---------------------------------
# PROGNOOSANDMED
# ---------------------------------

prognoosi_graafik = (
    prognoos_filtreeritud
    .groupby(
        ["Kuupäev", "Piiripunkt"],
        observed=True
    )[["Prognoos_kategooria_A7", "Prognoos_kategooria_A9"]]
    .sum()
    .reset_index()
)

# ---------------------------------
# OKTOOBRI TEGELIKUD VÄÄRTUSED
# ---------------------------------

oktoobri_tegelik = graafiku_andmed[
    graafiku_andmed["Kuupäev"] == "2026-10-01"
][
    ["Kuupäev", "Piiripunkt", "Piiriületuste arv"]
].copy()


# ---------------------------------
# A7 PROGNOOS
# ---------------------------------

prognoos_a7 = prognoosi_graafik[
    ["Kuupäev", "Piiripunkt", "Prognoos_kategooria_A7"]
].rename(
    columns={
        "Prognoos_kategooria_A7": "Piiriületuste arv"
    }
)

prognoos_a7 = pd.concat(
    [oktoobri_tegelik, prognoos_a7],
    ignore_index=True
)

prognoos_a7["Stsenaarium"] = "A7 prognoos"


# ---------------------------------
# A9 PROGNOOS
# ---------------------------------

prognoos_a9 = prognoosi_graafik[
    ["Kuupäev", "Piiripunkt", "Prognoos_kategooria_A9"]
].rename(
    columns={
        "Prognoos_kategooria_A9": "Piiriületuste arv"
    }
)

prognoos_a9 = pd.concat(
    [oktoobri_tegelik, prognoos_a9],
    ignore_index=True
)

prognoos_a9["Stsenaarium"] = "A9 prognoos"

# ---------------------------------
# ÜHENDAME ANDMED
# ---------------------------------

graafiku_andmed = pd.concat(
    [
        graafiku_andmed[
            ["Kuupäev", "Piiripunkt", "Piiriületuste arv", "Stsenaarium"]
        ],
        prognoos_a7,
        prognoos_a9
    ],
    ignore_index=True
)

# ---------------------------------
# JOONDIAGRAMM
# ---------------------------------

import plotly.express as px


fig = px.line(
    graafiku_andmed,
    x="Kuupäev",
    y="Piiriületuste arv",
    color="Piiripunkt",
    line_dash="Stsenaarium",
    symbol="Stsenaarium",
    markers=True,
    title="Piiriületused kuude lõikes",
    line_dash_map={
        "Tegelik": "solid",
        "A7 prognoos": "dash",
        "A9 prognoos": "dot"
    },
    symbol_map={
        "Tegelik": "circle",
        "A7 prognoos": "diamond",
        "A9 prognoos": "square"
    }
)

# ---------------------------------
# PIIRIPUNKTIDE ALGSED VÄRVID
# ---------------------------------

piiripunkti_varvid = {}

for trace in fig.data:
    if trace.name.endswith(", Tegelik"):
        piiripunkt = trace.name.rsplit(", ", 1)[0]
        piiripunkti_varvid[piiripunkt] = trace.line.color

# ---------------------------------
# JOONTE VÄRVID, STIILID JA PAKSUS
# ---------------------------------

for trace in fig.data:
    piiripunkt = trace.name.rsplit(", ", 1)[0]
    varv = piiripunkti_varvid.get(piiripunkt)

    if varv:
        trace.line.color = varv
        trace.marker.color = varv

    if trace.name.endswith(", Tegelik"):
        trace.line.width = 2
        trace.marker.size = 5

    elif trace.name.endswith(", A7 prognoos"):
        trace.line.width = 2.5
        trace.marker.size = 6

    elif trace.name.endswith(", A9 prognoos"):
        trace.line.width = 2.5
        trace.marker.size = 6

fig.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Piiriületuste arv",
    hovermode="x unified",
    legend_title="Piiripunkt / stsenaarium"
)

st.plotly_chart(
    fig,
    width="stretch",
    key="piiriuletuste_ajagraafik"
)



# ---------------------------------
# CATBOOSTI JA AJALOOLISTE ANDMETE LAADIMINE
# ---------------------------------

@st.cache_data
def lae_piiripunktide_osakaalud():

    ajaloolised = pd.read_csv(
        "ajaloolised_piiripunktide_osakaalud.csv",
        parse_dates=["Kuupäev"]
    )

    prognoosid = pd.read_csv(
        "catboost_piiripunktide_prognoos.csv",
        parse_dates=["Kuupäev"]
    )

    detailne_prognoos = pd.read_csv(
        "catboost_detailne_prognoos.csv",
        parse_dates=["Kuupäev"]
    )

    return ajaloolised, prognoosid, detailne_prognoos


(
    ajaloolised_osakaalud,
    catboost_osakaalud,
    catboost_detailne_prognoos
) = lae_piiripunktide_osakaalud()


ajalooliste_summa_kontroll = (
    ajaloolised_osakaalud
    .groupby("Kuupäev")["Osakaal_%"]
    .sum()
)

# ---------------------------------
# SCHENGENI LIIKMESUSE JA LÄHTEANDMETE KLASSIFIKATSIOONI VÕRDLUS
# ---------------------------------

import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.subheader(
    "Schengeni liikmelisuse ja lähteandmestiku riikide grupi klassifikatsiooni võrdlus"
)

st.markdown(
    """
    Naiste osakaalu analüüsimisel tekkis täiendav küsimus, 
    kas lähteandmestikus kasutatav riikide gruppide klassifikatsioon vastab 
    riikide tegelikule ajaloolisele Schengeni liikmelisusele.

    Selle kontrollimiseks vaatleme kolme riiki, mille puhul 
    ilmnesid erinevused: Bulgaaria, Rumeenia ja Horvaatia.
    """
)

# ---------------------------------
# LÄHTEANDMED
# ---------------------------------

schengeni_riigid = {
    "Bulgaaria Vabariik": {
        "nimi": "Bulgaaria",
        "liikmesus": "2025-01-01"
    },
    "Rumeenia": {
        "nimi": "Rumeenia",
        "liikmesus": "2025-01-01"
    },
    "Horvaatia Vabariik": {
        "nimi": "Horvaatia",
        "liikmesus": "2023-01-01"
    }
}

gruppide_varvid = {
    "EL/EMP/CH": "#E69F00",
    "Schengen, EL/EMP/CH": "#178939"
}

schengeni_kontroll = df[
    df["Kodakondsus"].isin(schengeni_riigid)
].copy()

schengeni_kontroll["Kuupäev"] = (
    pd.to_datetime(schengeni_kontroll["Piiriületuse kpv"])
    .dt.to_period("M")
    .dt.to_timestamp()
)

kuukoond = (
    schengeni_kontroll
    .groupby(
        ["Kodakondsus", "Kuupäev", "Riikide grupp"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# ---------------------------------
# KOKKUVÕTE
# ---------------------------------

gruppide_kokkuvote = (
    schengeni_kontroll
    .groupby(
        ["Kodakondsus", "Riikide grupp"],
        observed=True
    )
    .agg(
        Piiriületuste_arv=("Piiriületuse kpv", "size"),
        Esimene_kuupäev=("Piiriületuse kpv", "min"),
        Viimane_kuupäev=("Piiriületuse kpv", "max")
    )
    .reset_index()
)

# ---------------------------------
# GRAAFIK
# ---------------------------------

riigid = list(schengeni_riigid.keys())

fig_schengeni_kontroll = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=[
        "<b style='color:black'>Bulgaaria</b>",
        "<b style='color:black'>Rumeenia</b>",
        "<b style='color:black'>Horvaatia</b>"
    ],
    shared_xaxes=True,
    vertical_spacing=0.10
)

for rea, riik in enumerate(riigid, start=1):

    for grupp, varv in gruppide_varvid.items():

        grupi_andmed = (
            kuukoond[
                (kuukoond["Kodakondsus"] == riik)
                & (kuukoond["Riikide grupp"] == grupp)
            ]
            .sort_values("Kuupäev")
        )

        fig_schengeni_kontroll.add_trace(
            go.Bar(
                x=grupi_andmed["Kuupäev"],
                y=grupi_andmed["Piiriületuste arv"],
                name=grupp,
                legendgroup=grupp,
                showlegend=(rea == 1),
                marker_color=varv,
                hovertemplate=(
                    "<b>%{x|%B %Y}</b><br>"
                    + grupp
                    + "<br>Piiriületusi: %{y:,}"
                    + "<extra></extra>"
                )
            ),
            row=rea,
            col=1
        )

    # Ametliku Schengeni liikmelisuse algus
    liikmesuse_kuupaev = pd.Timestamp(
        schengeni_riigid[riik]["liikmesus"]
    )

    fig_schengeni_kontroll.add_vline(
        x=liikmesuse_kuupaev,
        line_dash="dash",
        line_color="#D62728",
        line_width=2,
        row=rea,
        col=1
    )

    # Liikmesuse kuupäeva selgitus
    fig_schengeni_kontroll.add_annotation(
        x=liikmesuse_kuupaev,
        y=1,
        xref="x domain" if rea == 1 else f"x{rea} domain",
        yref="y domain" if rea == 1 else f"y{rea} domain",
        text=(
            "Ametlik Schengeni liikmesuse algus<br>"
            + liikmesuse_kuupaev.strftime("%d.%m.%Y")
        ),
        showarrow=False,
        xanchor="left",
        yanchor="top",
        xshift=5,
        font=dict(size=10, color="#D62728"),
        bgcolor="rgba(255,255,255,0.9)"
    )


# ---------------------------------
# KUJUNDUS
# ---------------------------------

fig_schengeni_kontroll.update_layout(
    height=1050,
    barmode="group",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(
    title="Lähteandmestiku riikide grupp",
    orientation="v",
    yanchor="middle",
    y=0.5,
    xanchor="left",
    x=1.02
),
    margin=dict(
    l=70,
    r=260,
    t=100,
    b=60
)
)

fig_schengeni_kontroll.update_yaxes(
    title_text="Piiriületuste arv",
    rangemode="tozero",
    showgrid=True,
    gridcolor="#E5E5E5"
)

fig_schengeni_kontroll.update_xaxes(
    title_text="Aeg",
    tickformat="%Y",
    showgrid=False
)

st.plotly_chart(
    fig_schengeni_kontroll,
    width="stretch"
)

st.markdown(
    """
    <p style="font-size: 15px; color: black;">
    <em>
    Punane katkendjoon tähistab riigi ametliku Schengeni liikmesuse alguskuupäeva.
    Tulbad kajastavad lähteandmestikus kasutatud riikide gruppide klassifikatsiooni
    ajalist jaotust. Ametliku liikmesuse kuupäeva ja lähteandmestikus kajastatud
    klassifikatsiooni vahel ilmnevad erinevused osutavad ajalise klassifitseerimise
    lahknevustele, kuid ei võimalda iseenesest järeldada lähteandmete ebaõigsust.
    </em>
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------------------------
# ANALÜÜSI TULEMUSTE ALLALAADIMINE
# ---------------------------------

st.divider()

st.subheader("Laadi analüüsi tulemused alla")

# Loome Exceli faili mälus
def loo_excel():
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:

        graafiku_andmed.to_excel(
            writer, sheet_name="Ajaline koond", index=False
        )

        aastate_andmed.to_excel(
            writer, sheet_name="Aastate koond", index=False
        )

        muutuste_tabel.to_excel(
            writer, sheet_name="Muutuste analüüs", index=False
        )

        kodakondsuste_koond.to_excel(
            writer, sheet_name="Kodakondsuste koond", index=False
        )

        top10_kodakondsused.to_excel(
            writer, sheet_name="TOP 10 kodakondsust", index=False
        )

        riikide_grupid.to_excel(
            writer, sheet_name="Riikide grupid", index=False
        )

        hooajalisus.to_excel(
            writer, sheet_name="Hooajalisus", index=False
        )

    return excel_buffer.getvalue()


st.download_button(
    label="Lae kogu analüüs alla (Excel)",
    data=loo_excel,
    file_name="eesti_piiriuletuste_analuus.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    width="stretch"
)

# ---------------------------------
# ALGANDMETE ALLALAADIMINE
# ---------------------------------

st.subheader("Algandmete allalaadimine")

csv_andmed = filtreeritud.to_csv(
    index=False,
    sep=";",
    encoding="utf-8-sig"
).encode("utf-8-sig")

st.download_button(
    label="Lae filtreeritud algandmed alla (CSV)",
    data=csv_andmed,
    file_name="eesti_piiriuletuste_algandmed.csv",
    mime="text/csv",
    width="stretch"
)