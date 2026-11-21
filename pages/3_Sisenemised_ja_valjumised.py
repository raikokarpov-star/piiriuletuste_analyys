
# ==========================================
# SISENEMISED JA VÄLJUMISED – ÜLEVAADE
# Ajaloolised andmed 2016–2026
# ==========================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.title("Sisenemised ja väljumised")
st.caption("Eesti piiriületuste võrdlus | 2016–2026")

# ------------------------------------------
# ANDMETE ASUKOHT
# ------------------------------------------

ANDMEKAUST = (
    Path(__file__).resolve().parent.parent
    / "streamlit_andmed"
)

# --------STICKY MÕÕDIKURIBA CSS----------

st.markdown("""
<style>

/* Fikseeritud mõõdikuriba */
.st-key-sv_sticky_metrics {
    position: fixed !important;
    top: 7rem !important;

    left: calc(21rem + 1vw) !important;
    right: 3rem !important;
    width: auto !important;
    max-width: none !important;

    z-index: 9999 !important;
    box-sizing: border-box !important;

    background: #ffffff;
    padding: 0.6rem 0.8rem !important;
    border: 1px solid rgba(128,128,128,0.18);
    border-radius: 0.7rem;
    box-shadow: 0 3px 12px rgba(0,0,0,0.10);
}

/* Väiksemad numbrid */
.st-key-sv_sticky_metrics [data-testid="stMetricValue"] {
    font-size: 1.35rem !important;
}

/* Väiksemad nimetused */
.st-key-sv_sticky_metrics [data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
}

/* Kitsamal ekraanil */
@media (max-width: 900px) {
    .st-key-sv_sticky_metrics {
        left: 1rem !important;
        right: 1rem !important;
    }
}

/* Jätame pealkirjale ja filtritele ruumi */
[data-testid="stMainBlockContainer"] {
    padding-top: 11rem !important;
}

/* Viie mõõdiku paigutus */
.sv-metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1.15fr 0.9fr 0.9fr;
    gap: 8px;
    align-items: center;
    width: 100%;
}

.sv-metric {
    min-width: 0;
    padding: 4px;
}

.sv-label {
    font-size: 0.78rem;
    opacity: 0.75;
    margin-bottom: 5px;
}

.sv-value {
    font-size: 1.15rem;
    font-weight: 650;
    white-space: nowrap;
}

.sv-small {
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.4;
    white-space: normal;
}

@media (max-width: 1200px) {
    .sv-metrics-grid {
        gap: 4px;
    }

    .sv-value {
        font-size: 0.95rem;
    }

    .sv-small {
        font-size: 0.85rem;
    }
}

/* Kui täiendav paneel avaneb,
   ei kasva see ekraanist välja */

.st-key-sv_sticky_metrics {
    max-height: 75vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* Avatava paneeli kompaktsem kujundus */
.st-key-sv_sticky_metrics [data-testid="stExpander"] {
    margin-top: 0.35rem;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------
# ANDMETE LAADIMINE
# ------------------------------------------

@st.cache_data(show_spinner="Laen andmeid...")
def lae_liikumiste_andmed():

    sis = pd.read_parquet(
        ANDMEKAUST / "sisenemised_2016_2026.parquet"
    )

    val = pd.read_parquet(
        ANDMEKAUST / "valjumised_2016_2026.parquet"
    )

    sis = sis.rename(columns={
        "Piiriületajate arv": "Piiriületuste arv"
    })

    val = val.rename(columns={
        "Piirilt lahkujate arv": "Piiriületuste arv"
    })

    sis["Suund"] = "Sisenemised"
    val["Suund"] = "Väljumised"

    df = pd.concat([sis, val], ignore_index=True)

    df["Kuupäev"] = pd.to_datetime(df["Kuupäev"])

    return df


andmed = lae_liikumiste_andmed()


# ------------------------------------------
# FILTRID
# ------------------------------------------

# Ühine fikseeritud konteiner: esmalt reserveerime koha mõõdikutele,
# seejärel kuvame filtrid. Mõõdikud täidetakse pärast arvutusi.
sticky_riba = st.container(key="sv_sticky_metrics")
with sticky_riba:
    moodikute_koht = st.empty()
    with st.expander("🔎 Analüüsi filtrid", expanded=False):

        st.caption(
            "Tühjaks jäetud valik tähendab kõiki väärtusi. "
            "Filtrid kehtivad mõlemale liikumissuunale."
        )

        f1, f2, f3, f4 = st.columns(4)

        aastate_valikud = sorted(
            andmed["aasta"].dropna().unique().tolist()
        )

        kuude_nimed = {
            1: "Jaanuar",
            2: "Veebruar",
            3: "Märts",
            4: "Aprill",
            5: "Mai",
            6: "Juuni",
            7: "Juuli",
            8: "August",
            9: "September",
            10: "Oktoober",
            11: "November",
            12: "Detsember",
        }

        # AASTA
        with f1:
            aastad = st.multiselect(
                "Aasta",
                options=aastate_valikud,
                default=aastate_valikud,
                key="sv_aastad"
            )

        # KUU
        with f2:
            kuud = st.multiselect(
                "Kuu",
                options=list(kuude_nimed),
                default=list(kuude_nimed),
                format_func=lambda k: kuude_nimed[k],
                key="sv_kuud"
            )

        # PIIRIPUNKTI TÜÜP
        with f3:
            piirityybid = st.multiselect(
                "Piiripunkti tüüp",
                options=sorted(
                    andmed["Piiripunkti tüüp"]
                    .dropna().unique().tolist()
                ),
                default=["Maismaapiir", "Õhupiir"],
                key="sv_piirityybid"
            )

        # PIIRIPUNKT
        punktide_alus = andmed[
            andmed["Piiripunkti tüüp"].isin(piirityybid)
        ]

        with f4:
            piiripunktid = st.multiselect(
                "Piiripunkt",
                options=sorted(
                    punktide_alus["Piiripunkt"]
                    .dropna().unique().tolist()
                ),
                default=[],
                placeholder="Kõik piiripunktid",
                key="sv_piiripunktid"
            )

        # TEINE FILTRITE RIDA
        f5, f6, f7, f8 = st.columns(4)

        # KODAKONDSUS
        with f5:
            kodakondsused = st.multiselect(
                "Kodakondsus",
                options=sorted(
                    andmed["Kodakondsus"]
                    .dropna().unique().tolist()
                ),
                default=[],
                placeholder="Kõik kodakondsused",
                key="sv_kodakondsused"
            )

        # RIIKIDE GRUPP
        with f6:
            riikide_grupid = st.multiselect(
                "Riikide grupp",
                options=sorted(
                    andmed["Riikide grupp"]
                    .dropna().unique().tolist()
                ),
                default=[],
                placeholder="Kõik grupid",
                key="sv_riikide_grupid"
            )

        # SUGU
        with f7:
            sood = st.multiselect(
                "Sugu",
                options=sorted(
                    andmed["Sugu"].dropna().unique().tolist()
                ),
                default=[],
                placeholder="Kõik",
                key="sv_sugu"
            )

        # VANUSERÜHM
        with f8:
            vanused = st.multiselect(
                "Vanuserühm",
                options=sorted(
                    andmed["Vanuserühm"]
                    .dropna().unique().tolist()
                ),
                default=[],
                placeholder="Kõik",
                key="sv_vanused"
            )

# ------------------------------------------
# FILTREERIMINE
# ------------------------------------------


mask = (
    andmed["aasta"].isin(aastad)
    & andmed["kuu"].isin(kuud)
    & andmed["Piiripunkti tüüp"].isin(piirityybid)
)

valikulised_filtrid = {
    "Piiripunkt": piiripunktid,
    "Kodakondsus": kodakondsused,
    "Riikide grupp": riikide_grupid,
    "Sugu": sood,
    "Vanuserühm": vanused,
}

for veerg, valitud in valikulised_filtrid.items():
    if valitud:
        mask &= andmed[veerg].isin(valitud)

filtreeritud = andmed.loc[mask]

if filtreeritud.empty:
    st.warning("Valitud filtritele vastavaid andmeid ei ole.")
    st.stop()


# ------------------------------------------
# PÕHIMÕÕDIKUD
# ------------------------------------------


# ------------------------------------------
# PÕHIMÕÕDIKUD – SISENEMISED JA VÄLJUMISED
# ------------------------------------------

st.divider()

# Ajalooliselt saadaolevad kuud.
# Kasutame kogu andmestiku kalendrit, et harva
# esinev kodakondsus või piiripunkt ei muudaks
# ekslikult andmete kättesaadavuse perioodi.

saadaolevad_kuud = (
    andmed[["aasta", "kuu"]]
    .drop_duplicates()
    .groupby("aasta")["kuu"]
    .apply(set)
    .to_dict()
)

valitud_aastad = sorted(set(aastad))
valitud_kuud = set(kuud)


def aasta_summa(df, aasta, kuude_valik):
    return int(
        df.loc[
            (df["aasta"] == aasta)
            & df["kuu"].isin(kuude_valik),
            "Piiriületuste arv"
        ].sum()
    )


def protsendimuutus(uus, vana):
    if vana <= 0:
        return None
    return (uus / vana - 1) * 100


def vorminda_arv(arv, margiga=False):
    formaat = "+," if margiga else ","
    return format(arv, formaat).replace(",", " ")


def vorminda_pct(arv):
    if arv is None or not pd.notna(arv):
        return "–"
    return f"{arv:+.2f}%".replace(".", ",")


def varv(arv):
    if arv is None or not pd.notna(arv):
        return "#808080"
    if arv > 0:
        return "#178939"
    if arv < 0:
        return "#D9534F"
    return "#808080"


def varviline_moodik(label, vaartus, abi=None, protsent=True):
    tekst = (
        vorminda_pct(vaartus)
        if protsent
        else (vorminda_arv(vaartus, True)
              if vaartus is not None else "–")
    )

    st.markdown(
        f"""
        <div style="margin-bottom:12px;">
            <div style="
                font-size:0.88rem;
                opacity:0.75;
                margin-bottom:6px;
            ">{label}</div>
            <div style="
                font-size:1.7rem;
                font-weight:650;
                color:{varv(vaartus)};
            ">{tekst}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if abi:
        st.caption(abi)


def arvuta_moodikud(df):
    kokku = int(df["Piiriületuste arv"].sum())

    muutus = None
    cagr = None
    yoy = None
    muutus_12k = None

    # 1. Võrreldavate aastate muutus ja CAGR
    # Võrdleme esimest ja viimast valitud aastat
    # ainult mõlemas saadaval olevatel kuudel.

    if len(valitud_aastad) >= 2:
        esimene = valitud_aastad[0]
        viimane = valitud_aastad[-1]

        uhised_kuud = (
            valitud_kuud
            & saadaolevad_kuud.get(esimene, set())
            & saadaolevad_kuud.get(viimane, set())
        )

        if uhised_kuud:
            algus = aasta_summa(df, esimene, uhised_kuud)
            lopp = aasta_summa(df, viimane, uhised_kuud)

            muutus = protsendimuutus(lopp, algus)

            aastate_vahe = viimane - esimene

            if algus > 0 and lopp > 0 and aastate_vahe > 0:
                cagr = (
                    (lopp / algus) ** (1 / aastate_vahe) - 1
                ) * 100

    # 2. YoY – viimane valitud aasta võrreldes
    # vahetult eelneva kalendriaastaga.

    if valitud_aastad:
        viimane = valitud_aastad[-1]
        eelmine = viimane - 1

        if eelmine in valitud_aastad:
            uhised_kuud = (
                valitud_kuud
                & saadaolevad_kuud.get(viimane, set())
                & saadaolevad_kuud.get(eelmine, set())
            )

            if uhised_kuud:
                uus = aasta_summa(df, viimane, uhised_kuud)
                vana = aasta_summa(df, eelmine, uhised_kuud)
                yoy = protsendimuutus(uus, vana)

    # 3. Viimased 12 kuud võrreldes eelneva 12 kuuga.
    # Arvutame ainult siis, kui valitud perioodis
    # on olemas kõik 24 järjestikust kalendrikuud.

    kalendri_valik = andmed.loc[
        andmed["aasta"].isin(valitud_aastad)
        & andmed["kuu"].isin(valitud_kuud),
        "Kuupäev"
    ].drop_duplicates()

    if not kalendri_valik.empty:
        loppkuup = pd.Timestamp(kalendri_valik.max())

        periood_24 = pd.date_range(
            end=loppkuup,
            periods=24,
            freq="MS"
        )

        olemas = set(
            pd.to_datetime(kalendri_valik).tolist()
        )

        if all(k in olemas for k in periood_24):
            eelnevad = periood_24[:12]
            viimased = periood_24[12:]

            vana_12 = df.loc[
                df["Kuupäev"].isin(eelnevad),
                "Piiriületuste arv"
            ].sum()

            uus_12 = df.loc[
                df["Kuupäev"].isin(viimased),
                "Piiriületuste arv"
            ].sum()

            muutus_12k = protsendimuutus(uus_12, vana_12)

    # 4. TOP 3 piiripunkti kontsentratsioon
    # Osmanäitajana kasutame iga suuna kogumahtu.

    punktid = (
        df.groupby("Piiripunkt")["Piiriületuste arv"]
        .sum()
        .sort_values(ascending=False)
    )

    top3_osakaal = (
        punktid.head(3).sum() / kokku * 100
        if kokku > 0
        else None
    )

    return {
        "kokku": kokku,
        "muutus": muutus,
        "cagr": cagr,
        "yoy": yoy,
        "muutus_12k": muutus_12k,
        "top3": top3_osakaal,
    }


sis_df = filtreeritud[
    filtreeritud["Suund"] == "Sisenemised"
]

val_df = filtreeritud[
    filtreeritud["Suund"] == "Väljumised"
]

sis_m = arvuta_moodikud(sis_df)
val_m = arvuta_moodikud(val_df)


# ------------------------------------------
# KOMPAKTSED PÕHINÄITAJAD
# ------------------------------------------

sis_kokku = sis_m["kokku"]
val_kokku = val_m["kokku"]
erinevus = sis_kokku - val_kokku

erinevus_pct = (
    erinevus / val_kokku * 100
    if val_kokku > 0 else None
)

suhe = (
    sis_kokku / val_kokku
    if val_kokku > 0 else None
)


# ------------------------------------------
# STICKY PÕHIMÕÕDIKUD
# ------------------------------------------

st.subheader("Põhinäitajad")

# Kompaktsed väärtused mõõdikuriba jaoks
def lyhi_arv(arv):
    if abs(arv) >= 1_000_000:
        return f"{arv / 1_000_000:.2f}".replace(".", ",") + " mln"
    return vorminda_arv(arv)

with moodikute_koht.container():

    st.html(
        f"""
        <div class="sv-metrics-grid">

            <div class="sv-metric">
                <div class="sv-label">Sisenemised</div>
                <div class="sv-value">
                    {lyhi_arv(sis_kokku)}
                </div>
            </div>

            <div class="sv-metric">
                <div class="sv-label">Väljumised</div>
                <div class="sv-value">
                    {lyhi_arv(val_kokku)}
                </div>
            </div>

            <div class="sv-metric">
                <div class="sv-label">Erinevus</div>
                <div class="sv-value">
                    {vorminda_arv(erinevus, True)}
                </div>
                <div class="sv-small"
                        style="color:{varv(erinevus_pct)};">
                    {vorminda_pct(erinevus_pct)}
                </div>
            </div>

            <div class="sv-metric">
                <div class="sv-label">CAGR</div>
                <div class="sv-small"
                        style="color:{varv(sis_m['cagr'])};">
                    S: {vorminda_pct(sis_m['cagr'])}
                </div>
                <div class="sv-small"
                        style="color:{varv(val_m['cagr'])};">
                    V: {vorminda_pct(val_m['cagr'])}
                </div>
            </div>

            <div class="sv-metric">
                <div class="sv-label">YoY</div>
                <div class="sv-small"
                        style="color:{varv(sis_m['yoy'])};">
                    S: {vorminda_pct(sis_m['yoy'])}
                </div>
                <div class="sv-small"
                        style="color:{varv(val_m['yoy'])};">
                    V: {vorminda_pct(val_m['yoy'])}
                </div>
            </div>

        </div>
        """
    )
        
        

with sticky_riba:
    with st.expander(
        "📊 Täiendavad kasvunäitajad ja võrdlus",
        expanded=False
    ):

        vordlus = pd.DataFrame({
            "Mõõdik": [
                "Muutus võrreldavatel aastatel",
                "Keskmine aastane kasv (CAGR)",
                "Viimase aasta muutus (YoY)",
                "Viimase 12 kuu muutus",
                "TOP 3 piiripunkti osakaal"
            ],
            "Sisenemised": [
                sis_m["muutus"],
                sis_m["cagr"],
                sis_m["yoy"],
                sis_m["muutus_12k"],
                sis_m["top3"]
            ],
            "Väljumised": [
                val_m["muutus"],
                val_m["cagr"],
                val_m["yoy"],
                val_m["muutus_12k"],
                val_m["top3"]
            ]
        })

        def kujunda_pct(vaartus):
            if pd.isna(vaartus):
                return "color: gray"

            if vaartus > 0:
                return "color: #178939; font-weight: 600"

            if vaartus < 0:
                return "color: #D9534F; font-weight: 600"

            return "color: gray"

        def kujunda_veerg(veerg):
            return [
                "" if i == 4 else kujunda_pct(vaartus)
                for i, vaartus in enumerate(veerg)
            ]

        tabel = (
            vordlus
            .set_index("Mõõdik")
            .style
            .format(
                lambda x: (
                    f"{x:+.2f}%".replace(".", ",")
                    if pd.notna(x) else "–"
                )
            )
            .apply(
                kujunda_veerg,
                subset=["Sisenemised", "Väljumised"]
            )
        )

        st.dataframe(
            tabel,
            width="stretch"
        )

        suhe = (
            sis_kokku / val_kokku
            if val_kokku > 0
            else None
        )

        st.metric(
            "Sisenemiste/väljumiste suhe",
            f"{suhe:.3f}".replace(".", ",")
            if suhe is not None
            else "–"
        )

# ------------------------------------------
# KUUDE DÜNAAMIKA
# ------------------------------------------

st.divider()
st.subheader("Sisenemiste ja väljumiste dünaamika")

kuupohine = (
    filtreeritud
    .groupby(["Kuupäev", "Suund"])["Piiriületuste arv"]
    .sum()
    .unstack("Suund", fill_value=0)
    .sort_index()
)

for suund in ["Sisenemised", "Väljumised"]:
    if suund not in kuupohine.columns:
        kuupohine[suund] = 0

fig_kuud = go.Figure()

for suund, varv in [
    ("Sisenemised", "#178939"),
    ("Väljumised", "#2878B5"),
]:
    fig_kuud.add_trace(
        go.Scatter(
            x=kuupohine.index,
            y=kuupohine[suund],
            mode="lines",
            name=suund,
            line=dict(color=varv, width=2.5)
        )
    )

fig_kuud.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Piiriületuste arv",
    hovermode="x unified",
    template="plotly_white",
    height=470
)

