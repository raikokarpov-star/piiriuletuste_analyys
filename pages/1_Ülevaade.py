
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

def filtri_tingimused(andmed, aasta_valik=None):

    piiri_tyyp = st.session_state["piiri_tyyp"]
    valitud_punktid = st.session_state["valitud_punktid"]
    valitud_kuud = st.session_state["valitud_kuud"]
    valitud_kodakondsused = st.session_state["valitud_kodakondsused"]
    valitud_vanuseruhmad = st.session_state["valitud_vanuseruhmad"]
    valitud_riikide_grupid = st.session_state["valitud_riikide_grupid"]

    if aasta_valik is None:
        aasta_valik = st.session_state["valitud_aastad"]

    if piiri_tyyp == "Kõik":
        valitud_tyypide_nimekiri = [
            "Maismaapiir",
            "Õhupiir"
        ]
    else:
        valitud_tyypide_nimekiri = [piiri_tyyp]

    return andmed[
        (andmed["Piiripunkti tüüp"].isin(valitud_tyypide_nimekiri))
        & (andmed["Piiripunkt"].isin(valitud_punktid))
        & (andmed["aasta"].isin(aasta_valik))
        & (andmed["kuu"].isin(valitud_kuud))
        & (andmed["Kodakondsus"].isin(valitud_kodakondsused))
        & (andmed["Riikide grupp"].isin(valitud_riikide_grupid))
        & (andmed["Vanuserühm"].isin(valitud_vanuseruhmad))
    ]


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
# PROGNOOSANDMED SOO JÄRGI
# ---------------------------------

prognoosi_soo = (
    catboost_detailne_prognoos
    .groupby(
        ["Kuupäev", "Sugu"],
        observed=True
    )[
        [
            "Prognoos_kategooria_A7",
            "Prognoos_kategooria_A9"
        ]
    ]
    .sum()
    .reset_index()
)

# Arvutame kõigi soogruppide koguprognoosi kuus
prognoosi_koguarv = (
    prognoosi_soo
    .groupby("Kuupäev")[
        [
            "Prognoos_kategooria_A7",
            "Prognoos_kategooria_A9"
        ]
    ]
    .sum()
    .reset_index()
    .rename(
        columns={
            "Prognoos_kategooria_A7": "Koguarv_A7",
            "Prognoos_kategooria_A9": "Koguarv_A9"
        }
    )
)

# Ühendame koguarvud soo prognoosidega
prognoosi_soo = prognoosi_soo.merge(
    prognoosi_koguarv,
    on="Kuupäev",
    how="left"
)

# Arvutame meeste ja naiste osakaalu koguprognoosist
prognoosi_soo["Osakaal_A7 (%)"] = (
    prognoosi_soo["Prognoos_kategooria_A7"]
    / prognoosi_soo["Koguarv_A7"]
    * 100
)

prognoosi_soo["Osakaal_A9 (%)"] = (
    prognoosi_soo["Prognoos_kategooria_A9"]
    / prognoosi_soo["Koguarv_A9"]
    * 100
)

# Jätame alles ainult mehed ja naised
prognoosi_soo = prognoosi_soo[
    prognoosi_soo["Sugu"].isin(["Mees", "Naine"])
].copy()

prognoosi_soo["Seeria"] = prognoosi_soo["Sugu"].map({
    "Mees": "Mehed",
    "Naine": "Naised"
})


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
# A7 JA A9 PROGNOOSIJONED
# ---------------------------------

prognoosi_varvid = {
    "Mehed": varvid["Mehed"],
    "Naised": varvid["Naised"]
}

prognoosi_stiilid = {
    "A7": "dash",
    "A9": "dot"
}

# Viimase tegeliku kuu väärtused prognoosijoonte ühendamiseks
oktoobri_tegelik = scatter_andmed[
    scatter_andmed["Kuupäev"] == "2026-10-01"
]

