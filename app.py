import streamlit as st

st.set_page_config(
    page_title="Eesti piiriületuste analüüs",
    page_icon="🇪🇪",
    layout="wide"
)

leht = st.navigation(
    [
        st.Page(
            "pages/1_Ülevaade.py",
            title="Ülevaade",
            default=True
        ),
        st.Page(
            "pages/2_Prognoos.py",
            title="Prognoos",
            icon="📈"
        )
    ]
)

leht.run()