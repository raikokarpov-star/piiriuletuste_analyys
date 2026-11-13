import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils import filtri_tingimused


# ---------------------------------
# LEHE SEADISTUSED
# ---------------------------------

st.title("Sugu ja vanuserühmad")


# ---------------------------------
# ÜHISED ANDMED APP.PY-ST
# ---------------------------------

df = st.session_state["andmed_df"]

catboost_detailne_prognoos = st.session_state["catboost_df"]


# ---------------------------------
# ÜHISED FILTRID
# ---------------------------------

valitud_aastad = st.session_state["valitud_aastad"]
valitud_kodakondsused = st.session_state["valitud_kodakondsused"]
valitud_vanuseruhmad = st.session_state["valitud_vanuseruhmad"]
valitud_riikide_grupid = st.session_state["valitud_riikide_grupid"]


# ---------------------------------
# ANDMETE FILTREERIMINE
# ---------------------------------

filtreeritud = filtri_tingimused(df)

prognoos_filtreeritud = filtri_tingimused(
    catboost_detailne_prognoos
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
    width="stretch",
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
    pd.to_numeric(tegelikud_soo_andmed["Naiste_arv"])
    / tegelikud_soo_andmed["Koguarv"]
    * 100
)

tegelikud_soo_andmed["Meeste osakaal (%)"] = (
    pd.to_numeric(tegelikud_soo_andmed["Meeste_arv"])
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

    tegelikud_andmed = tegelikud_soo_andmed.copy()
    tegelikud_andmed = tegelikud_andmed.sort_values(
        ["Riikide grupp", "Kuupäev"]
    )
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
        width="stretch",
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
                            width="stretch",
                            key=f"liblika_{algus}_{kodakondsus}"
                        )