for seeria in ["Mehed", "Naised"]:

    tegelik = oktoobri_tegelik[
        oktoobri_tegelik["Seeria"] == seeria
    ]

    if tegelik.empty:
        continue

    for mudel in ["A7", "A9"]:

        prognoos = (
            prognoosi_soo[
                prognoosi_soo["Seeria"] == seeria
            ]
            .sort_values("Kuupäev")
        )

        osakaalu_veerg = f"Osakaal_{mudel} (%)"

        # Lisame oktoobri tegeliku väärtuse prognoosijoone algusesse
        x = [
            tegelik["Kuupäev"].iloc[0]
        ] + prognoos["Kuupäev"].tolist()

        y = [
            tegelik["Osakaal (%)"].iloc[0]
        ] + prognoos[osakaalu_veerg].tolist()

        fig_aastad.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=f"{seeria} – {mudel} prognoos",
                line=dict(
                    color=prognoosi_varvid[seeria],
                    width=3,
                    dash=prognoosi_stiilid[mudel]
                ),
                marker=dict(
                    size=6,
                    symbol="diamond" if mudel == "A7" else "square"
                ),
                hovertemplate=(
                    "%{x|%Y-%m}<br>"
                    "Prognoos: %{y:.2f}%"
                    "<extra>" + seeria + " – " + mudel + "</extra>"
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
# TEGELIKUD ANDMED
# ---------------------------------

tegelikud_soo_andmed = (
    filtreeritud
    .groupby(
        ["aasta", "kuu", "Riikide grupp"],
        observed=True
    )
    .agg(
        Koguarv=("Sugu", "size"),
        Naiste_arv=("Sugu", lambda x: (x == "Naine").sum()),
        Meeste_arv=("Sugu", lambda x: (x == "Mees").sum())
    )
    .reset_index()
)

tegelikud_soo_andmed["Kuupäev"] = pd.to_datetime(
    dict(
        year=tegelikud_soo_andmed["aasta"],
        month=tegelikud_soo_andmed["kuu"],
        day=1
    )
)

# Tegelikud andmed kuni oktoobrini 2026
tegelikud_soo_andmed = tegelikud_soo_andmed[
    (tegelikud_soo_andmed["Kuupäev"] < "2026-11-01")
    & (tegelikud_soo_andmed["Riikide grupp"] != "Puudub")
].copy()

tegelikud_soo_andmed["Naiste osakaal (%)"] = (
    tegelikud_soo_andmed["Naiste_arv"]
    / tegelikud_soo_andmed["Koguarv"]
    * 100
)

tegelikud_soo_andmed["Meeste osakaal (%)"] = (
    tegelikud_soo_andmed["Meeste_arv"]
    / tegelikud_soo_andmed["Koguarv"]
    * 100
)


# ---------------------------------
# PROGNOOSIANDMETE FILTREERIMINE
# ---------------------------------

prognoosi_lahteandmed = catboost_detailne_prognoos.copy()

# Rakendame prognoosidele samad kategoorilised filtrid,
# mis kehtivad tegelikele andmetele.
filtreeritavad_veerud = [
    "Piiripunkt",
    "Piiripunkti tüüp",
    "Kodakondsus",
    "Riikide grupp",
    "Vanuserühm"
]

for veerg in filtreeritavad_veerud:
    prognoosi_lahteandmed = prognoosi_lahteandmed[
        prognoosi_lahteandmed[veerg].isin(
            filtreeritud[veerg].dropna().unique()
        )
    ]

prognoosi_lahteandmed["Kuupäev"] = pd.to_datetime(
    prognoosi_lahteandmed["Kuupäev"]
)

prognoosi_lahteandmed = prognoosi_lahteandmed[
    prognoosi_lahteandmed["Riikide grupp"] != "Puudub"
].copy()


# ---------------------------------
# PROGNOOSID SOO JA RIIKIDE GRUPI JÄRGI
# ---------------------------------

prognoosi_soo = (
    prognoosi_lahteandmed
    .groupby(
        ["Kuupäev", "Riikide grupp", "Sugu"],
        observed=True
    )[
        [
            "Prognoos_kategooria_A7",
            "Prognoos_kategooria_A9"
        ]
    ]
    .sum()
    .reset_index()
)

# Kõigi soogruppide prognoositud koguarv
prognoosi_koguarv = (
    prognoosi_soo
    .groupby(
        ["Kuupäev", "Riikide grupp"],
        observed=True
    )[
        [
            "Prognoos_kategooria_A7",
            "Prognoos_kategooria_A9"
        ]
    ]
    .sum()
    .reset_index()
    .rename(
        columns={
            "Prognoos_kategooria_A7": "Koguarv_A7",
            "Prognoos_kategooria_A9": "Koguarv_A9"
        }
    )
)

# ---------------------------------
# SOO OSAKAALU GRAAFIKU FUNKTSIOON
# ---------------------------------

def loo_soo_osakaalu_graafik(sugu, osakaalu_veerg, pealkiri, graafiku_voti):

    # -----------------------------
    # TEGELIKUD ANDMED
    # -----------------------------

    tegelik = tegelikud_soo_andmed.copy()

    if sugu == "Naine":
        arvude_veerg = "Naiste_arv"
    else:
        arvude_veerg = "Meeste_arv"

    tegelik = tegelik.sort_values(
        ["Riikide grupp", "Kuupäev"]
    )

    fig = px.line(
        tegelik,
        x="Kuupäev",
        y=osakaalu_veerg,
        color="Riikide grupp",
        markers=True,
        title=pealkiri,
        labels={
            "Kuupäev": "Aeg",
            osakaalu_veerg: f"{sugu} osakaal piiriületustest (%)",
            "Riikide grupp": "Riikide grupp"
        },
        hover_data={
            "Koguarv": ":,",
            arvude_veerg: ":,",
            osakaalu_veerg: ":.2f"
        }
    )

    # Salvestame tegelike joonte värvid
    grupi_varvid = {
        trace.name: trace.line.color
        for trace in fig.data
    }


    # -----------------------------
    # PROGNOOSANDMED VALITUD SOO JAOKS
    # -----------------------------

    prognoos = (
        prognoosi_soo[
            prognoosi_soo["Sugu"] == sugu
        ]
        .merge(
            prognoosi_koguarv,
            on=["Kuupäev", "Riikide grupp"],
            how="left"
        )
        .sort_values(["Riikide grupp", "Kuupäev"])
    )

    prognoos["Osakaal_A7 (%)"] = (
        prognoos["Prognoos_kategooria_A7"]
        / prognoos["Koguarv_A7"]
        * 100
    )

    prognoos["Osakaal_A9 (%)"] = (
        prognoos["Prognoos_kategooria_A9"]
        / prognoos["Koguarv_A9"]
        * 100
    )


    # -----------------------------
    # A7 JA A9 PROGNOOSIJONED
    # -----------------------------

    for grupp in prognoos["Riikide grupp"].dropna().unique():

        grupi_prognoos = prognoos[
            prognoos["Riikide grupp"] == grupp
        ].sort_values("Kuupäev")

        # Oktoobri tegelik väärtus prognoosijoone ühendamiseks
        oktoobri_tegelik = tegelik[
            (tegelik["Riikide grupp"] == grupp)
            & (tegelik["Kuupäev"] == "2026-10-01")
        ]

        for mudel in ["A7", "A9"]:

            osakaalu_veerg_prognoos = f"Osakaal_{mudel} (%)"

            x = grupi_prognoos["Kuupäev"].tolist()
            y = grupi_prognoos[osakaalu_veerg_prognoos].tolist()

            # Lisame oktoobri tegeliku väärtuse joone algusesse
            if not oktoobri_tegelik.empty:

                x.insert(
                    0,
                    oktoobri_tegelik["Kuupäev"].iloc[0]
                )

                y.insert(
                    0,
                    oktoobri_tegelik[osakaalu_veerg].iloc[0]
                )

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    name=f"{grupp} – {mudel} prognoos",
                    line=dict(
                        color=grupi_varvid.get(grupp),
                        width=2.5,
                        dash="dash" if mudel == "A7" else "dot"
                    ),
                    marker=dict(
                        size=6,
                        symbol="diamond" if mudel == "A7" else "square"
                    ),
                    hovertemplate=(
                        "%{x|%Y-%m}<br>"
                        "Osakaal: %{y:.2f}%"
                        f"<extra>{grupp} – {mudel} prognoos</extra>"
                    )
                )
            )


    # -----------------------------
    # 50% VÕRDLUSJOON
    # -----------------------------

    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color="gray",
        line_width=1.5,
        annotation_text="50%",
        annotation_position="top left"
    )


    # -----------------------------
    # GRAAFIKU KUJUNDUS
    # -----------------------------

    fig.update_layout(
        xaxis_title="Aeg",
        yaxis=dict(
            title=f"{sugu} osakaal piiriületustest (%)",
            range=[0, 100]
        ),
        legend_title="Riikide grupp / stsenaarium",
        hovermode="closest"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=graafiku_voti
    )