st.plotly_chart(fig_kuud, width="stretch")


# ------------------------------------------
# HOOAJALISUSE INDEKS
# SISENEMISED VS VÄLJUMISED
# ------------------------------------------

st.subheader("Hooajalisus kuude lõikes")

st.caption(
    "Indeks 100 tähistab vastava aasta keskmist kuutaset. "
    "Näiteks 120 tähendab 20% kõrgemat ning 80 "
    "20% madalamat piiriületuste arvu."
)

# Kasutame samu filtreid, mis ülejäänud lehel.
# Hooajalisuse arvutamiseks vajame täisaastaid.
# Kui kuu filter on piiratud, arvutame indeksi
# ikkagi kõigi 12 kuu põhjal.

hooaja_alus = andmed.loc[
    andmed["aasta"].isin(aastad)
    & andmed["Piiripunkti tüüp"].isin(piirityybid)
].copy()

for veerg, valitud in valikulised_filtrid.items():
    if valitud:
        hooaja_alus = hooaja_alus.loc[
            hooaja_alus[veerg].isin(valitud)
        ]

# Ainult kalendaarselt täielikud aastad.
# 2026 on ajaloolistes andmetes osaline.

tais_aastad = [
    aasta for aasta in sorted(aastad)
    if len(saadaolevad_kuud.get(aasta, set())) == 12
]

