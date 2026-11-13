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
    use_container_width=True,
    key="ohu_maismaa_vordlus"
)
