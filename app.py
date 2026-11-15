import streamlit as st
from utils import lae_andmed, lae_catboost_detailne_prognoos

st.set_page_config(page_title="Eesti piiriületuste analüüs", page_icon="🇪🇪", layout="wide")

if "andmed_df" not in st.session_state:
    st.session_state["andmed_df"] = lae_andmed()

if "catboost_df" not in st.session_state:
    st.session_state["catboost_df"] = lae_catboost_detailne_prognoos()

# Uued lehed ei kasuta app.py ühiseid filtreid.
leht = st.navigation([
    st.Page("pages/6_Lühianalüüsi_metoodiline_kirjeldus.py", title="Lühianalüüs", icon="📚", default=True),
    st.Page("pages/1_Ülevaade.py", title="Ülevaade", icon="📊"),
    st.Page("pages/7_Kodakondsuste_vordlus.py", title="Kodakondsuste võrdlus", icon="🌍"),
    st.Page("pages/3_Sugu_ja_vanuseruhmad.py", title="Sugu ja vanuserühmad", icon="👥"),
    st.Page("pages/4_Ohupiir_ja_maismaapiir.py", title="Õhupiir vs maismaapiir", icon="✈️"),
    st.Page("pages/5_Hooajalisus.py", title="Hooajalisus", icon="📅"),
    st.Page("pages/2_Prognoos_ja_mudelite_vordlus.py", title="Prognoos ja mudelid", icon="📈"),
])
leht.run()
