import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Kodakondsuste võrdlus")
st.caption("Tegelikud Eestisse sisenemised · riikide grupid, piiripunktid ja muutused")

df = st.session_state["andmed_df"]

from lehe_filtrid import vali_piirityyp, vali_piiripunkt

with st.expander("Täiendav piiripunkti filter", expanded=False):
    c_t, c_p = st.columns(2)
    with c_t:
        piiri_tyyp = vali_piirityyp("kv")
    with c_p:
        punkt = vali_piiripunkt(df, "kv")

mask = df["Piiripunkti tüüp"].isin(
    ["Maismaapiir", "Õhupiir"] if piiri_tyyp == "Kõik" else [piiri_tyyp]
)
if punkt != "Kõik piiripunktid":
    mask &= df["Piiripunkt"].astype(str).eq(punkt)
mask &= df["aasta"].between(2021, 2026)
base = df.loc[mask, ["aasta", "kuu", "Piiripunkt", "Piiripunkti tüüp", "Kodakondsus", "Riikide grupp"]].copy()

if base.empty:
    st.warning("Valitud piiripunktiga andmeid ei leitud.")
    st.stop()

grupid = sorted(base["Riikide grupp"].dropna().astype(str).unique().tolist())
grupid = [g for g in grupid if g != "Puudub"]
if not grupid:
    st.warning("Riikide gruppe ei leitud.")
    st.stop()

def vaikimisi_grupp(grupid):
    return next((g for g in grupid if g == "3.riik" or "kolmand" in g.lower()), grupid[0])

c1, c2, c3 = st.columns([2.2, 1.2, 1.4])
with c1:
    grupp = st.selectbox("Riikide grupp", grupid, index=grupid.index(vaikimisi_grupp(grupid)), key="kv_grupp")
with c2:
    top_n = st.selectbox("TOP kodakondsusi", [5, 10, 15, 20, 30, 50], index=1, key="kv_top")
with c3:
    jarjestus = st.selectbox("Järjesta", ["Piiriületuste arv", "Absoluutne muutus", "Protsentuaalne muutus"], key="kv_jarjestus")

base = base.loc[base["Riikide grupp"].astype(str) == grupp].copy()
if base.empty:
    st.warning("Selles riikide grupis ei ole valitud filtritega andmeid.")
    st.stop()

saadaolevad_aastad = sorted(int(a) for a in base["aasta"].dropna().unique())
# Ajalooline analüüs eelistab 2021–2025; 2026 lubatakse ainult tegeliku osaperioodina.
a1, a2 = st.columns(2)
with a1:
    alg_aasta = st.selectbox("Võrdluse algusaasta", saadaolevad_aastad, index=0, key="kv_alg")
with a2:
    lopp_aasta = st.selectbox("Võrdluse lõppaasta", saadaolevad_aastad, index=(saadaolevad_aastad.index(2025) if 2025 in saadaolevad_aastad else len(saadaolevad_aastad)-1), key="kv_lopp")
if alg_aasta >= lopp_aasta:
    st.warning("Lõppaasta peab olema algusaastast hilisem.")
    st.stop()

base = base.loc[base["aasta"].between(alg_aasta, lopp_aasta)].copy()
# Võrdleme samu kalendrikuusid mõlemal aastal, et osalise 2026. aasta puhul ei tekiks kunstlikku langust.
alg_kuud = set(base.loc[base["aasta"] == alg_aasta, "kuu"].dropna().astype(int))
lopp_kuud = set(base.loc[base["aasta"] == lopp_aasta, "kuu"].dropna().astype(int))
vordluskuud = sorted(alg_kuud & lopp_kuud)
if not vordluskuud:
    st.warning("Algus- ja lõppaastal puuduvad ühised võrreldavad kuud.")
    st.stop()

# Kõigi kodakondsuste aasta-/piiripunktipõhine koondamine enne graafikute koostamist.
aastad = (base.groupby(["Kodakondsus", "aasta"], observed=True).size()
          .rename("Arv").reset_index())
alg = aastad.loc[aastad["aasta"] == alg_aasta, ["Kodakondsus", "Arv"]].rename(columns={"Arv": "Algus"})
lopp = aastad.loc[aastad["aasta"] == lopp_aasta, ["Kodakondsus", "Arv"]].rename(columns={"Arv": "Lõpp"})
# Ühiste kuude põhjal arvutatud võrreldavad algus- ja lõppaasta arvud.
otsad = base.loc[base["aasta"].isin([alg_aasta, lopp_aasta]) & base["kuu"].isin(vordluskuud)]
otsad_koond = (otsad.groupby(["Kodakondsus", "aasta"], observed=True).size()
                .unstack(fill_value=0).reindex(columns=[alg_aasta, lopp_aasta], fill_value=0))