hooaja_alus = hooaja_alus.loc[
    hooaja_alus["aasta"].isin(tais_aastad)
]

if hooaja_alus.empty:
    st.info(
        "Hooajalisuse arvutamiseks vali vähemalt "
        "üks täielik kalendriaasta."
    )

else:
    # Kuude kogusummad suuna ja aasta lõikes
    hooaja_kuud = (
        hooaja_alus
        .groupby(
            ["Suund", "aasta", "kuu"],
            as_index=False
        )["Piiriületuste arv"]
        .sum()
    )

    # Iga suuna ja aasta keskmine kuutase
    aasta_keskmine = (
        hooaja_kuud
        .groupby(["Suund", "aasta"])["Piiriületuste arv"]
        .transform("mean")
    )

    # Hooajalisuse indeks aasta sees
    hooaja_kuud["Indeks"] = (
        hooaja_kuud["Piiriületuste arv"]
        / aasta_keskmine.where(aasta_keskmine > 0)
        * 100
    )

    # Sama kalendrikuu indeksite keskmine aastate lõikes
    hooaja_indeks = (
        hooaja_kuud
        .groupby(["Suund", "kuu"])["Indeks"]
        .mean()
        .reset_index()
    )

    fig_hooaeg = go.Figure()

    for suund, varv in [
        ("Sisenemised", "#178939"),
        ("Väljumised", "#2878B5")
    ]:
        suuna_andmed = hooaja_indeks.loc[
            hooaja_indeks["Suund"] == suund
        ].sort_values("kuu")

        fig_hooaeg.add_trace(
            go.Scatter(
                x=[
                    kuude_nimed[k]
                    for k in suuna_andmed["kuu"]
                ],
                y=suuna_andmed["Indeks"],
                mode="lines+markers",
                name=suund,
                line=dict(color=varv, width=3),
                marker=dict(size=7),
                hovertemplate=(
                    "%{x}<br>"
                    "Hooajalisuse indeks: %{y:.1f}"
                    "<extra>%{fullData.name}</extra>"
                )
            )
        )

    fig_hooaeg.add_hline(
        y=100,
        line_dash="dash",
        line_color="gray",
        annotation_text="Aasta keskmine = 100"
    )

    fig_hooaeg.update_layout(
        xaxis_title="Kuu",
        yaxis_title="Hooajalisuse indeks",
        template="plotly_white",
        hovermode="x unified",
        height=430,
        legend=dict(orientation="h", y=1.12)
    )

    st.plotly_chart(
        fig_hooaeg,
        width="stretch"
    )

    st.caption(
        "Hooajalisuse indeks on arvutatud "
        f"{min(tais_aastad)}–{max(tais_aastad)} "
        "täisaastate põhjal. Iga aasta on esmalt "
        "normaliseeritud oma keskmise kuutasemega. "
        "Kuu filter seda graafikut ei mõjuta."
    )


