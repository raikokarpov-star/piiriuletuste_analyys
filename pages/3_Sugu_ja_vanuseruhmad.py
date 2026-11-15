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
        grupp = vali_grupp(df, "sugu")
    with c2:
        kodakondsus = vali_kodakondsus(df, grupp, "sugu")
    kaasa_2026 = st.checkbox("Kaasa 2026 tegelikud andmed (osaline aasta)", value=False,
                              key="sugu_2026")
    aastad = vali_aastad(df, "sugu", kaasa_2026=kaasa_2026)
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

st.title("Sugu ja vanuserühmad")
st.caption("Eestisse sisenemiste demograafiline struktuur · ajalooline põhianalüüs 2021–2025")
d, aastad = lae_tegelik()
# Sisaldab ainult tegelikke piiriületusi: prognoose siia ei liideta.
s = d.loc[d["Sugu"].isin(["Mees", "Naine"])].copy()
if s.empty:
    st.warning("Valitud filtrites puuduvad soo andmed.")
    st.stop()
n = len(s)
mehi = int((s["Sugu"] == "Mees").sum())
naisi = int((s["Sugu"] == "Naine").sum())
muutus, cagr, periood = vordlus(s, aastad)
vanus = (s.groupby("Vanuserühm", observed=True).size().sort_values(ascending=False))
suurim_vanus = str(vanus.index[0]) if not vanus.empty else "—"

m1,m2,m3,m4,m5 = st.columns(5)
with m1: naidik("Piiriületusi (teadaolev sugu)", vorminda(n))
with m2: naidik("Meeste osakaal", protsent(mehi / n * 100))
with m3: naidik("Naiste osakaal", protsent(naisi / n * 100))
with m4: naidik("Muutus võrdlusaastatel", muutus, muutus=True)
with m5: naidik("Suurim vanuserühm", suurim_vanus)
if periood:
    a,b,kuud = periood
    st.caption(f"Aastamuutus: {a} → {b}; võrreldud samad kuud ({', '.join(map(str,kuud))}). ")

st.divider()
st.subheader("Soo ja vanuserühmade jaotus")
koond = (s.groupby(["Vanuserühm","Sugu"], observed=True).size().reset_index(name="Piiriületused"))
jarjekord = [x for x in ["0-17", "18-64", "65+"] if x in koond["Vanuserühm"].astype(str).unique()]
jarjekord += sorted(set(koond["Vanuserühm"].astype(str)) - set(jarjekord))
koond["Vanuserühm"] = koond["Vanuserühm"].astype(str)
fig = px.bar(koond, x="Vanuserühm", y="Piiriületused", color="Sugu",
             category_orders={"Vanuserühm":jarjekord}, barmode="group",
             color_discrete_map={"Mees":SININE,"Naine":ORANZ},
             hover_data={"Piiriületused":":,.0f"})
fig.update_layout(xaxis_title="Vanuserühm", yaxis_title="Piiriületuste arv", legend_title="Sugu")
st.plotly_chart(kujunda(fig), use_container_width=True)

st.subheader("Meeste ja naiste osakaalu muutumine ajas")
kuud = (s.groupby(["aasta","kuu","Sugu"], observed=True).size().reset_index(name="Arv"))
kuud["Kuupäev"] = pd.to_datetime(dict(year=kuud["aasta"],month=kuud["kuu"],day=1))
kuud["Osakaal (%)"] = kuud["Arv"] / kuud.groupby("Kuupäev")["Arv"].transform("sum") * 100
fig2 = px.line(kuud.sort_values("Kuupäev"),x="Kuupäev",y="Osakaal (%)", color="Sugu",
               color_discrete_map={"Mees":SININE,"Naine":ORANZ},
               hover_data={"Arv":":,.0f","Osakaal (%)":":.1f"})
fig2.add_hline(y=50,line_dash="dot",line_color="#888888")
fig2.update_layout(xaxis_title="Aeg",yaxis_title="Osakaal teadaoleva sooga piiriületustest (%)", yaxis_range=[0,100])
st.plotly_chart(kujunda(fig2), use_container_width=True)

with st.expander("Detailne vanuserühmade tabel ja eksport", expanded=False):
    tabel = koond.pivot_table(index="Vanuserühm",columns="Sugu",values="Piiriületused",fill_value=0,observed=True).reset_index()
    st.dataframe(tabel, use_container_width=True, hide_index=True)
    st.download_button("Laadi CSV alla", tabel.to_csv(index=False).encode("utf-8-sig"),
                       "sugu_vanuseruhmad.csv", "text/csv")
st.caption("Mõõdikud kajastavad piiriületusi, mitte unikaalseid isikuid. Meeste ja naiste osakaal on arvutatud teadaoleva sooga kirjete hulgas. Kodakondsus ei näita isiku hoiakuid ega julgeolekuriski.")
