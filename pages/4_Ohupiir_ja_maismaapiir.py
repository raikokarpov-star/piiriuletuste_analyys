import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils import filtri_tingimused


# ---------------------------------
# LEHE SEADISTUSED
# ---------------------------------

st.title("Õhupiir vs maismaapiir")


# ---------------------------------
# ÜHISED ANDMED APP.PY-ST
# ---------------------------------

df = st.session_state["andmed_df"]

catboost_detailne_prognoos = st.session_state["catboost_df"]


# ---------------------------------
# ANDMETE FILTREERIMINE
# ---------------------------------

filtreeritud = filtri_tingimused(df)

prognoos_filtreeritud = filtri_tingimused(
    catboost_detailne_prognoos
)


valitud_aastad = st.session_state["valitud_aastad"]

col_pealkiri, col_aastad, col_tyhi = st.columns([4, 1.5, 4])

with col_pealkiri:
    st.subheader("Õhu- ja maismaapiiri kasutamine")

with col_aastad:
    st.markdown(
        f"""
        <div style="
            text-align: left;
            padding-top: 8px;
            font-size: 24px;
            font-weight: 600;
        ">
        {
            f"{min(valitud_aastad)}–{max(valitud_aastad)}"
            if valitud_aastad
            else "Aastaid pole valitud"
        }
        </div>
        """,
        unsafe_allow_html=True
    )
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
        ["Piiriületuste arv", "Keskmine piiriületuste arv kuus", "Osakaal (%)"],
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
# TEGELIKUD JA PROGNOOSITUD ANDMED
# ---------------------------------

piirityypide_jarjekord = [
    "Maismaapiir",
    "Õhupiir"
]

# Tegelikud piiriületused
ohu_maismaa = filtreeritud[
    filtreeritud["Piiripunkti tüüp"].isin(
        piirityypide_jarjekord
    )
].copy()

# A7 prognoosid
prognoos_ohu_maismaa = prognoos_filtreeritud[
    prognoos_filtreeritud["Piiripunkti tüüp"].isin(
        piirityypide_jarjekord
    )
].copy()


# Rakendame kohalikud filtrid mõlemale andmestikule
if vordlus == "Sugu":

    ohu_maismaa = ohu_maismaa[
        ohu_maismaa["Vanuserühm"].isin(vanusevalik)
    ]

    prognoos_ohu_maismaa = prognoos_ohu_maismaa[
        prognoos_ohu_maismaa["Vanuserühm"].isin(vanusevalik)
    ]

    grupeerimise_veerg = "Sugu"

else:

    ohu_maismaa = ohu_maismaa[
        ohu_maismaa["Sugu"].isin(suguvalik)
    ]

    prognoos_ohu_maismaa = prognoos_ohu_maismaa[
        prognoos_ohu_maismaa["Sugu"].isin(suguvalik)
    ]

    grupeerimise_veerg = "Vanuserühm"

# ---------------------------------
# KUU PÕHINE KOONDAMINE
# ---------------------------------

