"""Edasianalüüs: A7/A9 sisenemiste ja väljumiste prognoosid.

Salvesta projekti pages/8_Edasianaluus_prognoosid.py.
Ei muuda kodutöö lehti ega kasuta sisenemiste ajaloolisi andmeid väljumistena.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "Sisenemised": "catboost_detailne_prognoos.csv",
    "Väljumised": "catboost_detailne_valjumine.csv",
}
BACKTEST = {
    "Sisenemised": {
        "a7": "a7_tagasitestimine.csv",
        "a7_detail": "a7_tagasitestimine_detail.csv",
        "a9_test": "a9_treeningakende_test.csv",
        "a9_koond": "a9_treeningakende_koond.csv",
    },
    "Väljumised": {
        "a7": "a7_tagasitestimine_valjumine.csv",
        "a7_detail": "a7_tagasitestimine_detail_valjumine.csv",
        "a9_test": "a9_treeningakende_test_valjumine.csv",
        "a9_koond": "a9_treeningakende_koond_valjumine.csv",
    },
}
MODELS = {"A7": "Prognoos_kategooria_A7", "A9": "Prognoos_kategooria_A9"}
COLORS = {"Sisenemised": "#178939", "Väljumised": "#E69532"}

@st.cache_data(show_spinner=False)
def load_csv(filename):
    return pd.read_csv(ROOT / filename, parse_dates=["Kuupäev"] if filename.startswith("catboost_detailne") or "detail_" in filename else None)

@st.cache_data(show_spinner=False)
def load_backtest(filename):
    return pd.read_csv(ROOT / filename)


def load_forecasts():
    missing = [x for x in FILES.values() if not (ROOT / x).is_file()]
    if missing:
        st.error("Puuduvad prognoosifailid projekti juurkaustas: " + ", ".join(missing))
        st.stop()
    data = {direction: load_csv(filename) for direction, filename in FILES.items()}
    needed = ["Kuupäev", "Riikide grupp", "Piiripunkti tüüp", "Piiripunkt", *MODELS.values()]
    for direction, df in data.items():
        missing_columns = sorted(set(needed) - set(df.columns))
        if missing_columns:
            st.error(f"{direction}: puuduvad veerud {missing_columns}")
            st.stop()
        df["Kuupäev"] = pd.to_datetime(df["Kuupäev"])
    return data


def monthly(df, model):
    if df.empty:
        return pd.DataFrame(columns=["Kuupäev", "Prognoos"])
    return (df.groupby("Kuupäev", as_index=False, observed=True)[MODELS[model]]
            .sum().rename(columns={MODELS[model]: "Prognoos"}).sort_values("Kuupäev"))


def fmt(n):
    return f"{n:,.0f}".replace(",", " ")

st.title("Edasianalüüs · sisenemised ja väljumised")
st.caption("A7 (SARIMAX) ja A9 (trend + hooajalisus) · november 2026 – detsember 2027. Prognoosid ei ole tegelikud piiriületused.")

data = load_forecasts()

view = st.radio("Vaade", ["Võrdlus", "Sisenemised", "Väljumised"], horizontal=True, key="ea_vaade")
model = st.radio("Mudel", ["A7", "A9"], horizontal=True, key="ea_mudel")

all_groups = sorted(set().union(*[set(df["Riikide grupp"].dropna().astype(str)) for df in data.values()]))
all_types = [t for t in ["Maismaapiir", "Õhupiir"] if any((df["Piiripunkti tüüp"].astype(str) == t).any() for df in data.values())]
all_points = sorted(set().union(*[set(df["Piiripunkt"].dropna().astype(str)) for df in data.values()]))

c1, c2, c3 = st.columns(3)
with c1:
    group = st.selectbox("Riikide grupp", ["Kõik"] + all_groups, key="ea_grupp")
with c2:
    typ = st.selectbox("Piiripunkti tüüp", ["Kõik"] + all_types, key="ea_tyyp")
with c3:
    point = st.selectbox("Piiripunkt", ["Kõik"] + all_points, key="ea_punkt")

filtered = {}
for direction, source in data.items():
    mask = source["Piiripunkti tüüp"].astype(str).isin(["Maismaapiir", "Õhupiir"])
    if group != "Kõik":
        mask &= source["Riikide grupp"].astype(str).eq(group)
    if typ != "Kõik":
        mask &= source["Piiripunkti tüüp"].astype(str).eq(typ)
    if point != "Kõik":
        mask &= source["Piiripunkt"].astype(str).eq(point)
    filtered[direction] = source.loc[mask]

if view == "Võrdlus":
    entering = monthly(filtered["Sisenemised"], model).rename(columns={"Prognoos": "Sisenemised"})
    exiting = monthly(filtered["Väljumised"], model).rename(columns={"Prognoos": "Väljumised"})
    compare = entering.merge(exiting, on="Kuupäev", how="outer", validate="one_to_one").sort_values("Kuupäev")
    if compare.empty:
        st.warning("Valitud filtritega prognoose ei leitud.")
        st.stop()
    # Kui üks liikumissuund on antud kategoorias puudu, näitame puuduvat kuumahtu nullina.
    compare[["Sisenemised", "Väljumised"]] = compare[["Sisenemised", "Väljumised"]].fillna(0)
    compare["Erinevus"] = compare["Sisenemised"] - compare["Väljumised"]
    k1, k2, k3 = st.columns(3)
    k1.metric(f"Sisenemised {model} · 14 kuud", fmt(compare["Sisenemised"].sum()))
    k2.metric(f"Väljumised {model} · 14 kuud", fmt(compare["Väljumised"].sum()))
    k3.metric("Sisenemised − väljumised", f"{compare['Erinevus'].sum():+,.0f}".replace(",", " "))
    figure = go.Figure()
    for name in ["Sisenemised", "Väljumised"]:
        figure.add_trace(go.Scatter(x=compare["Kuupäev"], y=compare[name], mode="lines+markers",
                                    name=f"{name} {model}", line=dict(color=COLORS[name], width=2.5)))
    figure.update_layout(template="plotly_white", height=440, hovermode="x unified", xaxis_title="Kuu", yaxis_title="Prognoositud piiriületusi", font=dict(family="Arial"))
    st.plotly_chart(figure, width="stretch")
    st.dataframe(compare, hide_index=True, width="stretch", column_config={
        "Sisenemised": st.column_config.NumberColumn(format="%.0f"),
        "Väljumised": st.column_config.NumberColumn(format="%.0f"),
        "Erinevus": st.column_config.NumberColumn(format="%.0f"),
    })
    st.download_button("Laadi võrdlus CSV-na", compare.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"edasiarendus_vordlus_{model.lower()}.csv", mime="text/csv")
    st.caption("Erinevus on registreeritud piiriületuste arvu erinevus, mitte rändesaldo. Filtrite rakendamisel võrdleme ainult valitud kategooriat.")
else:
    df = filtered[view]
    result = monthly(df, model)
    if result.empty:
        st.warning("Valitud filtritega prognoose ei leitud.")
        st.stop()
    st.metric(f"{view} · {model} prognoos kokku", fmt(result["Prognoos"].sum()))
    fig = go.Figure(go.Scatter(x=result["Kuupäev"], y=result["Prognoos"], mode="lines+markers",
                                name=f"{view} {model}", line=dict(color=COLORS[view], width=2.5)))
    fig.update_layout(template="plotly_white", height=440, xaxis_title="Kuu", yaxis_title="Prognoositud piiriületusi")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(result, hide_index=True, width="stretch")
    st.download_button("Laadi prognoos CSV-na", result.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"edasiarendus_{view.lower()}_{model.lower()}.csv", mime="text/csv")

st.divider()
with st.expander("Mudelite tagasitestimise tulemused (riiklik tase)", expanded=False):
    direction = st.selectbox("Liikumissuund", ["Sisenemised", "Väljumised"], key="ea_test_suund")
    files = BACKTEST[direction]
    missing = [name for name in files.values() if not (ROOT / name).exists()]
    if missing:
        st.warning("Puuduvad tagasitestimise CSV-d: " + ", ".join(missing))
    else:
        a7_detail = load_backtest(files["a7_detail"])
        a7_detail["Absoluutviga"] = (a7_detail["Tegelik"] - a7_detail["Prognoos_A7"]).abs()
        a7_wape = 100 * a7_detail["Absoluutviga"].sum() / a7_detail["Tegelik"].abs().sum()
        a9_summary = load_backtest(files["a9_koond"])
        a9_summary["Treeningaken"] = pd.to_numeric(a9_summary["Treeningaken"])
        best = a9_summary.loc[a9_summary["WAPE"].idxmin()]
        st.write(f"A7: WAPE **{a7_wape:.2f}%** (2023–2026, {len(a7_detail)} kuud).")
        st.write(f"A9: väikseim tabeli WAPE **{best['WAPE']:.2f}%**, treeningaken **{int(best['Treeningaken'])} kuud**.")
        if direction == "Väljumised":
            st.caption("Väljumiste A9 treeningakende võrdlus põhineb 2024–2026 perioodi 34 kuul; A7 hõlmab 2023–2026 perioodi 46 kuud. Neid WAPE-sid ei saa pidada samal testperioodil tehtud otseseks mudelite võrdluseks.")
        st.dataframe(a9_summary.sort_values("WAPE"), hide_index=True, width="stretch")
        st.dataframe(load_backtest(files["a7"]), hide_index=True, width="stretch")

st.caption("See on eraldi edasiarendus. Kodutöö lehti ja nende CSV-faile ei muudeta.")
