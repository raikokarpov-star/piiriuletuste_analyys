
import streamlit as st
import pandas as pd


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


@st.cache_data
def lae_catboost_detailne_prognoos():

    return pd.read_csv(
        "catboost_detailne_prognoos.csv",
        parse_dates=["Kuupäev"]
    )


@st.cache_data
def loo_punktide_valikud(df):

    return df[
        ["Piiripunkti tüüp", "Piiripunkt"]
    ].drop_duplicates()

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