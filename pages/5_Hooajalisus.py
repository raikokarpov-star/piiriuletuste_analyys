# LEHEKESKSED FILTRID — parandatud versioon 2026-11-15
"""PPA Eestisse sisenemiste hooajalisus: tegelikud 2021–2025 ja 2026 võrdlus."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.title("Piiriületuste hooajalisus")
st.caption(
    "Tegelikud Eestisse sisenemised · 2021–2025 täisaastate hooajaline muster "
    "ja 2026. aasta võrdlus sama perioodiga 2025. aastal"
)

df = st.session_state["andmed_df"]
KUUD = {
    1: "Jaan", 2: "Veebr", 3: "Märts", 4: "Apr", 5: "Mai", 6: "Juuni",
    7: "Juuli", 8: "Aug", 9: "Sept", 10: "Okt", 11: "Nov", 12: "Dets",
}
ROHELINE = "#178939"
PUNANE = "#FF4B4B"
HALL = "#808495"

from lehe_filtrid import vali_grupp, vali_piiripunkt, grupi_mask

c_gr, c_punkt = st.columns(2)
with c_gr:
    grupp = vali_grupp(df, "hoo")
with c_punkt:
    punkt = vali_piiripunkt(df, "hoo")

mask = grupi_mask(df, grupp) & df["Piiripunkti tüüp"].isin(["Maismaapiir", "Õhupiir"])
if punkt != "Kõik piiripunktid":
    mask &= df["Piiripunkt"].astype(str).eq(punkt)
mask &= df["aasta"].isin([2021, 2022, 2023, 2024, 2025, 2026])
aastad_valitud = [2021, 2022, 2023, 2024, 2025, 2026]

# Eraldame ainult vajalikud veerud, mitte kogu 5+ miljoni reaga andmestiku koopiat.
andmed = df.loc[mask, ["aasta", "kuu", "Piiripunkt"]]
if andmed.empty:
    st.warning("Valitud filtritega puuduvad tegelikud piiriületused.")
    st.stop()

# Lähteandmestiku kuu täielikkus on üldandmestiku, mitte piiratud valimi omadus.
# Kasutame maksimaalset kuupäeva ainult 2026 võrdluse viimase kuu leidmiseks.
max_kpv = pd.to_datetime(df["Piiriületuse kpv"].max())
viimane_taiskuu_2026 = 0
if pd.notna(max_kpv) and max_kpv.year >= 2026:
    if max_kpv.year > 2026:
        viimane_taiskuu_2026 = 12
    else:
        viimane_taiskuu_2026 = max_kpv.month
        if max_kpv.day < max_kpv.days_in_month:
            viimane_taiskuu_2026 -= 1

st.caption("Hooajalisuse arvutamisel kasutatakse täisaasta kõiki 12 kuud; kuufiltrit ei rakendata.")

valitavad_aastad = [a for a in range(2021, 2026) if a in aastad_valitud]
if not valitavad_aastad:
    st.warning("Vali vähemalt üks aasta vahemikus 2021–2025.")
    st.stop()

c_a, c_p = st.columns([1.4, 2.6])
with c_a:
    valitud_hooajad = st.multiselect(
        "Võrreldavad täisaastad",
        options=valitavad_aastad,
        default=valitavad_aastad,
        key="hoo_aastad_uus",
    )
with c_p:
    potentsiaalsed_punktid = sorted(str(p) for p in andmed["Piiripunkt"].dropna().unique())
    punktide_arv = st.selectbox("Soojuskaardil kuvatavaid piiripunkte", [5, 10, 15], index=0, key="hoo_top_uus")

if not valitud_hooajad:
    st.info("Vali vähemalt üks täisaasta.")
    st.stop()

# Arvutame kuu mahud tervikuna, aasta ja piiripunkti kaupa.
kuud_koond = (
    andmed.groupby(["aasta", "kuu"], observed=True)
    .size().reset_index(name="Piiriületused")
)
punktid_koond = (
    andmed.groupby(["aasta", "kuu", "Piiripunkt"], observed=True)
    .size().reset_index(name="Piiriületused")
)

# 2021–2025: alati 12 kuud ühe aasta kohta.
ajaloolised = kuud_koond[kuud_koond["aasta"].isin(valitud_hooajad)]
kalender = pd.MultiIndex.from_product(
    [valitud_hooajad, range(1, 13)], names=["aasta", "kuu"]
)
ajaloolised = (ajaloolised.set_index(["aasta", "kuu"])
                .reindex(kalender, fill_value=0).reset_index())
keskmised = ajaloolised.groupby("aasta")["Piiriületused"].transform("mean")
ajaloolised["Indeks"] = np.where(
    keskmised > 0,
    ajaloolised["Piiriületused"] / keskmised.replace(0, np.nan) * 100,
    np.nan,
)
ajaloolised["Kuu"] = ajaloolised["kuu"].map(KUUD)
ajaloolised["Aasta"] = ajaloolised["aasta"].astype(str)

# Mõõdikud: iga kuu võrdselt kaalutud keskmine indeks valitud aastate lõikes.
kuude_indeks = ajaloolised.groupby("kuu")["Indeks"].mean().dropna()
if kuude_indeks.empty:
    st.warning("Valitud aastatel ei ole hooajalisuse arvutamiseks piiriületusi.")
    st.stop()

aktiivseim = int(kuude_indeks.idxmax())
vaikseim = int(kuude_indeks.idxmin())
indeks_max = float(kuude_indeks.max())
indeks_min = float(kuude_indeks.min())

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Kõige aktiivsem kuu", KUUD[aktiivseim])
with m2:
    st.metric("Kõige vaiksem kuu", KUUD[vaikseim])
with m3:
    st.markdown("Kõrgeim hooajalisuse indeks")
    st.markdown(f"<div style='font-size:28px;font-weight:600;color:{ROHELINE if indeks_max > 100 else HALL}'>{indeks_max:.1f}</div>", unsafe_allow_html=True)
with m4:
    st.markdown("Madalaim hooajalisuse indeks")
    st.markdown(f"<div style='font-size:28px;font-weight:600;color:{PUNANE if indeks_min < 100 else HALL}'>{indeks_min:.1f}</div>", unsafe_allow_html=True)

st.caption("Indeks 100 = vastava aasta keskmine kuu. Mõõdikud põhinevad valitud täisaastate kuuindeksite keskmistel.")

# 1. Täisaastate hooajalise mustri võrdlus.
st.subheader("1. Täisaastate hooajalisuse võrdlus")
fig1 = px.line(
    ajaloolised,
    x="kuu", y="Indeks", color="Aasta", markers=True,
    custom_data=["Piiriületused"],
    labels={"kuu": "Kuu", "Indeks": "Hooajalisuse indeks", "aasta": "Aasta"},
    color_discrete_sequence=px.colors.qualitative.Safe,
)
fig1.update_traces(
    hovertemplate="Kuu: %{x}<br>Indeks: %{y:.1f}<br>Piiriületusi: %{customdata[0]:,.0f}<extra>%{fullData.name}</extra>"
)
fig1.add_hline(y=100, line_dash="dash", line_color=HALL)
fig1.update_layout(
    height=430, template="plotly_white", hovermode="x unified",
    xaxis=dict(tickmode="array", tickvals=list(KUUD), ticktext=list(KUUD.values()),
               tickfont=dict(color="black")),
    yaxis=dict(title="Hooajalisuse indeks", tickfont=dict(color="black")),
    legend_title="Aasta", font=dict(family="Arial", color="black"),
)
st.plotly_chart(fig1, use_container_width=True)

# 2. Piiripunktide hooajaline muster 2021–2025.
st.subheader("2. Piiripunktide hooajalisuse soojuskaart")
puu = punktid_koond[punktid_koond["aasta"].isin(valitud_hooajad)]
top_punktid = (puu.groupby("Piiripunkt", observed=True)["Piiriületused"]
               .sum().nlargest(punktide_arv).index.tolist())

if top_punktid:
    tabel_kalender = pd.MultiIndex.from_product(
        [top_punktid, valitud_hooajad, range(1, 13)],
        names=["Piiripunkt", "aasta", "kuu"],
    )
    p_koond = (puu[puu["Piiripunkt"].isin(top_punktid)]
               .set_index(["Piiripunkt", "aasta", "kuu"])
               .reindex(tabel_kalender, fill_value=0).reset_index())
    p_keskmine = p_koond.groupby(["Piiripunkt", "aasta"], observed=True)["Piiriületused"].transform("mean")
    p_koond["Indeks"] = (
        p_koond["Piiriületused"] / p_keskmine.replace(0, np.nan) * 100
    )
    punktide_kuud = (p_koond.groupby(["Piiripunkt", "kuu"], observed=True)["Indeks"]
                    .mean().reset_index())
    heat = (punktide_kuud.pivot(index="Piiripunkt", columns="kuu", values="Indeks")
            .reindex(index=top_punktid, columns=list(KUUD)))
    fig2 = go.Figure(go.Heatmap(
        z=heat.to_numpy(), x=list(KUUD.values()), y=heat.index.tolist(),
        colorscale=[[0, "#FCE8E8"], [0.5, "#F4F5F6"], [1, "#B3E5C4"]],
        zmid=100, zmin=50, zmax=150,
        colorbar=dict(title="Indeks"),
        hovertemplate="Piiripunkt: %{y}<br>Kuu: %{x}<br>Indeks: %{z:.1f}<extra></extra>",
    ))
    fig2.update_layout(
        height=max(320, 54 * len(top_punktid) + 120),
        template="plotly_white", font=dict(family="Arial", color="black"),
        xaxis_title="Kuu", yaxis_title="", yaxis_autorange="reversed",
        margin=dict(l=20, r=20, t=30, b=30),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Soojuskaart kuvab piiripunkti aastapõhiste indeksite keskmist. Nulliga täidetud kuud võivad tähendada ka punktis tegevuse puudumist; põhjus ei selgu avaandmetest.")
else:
    st.info("Valitud filtritega ei ole soojuskaardi jaoks piiripunkte.")

# 3. 2026 võrreldes 2025 sama kuuga – üksnes tegelikud, lõpetatud kuud.
st.subheader("3. Muutus 2026 vs 2025 samal kuul")
if 2026 not in aastad_valitud or 2025 not in aastad_valitud:
    st.info("2025. ja 2026. aasta võrdlemiseks on vaja mõlema aasta tegelikke andmeid.")
elif viimane_taiskuu_2026 < 1:
    st.info("2026. aasta lõpetatud kuude andmeid pole veel saadaval.")
else:
    k = list(range(1, min(12, viimane_taiskuu_2026) + 1))
    v25 = (kuud_koond.loc[kuud_koond["aasta"] == 2025]
           .set_index("kuu")["Piiriületused"].reindex(k, fill_value=0))
    v26 = (kuud_koond.loc[kuud_koond["aasta"] == 2026]
           .set_index("kuu")["Piiriületused"].reindex(k, fill_value=0))
    yoy = pd.DataFrame({"kuu": k, "2025": v25.to_numpy(), "2026": v26.to_numpy()})
    yoy["Muutus (%)"] = np.where(
        yoy["2025"] > 0,
        (yoy["2026"] - yoy["2025"]) / yoy["2025"].replace(0, np.nan) * 100,
        np.nan,
    )
    yoy["Kuu"] = yoy["kuu"].map(KUUD)
    yoy["Värv"] = np.where(yoy["Muutus (%)"] > 0, ROHELINE,
                            np.where(yoy["Muutus (%)"] < 0, PUNANE, HALL))
    fig3 = go.Figure(go.Bar(
        x=yoy["Kuu"], y=yoy["Muutus (%)"], marker_color=yoy["Värv"],
        customdata=yoy[["2025", "2026"]].to_numpy(),
        hovertemplate=("Kuu: %{x}<br>Muutus: %{y:+.1f}%"
                       "<br>2025: %{customdata[0]:,.0f}"
                       "<br>2026: %{customdata[1]:,.0f}<extra></extra>"),
    ))
    fig3.add_hline(y=0, line_color=HALL, line_width=1)
    fig3.update_layout(
        height=400, template="plotly_white", font=dict(family="Arial", color="black"),
        xaxis_title="Kuu", yaxis_title="Muutus võrreldes 2025. aastaga (%)",
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Võrreldud on üksnes mõlemal aastal olemasolevaid täiskuid. Kui 2025. aasta kuu maht on null, on protsentuaalne muutus määramata.")

with st.expander("Detailne hooajalisuse andmetabel ja metoodika", expanded=False):
    st.dataframe(
        ajaloolised[["aasta", "Kuu", "Piiriületused", "Indeks"]].rename(
            columns={"aasta": "Aasta", "Indeks": "Hooajalisuse indeks"}
        ),
        use_container_width=True,
        hide_index=True,
        column_config={"Hooajalisuse indeks": st.column_config.NumberColumn(format="%.1f")},
    )
    st.download_button(
        "Laadi hooajalisuse tabel CSV-na",
        ajaloolised[["aasta", "kuu", "Piiriületused", "Indeks"]]
        .to_csv(index=False).encode("utf-8-sig"),
        file_name="hooajalisuse_vordlus.csv", mime="text/csv",
    )
    st.markdown(
        "**Arvutus:** hooajalisuse indeks = kuu piiriületuste arv / sama aasta "
        "keskmine kuumaht × 100. Iga aasta keskmine arvutatakse 12 kuu põhjal. "
        "Hooajalisuse indeks ei tõenda muutuste põhjuseid. "
        "PPA andmed kajastavad piiriületusi, mitte unikaalseid isikuid."
    )