# ---------------------------------
# NAISTE OSAKAAL RIIKIDE GRUPPIDE LÕIKES
# ---------------------------------

st.subheader("Naiste osakaalu muutus riikide gruppide lõikes")

loo_soo_osakaalu_graafik(
    sugu="Naine",
    osakaalu_veerg="Naiste osakaal (%)",
    pealkiri="Naiste osakaalu muutus riikide gruppide lõikes",
    graafiku_voti="naiste_osakaal_riikide_gruppide_prognoos"
)


# ---------------------------------
# MEESTE OSAKAAL RIIKIDE GRUPPIDE LÕIKES
# ---------------------------------

st.subheader("Meeste osakaalu muutus riikide gruppide lõikes")

loo_soo_osakaalu_graafik(
    sugu="Mees",
    osakaalu_veerg="Meeste osakaal (%)",
    pealkiri="Meeste osakaalu muutus riikide gruppide lõikes",
    graafiku_voti="meeste_osakaal_riikide_gruppide_prognoos"
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



# SOO JA VANUSERÜHMADE VÕRDLUS KODAKONDSUSTE LÕIKES
# ---------------------------------

st.subheader("Soo ja vanuserühmade võrdlus riikide gruppide / kodakondsuste lõikes")

# Aastate järjestamine
aastad = sorted(valitud_aastad)

# Koondame piiriületused kodakondsuse, vanuserühma ja soo järgi
liblika_andmed = (
    filtreeritud.loc[
        filtreeritud["Sugu"].isin(["Mees", "Naine"])
    ]
    .groupby(
        ["Riikide grupp", "Kodakondsus", "Vanuserühm", "Sugu"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Vanuserühmade järjestus
vanuseruhmade_jarjekord = ["0-17", "18-64", "65+"]

# Kontrollime, kas kõik kodakondsused on valitud
koik_kodakondsused = set(
    df["Kodakondsus"].dropna().unique()
)

koik_valitud = (
    set(valitud_kodakondsused) == koik_kodakondsused
)

# Aastate kuvamine pealkirjas
if aastad and all(
    aastad[i] + 1 == aastad[i + 1]
    for i in range(len(aastad) - 1)
):
    aastate_tekst = f"{aastad[0]}–{aastad[-1]}"
else:
    aastate_tekst = ", ".join(
        str(aasta) for aasta in aastad
    )

# Kõikide kodakondsuste korral koondame andmed kokku
# Kõikide kodakondsuste korral kuvame valitud riikide grupid eraldi
if koik_valitud:

    diagrammid = []

    for riikide_grupp in valitud_riikide_grupid:

        andmed = (
            liblika_andmed[
                liblika_andmed["Riikide grupp"] == riikide_grupp
            ]
            .groupby(
                ["Vanuserühm", "Sugu"],
                observed=True
            )["Piiriületuste arv"]
            .sum()
            .reset_index()
        )

        if not andmed.empty:

            # Muudame tehnilise nimetuse kasutajasõbralikuks
            grupi_pealkirjad = {
                "3.riik": "Kolmandad riigid"
            }

            pealkiri = grupi_pealkirjad.get(
                riikide_grupp,
                riikide_grupp
            )

            diagrammid.append(
                (pealkiri, andmed, "Riikide grupp", riikide_grupp)
            )

else:
    # Iga valitud kodakondsuse kohta eraldi diagramm
    diagrammid = []

    for kodakondsus in valitud_kodakondsused:

        andmed = liblika_andmed[
            liblika_andmed["Kodakondsus"] == kodakondsus
        ]

        if not andmed.empty:
            diagrammid.append(
                (kodakondsus, andmed, "Kodakondsus", kodakondsus)
            )

# Kuvame diagrammid kolme kaupa ühel real
for algus in range(0, len(diagrammid), 3):

    diagrammide_rida = diagrammid[algus:algus + 3]
    veerud = st.columns(len(diagrammide_rida))

for veerg, (kodakondsus, andmed, tunnuse_nimi, tunnuse_vaartus) in zip(
    veerud,
    diagrammide_rida
):

    with veerg:

        # Selle kodakondsuse andmed mõõdikute jaoks
        mõõdikute_andmed = filtreeritud[
            filtreeritud["Sugu"].isin(["Mees", "Naine"])
        ]

        mõõdikute_andmed = mõõdikute_andmed[
            mõõdikute_andmed[tunnuse_nimi] == tunnuse_vaartus
        ]

        # Absoluutne arv
        absoluutne_arv = len(mõõdikute_andmed)

        # Aastate võrdlus
        aastate_kaupa = (
            mõõdikute_andmed
            .groupby("aasta")
            .size()
        )

        # Keskmine aastane muutus
        aastaste_muutuste_protsendid = []

        for aasta in aastad:

            eelmine_aasta = aasta - 1

            if eelmine_aasta in aastate_kaupa.index and aasta in aastate_kaupa.index:

                eelmine_arv = aastate_kaupa.get(eelmine_aasta, 0)
                praegune_arv = aastate_kaupa.get(aasta, 0)

                if eelmine_arv > 0:

                    aastane_muutus = (
                        (praegune_arv - eelmine_arv)
                        / eelmine_arv
                    ) * 100

                    aastaste_muutuste_protsendid.append(
                        aastane_muutus
                    )

        if aastaste_muutuste_protsendid:

            keskmine_aastane_muutus = sum(
                aastaste_muutuste_protsendid
            ) / len(aastaste_muutuste_protsendid)

        else:
            keskmine_aastane_muutus = None

        # Arvestame ainult aastaid, mille kohta on andmed olemas
        olemasolevad_aastad = [
            aasta for aasta in aastad
            if aastate_kaupa.get(aasta, 0) > 0
        ]

        # Selle diagrammi tegelikud andmed mõõdikute jaoks
        mõõdikute_andmed = filtreeritud[
            filtreeritud["Sugu"].isin(["Mees", "Naine"])
        ].copy()

        # Rakendame vastava kodakondsuse või riikide grupi filtri
        mõõdikute_andmed = mõõdikute_andmed[
            mõõdikute_andmed[tunnuse_nimi] == tunnuse_vaartus
        ]

        # Tegelik absoluutarv
        tegelik_arv = len(mõõdikute_andmed)

        # Selle diagrammi prognoosiandmed
        prognoosi_mõõdikute_andmed = prognoos_filtreeritud[
            prognoos_filtreeritud["Sugu"].isin(["Mees", "Naine"])
        ].copy()

        # Rakendame vastava kodakondsuse või riikide grupi filtri
        prognoosi_mõõdikute_andmed = prognoosi_mõõdikute_andmed[
            prognoosi_mõõdikute_andmed[tunnuse_nimi] == tunnuse_vaartus
        ]

        # Prognoositud absoluutarv A7 mudeli järgi
        prognoositud_arv = prognoosi_mõõdikute_andmed[
            "Prognoos_kategooria_A7"
        ].sum()

        #Tegelik + prognoositud absoluutarv
        absoluutne_arv = tegelik_arv + prognoositud_arv

        # Aastate võrdlus
        aastate_kaupa = (
            mõõdikute_andmed
            .groupby("aasta")
            .size()
        )

        protsendi_muutus = None

        # Esimene valitud aasta
        algusaasta = aastad[0]

        algusaasta_arv = aastate_kaupa.get(
            algusaasta,
            0
        )

        # Viimase valitud aasta arv
        lopp_aasta = aastad[-1]

        if algusaasta_arv > 0:

            if lopp_aasta == 2027:

                # 2026 tegelik arv + 2027 prognoos
                lopp_aasta_arv = (
                aastate_kaupa.get(2026, 0)
                + prognoositud_arv
                )

            else:

                lopp_aasta_arv = aastate_kaupa.get(
                    lopp_aasta,
                    0
                )

            protsendi_muutus = (
                (lopp_aasta_arv - algusaasta_arv)
                / algusaasta_arv
            ) * 100

         #Kodakondsuse pealkiri
        st.subheader(f"{kodakondsus} | {aastate_tekst}")

        # Mõõdikud
        col_arv, col_muutus = st.columns(2)

        with col_arv:
            st.metric(
                "Absoluutne arv",
                f"{absoluutne_arv:,.0f}".replace(",", " ")
            )

            
        with col_muutus:

            col_periood, col_aasta = st.columns(2)

            # Muutus valitud aastatel
            with col_periood:

                if protsendi_muutus is not None:
                    varv = (
                        "#178939"
                        if protsendi_muutus > 0
                        else "#D32F2F"
                        if protsendi_muutus < 0
                        else "#808080"
                    )

                    vaartus = f"{protsendi_muutus:+.1f}%"

                else:
                    varv = "#808080"
                    vaartus = "—"

                st.markdown(
                    f"""
                    <div>
                        <div style="
                            font-size: 14px;
                            margin-bottom: 8px;
                        ">
                            Muutus valitud aastatel
                        </div>
                        <div style="
                            font-size: 29px;
                            font-weight: 600;
                            color: {varv};
                        ">
                            {vaartus}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Keskmine aastane muutus
            with col_aasta:

                if keskmine_aastane_muutus is not None:
                    varv_aasta = (
                        "#178939"
                        if keskmine_aastane_muutus > 0
                        else "#D32F2F"
                        if keskmine_aastane_muutus < 0
                        else "#808080"
                    )

                    vaartus_aasta = f"{keskmine_aastane_muutus:+.1f}%"

                else:
                    varv_aasta = "#808080"
                    vaartus_aasta = "—"

                st.markdown(
                    f"""
                    <div>
                        <div style="
                            font-size: 14px;
                            margin-bottom: 8px;
                        ">
                            Keskmine aastane muutus
                        </div>
                        <div style="
                            font-size: 29px;
                            font-weight: 600;
                            color: {varv_aasta};
                        ">
                            {vaartus_aasta}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Liblikdiagramm
        mehed = andmed[andmed["Sugu"] == "Mees"]
        naised = andmed[andmed["Sugu"] == "Naine"]

        fig = go.Figure()

        fig.add_trace(
                        go.Bar(
                            x=-mehed["Piiriületuste arv"],
                            y=mehed["Vanuserühm"],
                            orientation="h",
                            name="Mehed",
                            marker_color="#2878B5",
                            customdata=mehed["Piiriületuste arv"],
                            hovertemplate=(
                                "Vanuserühm: %{y}<br>"
                                "Mehed: %{customdata:,}"
                                "<extra></extra>"
                            )
                        )
                    )

        fig.add_trace(
                        go.Bar(
                            x=naised["Piiriületuste arv"],
                            y=naised["Vanuserühm"],
                            orientation="h",
                            name="Naised",
                            marker_color="#D65F8D",
                            customdata=naised["Piiriületuste arv"],
                            hovertemplate=(
                                "Vanuserühm: %{y}<br>"
                                "Naised: %{customdata:,}"
                                "<extra></extra>"
                            )
                        )
                    )

        max_arv = andmed["Piiriületuste arv"].max()
        telje_piir = max_arv * 1.2 if max_arv > 0 else 1

        fig.update_layout(
                        xaxis=dict(
                            title="Piiriületuste arv",
                            range=[-telje_piir, telje_piir],
                            zeroline=True,
                            zerolinewidth=2,
                            zerolinecolor="black",
                            tickformat=","
                        ),
                        yaxis=dict(
                            title="Vanuserühm",
                            categoryorder="array",
                            categoryarray=vanuseruhmade_jarjekord
                        ),
                        barmode="overlay",
                        legend_title="Sugu",
                        template="plotly_white",
                        height=350
                    )

        fig.update_xaxes(
                        tickvals=[
                            -telje_piir,
                            -telje_piir / 2,
                            0,
                            telje_piir / 2,
                            telje_piir
                        ],
                        ticktext=[
                            f"{telje_piir:,.0f}".replace(",", " "),
                            f"{telje_piir / 2:,.0f}".replace(",", " "),
                            "0",
                            f"{telje_piir / 2:,.0f}".replace(",", " "),
                            f"{telje_piir:,.0f}".replace(",", " ")
                        ]
                    )
        fig.update_layout(
            xaxis=dict(
                tickfont=dict(
                    size=16,
                    family="Arial",
                    color="black"
                )
            ),
            yaxis=dict(
                tickfont=dict(
                    size=16,
                    family="Arial",
                    color="black"
                )
            )
        )

        fig.update_traces(
            textfont=dict(
                size=16,
                family="Arial Black",
                color="black"
            )
        )


        st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=f"liblika_{algus}_{kodakondsus}"
                    )





st.subheader("Õhu- ja maismaapiiri kasutamine")

# ---------------------------------
# FILTRID
# ---------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    vordlus = st.selectbox(
        "Võrdle tunnuse järgi",
        ["Sugu", "Vanuserühm"],
        key="piiri_vordlus"
    )

with col2:
    if vordlus == "Sugu":
        vanusevalik = st.multiselect(
            "Vanuserühm",
            sorted(filtreeritud["Vanuserühm"].dropna().unique()),
            default=sorted(filtreeritud["Vanuserühm"].dropna().unique()),
            key="piiri_vanusefilter"
        )
    else:
        suguvalik = st.multiselect(
            "Sugu",
            sorted(filtreeritud["Sugu"].dropna().unique()),
            default=sorted(filtreeritud["Sugu"].dropna().unique()),
            key="piiri_sugufilter"
        )

with col3:
    moot = st.selectbox(
        "Näitajad",
        ["Piiriületuste arv", "Osakaal (%)"],
        key="piiri_moot"
    )

st.markdown(
    """
    <style>
    div[data-testid="stWidgetLabel"] p {
        font-size: 16px;
        font-weight: 400;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------
# ANDMETE FILTREERIMINE
# ---------------------------------

ohu_maismaa = filtreeritud[
    filtreeritud["Piiripunkti tüüp"].isin(
        ["Maismaapiir", "Õhupiir"]
    )
].copy()

if vordlus == "Sugu":
    ohu_maismaa = ohu_maismaa[
        ohu_maismaa["Vanuserühm"].isin(vanusevalik)
    ]
    grupeerimise_veerg = "Sugu"

else:
    ohu_maismaa = ohu_maismaa[
        ohu_maismaa["Sugu"].isin(suguvalik)
    ]
    grupeerimise_veerg = "Vanuserühm"


# ---------------------------------
# PIIRIÜLETUSTE ARVUTAMINE
# ---------------------------------

piirityypide_jarjekord = [
    "Maismaapiir",
    "Õhupiir"
]

tulemused = (
    ohu_maismaa
    .groupby(
        [grupeerimise_veerg, "Piiripunkti tüüp"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

tulemused["Osakaal (%)"] = (
    tulemused["Piiriületuste arv"]
    / tulemused.groupby(
        "Piiripunkti tüüp"
    )["Piiriületuste arv"].transform("sum")
    * 100
)


# ---------------------------------
# MÕÕDIKUD
# ---------------------------------

maismaa_arv = (
    ohu_maismaa["Piiripunkti tüüp"] == "Maismaapiir"
).sum()

ohu_arv = (
    ohu_maismaa["Piiripunkti tüüp"] == "Õhupiir"
).sum()

# Osakaalude erinevus
osakaalude_tabel = tulemused.pivot(
    index=grupeerimise_veerg,
    columns="Piiripunkti tüüp",
    values="Osakaal (%)"
).reindex(columns=piirityypide_jarjekord)

if (
    "Maismaapiir" in osakaalude_tabel.columns
    and "Õhupiir" in osakaalude_tabel.columns
    and not osakaalude_tabel.empty
):
    osakaalude_vahed = (
        osakaalude_tabel["Õhupiir"]
        - osakaalude_tabel["Maismaapiir"]
    ).abs()

    suurim_vahe = osakaalude_vahed.max()
    suurima_vahe_grupp = osakaalude_vahed.idxmax()

else:
    suurim_vahe = None
    suurima_vahe_grupp = None

# Maismaa / õhu suhe
if ohu_arv > 0:
    maismaa_ohu_suhe = maismaa_arv / ohu_arv
else:
    maismaa_ohu_suhe = None



# Eelmise aasta sama perioodi võrdlus
aastane_muutus = None

# Võtame ainult tegelikud aastad algandmestikust
tegelikud_aastad = sorted(
    set(valitud_aastad)
    & set(df["aasta"].dropna().unique())
)

if tegelikud_aastad:
    viimane_aasta = max(tegelikud_aastad)
    eelmine_aasta = viimane_aasta - 1

    praeguse_aasta_andmed = filtri_tingimused(
        df,
        aasta_valik=[viimane_aasta]
    )

    eelmise_aasta_andmed = filtri_tingimused(
        df,
        aasta_valik=[eelmine_aasta]
    )

    # Rakendame graafiku täiendavad filtrid
    if vordlus == "Sugu":
        praeguse_aasta_andmed = praeguse_aasta_andmed[
            praeguse_aasta_andmed["Vanuserühm"].isin(vanusevalik)
        ]

        eelmise_aasta_andmed = eelmise_aasta_andmed[
            eelmise_aasta_andmed["Vanuserühm"].isin(vanusevalik)
        ]

    else:
        praeguse_aasta_andmed = praeguse_aasta_andmed[
            praeguse_aasta_andmed["Sugu"].isin(suguvalik)
        ]

        eelmise_aasta_andmed = eelmise_aasta_andmed[
            eelmise_aasta_andmed["Sugu"].isin(suguvalik)
        ]

    # Ainult õhu- ja maismaapiir
    praeguse_aasta_andmed = praeguse_aasta_andmed[
        praeguse_aasta_andmed["Piiripunkti tüüp"].isin(
            ["Maismaapiir", "Õhupiir"]
        )
    ]

    eelmise_aasta_andmed = eelmise_aasta_andmed[
        eelmise_aasta_andmed["Piiripunkti tüüp"].isin(
            ["Maismaapiir", "Õhupiir"]
        )
    ]

    praegune_arv = len(praeguse_aasta_andmed)
    eelmine_arv = len(eelmise_aasta_andmed)

    if eelmine_arv > 0:
        aastane_muutus = (
            (praegune_arv - eelmine_arv)
            / eelmine_arv
            * 100
        )



# ---------------------------------
# GRAAFIKU PEALKIRI JA MÕÕDIKUD
# ---------------------------------

pealkiri, m1, m2, m3 = st.columns([2.2, 1, 1, 1])

with pealkiri:
    st.markdown(
        f"**{grupeerimise_veerg} piiriületused**"
    )
    st.caption("Õhu- ja maismaapiiri võrdlus")

with m1:
    if suurim_vahe is not None:
        st.markdown(
    f"""
    <div style="font-size: 14px;">
        Suurim osakaalude erinevus
    </div>
    <div style="
        font-size: 28px;
        font-weight: 400;
        color: inherit;
    " title="Suurim erinevus grupis: {suurima_vahe_grupp}">
        {suurim_vahe:.1f} protsendipunkti (pp)
    </div>
    """,
    unsafe_allow_html=True
)
    else:
        st.metric("Osakaalude erinevus", "—")

with m2:
    if maismaa_ohu_suhe is not None:
        st.markdown(
            f"""
            <div style="font-size: 14px;">
                Maismaa / õhu suhe
            </div>
            <div style="
                font-size: 28px;
                font-weight: 400;
                color: inherit;
            ">
                {maismaa_ohu_suhe:.2f} : 1
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.metric("Maismaa / õhu suhe", "—")

with m3:
    if aastane_muutus is not None:

        varv = (
            "#178939"
            if aastane_muutus > 0
            else "#FF4B4B"
            if aastane_muutus < 0
            else "#808495"
        )

        st.markdown(
            f"""
            <div style="font-size: 14px;">
                Muutus {viimane_aasta} vs {eelmine_aasta}
            </div>
            <div style="
                font-size: 28px;
                font-weight: 400;
                color: {varv};
            ">
                {aastane_muutus:+.1f}%
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.metric("Muutus vs eelmine aasta", "—")
# ---------------------------------
# GRAAFIK
# ---------------------------------

if moot == "Piiriületuste arv":
    y_veerg = "Piiriületuste arv"
    y_telg = "Piiriületuste arv"

else:
    y_veerg = "Osakaal (%)"
    y_telg = "Osakaal (%)"

fig_piir = px.bar(
    tulemused,
    x="Piiripunkti tüüp",
    y=y_veerg,
    color=grupeerimise_veerg,
    barmode="group",
    category_orders={
        "Piiripunkti tüüp": piirityypide_jarjekord
    },
    text_auto=".2s",
    title=f"{grupeerimise_veerg} piiriületused õhu- ja maismaapiiril",
    hover_data={
        "Piiriületuste arv": ":,.0f",
        "Osakaal (%)": ":.2f"
    }
)

fig_piir.update_layout(
    xaxis_title="Piiripunkti tüüp",
    yaxis_title=y_telg,
    legend_title=grupeerimise_veerg,
    showlegend=True
)

fig.update_layout(
    xaxis=dict(
        tickfont=dict(
            size=22,
            family="Arial",
            color="black"
        )
    ),
    yaxis=dict(
        tickfont=dict(
            size=22,
            family="Arial",
            color="black"
        )
    )
)

fig.update_traces(
    textfont=dict(
        size=20,
        family="Arial Black",
        color="black"
    )
)

st.plotly_chart(
    fig_piir,
    use_container_width=True,
    key="ohu_maismaa_vordlus"
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