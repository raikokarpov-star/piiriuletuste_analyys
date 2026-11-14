import streamlit as st

from utils import (
    lae_andmed,
    lae_catboost_detailne_prognoos,
    loo_punktide_valikud
)

st.set_page_config(
    page_title="Eesti piiriületuste analüüs",
    page_icon="🇪🇪",
    layout="wide"
)


# ---------------------------------
# ÜHISED ANDMED
# ---------------------------------

if "andmed_df" not in st.session_state:
    st.session_state["andmed_df"] = lae_andmed()

if "catboost_df" not in st.session_state:
    st.session_state["catboost_df"] = lae_catboost_detailne_prognoos()

df = st.session_state["andmed_df"]
catboost_detailne_prognoos = st.session_state["catboost_df"]


# ---------------------------------
# ÜHISED FILTRID
# ---------------------------------

st.sidebar.header("Filtrid")

piiri_tyyp = st.sidebar.selectbox(
    "Piiripunkti tüüp",
    ["Kõik", "Maismaapiir", "Õhupiir"],
    key="piiri_tyyp"
)

# ---------------------------------
# PIIRIPUNKTID
# ---------------------------------


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

# Piiripunkti tüübi muutmisel uuendame automaatselt valiku
if st.session_state.get("eelmine_piiri_tyyp") != piiri_tyyp:
    st.session_state["valitud_punktid"] = punktid
    st.session_state["eelmine_piiri_tyyp"] = piiri_tyyp

valitud_punktid = st.sidebar.multiselect(
    "Piiripunkt",
    options=punktid,
    key="valitud_punktid"
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
    default=aastad,
    key="valitud_aastad"
)

# ---------------------------------
# KUUD
# ---------------------------------

kuud = list(range(1, 13))

valitud_kuud = st.sidebar.multiselect(
    "Kuu",
    options=kuud,
    default=kuud,
    key="valitud_kuud"
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
    default=kodakondsused,
    key="valitud_kodakondsused"
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
    default=vanuseruhmad,
    key="valitud_vanuseruhmad"
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
    default=riikide_grupid,
    key="valitud_riikide_grupid"
)

# ---------------------------------
# LEHTEDE NAVIGATSIOON
# ---------------------------------

leht = st.navigation(
    [
        st.Page(
            "pages/1_Ülevaade.py",
            title="Ülevaade",
            default=True
        ),
        st.Page(
            "pages/3_Sugu_ja_vanuseruhmad.py",
            title="Sugu ja vanuserühmad",
            icon="👥"
        ),
        st.Page(
            "pages/4_Ohupiir_ja_maismaapiir.py",
            title="Õhupiir vs maismaapiir",
            icon="✈️"
        ),
        st.Page(
            "pages/5_Hooajalisus.py",
            title="Hooajalisus",
            icon="📅"
        ),
        st.Page(
            "pages/2_Prognoos.py",
            title="Prognoos",
            icon="📈"
        ),
    ]
)


leht.run()
