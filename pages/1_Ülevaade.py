import streamlit as st
import pandas as pd
import io
import time
import numpy as np
import psutil

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

@st.cache_data
def lae_andmed():
    df = pd.read_parquet("piiriuletused.parquet")

    kategooriad = [
        "Piiripunkt",
        "Piiripunkti tüüp",
        "Kodakondsus",
        "Kodakondsus lühend",
        "Riikide grupp",
        "Sugu",
        "Vanuserühm"
    ]

    for veerg in kategooriad:
        df[veerg] = df[veerg].astype("category")

    return df

df = lae_andmed()

# ---------------------------------
# CATBOOSTI DETAILSE PROGNOOSI LAADIMINE
# ---------------------------------

@st.cache_data
def lae_catboost_detailne_prognoos():

    return pd.read_csv(
        "catboost_detailne_prognoos.csv",
        parse_dates=["Kuupäev"]
    )


catboost_detailne_prognoos = lae_catboost_detailne_prognoos()

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

st.sidebar.header("Filtrid")

# Piiripunkti tüüp
piiri_tyyp = st.sidebar.selectbox(
    "Piiripunkti tüüp",
    ["Kõik", "Maismaapiir", "Õhupiir"]
)

# Piiripunktide valik vastavalt tüübile
# ---------------------------------
# PIIRIPUNKTIDE VALIKUD
# ---------------------------------

@st.cache_data
def loo_punktide_valikud(df):
    return df[
        ["Piiripunkti tüüp", "Piiripunkt"]
    ].drop_duplicates()


punktide_valikud = loo_punktide_valikud(df)

if piiri_tyyp == "Kõik":
    punktid = sorted(
        punktide_valikud.loc[
            punktide_valikud["Piiripunkti tüüp"].isin(
                ["Maismaapiir", "Õhupiir"]
            ),
            "Piiripunkt"
        ].dropna().unique()
    )
else:
    punktid = sorted(
        punktide_valikud.loc[
            punktide_valikud["Piiripunkti tüüp"] == piiri_tyyp,
            "Piiripunkt"
        ].dropna().unique()
    )

valitud_punktid = st.sidebar.multiselect(
    "Piiripunkt",
    options=punktid,
    default=punktid
)

# ---------------------------------
# AASTAD
# ---------------------------------

aastad = sorted(
    set(df["aasta"].unique())
    | set(catboost_detailne_prognoos["aasta"].unique())
)

valitud_aastad = st.sidebar.multiselect(
    "Aasta",
    options=aastad,
    default=aastad
)

# ---------------------------------
# KUUD
# ---------------------------------

kuud = list(range(1, 13))

valitud_kuud = st.sidebar.multiselect(
    "Kuu",
    options=kuud,
    default=kuud
)

# ---------------------------------
# KODAKONDSUSED
# ---------------------------------

kodakondsused = sorted(
    df["Kodakondsus"].dropna().unique()
)

valitud_kodakondsused = st.sidebar.multiselect(
    "Kodakondsus",
    options=kodakondsused,
    default=kodakondsused
)

# ---------------------------------
# VANUSERÜHMAD
# ---------------------------------

vanuseruhmad = sorted(
    df["Vanuserühm"].dropna().unique()
)

valitud_vanuseruhmad = st.sidebar.multiselect(
    "Vanuserühm",
    options=vanuseruhmad,
    default=vanuseruhmad
)

# ---------------------------------
# RIIKIDE GRUPID
# ---------------------------------

riikide_grupid = sorted(
    df["Riikide grupp"].dropna().unique()
)

valitud_riikide_grupid = st.sidebar.multiselect(
    "Riikide grupp",
    options=riikide_grupid,
    default=riikide_grupid
)

algusaeg = time.perf_counter()

# ---------------------------------
# ANDMETE FILTREERIMINE
# ---------------------------------

def filtri_tingimused(andmed):

    if piiri_tyyp == "Kõik":
        valitud_tyypide_nimekiri = (
            andmed["Piiripunkti tüüp"].dropna().unique()
        )
    else:
        valitud_tyypide_nimekiri = [piiri_tyyp]

    return andmed[
        (andmed["Piiripunkti tüüp"].isin(valitud_tyypide_nimekiri))
        & (andmed["Piiripunkt"].isin(valitud_punktid))
        & (andmed["aasta"].isin(valitud_aastad))
        & (andmed["kuu"].isin(valitud_kuud))
        & (andmed["Kodakondsus"].isin(valitud_kodakondsused))
        & (andmed["Riikide grupp"].isin(valitud_riikide_grupid))
        & (andmed["Vanuserühm"].isin(valitud_vanuseruhmad))
    ]


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