# ------------------------------------------
# AASTATE VÕRDLUS
# ------------------------------------------

st.divider()
st.subheader("Aastate võrdlus")

aastapohine = (
    filtreeritud
    .groupby(["aasta", "Suund"])["Piiriületuste arv"]
    .sum()
    .unstack("Suund", fill_value=0)
    .sort_index()
)

for suund in ["Sisenemised", "Väljumised"]:
    if suund not in aastapohine.columns:
        aastapohine[suund] = 0

aastapohine["Erinevus"] = (
    aastapohine["Sisenemised"]
    - aastapohine["Väljumised"]
)

fig_aastad = go.Figure()

fig_aastad.add_trace(
    go.Bar(
        x=aastapohine.index.astype(str),
        y=aastapohine["Sisenemised"],
        name="Sisenemised",
        marker_color="#178939"
    )
)

fig_aastad.add_trace(
    go.Bar(
        x=aastapohine.index.astype(str),
        y=aastapohine["Väljumised"],
        name="Väljumised",
        marker_color="#2878B5"
    )
)

fig_aastad.update_layout(
    barmode="group",
    xaxis_title="Aasta",
    yaxis_title="Piiriületuste arv",
    template="plotly_white",
    height=420
)

st.plotly_chart(fig_aastad, width="stretch")