otsad_koond.columns = ["Algus", "Lõpp"]
koond = otsad_koond.reset_index()
koond["Absoluutne muutus"] = koond["Lõpp"] - koond["Algus"]
koond["Protsentuaalne muutus"] = np.where(koond["Algus"] > 0, (koond["Lõpp"] / koond["Algus"] - 1) * 100, np.nan)
koond["Keskmine aastane kasv (%)"] = np.where(
    (koond["Algus"] > 0) & (koond["Lõpp"] > 0),
    ((koond["Lõpp"] / koond["Algus"]) ** (1 / (lopp_aasta - alg_aasta)) - 1) * 100,
    np.nan,
)
koond["Koguarv"] = koond["Kodakondsus"].map(base.groupby("Kodakondsus", observed=True).size()).fillna(0).astype(int)

jarjestus_veerg = {"Piiriületuste arv": "Koguarv", "Absoluutne muutus": "Absoluutne muutus", "Protsentuaalne muutus": "Protsentuaalne muutus"}[jarjestus]
koond = koond.sort_values(jarjestus_veerg, ascending=False, na_position="last")
valik_kodakondsused = koond.head(top_n)["Kodakondsus"].astype(str).tolist()

koik_kodakondsused = sorted(base["Kodakondsus"].dropna().astype(str).unique().tolist())
kas_kasitsi = st.toggle("Valin kodakondsused ise", value=False, key="kv_kasitsi")
if kas_kasitsi:
    valik_kodakondsused = st.multiselect("Kodakondsused", koik_kodakondsused, default=valik_kodakondsused, key="kv_riigid")
if not valik_kodakondsused:
    st.info("Vali vähemalt üks kodakondsus.")
    st.stop()

valitud = base.loc[base["Kodakondsus"].astype(str).isin(valik_kodakondsused)].copy()
valitud_koond = koond.loc[koond["Kodakondsus"].astype(str).isin(valik_kodakondsused)].copy()

# Mõõdikute kogusumma ja muutus põhinevad valitud kodakondsustel ja võrreldavatel kuudel.
algus_summa = int(valitud_koond["Algus"].sum())
lopp_summa = int(valitud_koond["Lõpp"].sum())
muutus = ((lopp_summa / algus_summa - 1) * 100) if algus_summa else None
cagr = (((lopp_summa / algus_summa) ** (1 / (lopp_aasta - alg_aasta)) - 1) * 100) if algus_summa > 0 and lopp_summa > 0 else None
maismaa = int((valitud["Piiripunkti tüüp"] == "Maismaapiir").sum())
maismaa_pct = 100 * maismaa / len(valitud) if len(valitud) else 0

st.subheader(f"{grupp} | {alg_aasta}–{lopp_aasta}")
if len(vordluskuud) < 12:
    st.info(f"Algus- ja lõppaasta muutust võrreldakse ainult samade kuude põhjal: {', '.join(map(str, vordluskuud))}. Koguarv hõlmab kõiki valitud perioodi olemasolevaid kuid.")

# Kasv on roheline, langus punane; neutraalne väärtus järgib rakenduse teksti värvi.
def varviline_moodik(pealkiri, vaartus, protsent=None):
    import html
    varv = (
        "#178939" if protsent is not None and protsent > 0
        else "#FF4B4B" if protsent is not None and protsent < 0
        else "inherit"
    )
    st.markdown(
        f"""<div style="font-size:14px;min-height:42px;line-height:1.35;">
        {html.escape(str(pealkiri))}</div>
        <div style="font-size:26px;font-weight:500;color:{varv};">
        {html.escape(str(vaartus))}</div>""",
        unsafe_allow_html=True,
    )

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    varviline_moodik("Piiriületusi kokku", f"{len(valitud):,}".replace(",", " "))
with m2:
    varviline_moodik(f"Muutus {alg_aasta} → {lopp_aasta}",
                     f"{muutus:+.1f}%" if muutus is not None else "—", muutus)
with m3:
    varviline_moodik("Keskmine aastane kasv (CAGR)",
                     f"{cagr:+.1f}%" if cagr is not None else "—", cagr)
with m4:
    varviline_moodik("Maismaapiiri osakaal", f"{maismaa_pct:.1f}%")
with m5:
    varviline_moodik("Võrreldavaid kodakondsusi", len(valik_kodakondsused))

