
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

