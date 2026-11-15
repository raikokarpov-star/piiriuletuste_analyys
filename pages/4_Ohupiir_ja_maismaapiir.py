# LEHEKESKSED FILTRID — parandatud versioon 2026-11-15
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from lehe_filtrid import vali_grupp, vali_kodakondsus, vali_aastad, filtreeri

ROHELINE = "#178939"
PUNANE = "#FF4B4B"
SININE = "#2878B5"
ORANZ = "#E69532"

def vorminda(n):
    return f"{int(n):,}".replace(",", " ")

def protsent(v, margiga=False):
    if v is None or not np.isfinite(v):
        return "—"
    return f"{v:+.1f}%" if margiga else f"{v:.1f}%"

def naidik(nimi, vaartus, muutus=False):
    color = "inherit"
    if muutus and vaartus is not None and np.isfinite(vaartus):
        color = ROHELINE if vaartus > 0 else PUNANE if vaartus < 0 else "inherit"
    sisu = protsent(vaartus, True) if muutus else str(vaartus)
    st.markdown(
        f'<div style="font-size:14px;opacity:.85">{nimi}</div>'
        f'<div style="font-size:26px;font-weight:600;color:{color}">{sisu}</div>',
        unsafe_allow_html=True
    )

def lae_tegelik():
    df = st.session_state["andmed_df"]
    c1, c2 = st.columns(2)
    with c1:
        grupp = vali_grupp(df, "piir")
    with c2:
        kodakondsus = vali_kodakondsus(df, grupp, "piir")
    kaasa_2026 = st.checkbox("Kaasa 2026 tegelikud andmed (osaline aasta)", value=False,
                              key="piir_2026")
    aastad = vali_aastad(df, "piir", kaasa_2026=kaasa_2026)
    if not aastad:
        st.info("Vali vähemalt üks aasta.")
        st.stop()
    d = filtreeri(df, grupp=grupp, kodakondsus=kodakondsus, aastad=aastad)
    if d.empty:
        st.warning("Valitud filtritega tegelikke piiriületusi ei leitud.")
        st.stop()
    return d, aastad

def vordlus(d, aastad):
    if len(aastad) < 2:
        return None, None, None
    alg, lopp = min(aastad), max(aastad)
    algkuud = set(d.loc[d["aasta"] == alg, "kuu"].astype(int))
    loppkuud = set(d.loc[d["aasta"] == lopp, "kuu"].astype(int))
    kuud = sorted(algkuud & loppkuud)
    if not kuud:
        return None, None, None
    n0 = int(((d["aasta"] == alg) & d["kuu"].isin(kuud)).sum())
    n1 = int(((d["aasta"] == lopp) & d["kuu"].isin(kuud)).sum())
    if n0 == 0:
        return None, None, None
    muut = (n1 / n0 - 1) * 100
    kasv = ((n1 / n0) ** (1 / (lopp - alg)) - 1) * 100 if n1 > 0 else None
    return muut, kasv, (alg, lopp, kuud)

def kujunda(fig, korgus=450):
    fig.update_layout(
        template="plotly_white", height=korgus, margin=dict(l=20, r=25, t=45, b=55),
        font=dict(family="Arial", color="black"), hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black"))
    )
    return fig

st.title("Maismaa- ja õhupiiri võrdlus")
st.caption("Eestisse sisenemiste piiritüübipõhine struktuur · ajalooline põhianalüüs 2021–2025")
d, aastad = lae_tegelik()
piirid = ["Maismaapiir", "Õhupiir"]
koond = d.groupby("Piiripunkti tüüp", observed=True).size().reindex(piirid, fill_value=0)
maa, ohk = int(koond["Maismaapiir"]), int(koond["Õhupiir"])
n = maa + ohk
muutus, cagr, periood = vordlus(d, aastad)

m1,m2,m3,m4,m5 = st.columns(5)
with m1: naidik("Piiriületusi kokku", vorminda(n))
with m2: naidik("Maismaapiiri osakaal", protsent(100*maa/n))
with m3: naidik("Õhupiiri osakaal", protsent(100*ohk/n))
with m4: naidik("Maismaa / õhu suhe", f"{maa/ohk:.2f} : 1" if ohk else "—")
with m5: naidik("Muutus võrdlusaastatel", muutus, muutus=True)
if periood:
    a,b,kuud = periood
    st.caption(f"Muutus: {a} → {b}, ainult ühised kuud ({', '.join(map(str,kuud))}).")

st.divider()
st.subheader("Maismaa- ja õhupiiri piiriületuste arv")
val = koond.reset_index()
val.columns = ["Piiripunkti tüüp","Piiriületused"]
fig = px.bar(val,x="Piiripunkti tüüp",y="Piiriületused", color="Piiripunkti tüüp",
             color_discrete_map={"Maismaapiir":ROHELINE,"Õhupiir":SININE},
             text="Piiriületused", category_orders={"Piiripunkti tüüp":piirid})
fig.update_traces(texttemplate="%{text:,.0f}",textposition="outside",cliponaxis=False)
fig.update_layout(showlegend=False,xaxis_title="Piiripunkti tüüp",yaxis_title="Piiriületuste arv")
st.plotly_chart(kujunda(fig,410),use_container_width=True)

st.subheader("Piiritüüpide osakaalu muutumine ajas")
kuukoond = (d.groupby(["aasta","kuu","Piiripunkti tüüp"], observed=True).size().reset_index(name="Arv"))
kuukoond["Kuupäev"] = pd.to_datetime(dict(year=kuukoond["aasta"],month=kuukoond["kuu"],day=1))
kuukoond["Osakaal (%)"] = kuukoond["Arv"] / kuukoond.groupby("Kuupäev")["Arv"].transform("sum") * 100
fig2 = px.line(kuukoond.sort_values("Kuupäev"), x="Kuupäev", y="Osakaal (%)", color="Piiripunkti tüüp",
               color_discrete_map={"Maismaapiir":ROHELINE,"Õhupiir":SININE})
fig2.update_layout(xaxis_title="Aeg",yaxis_title="Piiritüübi osakaal (%)",yaxis_range=[0,100],legend_title=None)
st.plotly_chart(kujunda(fig2),use_container_width=True)

with st.expander("Piiripunktide detailvõrdlus", expanded=False):
    punktid = (d.groupby(["Piiripunkt","Piiripunkti tüüp"],observed=True)
               .size().reset_index(name="Piiriületused").sort_values("Piiriületused",ascending=False))
    top = punktid.head(10).sort_values("Piiriületused")
    fig3 = px.bar(top,y="Piiripunkt",x="Piiriületused",orientation="h",color="Piiripunkti tüüp",
                  color_discrete_map={"Maismaapiir":ROHELINE,"Õhupiir":SININE})
    fig3.update_layout(xaxis_title="Piiriületuste arv",yaxis_title="",legend_title=None)
    st.plotly_chart(kujunda(fig3,450),use_container_width=True)
    st.dataframe(punktid,use_container_width=True,hide_index=True)
    st.download_button("Laadi CSV alla",punktid.to_csv(index=False).encode("utf-8-sig"),
                       "piiripunktide_vordlus.csv","text/csv")
st.caption("Piiriületuste arvu muutus ei tõenda iseenesest geopoliitilise sündmuse või piirimeetme põhjuslikku mõju.")
