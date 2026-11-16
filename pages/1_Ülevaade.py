
import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Eesti piiriületuste ülevaade")
st.caption("Tegelikud Eestisse sisenemised. Põhianalüüs 2021–2025; 2026 on osaline aasta.")

df = st.session_state["andmed_df"]

from lehe_filtrid import vali_grupp, vali_piiripunkt, vali_aastad, grupi_mask


# Riikide grupi ja piiripunkti filtrid
c1, c2 = st.columns([1.5, 2])

with c1:
    grupp = vali_grupp(df, "ulev", koik=True)

with c2:
    punkt_valik = vali_piiripunkt(df, "ulev")

# 2026 märkeruut aastate filtri kohal
aasta_2026 = st.checkbox(
    "Lisa 2026 tegelikud andmed",
    value=False,
    key="ulev_2026"
)

# Aastate filter
aastad_valitud = vali_aastad(
    df,
    "ulev",
    kaasa_2026=aasta_2026
)

# Lisa või eemalda 2026 automaatselt märkeruudu järgi
lubatud_aastad = [a for a in aastad_valitud if a != 2026]

if aasta_2026:
    lubatud_aastad.append(2026)

if not lubatud_aastad:
    st.info("Vali vähemalt üks aasta.")
    st.stop()

piiri_tyyp = "Kõik"
piiripunktid = ([punkt_valik] if punkt_valik != "Kõik piiripunktid"
                 else df["Piiripunkt"].dropna().astype(str).unique().tolist())
kuud_valitud = list(range(1, 13))
kodakondsused = df["Kodakondsus"].dropna().astype(str).unique().tolist()
vanused = df["Vanuserühm"].dropna().astype(str).unique().tolist()
riikide_grupid = ([grupp] if grupp != "Kõik riikide grupid" else
                  [g for g in df["Riikide grupp"].dropna().astype(str).unique() if g != "Puudub"])

piiriliigid = ["Maismaapiir", "Õhupiir"] if piiri_tyyp == "Kõik" else [piiri_tyyp]

mask = df["Piiripunkti tüüp"].isin(piiriliigid)
mask &= df["Piiripunkt"].isin(piiripunktid)
mask &= df["aasta"].isin(lubatud_aastad)
mask &= df["kuu"].isin(kuud_valitud)
mask &= df["Kodakondsus"].isin(kodakondsused)
mask &= df["Vanuserühm"].isin(vanused)
mask &= df["Riikide grupp"].isin(riikide_grupid)

andmed = df.loc[mask, [
    "aasta", "kuu", "Piiripunkt", "Piiripunkti tüüp", "Kodakondsus",
    "Riikide grupp", "Sugu", "Vanuserühm"
]]

if andmed.empty:
    st.warning("Valitud filtritele vastavaid tegelikke piiriületusi ei leitud.")
    st.stop()

# Lisatud aasta- ja kuupõhine koond võimaldab kiireid Plotly jooniseid.
kuukoond = (andmed.groupby(["aasta", "kuu"], observed=True)
            .size().reset_index(name="Piiriületusi"))
kuukoond["Kuupäev"] = pd.to_datetime(dict(
    year=kuukoond["aasta"], month=kuukoond["kuu"], day=1
))

punktikuud = (andmed.groupby(["aasta", "kuu", "Piiripunkt"], observed=True)
             .size().reset_index(name="Piiriületusi"))
punktikuud["Kuupäev"] = pd.to_datetime(dict(
    year=punktikuud["aasta"], month=punktikuud["kuu"], day=1
))

# Muutusi võrreldakse ainult aastatevahelise ÜHISE kuuvaliku põhjal.
# Nii ei tekita 2026 osaline aasta kunstlikult negatiivset aastamuutust.
aastate_nimekiri = sorted(int(a) for a in andmed["aasta"].unique())
muutus = None
cagr = None
vordlus_alg = None
vordlus_lopp = None
vordluskuud = []
if len(aastate_nimekiri) >= 2:
    vordlus_alg, vordlus_lopp = aastate_nimekiri[0], aastate_nimekiri[-1]
    alg_kuud = set(andmed.loc[andmed["aasta"] == vordlus_alg, "kuu"].astype(int))
    lopp_kuud = set(andmed.loc[andmed["aasta"] == vordlus_lopp, "kuu"].astype(int))
    vordluskuud = sorted(alg_kuud & lopp_kuud)
    alg_maht = int(((andmed["aasta"] == vordlus_alg) & andmed["kuu"].isin(vordluskuud)).sum())
    lopp_maht = int(((andmed["aasta"] == vordlus_lopp) & andmed["kuu"].isin(vordluskuud)).sum())
    if vordluskuud and alg_maht > 0:
        muutus = (lopp_maht / alg_maht - 1) * 100
        if lopp_maht > 0 and vordlus_lopp > vordlus_alg:
            cagr = ((lopp_maht / alg_maht) ** (1 / (vordlus_lopp - vordlus_alg)) - 1) * 100