# ------------------------------------------
# SISENEMISTE JA VÄLJUMISTE VAHE
# ------------------------------------------

st.subheader("Sisenemiste ja väljumiste kuine erinevus")

kuupohine["Erinevus"] = (
    kuupohine["Sisenemised"]
    - kuupohine["Väljumised"]
)

fig_erinevus = go.Figure()

fig_erinevus.add_trace(
    go.Bar(
        x=kuupohine.index,
        y=kuupohine["Erinevus"],
        marker_color=[
            "#178939" if x >= 0 else "#D9534F"
            for x in kuupohine["Erinevus"]
        ],
        name="Erinevus"
    )
)

fig_erinevus.add_hline(
    y=0,
    line_color="gray",
    line_width=1
)

fig_erinevus.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Sisenemised − väljumised",
    template="plotly_white",
    height=420
)

st.plotly_chart(fig_erinevus, width="stretch")


# ------------------------------------------
# PIIRIPUNKTIDE VÕRDLUS
# ------------------------------------------

st.divider()
st.subheader("Piiripunktide võrdlus")

punktide_tabel = (
    filtreeritud
    .groupby(["Piiripunkt", "Suund"])["Piiriületuste arv"]
    .sum()
    .unstack("Suund", fill_value=0)
)

for suund in ["Sisenemised", "Väljumised"]:
    if suund not in punktide_tabel.columns:
        punktide_tabel[suund] = 0