# Tegelikud piiriületused
tegelikud_kuu = (
    ohu_maismaa
    .groupby(
        [
            "aasta",
            "kuu",
            grupeerimise_veerg,
            "Piiripunkti tüüp"
        ],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# A7 prognoositud piiriületused
prognoos_kuu = (
    prognoos_ohu_maismaa
    .groupby(
        [
            "aasta",
            "kuu",
            grupeerimise_veerg,
            "Piiripunkti tüüp"
        ],
        observed=True
    )["Prognoos_kategooria_A7"]
    .sum()
    .reset_index(name="Piiriületuste arv")
)

# Ühendame tegelikud ja prognoositud andmed
kuu_tulemused = pd.concat(
    [
        tegelikud_kuu,
        prognoos_kuu
    ],
    ignore_index=True
)

# Koondame kuude kaupa
kuu_tulemused = (
    kuu_tulemused
    .groupby(
        [
            "aasta",
            "kuu",
            grupeerimise_veerg,
            "Piiripunkti tüüp"
        ],
        observed=True,
        as_index=False
    )["Piiriületuste arv"]
    .sum()
)


# ---------------------------------
# KOGU PERIOODI TULEMUSED
# ---------------------------------

tulemused = (
    kuu_tulemused
    .groupby(
        [grupeerimise_veerg, "Piiripunkti tüüp"],
        observed=True
    )["Piiriületuste arv"]
    .sum()
    .reset_index()
)

# Keskmine piiriületuste arv kuus
kuude_arv = (
    kuu_tulemused[
        ["aasta", "kuu"]
    ]
    .drop_duplicates()
    .shape[0]
)

if kuude_arv > 0:
    tulemused["Keskmine piiriületuste arv kuus"] = (
        tulemused["Piiriületuste arv"] / kuude_arv
    )
else:
    tulemused["Keskmine piiriületuste arv kuus"] = 0


# Osakaal
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

maismaa_arv = tulemused.loc[
    tulemused["Piiripunkti tüüp"] == "Maismaapiir",
    "Piiriületuste arv"
].sum()

ohu_arv = tulemused.loc[
    tulemused["Piiripunkti tüüp"] == "Õhupiir",
    "Piiriületuste arv"
].sum()

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



# ---------------------------------
# EELMISE AASTA SAMA PERIOODI VÕRDLUS
# ---------------------------------

aastane_muutus = None

# Eraldi kasvumäärad õhu- ja maismaapiirile
aastane_kasvumaara = {
    "Maismaapiir": None,
    "Õhupiir": None
}


def aasta_piiriuletuste_andmed(aasta):

    tegelikud = filtri_tingimused(
        df,
        aasta_valik=[aasta]
    )

    prognoosid = filtri_tingimused(
        catboost_detailne_prognoos,
        aasta_valik=[aasta]
    )

    # Kohalikud filtrid
    if vordlus == "Sugu":

        tegelikud = tegelikud[
            tegelikud["Vanuserühm"].isin(vanusevalik)
        ]

        prognoosid = prognoosid[
            prognoosid["Vanuserühm"].isin(vanusevalik)
        ]

    else:

        tegelikud = tegelikud[
            tegelikud["Sugu"].isin(suguvalik)
        ]

        prognoosid = prognoosid[
            prognoosid["Sugu"].isin(suguvalik)
        ]

    # Ainult õhu- ja maismaapiir
    piiriliigid = ["Maismaapiir", "Õhupiir"]

    tegelikud = tegelikud[
        tegelikud["Piiripunkti tüüp"].isin(piiriliigid)
    ]

    prognoosid = prognoosid[
        prognoosid["Piiripunkti tüüp"].isin(piiriliigid)
    ]

    # 2027 puhul kasutame A7 prognoosi
    if aasta == 2027:

        tulemus = (
            prognoosid
            .groupby(
                ["kuu", "Piiripunkti tüüp"],
                observed=True
            )["Prognoos_kategooria_A7"]
            .sum()
            .reset_index(name="Piiriületuste arv")
        )

    else:

        tulemus = (
            tegelikud
            .groupby(
                ["kuu", "Piiripunkti tüüp"],
                observed=True
            )
            .size()
            .reset_index(name="Piiriületuste arv")
        )

    return tulemus


if len(valitud_aastad) >= 2:

    eelmine_aasta = min(valitud_aastad)
    viimane_aasta = max(valitud_aastad)

    eelmine_andmed = aasta_piiriuletuste_andmed(
        eelmine_aasta
    )

    praegune_andmed = aasta_piiriuletuste_andmed(
        viimane_aasta
    )

    # Leiame kuud, mis on olemas mõlemal võrdlusaastal
    eelmine_kuu = set(eelmine_andmed["kuu"].dropna())
    praegune_kuu = set(praegune_andmed["kuu"].dropna())

    vordluskuud = sorted(eelmine_kuu & praegune_kuu)

    # Jätkame ainult siis, kui leidub võrreldavaid kuid
    if vordluskuud:

        eelmine_andmed = eelmine_andmed[
            eelmine_andmed["kuu"].isin(vordluskuud)
        ]

        praegune_andmed = praegune_andmed[
            praegune_andmed["kuu"].isin(vordluskuud)
        ]

        # Senine muutuse mõõdik: õhu- ja maismaapiir kokku
        eelmine_arv = eelmine_andmed[
            "Piiriületuste arv"
        ].sum()

        praegune_arv = praegune_andmed[
            "Piiriületuste arv"
        ].sum()

        if eelmine_arv > 0:

            aastane_muutus = (
                (praegune_arv - eelmine_arv)
                / eelmine_arv
                * 100
            )

        
# Arvutame osakaalude keskmise aastase kasvumäära
aastate_vahe = viimane_aasta - eelmine_aasta

# Õhu- ja maismaapiiri ületuste koguarv mõlemal võrdlusaastal
eelmine_kokku = eelmine_andmed[
    "Piiriületuste arv"
].sum()

praegune_kokku = praegune_andmed[
    "Piiriületuste arv"
].sum()

for piiriliik in ["Maismaapiir", "Õhupiir"]:

    eelmine_piir_arv = eelmine_andmed.loc[
        eelmine_andmed["Piiripunkti tüüp"] == piiriliik,
        "Piiriületuste arv"
    ].sum()

    praegune_piir_arv = praegune_andmed.loc[
        praegune_andmed["Piiripunkti tüüp"] == piiriliik,
        "Piiriületuste arv"
    ].sum()

    if (
        eelmine_kokku > 0
        and praegune_kokku > 0
        and aastate_vahe > 0
    ):

        eelmine_osakaal = (
            eelmine_piir_arv / eelmine_kokku
        )

        praegune_osakaal = (
            praegune_piir_arv / praegune_kokku
        )

        if eelmine_osakaal > 0:

            aastane_kasvumaara[piiriliik] = (
                (
                    praegune_osakaal
                    / eelmine_osakaal
                ) ** (1 / aastate_vahe)
                - 1
            ) * 100






# ---------------------------------
# GRAAFIKU PEALKIRI JA MÕÕDIKUD
# ---------------------------------


st.markdown(f"**{grupeerimise_veerg} piiriületused**")

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    if suurim_vahe is not None:
        st.markdown(
            f"""
            <div style="font-size: 14px;">
                Suurim osakaalude erinevus
            </div>
            <div style="
                font-size: 26px;
                font-weight: 400;
                color: inherit;
            " title="Suurim erinevus grupis: {suurima_vahe_grupp}">
                {suurim_vahe:.1f} (pp)
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
                font-size: 26px;
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
                Muutus valitud aastate vahel
            </div>
            <div style="
                font-size: 26px;
                font-weight: 400;
                color: {varv};
            ">
                {aastane_muutus:+.1f}%
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.metric(
            "Muutus valitud aastate vahel",
            "—"
        )

with m4:
    maismaa_kasv = aastane_kasvumaara["Maismaapiir"]

    if maismaa_kasv is not None:

        varv = (
            "#178939"
            if maismaa_kasv > 0
            else "#FF4B4B"
            if maismaa_kasv < 0
            else "#808495"
        )

        st.markdown(
            f"""
            <div style="font-size: 14px;">
                Maismaapiiri osakaalu keskmine aastane kasv
            </div>
            <div style="
                font-size: 26px;
                font-weight: 400;
                color: {varv};
            ">
                {maismaa_kasv:+.1f}%
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.metric(
            "Maismaapiiri osakaalu keskmine aastane kasv",
            "—"
        )

with m5:
    ohu_kasv = aastane_kasvumaara["Õhupiir"]

    if ohu_kasv is not None:

        varv = (
            "#178939"
            if ohu_kasv > 0
            else "#FF4B4B"
            if ohu_kasv < 0
            else "#808495"
        )

        st.markdown(
            f"""
            <div style="font-size: 14px;">
                Õhupiiri osakaalu keskmine aastane kasv
            </div>
            <div style="
                font-size: 26px;
                font-weight: 400;
                color: {varv};
            ">
                {ohu_kasv:+.1f}%
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.metric(
            "Õhupiiri osakaalu keskmine aastane kasv",
            "—"
        )


# ---------------------------------
# GRAAFIK
# ---------------------------------

if moot == "Piiriületuste arv":
    y_veerg = "Piiriületuste arv"
    y_telg = "Piiriületuste arv"

elif moot == "Keskmine piiriületuste arv kuus":
    y_veerg = "Keskmine piiriületuste arv kuus"
    y_telg = "Keskmine piiriületuste arv kuus"

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

fig_piir.update_layout(
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

fig_piir.update_traces(
    textfont=dict(
        size=20,
        family="Arial Black",
        color="black"
    )
)

st.plotly_chart(
    fig_piir,
    width="stretch",
    key="ohu_maismaa_vordlus"
)