maht = len(andmed)
maisi = int((andmed["Piiripunkti tüüp"] == "Maismaapiir").sum())
maa_osakaal = maisi / maht * 100
aktiivseid_punkte = int(andmed["Piiripunkt"].nunique())

def protsent(v):
    return f"{v:+.1f}%" if v is not None and np.isfinite(v) else "—"

def muutuse_color(v):
    if v is None or not np.isfinite(v):
        return "inherit"
    return "#178939" if v > 0 else ("#FF4B4B" if v < 0 else "inherit")

def varviline_moodik(label, value, color="inherit"):
    # Streamlit st.metric ei võimalda põhiväärtusele tingimusvärvi anda.
    st.markdown(
        f'<div style="font-size:14px">{label}</div>'
        f'<div style="font-size:26px;font-weight:600;color:{color}">{value}</div>',
        unsafe_allow_html=True
    )

st.subheader("Põhinäitajad")
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Piiriületusi kokku", f"{maht:,}".replace(",", " "))
with m2:
    varviline_moodik("Muutus võrreldavatel aastatel", protsent(muutus), muutuse_color(muutus))
with m3:
    varviline_moodik("Keskmine aastane kasv (CAGR)", protsent(cagr), muutuse_color(cagr))
with m4:
    st.metric("Aktiivseid piiripunkte", aktiivseid_punkte)
with m5:
    st.metric("Maismaapiiri osakaal", f"{maa_osakaal:.1f}%")

if vordlus_alg is not None:
    st.caption(
        f"Muutuse võrdlus: {vordlus_alg} → {vordlus_lopp}; "
        f"ühised kalendrikuud: {', '.join(map(str, vordluskuud)) or 'puuduvad'}. "
        "Koguarv kajastab kõiki valitud perioodi tegelikke piiriületusi."
    )
else:
    st.caption("Muutuse ja CAGR-i arvutamiseks peab olema valitud vähemalt kaks aastat.")

st.divider()
st.subheader("Piiriületuste ajaline dünaamika")
fig = px.line(kuukoond, x="Kuupäev", y="Piiriületusi", markers=True,
              title="Tegelikud piiriületused kuude lõikes")
fig.update_traces(line_color="#178939", marker_size=5)
fig.update_layout(height=435, xaxis_title="Aeg", yaxis_title="Piiriületusi",
                  hovermode="x unified", font=dict(family="Arial"))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Piiripunktide dünaamika")
punktide_suurused = (punktikuud.groupby("Piiripunkt", observed=True)["Piiriületusi"]
                    .sum().sort_values(ascending=False))
top_valikud = punktide_suurused.head(5).index.astype(str).tolist()
valitud_jooned = st.multiselect(
    "Kuvatavad piiripunktid (vaikimisi TOP 5)",
    options=punktide_suurused.index.astype(str).tolist(), default=top_valikud,
    key="ulevaate_jooned"
)
if valitud_jooned:
    punktijooned = punktikuud.loc[punktikuud["Piiripunkt"].astype(str).isin(valitud_jooned)]
    fig_p = px.line(punktijooned, x="Kuupäev", y="Piiriületusi", color="Piiripunkt",
                    title="Piiripunktide tegelikud sisenemised kuude lõikes")
    fig_p.update_layout(height=480, xaxis_title="Aeg", yaxis_title="Piiriületusi",
                        font=dict(family="Arial"), hovermode="x unified"
    )
    
    import re

# Eemaldame kõigi legendi nimetuste lõpust sõna "piiripunkt"
    for trace in fig_p.data:
        trace.name = re.sub(
            r"\s+piiripunkt\s*$",
        "",
        trace.name,
        flags=re.IGNORECASE
    ).strip()

    trace.legendgroup = trace.name
    fig_p.update_layout(legend_title_text="")
    st.plotly_chart(fig_p, use_container_width=True)