punktide_tabel["Erinevus"] = (
    punktide_tabel["Sisenemised"]
    - punktide_tabel["Väljumised"]
)

punktide_tabel["Kokku"] = (
    punktide_tabel["Sisenemised"]
    + punktide_tabel["Väljumised"]
)

top_punktid = (
    punktide_tabel
    .sort_values("Kokku", ascending=False)
    .head(15)
    .sort_values("Kokku", ascending=True)
)

fig_punktid = go.Figure()

for suund, varv in [
    ("Sisenemised", "#178939"),
    ("Väljumised", "#2878B5")
]:
    fig_punktid.add_trace(
        go.Bar(
            y=top_punktid.index,
            x=top_punktid[suund],
            name=suund,
            orientation="h",
            marker_color=varv
        )
    )

fig_punktid.update_layout(
    title="15 suurima kogumahuga piiripunkti",
    barmode="group",
    xaxis_title="Piiriületuste arv",
    yaxis_title="",
    template="plotly_white",
    height=550
)

st.plotly_chart(fig_punktid, width="stretch")


# ------------------------------------------
# AASTATE TABEL JA ALLALAADIMINE
# ------------------------------------------

st.divider()
st.subheader("Aastate kokkuvõte")

aastate_tabel = aastapohine.reset_index()

st.dataframe(
    aastate_tabel.style.format({
        "Sisenemised": "{:,.0f}",
        "Väljumised": "{:,.0f}",
        "Erinevus": "{:+,.0f}"
    }),
    hide_index=True,
    width="stretch"
)

st.download_button(
    "Laadi aastate võrdlus alla (CSV)",
    data=aastate_tabel.to_csv(
        index=False,
        sep=";"
    ).encode("utf-8-sig"),
    file_name="sisenemised_valjumised_aastad.csv",
    mime="text/csv"
)

st.caption(
    "2026. aasta tegelikud andmed lõpevad oktoobriga. "
    "Prognoosid lisame eraldi, et tegelikud ja "
    "prognoositud piiriületused ei seguneks."
)