# Võrdlusgraafik: horisontaalsed tulbad on pikkade riiginimede puhul loetavamad.
st.markdown("#### Kodakondsuste võrdlus")
naidik = st.radio("Graafiku näitaja", ["Koguarv", "Absoluutne muutus", "Protsentuaalne muutus"], horizontal=True, key="kv_naidik")
plot_df = valitud_koond.sort_values(naidik, ascending=True, na_position="first").copy()
if naidik in ("Absoluutne muutus", "Protsentuaalne muutus"):
    plot_df["Muutuse suund"] = np.where(plot_df[naidik] > 0, "Kasv",
                                         np.where(plot_df[naidik] < 0, "Langus", "Muutuseta"))
    fig = px.bar(plot_df, x=naidik, y="Kodakondsus", orientation="h", text=naidik,
                 color="Muutuse suund",
                 color_discrete_map={"Kasv": "#178939", "Langus": "#FF4B4B", "Muutuseta": "#808495"},
                 hover_data={"Algus": True, "Lõpp": True, "Koguarv": True,
                             "Absoluutne muutus": True, "Protsentuaalne muutus": ":.1f"})
else:
    fig = px.bar(plot_df, x=naidik, y="Kodakondsus", orientation="h", text=naidik,
                 hover_data={"Algus": True, "Lõpp": True, "Koguarv": True,
                             "Absoluutne muutus": True, "Protsentuaalne muutus": ":.1f"})
fig.update_traces(texttemplate="%{x:,.1f}" if naidik == "Protsentuaalne muutus" else "%{x:,.0f}", textposition="outside", cliponaxis=False)
fig.update_layout(height=max(430, len(plot_df) * 34 + 140), xaxis_title=naidik + (" (%)" if naidik == "Protsentuaalne muutus" else ""),
                  yaxis_title="", margin=dict(l=15, r=85, t=20, b=30),
                  font=dict(family="Arial", color="black", size=13), showlegend=False)
fig.update_xaxes(tickfont=dict(color="black"), title_font=dict(color="black"))
fig.update_yaxes(tickfont=dict(color="black"))
st.plotly_chart(fig, width="stretch")

st.markdown("#### Muutused aastate lõikes")
aasta_koond = (valitud.groupby(["aasta", "Kodakondsus"], observed=True).size()
               .reset_index(name="Piiriületused"))
fig_a = px.line(aasta_koond, x="aasta", y="Piiriületused", color="Kodakondsus", markers=True)
fig_a.update_layout(height=460, font=dict(family="Arial", color="black"),
                    xaxis=dict(dtick=1, tickfont=dict(color="black")),
                    yaxis=dict(tickfont=dict(color="black")), legend_title="Kodakondsus")
st.plotly_chart(fig_a, width="stretch")

st.markdown("#### Maismaa- ja õhupiiri võrdlus")
tyyp_koond = (valitud.groupby(["Kodakondsus", "Piiripunkti tüüp"], observed=True).size()
              .reset_index(name="Piiriületused"))
fig_t = px.bar(tyyp_koond, x="Kodakondsus", y="Piiriületused", color="Piiripunkti tüüp", barmode="stack")
fig_t.update_layout(height=450, font=dict(family="Arial", color="black"), xaxis_tickangle=-35)
st.plotly_chart(fig_t, width="stretch")

st.markdown("#### Piiripunktide võrdlus")
punkt_koond = (valitud.groupby(["Piiripunkt", "Kodakondsus"], observed=True).size()
               .reset_index(name="Piiriületused"))
# Piirame piiripunktid kümne suurima kogumahuga punktiga.
top_punktid = punkt_koond.groupby("Piiripunkt", observed=True)["Piiriületused"].sum().nlargest(10).index
punkt_koond = punkt_koond.loc[punkt_koond["Piiripunkt"].isin(top_punktid)]
fig_p = px.bar(punkt_koond, x="Piiripunkt", y="Piiriületused", color="Kodakondsus", barmode="group")
fig_p.update_layout(height=490, font=dict(family="Arial", color="black"), xaxis_tickangle=-30)
st.plotly_chart(fig_p, width="stretch")

st.markdown("#### Täpne võrdlustabel")
tabel = valitud_koond[["Kodakondsus", "Koguarv", "Algus", "Lõpp", "Absoluutne muutus", "Protsentuaalne muutus", "Keskmine aastane kasv (%)"]].copy()
st.dataframe(tabel, width="stretch", hide_index=True,
             column_config={"Protsentuaalne muutus": st.column_config.NumberColumn(format="%.1f%%"),
                            "Keskmine aastane kasv (%)": st.column_config.NumberColumn(format="%.1f%%")})
st.download_button("Laadi võrdlustabel CSV-na", tabel.to_csv(index=False).encode("utf-8-sig"),
                   file_name="kodakondsuste_vordlus.csv", mime="text/csv")
st.caption("Piiriületuste arv ei võrdu unikaalsete isikute arvuga. Kodakondsus ei tõenda elukohta, mitmikkodakondsust ega julgeolekuriski. Protsentuaalne muutus on määramata, kui algusaastal piiriületusi ei olnud.")