else:
    st.info("Vali vähemalt üks piiripunkt.")

st.divider()
st.subheader("Andmete allalaadimine")
st.caption("Eksporditakse ainult selle lehe filtritele vastavaid tegelikke sisenemisi. "
           "A7/A9 prognooside kokkuvõte asub lühianalüüsi juures.")

# Filtrite muutmisel tühjendame eelmise valiku ekspordid,
# et allalaadimise nupp ei pakuks kogemata vanu andmeid.
filtri_tunnus = repr((
    piiri_tyyp, tuple(piiripunktid), tuple(lubatud_aastad),
    tuple(kuud_valitud), tuple(kodakondsused),
    tuple(vanused), tuple(riikide_grupid)
))
if st.session_state.get("ulevaade_ekspordi_filtri_tunnus") != filtri_tunnus:
    st.session_state.pop("ulevaade_parquet_baidid", None)
    st.session_state.pop("ulevaade_excel_baidid", None)
    st.session_state["ulevaade_ekspordi_filtri_tunnus"] = filtri_tunnus

# Parquet-fail genereeritakse vaid nupu vajutamisel, mitte lehe igal uuendamisel.
if st.button("Valmista filtreeritud Parquet-fail", key="ulevaade_parquet_loo"):
    # Kasutame originaalandmestiku kõiki veerge vastavalt valitud maskile.
    st.session_state["ulevaade_parquet_baidid"] = df.loc[mask].to_parquet(
        index=False, engine="pyarrow", compression="snappy"
    )
if "ulevaade_parquet_baidid" in st.session_state:
    st.download_button(
        "Laadi filtreeritud algandmed alla (Parquet)",
        data=st.session_state["ulevaade_parquet_baidid"],
        file_name="eesti_piiriuletuste_algandmed.parquet",
        mime="application/vnd.apache.parquet"
    )

# Exceli puhul ekspordime koondtabelid, mitte miljoneid algkirjeid.
if st.button("Valmista Exceli koondtabelid", key="ulevaade_excel_loo"):
    excel = io.BytesIO()
    kokku_punktid = (andmed.groupby("Piiripunkt", observed=True)
                     .size().reset_index(name="Piiriületusi")
                     .sort_values("Piiriületusi", ascending=False))
    grupid = (andmed.groupby("Riikide grupp", observed=True)
              .size().reset_index(name="Piiriületusi"))
    kodakondsuste_koond = (andmed.groupby("Kodakondsus", observed=True)
                          .size().reset_index(name="Piiriületusi")
                          .sort_values("Piiriületusi", ascending=False))
    with pd.ExcelWriter(excel, engine="openpyxl") as writer:
        kuukoond.to_excel(writer, sheet_name="Kuude koond", index=False)
        punktikuud.to_excel(writer, sheet_name="Piiripunktid kuude kaupa", index=False)
        kokku_punktid.to_excel(writer, sheet_name="Piiripunktide koond", index=False)
        grupid.to_excel(writer, sheet_name="Riikide grupid", index=False)
        kodakondsuste_koond.to_excel(writer, sheet_name="Kodakondsused", index=False)
    st.session_state["ulevaade_excel_baidid"] = excel.getvalue()
if "ulevaade_excel_baidid" in st.session_state:
    st.download_button(
        "Laadi analüüsi koondtulemused alla (Excel)",
        data=st.session_state["ulevaade_excel_baidid"],
        file_name="eesti_piiriuletuste_analuus.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with st.expander("Tehnilised andmekontrollid", expanded=False):
    st.write("Filtreeritud kirjete arv:", len(andmed))
    st.write("Valitud aastad:", sorted(andmed["aasta"].unique().tolist()))
    st.write("Filtreeritud andmete kuude arv:", kuukoond.shape[0])
    st.write("Aktiivsete piiripunktide arv:", aktiivseid_punkte)
    st.write("Kasutatud aastatevahelised võrdluskuud:", vordluskuud)

st.caption("Piiriületuste arv ei võrdu unikaalsete isikute arvuga. "
           "Kirjeldavad muutused ei tõenda geopoliitiliste sündmuste põhjuslikku mõju.")

