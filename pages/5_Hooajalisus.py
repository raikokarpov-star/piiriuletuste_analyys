import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
import plotly.graph_objects as go

st.title("Piiriületuste hooajalisus")

df = st.session_state["andmed_df"]

catboost_detailne_prognoos = st.session_state["catboost_df"]

piiri_tyyp = st.session_state["piiri_tyyp"]
valitud_punktid = st.session_state["valitud_punktid"]
valitud_aastad = st.session_state["valitud_aastad"]
valitud_kodakondsused = st.session_state["valitud_kodakondsused"]
valitud_vanuseruhmad = st.session_state["valitud_vanuseruhmad"]
valitud_riikide_grupid = st.session_state["valitud_riikide_grupid"]

prognoos_filtreeritud = (
    catboost_detailne_prognoos[
        (catboost_detailne_prognoos["Piiripunkti tüüp"].isin(
            ["Maismaapiir", "Õhupiir"]
            if piiri_tyyp == "Kõik"
            else [piiri_tyyp]
        ))
        & (catboost_detailne_prognoos["Piiripunkt"].isin(valitud_punktid))
        & (catboost_detailne_prognoos["Kodakondsus"].isin(valitud_kodakondsused))
        & (catboost_detailne_prognoos["Vanuserühm"].isin(valitud_vanuseruhmad))
        & (catboost_detailne_prognoos["Riikide grupp"].isin(valitud_riikide_grupid))
    ]
    .copy()
)

# ---------------------------------
# 2027. AASTA PROGNOOSIDE HOOAJALISUS
# ---------------------------------

prognoos_2027 = prognoos_filtreeritud[
    prognoos_filtreeritud["Kuupäev"].dt.year == 2027
].copy()

prognoos_2027["kuu"] = prognoos_2027["Kuupäev"].dt.month

prognoos_2027_kuu = (
    prognoos_2027
    .groupby(
        ["kuu", "Piiripunkt"],
        observed=True
    )[
        ["Prognoos_kategooria_A7", "Prognoos_kategooria_A9"]
    ]
    .sum()
    .reset_index()
)

# A7 prognoosi aasta keskmine kuuprognoos
prognoos_2027_kuu["A7 aasta keskmine"] = (
    prognoos_2027_kuu
    .groupby("Piiripunkt", observed=True)["Prognoos_kategooria_A7"]
    .transform("mean")
)

# A9 prognoosi aasta keskmine kuuprognoos
prognoos_2027_kuu["A9 aasta keskmine"] = (
    prognoos_2027_kuu
    .groupby("Piiripunkt", observed=True)["Prognoos_kategooria_A9"]
    .transform("mean")
)

# A7 hooajalisuse indeks
prognoos_2027_kuu["A7 hooajalisuse indeks"] = (
    prognoos_2027_kuu["Prognoos_kategooria_A7"]
    / prognoos_2027_kuu["A7 aasta keskmine"]
    * 100
).round(1)

# A9 hooajalisuse indeks
prognoos_2027_kuu["A9 hooajalisuse indeks"] = (
    prognoos_2027_kuu["Prognoos_kategooria_A9"]
    / prognoos_2027_kuu["A9 aasta keskmine"]
    * 100
).round(1)

# A7 stabiliseeritud indeks
prognoos_2027_kuu["A7 stabiliseeritud indeks"] = np.where(
    prognoos_2027_kuu["Prognoos_kategooria_A7"] == 0,
    0,
    100 + (
        prognoos_2027_kuu["A7 hooajalisuse indeks"] - 100
    ) * (
        prognoos_2027_kuu["A7 aasta keskmine"]
        / (prognoos_2027_kuu["A7 aasta keskmine"] + 10)
    )
).round(1)

# A9 stabiliseeritud indeks
prognoos_2027_kuu["A9 stabiliseeritud indeks"] = np.where(
    prognoos_2027_kuu["Prognoos_kategooria_A9"] == 0,
    0,
    100 + (
        prognoos_2027_kuu["A9 hooajalisuse indeks"] - 100
    ) * (
        prognoos_2027_kuu["A9 aasta keskmine"]
        / (prognoos_2027_kuu["A9 aasta keskmine"] + 10)
    )
).round(1)
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

prognoos_2027_kuu["Kuu"] = prognoos_2027_kuu["kuu"].map(kuu_nimed)

hooajalisus["Kuu"] = hooajalisus["kuu"].map(kuu_nimed)


# Valime aastad, mida soovime võrrelda
hooajalisuse_aastad = st.multiselect(
    "Võrdle aastaid",
    options=sorted(
        aasta for aasta in hooajalisus["aasta"].unique()
        if aasta != 2027
    ),
    default=sorted(
        aasta for aasta in hooajalisus["aasta"].unique()
        if aasta != 2027
    )[-3:]
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
                width="stretch",
                key=f"hooajalisuse_graafik_{aasta}"
)

graafikute_aeg = time.perf_counter() - algus_graafikud

# ---------------------------------
# 2027. AASTA PROGNOOSIGRAAFIK
# ---------------------------------

st.subheader("2027. aasta hooajalisuse prognoos")

prognoosi_jooned = []

for piiripunkt in sorted(prognoos_2027_kuu["Piiripunkt"].unique()):

    piiripunkti_andmed = prognoos_2027_kuu[
        prognoos_2027_kuu["Piiripunkt"] == piiripunkt
    ].sort_values("kuu")

    prognoosi_jooned.append(
        go.Scatter(
            x=piiripunkti_andmed["Kuu"],
            y=piiripunkti_andmed["A7 stabiliseeritud indeks"],
            mode="lines+markers",
            name=f"{piiripunkt} – A7"
        )
    )

    prognoosi_jooned.append(
        go.Scatter(
            x=piiripunkti_andmed["Kuu"],
            y=piiripunkti_andmed["A9 stabiliseeritud indeks"],
            mode="lines+markers",
            name=f"{piiripunkt} – A9",
            line=dict(dash="dash")
        )
    )

fig_prognoos_2027 = go.Figure(data=prognoosi_jooned)

fig_prognoos_2027.add_hline(
    y=100,
    line_dash="dash",
    annotation_text="Aasta keskmine (100)"
)

fig_prognoos_2027.update_layout(
    title="2027. aasta prognoositud hooajalisus",
    xaxis_title="Kuu",
    yaxis_title="Stabiliseeritud hooajalisuse indeks",
    hovermode="x unified",
    xaxis=dict(
        categoryorder="array",
        categoryarray=list(kuu_nimed.values())
    ),
    margin=dict(l=40, r=20, t=50, b=40)
)

st.plotly_chart(
    fig_prognoos_2027,
    width="stretch",
    key="hooajalisuse_prognoos_2027"
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
    width="stretch",
    hide_index=True
)
