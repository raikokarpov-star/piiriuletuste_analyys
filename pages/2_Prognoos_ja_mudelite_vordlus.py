"""PPA – Prognoos ja mudelite võrdlus.
Paiguta projekti pages/ kausta. Vajalikud CSV failid projekti juurkausta.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.title("Prognoos ja mudelite võrdlus")
st.caption("Tagasitestimine 2023–2026 · tegelikud sisenemised kuni 2026. aasta oktoobrini · prognoos november 2026 – detsember 2027")

ROHELINE = "#178939"
PUNANE = "#FF4B4B"
SININE = "#2878B5"
ORANZ = "#E69532"
FAILID = {
    "a7": "a7_tagasitestimine.csv",
    "a7_detail": "a7_tagasitestimine_detail.csv",
    "a9": "a9_treeningakende_test.csv",
    "a9_koond": "a9_treeningakende_koond.csv",
    "prognoos": "catboost_detailne_prognoos.csv",
}

@st.cache_data(show_spinner=False)
def loe_csv(nimi):
    return pd.read_csv(nimi)

puuduvad = [nimi for nimi in FAILID.values() if not Path(nimi).is_file()]
if puuduvad:
    st.error("Projekti põhikaustast puuduvad vajalikud failid: " + ", ".join(puuduvad))
    st.info("Kopeeri CSV-failid samasse kausta, kus asub app.py. Pythoni faili enda koht on pages/ kaustas.")
    st.stop()

a7 = loe_csv(FAILID["a7"])
a7_detail = loe_csv(FAILID["a7_detail"])
a9 = loe_csv(FAILID["a9"])
a9_koond = loe_csv(FAILID["a9_koond"])
prog = loe_csv(FAILID["prognoos"])
a7_detail["Kuupäev"] = pd.to_datetime(a7_detail["Kuupäev"])
prog["Kuupäev"] = pd.to_datetime(prog["Kuupäev"])

# Koondnäitajad arvutame A7 kuupõhistest absoluutvigadest.
a7_detail["Absoluutviga"] = (a7_detail["Tegelik"] - a7_detail["Prognoos_A7"]).abs()
a7_mae = a7_detail["Absoluutviga"].mean()
a7_wape = 100 * a7_detail["Absoluutviga"].sum() / a7_detail["Tegelik"].abs().sum()

# A9 koondtabeli WAPE kasutab testiaasta tegelike mahtudega kaalumist.
# MAE kuvame A9 tabeli aruandlusnäitajana; 2026 on kümne kuuga, mistõttu
# see pole täpselt sama kui kuuvaatluste kaalutud koond-MAE.
a9_koond["Treeningaken"] = pd.to_numeric(a9_koond["Treeningaken"])
parim = a9_koond.loc[a9_koond["WAPE"].idxmin()]
aken = int(parim["Treeningaken"])

m1, m2, m3, m4 = st.columns(4)
m1.metric("A7 · WAPE", f"{a7_wape:.2f}%")
m2.metric("A7 · MAE", f"{a7_mae:,.0f}".replace(",", " "))
m3.metric(f"A9 ({aken} kuud) · WAPE", f"{parim['WAPE']:.2f}%")
m4.metric("Tagasitestitud kuid", len(a7_detail))
st.caption("WAPE puhul väiksem väärtus on parem. A7 tulemused on arvutatud kuupõhisest detailfailist; A9 tulemused pärinevad treeningakende koondtabelist.")

st.divider()
st.subheader("1. Tagasitestimise tulemused")

c1, c2 = st.columns([1.1, 1])
with c1:
    fig_w = px.bar(
        a9_koond.sort_values("Treeningaken"), x="Treeningaken", y="WAPE",
        title="A9 · treeningakna mõju WAPE-le", text="WAPE",
        labels={"Treeningaken": "Treeningakna pikkus (kuud)", "WAPE": "WAPE (%)"},
    )
    fig_w.update_traces(marker_color=SININE, texttemplate="%{y:.1f}%", textposition="outside")
    fig_w.add_hline(y=a7_wape, line_dash="dash", line_color=ROHELINE,
                    annotation_text="A7 koond-WAPE", annotation_position="top left")
    fig_w.update_layout(height=430, font=dict(family="Arial", color="black"),
                        xaxis=dict(dtick=2), yaxis=dict(rangemode="tozero"),
                        margin=dict(t=60, b=40))
    st.plotly_chart(fig_w, use_container_width=True)
with c2:
    fig_a = px.bar(
        a7.sort_values("Testaasta"), x="Testaasta", y="WAPE", text="WAPE",
        title="A7 · WAPE testiaastate lõikes",
        labels={"Testaasta": "Testiaasta", "WAPE": "WAPE (%)"},
    )
    fig_a.update_traces(marker_color=ROHELINE, texttemplate="%{y:.1f}%", textposition="outside")
    fig_a.update_layout(height=430, font=dict(family="Arial", color="black"),
                        xaxis=dict(dtick=1), yaxis=dict(rangemode="tozero"),
                        margin=dict(t=60, b=40))
    st.plotly_chart(fig_a, use_container_width=True)

st.caption("A7 ja A9 võrdlus on suunav: A9 kasutab treeningakende katset ning täielikku mudelite A1–A9 edetabelit ei saa ilma teiste mudelite tagasitestimise tulemusteta koostada.")

st.divider()
st.subheader("2. Tegelikud sisenemised ja A7/A9 prognoos")

# Filtrid teadlikult lokaalsed: ei kasutata endisi külgriba session_state väärtusi.
grupid = sorted(prog["Riikide grupp"].dropna().astype(str).unique().tolist())

# Kasutame ainult maismaa- ja õhupiiri
lubatud_tyybid = ["Maismaapiir", "Õhupiir"]

prog = prog.loc[
    prog["Piiripunkti tüüp"].isin(lubatud_tyybid)
].copy()

tyybid = lubatud_tyybid

vaikegrupp = "3.riik" if "3.riik" in grupid else (grupid[0] if grupid else "")
f1, f2, f3 = st.columns([1.4, 1.4, 1.8])
with f1:
    ulatus = st.selectbox("Riikide grupp", ["Kõik"] + grupid, index=(["Kõik"] + grupid).index(vaikegrupp) if vaikegrupp else 0)
with f2:
    tyyp = st.selectbox("Piiripunkti tüüp", ["Kõik"] + tyybid)
with f3:
    punktid = sorted(prog["Piiripunkt"].dropna().astype(str).unique().tolist())
    punkt = st.selectbox("Piiripunkt", ["Kõik"] + punktid)

q = prog
if ulatus != "Kõik":
    q = q.loc[q["Riikide grupp"].astype(str) == ulatus]
if tyyp != "Kõik":
    q = q.loc[q["Piiripunkti tüüp"].astype(str) == tyyp]
if punkt != "Kõik":
    q = q.loc[q["Piiripunkt"].astype(str) == punkt]

kuine = (q.groupby("Kuupäev", observed=True)[["Prognoos_kategooria_A7", "Prognoos_kategooria_A9"]]
         .sum().reset_index().sort_values("Kuupäev"))

fig_p = go.Figure()
# Tagasitestimise ajalooline seeria on RIIGILIK kogusumma, mitte kohalike filtrite alamhulk.
# Kohalike filtrite puhul seda ei kuvata, et vältida vale võrdlust.
riiklik_ulatus = ulatus == "Kõik" and tyyp == "Kõik" and punkt == "Kõik"
if riiklik_ulatus:
    fig_p.add_trace(go.Scatter(x=a7_detail["Kuupäev"], y=a7_detail["Tegelik"],
                               name="Tegelik · tagasitestimise sihtseeria", mode="lines",
                               line=dict(color="black", width=2)))
for veerg, nimi, varv, stiil in [
    ("Prognoos_kategooria_A7", "A7 · prognoos", ROHELINE, "dash"),
    ("Prognoos_kategooria_A9", "A9 · prognoos", ORANZ, "dot"),
]:
    fig_p.add_trace(go.Scatter(x=kuine["Kuupäev"], y=kuine[veerg], name=nimi,
                               mode="lines+markers", line=dict(color=varv, width=2.5, dash=stiil)))
fig_p.update_layout(height=475, font=dict(family="Arial", color="black"),
                    xaxis_title="Aeg", yaxis_title="Piiriületusi kuus",
                    hovermode="x unified", legend=dict(orientation="h", y=-0.23),
                    margin=dict(t=35, b=100))
st.plotly_chart(fig_p, use_container_width=True)
if not riiklik_ulatus:
    st.info("Filtreeritud prognoos on valitud grupi/piiripunkti kohta. Ajaloolist riiklikku tagasitestimise seeriat ei kuvata, sest see ei oleks sama ulatusega. Ajaloolise filtrivõrdluse jaoks oleks vaja vastavat PPA algandmete kuukoondit.")
else:
    st.caption("Must joon on A7 tagasitestimise tegelik riiklik sihtseeria (2023–2026 oktoober). Prognoosid algavad novembris 2026. Need on erinevad perioodid ning prognoose ei käsitleta tegelike tulemustena.")

st.divider()
st.subheader("3. Piiripunktide prognoositud töökoormus")
prog_2027 = prog.loc[(prog["Kuupäev"].dt.year == 2027) & (prog["Piiripunkti tüüp"].isin(["Maismaapiir", "Õhupiir"]))].copy()
if ulatus != "Kõik":
    prog_2027 = prog_2027.loc[prog_2027["Riikide grupp"].astype(str) == ulatus]
if tyyp != "Kõik":
    prog_2027 = prog_2027.loc[prog_2027["Piiripunkti tüüp"].astype(str) == tyyp]
if punkt != "Kõik":
    prog_2027 = prog_2027.loc[prog_2027["Piiripunkt"].astype(str) == punkt]
punktid_2027 = (prog_2027.groupby("Piiripunkt", observed=True)[["Prognoos_kategooria_A7", "Prognoos_kategooria_A9"]]
                .sum().reset_index().sort_values("Prognoos_kategooria_A7", ascending=False).head(5))
if not punktid_2027.empty:
    ta = punktid_2027.melt(id_vars="Piiripunkt", var_name="Mudel", value_name="Piiriületusi")
    ta["Piiripunkt"] = ta["Piiripunkt"].astype(str).str.replace(r"\s+piiripunkt\s*$", "", regex=True, case=False)
    ta["Mudel"] = ta["Mudel"].map({"Prognoos_kategooria_A7": "A7", "Prognoos_kategooria_A9": "A9"})
    fig_t = px.bar(ta, x="Piiripunkt", y="Piiriületusi", color="Mudel", barmode="group",
                   color_discrete_map={"A7": ROHELINE, "A9": ORANZ},
                   title="2027 · prognoositud piiriületused TOP 5 piiripunktis")
    fig_t.update_layout(height=440, font=dict(family="Arial", color="black"), xaxis_title="", yaxis_title="Piiriületusi", margin=dict(t=65))
    st.plotly_chart(fig_t, use_container_width=True)
else:
    st.info("Valitud filtritega prognoosiandmeid ei leitud.")

with st.expander("Tagasitestimise tabelid ja piirangud", expanded=False):
    st.markdown("**A7: tulemused aastati**")
    st.dataframe(a7, hide_index=True, use_container_width=True)
    st.markdown("**A9: treeningakende kokkuvõte**")
    st.dataframe(a9_koond, hide_index=True, use_container_width=True)
    st.markdown("**A9: katsed aasta ja treeningakna järgi**")
    st.dataframe(a9, hide_index=True, use_container_width=True)
    st.caption("2026. aasta test hõlmab 10 kuud. WAPE ei väljenda üksikute inimeste riski. Ilma A1–A6/A8 hindamistulemusteta ei saa koostada täielikku A1–A9 võrdlust.")