st.subheader("Piiriületuste muutumine ajas ja masinõppepõhised prognoosid (november 2026 – detsember 2027)")

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
    use_container_width=True,
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
# PIIRIÜLETUSTE AJALINE TREND SOO JÄRGI
# ---------------------------------

st.subheader("Piiriületuste ajaline trend soo järgi")


# Kuupõhiste andmete koostamine soo järgi
soo_kuukoond = (
    filtreeritud
    .groupby(
        ["aasta", "kuu", "Sugu"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Kõigi piiriületuste arv kuus
koik_andmed = (
    filtreeritud
    .groupby(
        ["aasta", "kuu"],
        observed=True
    )
    .size()
    .reset_index(name="Koguarv")
)

# Ühendame koguarvu meeste ja naiste andmetega
soo_kuukoond = soo_kuukoond.merge(
    koik_andmed,
    on=["aasta", "kuu"],
    how="left"
)

# Arvutame meeste ja naiste osakaalu koguarvust
soo_kuukoond["Osakaal (%)"] = (
    soo_kuukoond["Piiriületuste arv"]
    / soo_kuukoond["Koguarv"]
    * 100
)

# Jätame alles ainult mehed ja naised
scatter_andmed = soo_kuukoond[
    soo_kuukoond["Sugu"].isin(["Mees", "Naine"])
].copy()

scatter_andmed["Seeria"] = scatter_andmed["Sugu"].map({
    "Mees": "Mehed",
    "Naine": "Naised"
})

scatter_andmed["Kuupäev"] = pd.to_datetime(
    dict(
        year=scatter_andmed["aasta"],
        month=scatter_andmed["kuu"],
        day=1
    )
)


# ---------------------------------
# SCATTERPLOT
# ---------------------------------

import plotly.express as px
import plotly.graph_objects as go

varvid = {
    "Mehed": "#2695db",
    "Naised": "#e58a36",
    "Kõik piiriületused": "#21a366"
}


fig_aastad = px.scatter(
    scatter_andmed,
    x="Kuupäev",
    y="Osakaal (%)",
    color="Seeria",
    color_discrete_map=varvid,
    title="Meeste ja naiste osakaal kõigist piiriületustest",
    labels={
        "Kuupäev": "Aeg",
        "Osakaal (%)": "Osakaal kõigist piiriületustest (%)",
        "Seeria": "Andmeseeria"
    },
    hover_data={
        "Kuupäev": "|%Y-%m",
        "Osakaal (%)": ":.2f"
    }
)



# ---------------------------------
# REGRESSIOONIJONED
# ---------------------------------

for seeria in ["Mehed", "Naised"]:

    andmed = (
        scatter_andmed[
            scatter_andmed["Seeria"] == seeria
        ]
        .sort_values("Kuupäev")
    )

    if len(andmed) >= 2:

        x = (
            andmed["Kuupäev"] - andmed["Kuupäev"].min()
        ).dt.days.to_numpy(dtype=float)

        y = andmed["Osakaal (%)"].to_numpy(dtype=float)

        # Lineaarne regressioon
        kordajad = np.polyfit(x, y, 1)

        y_prognoos = np.polyval(kordajad, x)

        fig_aastad.add_trace(
            go.Scatter(
                x=andmed["Kuupäev"],
                y=y_prognoos,
                mode="lines",
                name=f"{seeria} – regressioon",
                line=dict(
                    color=varvid[seeria],
                    width=3,
                    dash="dash"
                ),
                opacity=0.45,
                showlegend=True,
                hovertemplate=(
                    "%{x|%Y-%m}<br>"
                    "Trend: %{y:.2f}%"
                    "<extra>" + seeria + " regressioon</extra>"
                )
            )
        )


# ---------------------------------
# 50% VÕRDLUSJOON
# ---------------------------------

fig_aastad.add_hline(
    y=50,
    line_dash="dot",
    line_color="gray",
    line_width=1.5,
    annotation_text="50% koguarvust",
    annotation_position="top left"
)


# ---------------------------------
# GRAAFIKU KUJUNDUS
# ---------------------------------


fig_aastad.update_layout(
    xaxis_title="Aeg",
    yaxis=dict(
        title="Osakaal kõigist piiriületustest (%)",
        range=[0, 100]
    ),
    legend_title="Andmeseeria",
    hovermode="closest"
)


st.plotly_chart(
    fig_aastad,
    use_container_width=True,
    key="piiripunktide_vordlus"
)



# ---------------------------------
# NAISTE OSAKAAL RIIKIDE GRUPPIDE LÕIKES
# ---------------------------------

graafiku_andmed = (
    filtreeritud
    .groupby(
        ["aasta", "kuu", "Riikide grupp"],
        observed=True
    )
    .agg(
        Koguarv=("Sugu", "size"),
        Naiste_arv=(
            "Sugu",
            lambda x: (x == "Naine").sum()
        )
    )
    .reset_index()
)

graafiku_andmed["Naiste osakaal (%)"] = (
    graafiku_andmed["Naiste_arv"]
    / graafiku_andmed["Koguarv"]
    * 100
)

graafiku_andmed["Kuupäev"] = pd.to_datetime(
    dict(
        year=graafiku_andmed["aasta"],
        month=graafiku_andmed["kuu"],
        day=1
    )
)

graafiku_andmed = graafiku_andmed[
    graafiku_andmed["Riikide grupp"] != "Puudub"
].copy()

graafiku_andmed = graafiku_andmed.sort_values(
    ["Riikide grupp", "Kuupäev"]
)

fig_riikide_grupid = px.line(
    graafiku_andmed,
    x="Kuupäev",
    y="Naiste osakaal (%)",
    color="Riikide grupp",
    markers=True,
    title="Naiste osakaalu muutus riikide gruppide lõikes",
    labels={
        "Kuupäev": "Aeg",
        "Naiste osakaal (%)": "Naiste osakaal piiriületustest (%)",
        "Riikide grupp": "Riikide grupp"
    },
    hover_data={
        "Koguarv": ":,",
        "Naiste_arv": ":,",
        "Naiste osakaal (%)": ":.2f"
    }
)

fig_riikide_grupid.add_hline(
    y=50,
    line_dash="dot",
    line_color="gray",
    line_width=1.5,
    annotation_text="50%",
    annotation_position="top left"
)

fig_riikide_grupid.update_layout(
    xaxis_title="Aeg",
    yaxis=dict(
        title="Naiste osakaal piiriületustest (%)",
        range=[0, 100]
    ),
    legend_title="Riikide grupp",
    hovermode="closest"
)

st.plotly_chart(
    fig_riikide_grupid,
    use_container_width=True
)

st.dataframe(
    filtreeritud[
        ["Kodakondsus", "Riikide grupp"]
    ]
    .drop_duplicates()
    .sort_values(["Riikide grupp", "Kodakondsus"]),
    use_container_width=True
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
    use_container_width=True
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
# MUUTUSTE ANALÜÜS
# ---------------------------------

st.divider()

st.subheader("Piiriületuste muutused aastate lõikes")

# Koondame andmed piiripunktide ja aastate kaupa
muutuste_tabel = (
    filtreeritud
    .groupby(
        ["Piiripunkt", "aasta"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Sorteerime andmed
muutuste_tabel = muutuste_tabel.sort_values(
    ["Piiripunkt", "aasta"]
)

# Arvutame absoluutse muutuse
muutuste_tabel["Absoluutne muutus"] = (
    muutuste_tabel
    .groupby("Piiripunkt")["Piiriületuste arv"]
    .diff()
)

# Arvutame protsentuaalse muutuse
muutuste_tabel["Muutus %"] = (
    muutuste_tabel
    .groupby("Piiripunkt")["Piiriületuste arv"]
    .pct_change() * 100
)

# Vormindame tulemused
muutuste_tabel["Muutus %"] = (
    muutuste_tabel["Muutus %"].round(1)
)

# Kuvame tabeli
st.dataframe(
    muutuste_tabel,
    use_container_width=True,
    hide_index=True
)

st.subheader("TOP 10 kodakondsust")

# Koondame piiriületused kodakondsuse ja riikide grupi järgi
kodakondsuste_koond = (
    filtreeritud
    .groupby(
        ["Kodakondsus", "Riikide grupp"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Leiame 10 kõige arvukamat kodakondsust
top10_kodakondsused = (
    kodakondsuste_koond
    .sort_values("Piiriületuste arv", ascending=False)
    .head(10)
)

# Horisontaalne tulpdiagramm
fig_top10 = px.bar(
    top10_kodakondsused,
    x="Piiriületuste arv",
    y="Kodakondsus",
    color="Riikide grupp",
    orientation="h",
    text_auto=".2s",
    title="10 kõige arvukamat kodakondsust"
)

fig_top10.update_layout(
    xaxis_title="Piiriületuste arv",
    yaxis_title="Kodakondsus",
    yaxis={"categoryorder": "total ascending"},
    legend_title="Riikide grupp"
)

st.plotly_chart(
    fig_top10,
    use_container_width=True,
    key="top10_kodakondsused"
)

# Andmetabel koos riikide grupiga
st.dataframe(
    top10_kodakondsused,
    use_container_width=True,
    hide_index=True
)

st.subheader("Riikide gruppide dünaamika")

riikide_grupid = (
    filtreeritud
    .groupby(
        "Riikide grupp",
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
    .sort_values(
        "Piiriületuste arv",
        ascending=True
    )
)

fig_grupid = px.bar(
    riikide_grupid,
    x="Riikide grupp",
    y="Piiriületuste arv",
    title="Piiriületused riikide gruppide lõikes",
    text_auto=".2s"
)

fig_grupid.update_layout(
    xaxis_title="Riikide grupp",
    yaxis_title="Piiriületuste arv",
    xaxis=dict(categoryorder="total ascending"),
    showlegend=False
)

st.plotly_chart(
    fig_grupid,
    use_container_width=True,
    key="riikide_gruppide_jaotus"
)

# ---------------------------------
# HOOAJALISUSE ANALÜÜS
# ---------------------------------

st.divider()

st.subheader("Piiriületuste hooajalisus")

st.info(
    """
    **Mis on hooajalisuse indeks?**

    Hooajalisuse indeks näitab, kui palju erineb konkreetse kuu
    piiriületuste arv sama aasta keskmisest kuisest piiriületuste arvust.

    - 100 = aasta keskmine
    - Üle 100 = keskmisest aktiivsem kuu
    - Alla 100 = keskmisest vaiksem kuu

    Näiteks indeks 120 tähendab, et piiriületusi oli 20% rohkem
    kui selle aasta keskmisel kuul.
    """
)

algus_ettevalmistus = time.perf_counter()

# Kasutame piiritüübi, piiripunkti ja aasta filtreid,
# kuid mitte kuu filtrit.

viimane_kpv = df["Piiriületuse kpv"].max()

tingimus = (
    (df["Piiripunkti tüüp"].isin(
        ["Maismaapiir", "Õhupiir"]
        if piiri_tyyp == "Kõik"
        else [piiri_tyyp]
    ))
    & (df["Piiripunkt"].isin(valitud_punktid))
    & (df["aasta"].isin(valitud_aastad))
    & (df["Kodakondsus"].isin(valitud_kodakondsused))
    & (df["Riikide grupp"].isin(valitud_riikide_grupid))
    & (df["Vanuserühm"].isin(valitud_vanuseruhmad))
)

# Eemaldame osalise viimase kuu juba esialgses filtris
if pd.notna(viimane_kpv) and viimane_kpv.day < viimane_kpv.days_in_month:
    tingimus &= ~(
        (df["aasta"] == viimane_kpv.year)
        & (df["kuu"] == viimane_kpv.month)
    )

hooajalisuse_alus = df[tingimus]

aeg_filter = time.perf_counter()

algus_osaline_kuu = time.perf_counter()

# Kontrollime viimase kuu täielikkust
viimane_kpv = df["Piiriületuse kpv"].max()

# Eemaldame poolelioleva kuu
if pd.notna(viimane_kpv):
    if viimane_kpv.day < viimane_kpv.days_in_month:
        hooajalisuse_alus = hooajalisuse_alus[
            ~(
                (hooajalisuse_alus["aasta"] == viimane_kpv.year)
                & (hooajalisuse_alus["kuu"] == viimane_kpv.month)
            )
        ]

# Koondame tegelikud piiriületused
hooajalisus = (
    hooajalisuse_alus
    .groupby(
        ["aasta", "kuu", "Piiripunkt"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Loome iga aasta jaoks sobiva kuude kalendri
kalendrid = []

for aasta in valitud_aastad:

    if pd.notna(viimane_kpv) and aasta == viimane_kpv.year:
        viimane_taiskuu = viimane_kpv.month

        if viimane_kpv.day < viimane_kpv.days_in_month:
            viimane_taiskuu -= 1
    else:
        viimane_taiskuu = 12

    if viimane_taiskuu > 0:
        kalendrid.append(
            pd.MultiIndex.from_product(
                [
                    [aasta],
                    valitud_punktid,
                    range(1, viimane_taiskuu + 1)
                ],
                names=["aasta", "Piiripunkt", "kuu"]
            )
        )

if kalendrid:

    indeks = kalendrid[0].append(kalendrid[1:])

    # Lisame puuduvad kuud nullidega
    hooajalisus = (
        hooajalisus
        .set_index(["aasta", "Piiripunkt", "kuu"])
        .reindex(indeks, fill_value=0)
        .reset_index()
    )

    # Arvutame aasta keskmise
    hooajalisus["Aasta keskmine"] = (
        hooajalisus
        .groupby(
            ["aasta", "Piiripunkt"],
            observed=True
        )["Piiriületuste arv"]
        .transform("mean")
    )

    # Algne hooajalisuse indeks
    hooajalisus["Hooajalisuse indeks"] = (
        hooajalisus["Piiriületuste arv"]
        / hooajalisus["Aasta keskmine"]
        * 100
    ).fillna(0).round(1)

    # Stabiliseeritud indeks (k=10)
    hooajalisus["Stabiliseeritud indeks"] = np.where(
        hooajalisus["Piiriületuste arv"] == 0,
        0,
        100 + (
            hooajalisus["Hooajalisuse indeks"] - 100
        ) * (
            hooajalisus["Aasta keskmine"]
            / (hooajalisus["Aasta keskmine"] + 10)
        )
    ).round(1)

else:
    hooajalisus = pd.DataFrame(
        columns=[
            "aasta",
            "Piiripunkt",
            "kuu",
            "Piiriületuste arv",
            "Aasta keskmine",
            "Hooajalisuse indeks",
            "Stabiliseeritud indeks"
        ]
    )

# Kuu nimetused
kuu_nimed = {
    1: "Jaanuar",
    2: "Veebruar",
    3: "Märts",
    4: "Aprill",
    5: "Mai",
    6: "Juuni",
    7: "Juuli",
    8: "August",
    9: "September",
    10: "Oktoober",
    11: "November",
    12: "Detsember"
}

hooajalisus["Kuu"] = hooajalisus["kuu"].map(kuu_nimed)


# Valime aastad, mida soovime võrrelda
hooajalisuse_aastad = st.multiselect(
    "Võrdle aastaid",
    options=sorted(hooajalisus["aasta"].unique()),
    default=sorted(hooajalisus["aasta"].unique())[-3:]
)

hooajalisuse_graafik = hooajalisus[
    hooajalisus["aasta"].isin(hooajalisuse_aastad)
]

algus_graafikud = time.perf_counter()

# Hooajalisuse graafikud eraldi aastate kaupa
st.subheader("Hooajalisuse võrdlus")

if not hooajalisuse_aastad:
    st.warning("Vali vähemalt üks aasta.")

else:
    y_max = hooajalisuse_graafik["Stabiliseeritud indeks"].max()
    y_max = ((y_max // 20) + 1) * 20

    veerud = st.columns(len(hooajalisuse_aastad))

    for veerg, aasta in zip(veerud, hooajalisuse_aastad):

        aasta_andmed = hooajalisuse_graafik[
            hooajalisuse_graafik["aasta"] == aasta
        ]

        fig_hooajalisus = px.line(
            aasta_andmed,
            x="Kuu",
            y="Stabiliseeritud indeks",
            color="Piiripunkt",
            markers=True,
            category_orders={
                "Kuu": list(kuu_nimed.values())
            },
            hover_data={
                "Piiriületuste arv": True,
                "Hooajalisuse indeks": True,
                "Stabiliseeritud indeks": True
            }
        )

        fig_hooajalisus.add_hline(
            y=100,
            line_dash="dash",
            annotation_text="Aasta keskmine (100)"
        )

        fig_hooajalisus.update_layout(
            title=str(aasta),
            xaxis_title="Kuu",
            yaxis_title="Stabiliseeritud hooajalisuse indeks",
            legend_title="Piiripunkt",
            hovermode="x unified",
            yaxis=dict(range=[0, y_max]),
            margin=dict(l=40, r=20, t=50, b=40)
        )

        with veerg:
            st.plotly_chart(
                fig_hooajalisus,
                use_container_width=True,
                key=f"hooajalisuse_graafik_{aasta}"
)

graafikute_aeg = time.perf_counter() - algus_graafikud

st.caption(
    f"Hooajalisuse graafikute loomine: {graafikute_aeg:.3f} sekundit"
)

# Hooajalisuse tabel
st.subheader("Hooajalisuse andmetabel")

st.dataframe(
    hooajalisus[
        hooajalisus["aasta"].isin(hooajalisuse_aastad)
    ][
        [
            "Piiripunkt",
            "aasta",
            "Kuu",
            "Piiriületuste arv",
            "Aasta keskmine",
            "Hooajalisuse indeks",
            "Stabiliseeritud indeks"
        ]
    ],
    use_container_width=True,
    hide_index=True
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
    use_container_width=True
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
    use_container_width=True
)