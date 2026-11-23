
# ==========================================
# SISENEMISED JA VÄLJUMISED – ÜLEVAADE
# Ajaloolised andmed 2016–2026
# ==========================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.title("Sisenemised ja väljumised")
st.caption("Eesti piiriületuste võrdlus | 2016–2027")

# ------------------------------------------
# ANDMETE ASUKOHT
# ------------------------------------------

ANDMEKAUST = (
    Path(__file__).resolve().parent.parent
    / "streamlit_andmed"
)

# ------------------------------------------
# PROGNOOSIDE LAADIMINE – A7 JA A9
# ------------------------------------------

@st.cache_data(show_spinner="Laen prognoose...")
def lae_prognoosid():

    sis = pd.read_parquet(
        ANDMEKAUST / "sisenemised_prognoos_2027.parquet"
    )

    val = pd.read_parquet(
        ANDMEKAUST / "valjumised_prognoos_2027.parquet"
    )

    sis["Suund"] = "Sisenemised"
    val["Suund"] = "Väljumised"

    df = pd.concat([sis, val], ignore_index=True)

    df["Kuupäev"] = pd.to_datetime(df["Kuupäev"])
    df["aasta"] = df["Kuupäev"].dt.year
    df["kuu"] = df["Kuupäev"].dt.month

    return df

prognoosid = lae_prognoosid()


# --------STICKY MÕÕDIKURIBA CSS----------

st.markdown("""
<style>

/* Fikseeritud mõõdikuriba */
.st-key-sv_sticky_metrics {
    position: fixed !important;
    top: 3.5rem !important;

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
    padding-top: 9rem !important;
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
def lae_liikumiste_andmed(failide_versioonid):

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

    # ------------------------------------------
    # OSALISE KUU TEGELIKUD ANDMED
    # ------------------------------------------

    paevafailid = {
        "Sisenemised": (
            "sisenemised_paevad_2016_2026.parquet",
            "Piiriületajate arv"
        ),
        "Väljumised": (
            "valjumised_paevad_2016_2026.parquet",
            "Piirilt lahkujate arv"
        ),
    }

    tunnused = [
        "Sugu",
        "Vanuserühm",
        "Riikide grupp",
        "Kodakondsus",
        "Piiripunkti tüüp",
        "Piiripunkt",
    ]

    osalised = []
    osalised_kuud = {}

    for suund, (fail, arv) in paevafailid.items():

        paevad = pd.read_parquet(
            ANDMEKAUST / fail,
            columns=[
                "Piiriületuse kpv",
                "aasta",
                "kuu",
                *tunnused,
                arv,
            ]
        )

        paevad["Piiriületuse kpv"] = pd.to_datetime(
            paevad["Piiriületuse kpv"]
        )

        # Leiame viimase avaldatud päeva.
        viimane_paev = paevad["Piiriületuse kpv"].max()

        kuu_algus = viimane_paev.to_period("M").to_timestamp()

        # Kui kuu on kuupõhises failis juba olemas,
        # ei lisa me seda uuesti.
        kuupohised_kuud = df.loc[
            df["Suund"] == suund,
            "Kuupäev"
        ]

        if kuu_algus in set(kuupohised_kuud):
            continue

        # Koondame ainult viimase osalise kuu.
        osaline = paevad.loc[
            paevad["Piiriületuse kpv"].dt.to_period("M")
            == viimane_paev.to_period("M")
        ].copy()

        osaline["Kuupäev"] = kuu_algus

        osaline = (
            osaline.groupby(
                [
                    "Kuupäev",
                    "aasta",
                    "kuu",
                    *tunnused,
                ],
                observed=True,
                dropna=False
            )[arv]
            .sum()
            .reset_index()
        )

        osaline = osaline.rename(columns={
            arv: "Piiriületuste arv"
        })

        osaline["Suund"] = suund

        osalised.append(osaline)

        osalised_kuud[suund] = {
            "kuu": kuu_algus,
            "viimane_paev": viimane_paev,
        }

    if osalised:
        df = pd.concat(
            [df, *osalised],
            ignore_index=True
        )

    return df, osalised_kuud


# Cache uueneb automaatselt, kui mõni andmefail muutub.
andmefailid = [
    "sisenemised_2016_2026.parquet",
    "valjumised_2016_2026.parquet",
    "sisenemised_paevad_2016_2026.parquet",
    "valjumised_paevad_2016_2026.parquet",
]

failide_versioonid = tuple(
    (fail, (ANDMEKAUST / fail).stat().st_mtime_ns)
    for fail in andmefailid
)

andmed, osalised_kuud = lae_liikumiste_andmed(
    failide_versioonid
)

@st.cache_resource(show_spinner="Laen päevapõhiseid andmeid...")
def lae_paevased_andmed():
    """Laeme päevapõhised koondfailid ainult nädalapäeva vaate jaoks.

    Cache resource jagab sama ainult-loetavat objekti rerun'ide vahel.
    """
    filtriveerud = [
        "aasta", "nadalapaev", "Piiripunkti tüüp", "Piiripunkt",
        "Kodakondsus", "Riikide grupp", "Sugu", "Vanuserühm",
    ]
    sis = pd.read_parquet(
        ANDMEKAUST / "sisenemised_paevad_2016_2026.parquet",
        columns=filtriveerud + ["Piiriületajate arv"],
    )
    val = pd.read_parquet(
        ANDMEKAUST / "valjumised_paevad_2016_2026.parquet",
        columns=filtriveerud + ["Piirilt lahkujate arv"],
    )
    return sis, val


# ------------------------------------------
# PPA TEGELIKE ANDMETE VIIMASED KUUPÄEVAD
# ------------------------------------------

@st.cache_data(show_spinner=False)
def lae_ppa_andmeseis(failide_versioonid):
    kaust = Path(__file__).resolve().parents[1] / "streamlit_andmed"

    def viimane_kuupaev(fail, veerg):
        df = pd.read_parquet(
            kaust / fail,
            columns=[veerg]
        )
        return pd.to_datetime(df[veerg].max())

    sisse_paev = viimane_kuupaev(
        "sisenemised_paevad_2016_2026.parquet",
        "Piiriületuse kpv"
    )

    valja_paev = viimane_kuupaev(
        "valjumised_paevad_2016_2026.parquet",
        "Piiriületuse kpv"
    )

    sisse_kuu = viimane_kuupaev(
        "sisenemised_2016_2026.parquet",
        "Kuupäev"
    )

    valja_kuu = viimane_kuupaev(
        "valjumised_2016_2026.parquet",
        "Kuupäev"
    )

    return sisse_paev, valja_paev, min(sisse_kuu, valja_kuu)


def ppa_andmeseis_tekstina():
    kaust = Path(__file__).resolve().parents[1] / "streamlit_andmed"

    failid = [
        "sisenemised_paevad_2016_2026.parquet",
        "valjumised_paevad_2016_2026.parquet",
        "sisenemised_2016_2026.parquet",
        "valjumised_2016_2026.parquet",
    ]

    # Cache uueneb, kui mõni andmefail muutub.
    versioonid = tuple(
        (fail, (kaust / fail).stat().st_mtime_ns)
        for fail in failid
    )

    sisse, valja, kuu = lae_ppa_andmeseis(versioonid)

    kuunimed = [
        "Jaanuar", "Veebruar", "Märts", "Aprill",
        "Mai", "Juuni", "Juuli", "August",
        "September", "Oktoober", "November", "Detsember"
    ]

    return (
        sisse.strftime("%d.%m.%Y"),
        valja.strftime("%d.%m.%Y"),
        f"{kuunimed[kuu.month - 1]} {kuu.year}"
    )



# ------------------------------------------
# AASTAFILTRI JA PROGNOOSI SÜNKRONISEERIMINE
# ------------------------------------------

def sv_aasta_muutus():
    valitud_aastad = st.session_state.get("sv_aastad", [])
    st.session_state["sv_naita_prognoosi"] = (
        2027 in valitud_aastad
    )


def sv_prognoosi_muutus():
    valitud_aastad = list(
        st.session_state.get("sv_aastad", [])
    )

    if st.session_state.get("sv_naita_prognoosi", False):
        if 2027 not in valitud_aastad:
            valitud_aastad.append(2027)
    else:
        valitud_aastad = [
            aasta for aasta in valitud_aastad
            if aasta != 2027
        ]

    st.session_state["sv_aastad"] = sorted(
        valitud_aastad
    )


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
            set(andmed["aasta"].dropna().astype(int))
            | set(prognoosid["aasta"].dropna().astype(int))
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
                default=[
                    a for a in aastate_valikud if a <= 2026
                ],
                key="sv_aastad",
                on_change=sv_aasta_muutus
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

# ------------------------------------------
# PROGNOOSIDE FILTREERIMINE
# ------------------------------------------

prognoosi_mask = (
    prognoosid["aasta"].isin(aastad)
    & prognoosid["kuu"].isin(kuud)
    & prognoosid["Piiripunkti tüüp"].isin(piirityybid)
)

prognoosi_filtrid = {
    "Piiripunkt": piiripunktid,
    "Riikide grupp": riikide_grupid,
    "Kodakondsus": kodakondsused,
    "Sugu": sood,
    "Vanuserühm": vanused,
}

for veerg, valitud in prognoosi_filtrid.items():
    if valitud:
        prognoosi_mask &= prognoosid[veerg].isin(valitud)

filtreeritud_prognoos = prognoosid.loc[prognoosi_mask].copy()


# ------------------------------------------
# TEGELIKUD ANDMED ASENDAVAD KUU PROGNOOSI
# ------------------------------------------

# Leiame kuud, mille kohta on tegelikud andmed.
# Kontroll toimub liikumissuuna ja kuu kaupa.
tegelikud_kuud = (
    andmed[["Suund", "Kuupäev"]]
    .drop_duplicates()
    .copy()
)

tegelikud_kuud["Kuupäev"] = (
    pd.to_datetime(tegelikud_kuud["Kuupäev"])
    .dt.to_period("M")
    .dt.to_timestamp()
)

filtreeritud_prognoos["Kuupäev"] = (
    pd.to_datetime(filtreeritud_prognoos["Kuupäev"])
    .dt.to_period("M")
    .dt.to_timestamp()
)

# Kui kuu tegelikud andmed on olemas,
# eemaldame selle kuu prognoosi.
filtreeritud_prognoos = (
    filtreeritud_prognoos.merge(
        tegelikud_kuud.assign(_tegelik=True),
        on=["Suund", "Kuupäev"],
        how="left"
    )
    .loc[lambda x: x["_tegelik"].isna()]
    .drop(columns="_tegelik")
    .copy()
)


# Mudelite prognoosid jäävad eraldi
prognoos_A7 = filtreeritud_prognoos[
    filtreeritud_prognoos["Mudel"] == "A7"
]

prognoos_A9 = filtreeritud_prognoos[
    filtreeritud_prognoos["Mudel"] == "A9"
]

# ------------------------------------------
# PROGNOOSIMUDELI VALIK
# ------------------------------------------

st.markdown("#### Prognoosi seaded")

valitud_mudel = st.radio(
    "Prognoosimudel",
    options=["A7", "A9"],
    index=0,
    horizontal=True,
    key="sv_prognoosimudel"
)

naita_prognoosi = st.toggle(
    "Kuva prognoos graafikutel",
    value=False,
    key="sv_naita_prognoosi",
    on_change=sv_prognoosi_muutus
)


aktiivne_prognoos = filtreeritud_prognoos[
    filtreeritud_prognoos["Mudel"] == valitud_mudel
].copy()



aktiivne_prognoos["Kuupäev"] = pd.to_datetime(
    aktiivne_prognoos["Kuupäev"]
).dt.to_period("M").dt.to_timestamp()

tegelikud_kuud["Kuupäev"] = pd.to_datetime(
    tegelikud_kuud["Kuupäev"]
).dt.to_period("M").dt.to_timestamp()

aktiivne_prognoos = (
    aktiivne_prognoos.merge(
        tegelikud_kuud.assign(_tegelik_olemas=True),
        on=["Suund", "Kuupäev"],
        how="left"
    )
    .loc[lambda df: df["_tegelik_olemas"].isna()]
    .drop(columns="_tegelik_olemas")
    .copy()
)


# ------------------------------------------
# TEGELIKE ANDMETE JA PROGNOOSIDE KONTROLL
# ------------------------------------------

if filtreeritud.empty and (
    aktiivne_prognoos.empty or not naita_prognoosi
):
    st.warning(
        "Valitud filtritele vastavaid tegelikke "
        "andmeid ega kuvatavat prognoosi ei ole."
    )
    st.stop()

if filtreeritud.empty and not aktiivne_prognoos.empty:
    st.info(
        "Valitud perioodil tegelikud andmed puuduvad. "
        "Kuvatakse ainult prognoos."
    )


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

    # Kasvunäitajad ainult tegelike andmete põhjal
    ajaloolised_aastad = sorted(
        a for a in valitud_aastad
        if a in saadaolevad_kuud
    )

def arvuta_moodikud(df):
    kokku = int(df["Piiriületuste arv"].sum())

    muutus = None
    cagr = None
    yoy = None
    muutus_12k = None

        # ------------------------------------------
    # 1. MUUTUS JA CAGR – TEGELIKUD AASTAD
    # ------------------------------------------

    ajaloolised_aastad = sorted(
        a for a in valitud_aastad
        if a in saadaolevad_kuud
    )

    if len(ajaloolised_aastad) >= 2:

        esimene = ajaloolised_aastad[0]
        viimane = ajaloolised_aastad[-1]

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

    # ------------------------------------------
    # 2. YOY – TEGELIKUD AASTAD
    # ------------------------------------------

    if ajaloolised_aastad:

        viimane = ajaloolised_aastad[-1]
        eelmine = viimane - 1

        if eelmine in ajaloolised_aastad:

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
# KASVUNÄITAJAD KOOS PROGNOOSIGA
# ------------------------------------------

def aasta_maht_koos_prognoosiga(suund, aasta, kuud_arvestuseks=None):

    kuud_kasutusel = (
        list(kuud)
        if kuud_arvestuseks is None
        else list(kuud_arvestuseks)
    )

    # Tegelikud andmed, kasutades samu detailfiltreid
    m = (
        (andmed["Suund"] == suund)
        & (andmed["aasta"] == aasta)
        & andmed["kuu"].isin(kuud_kasutusel)
        & andmed["Piiripunkti tüüp"].isin(piirityybid)
    )

    filtrid = {
        "Piiripunkt": piiripunktid,
        "Riikide grupp": riikide_grupid,
        "Kodakondsus": kodakondsused,
        "Sugu": sood,
        "Vanuserühm": vanused,
    }

    for veerg, valitud in filtrid.items():
        if valitud:
            m &= andmed[veerg].isin(valitud)

    tegelikud = andmed.loc[m]

    # Riiklikult olemasolevad tegelikud kuud
    olemasolevad_kuud = saadaolevad_kuud.get(aasta, set())

    # Prognoosi kasutame ainult kuudel,
    # mille tegelikud andmed veel puuduvad
    prognoosi_kuud = set(kuud_kasutusel) - olemasolevad_kuud

    # Kasutame täielikku prognoositabelit,
    # mitte aastafiltriga piiratud aktiivset prognoosi.

    prog_mask = (
        (prognoosid["Suund"] == suund)
        & (prognoosid["Mudel"] == valitud_mudel)
        & (prognoosid["aasta"] == aasta)
        & prognoosid["kuu"].isin(prognoosi_kuud)
        & prognoosid["Piiripunkti tüüp"].isin(piirityybid)
    )

    # Rakendame samad detailfiltrid
    for veerg, valitud in filtrid.items():
        if valitud:
            prog_mask &= prognoosid[veerg].isin(valitud)

    p = prognoosid.loc[prog_mask]

    # Kontrollime, kas kõik valitud kuud on kaetud
    kaetud_kuud = (
        olemasolevad_kuud
        | set(p["kuu"].unique())
    )

    if not set(kuud_kasutusel).issubset(kaetud_kuud):
        return None

    return (
        tegelikud["Piiriületuste arv"].sum()
        + p["Prognoos"].sum()
    )


def arvuta_prognoosi_kasv(suund):

    if not aastad or not kuud:
        return None, None

    esimene = min(aastad)
    viimane = max(aastad)

    # Prognoosipõhised näitajad ainult
    # siis, kui viimane valitud aasta on 2027
    if viimane != 2027:
        return None, None

    viimane_maht = aasta_maht_koos_prognoosiga(
        suund, viimane
    )

    eelmine_maht = aasta_maht_koos_prognoosiga(
        suund, viimane - 1
    )

    yoy = (
        protsendimuutus(viimane_maht, eelmine_maht)
        if viimane_maht is not None
        and eelmine_maht is not None
        else None
    )

    cagr = None

    if esimene < viimane:

        esimene_maht = aasta_maht_koos_prognoosiga(
            suund, esimene
        )

        if (
            esimene_maht is not None
            and viimane_maht is not None
            and esimene_maht > 0
            and viimane_maht > 0
        ):
            cagr = (
                (viimane_maht / esimene_maht)
                ** (1 / (viimane - esimene))
                - 1
            ) * 100

    return cagr, yoy


# Uuendame kasvunäitajad ainult prognoosi korral
if naita_prognoosi and 2027 in aastad:

    sis_cagr, sis_yoy = arvuta_prognoosi_kasv(
        "Sisenemised"
    )

    val_cagr, val_yoy = arvuta_prognoosi_kasv(
        "Väljumised"
    )

    sis_m["cagr"] = sis_cagr
    sis_m["yoy"] = sis_yoy

    val_m["cagr"] = val_cagr
    val_m["yoy"] = val_yoy


# ------------------------------------------
# TÄIENDAVAD PROGNOOSIPÕHISED MÕÕDIKUD
# ------------------------------------------

def prognoosi_lisamoodikud(suund):

    # 1. Muutus esimese ja viimase valitud aasta vahel
    muutus = None

    if len(set(aastad)) >= 2:

        esimene = min(aastad)
        viimane = max(aastad)

        algus = aasta_maht_koos_prognoosiga(
            suund, esimene
        )

        lopp = aasta_maht_koos_prognoosiga(
            suund, viimane
        )

        if algus is not None and lopp is not None:
            muutus = protsendimuutus(lopp, algus)

    # 2. Viimase 12 kuu muutus
    # 2027 detsembriga lõppev 12 kuud vs 2026
    muutus_12k = None

    if set(kuud) == set(range(1, 13)):

        uus = aasta_maht_koos_prognoosiga(
            suund, 2027
        )

        vana = aasta_maht_koos_prognoosiga(
            suund, 2026
        )

        if uus is not None and vana is not None:
            muutus_12k = protsendimuutus(uus, vana)

    # 3. TOP 3 piiripunkti osakaal
    tegelikud = filtreeritud[
        filtreeritud["Suund"] == suund
    ][["aasta", "kuu", "Piiripunkt", "Piiriületuste arv"]].copy()

    tegelikud = tegelikud.rename(
        columns={"Piiriületuste arv": "Maht"}
    )

    p = aktiivne_prognoos[
        aktiivne_prognoos["Suund"] == suund
    ].copy()

    # Väldime juba olemasolevate tegelike kuude
    # prognooside topeltarvestust.
    p = p[
        ~p.apply(
            lambda r: r["kuu"] in saadaolevad_kuud.get(
                r["aasta"], set()
            ),
            axis=1
        )
    ]

    p = p[
        ["aasta", "kuu", "Piiripunkt", "Prognoos"]
    ].rename(columns={"Prognoos": "Maht"})

    koond = pd.concat(
        [tegelikud, p],
        ignore_index=True
    )

    top3 = None

    if not koond.empty:

        punktid = (
            koond.groupby("Piiripunkt")["Maht"]
            .sum()
            .sort_values(ascending=False)
        )

        kokku = punktid.sum()

        if kokku > 0:
            top3 = punktid.head(3).sum() / kokku * 100

    return muutus, muutus_12k, top3


# Uuendame näitajaid ainult prognoosiaasta puhul
if naita_prognoosi and 2027 in aastad:

    for suund, moodikud in [
        ("Sisenemised", sis_m),
        ("Väljumised", val_m)
    ]:

        muutus, muutus_12k, top3 = (
            prognoosi_lisamoodikud(suund)
        )

        moodikud["muutus"] = muutus
        moodikud["muutus_12k"] = muutus_12k
        moodikud["top3"] = top3

# ------------------------------------------
# YOY – VIIMANE VALITUD AASTA VS EELMINE
# ------------------------------------------

def arvuta_yoy_uhiselt(suund):

    if not aastad or not kuud:
        return None

    viimane = max(aastad)
    eelmine = viimane - 1

    # Prognoosiga aastad
    if naita_prognoosi and viimane >= 2026:

        uus = aasta_maht_koos_prognoosiga(
            suund, viimane
        )

        vana = aasta_maht_koos_prognoosiga(
            suund, eelmine
        )

        if uus is None or vana is None:
            return None

        return protsendimuutus(uus, vana)

    # Ainult tegelike andmete võrdlus.
    # Võrdleme mõlemas aastas saadaolevaid kuid.

    uhised_kuud = (
        set(kuud)
        & saadaolevad_kuud.get(viimane, set())
        & saadaolevad_kuud.get(eelmine, set())
    )

    if not uhised_kuud:
        return None

    filtrid = {
        "Piiripunkt": piiripunktid,
        "Riikide grupp": riikide_grupid,
        "Kodakondsus": kodakondsused,
        "Sugu": sood,
        "Vanuserühm": vanused,
    }

    def tegelik_aastamaht(aasta):

        mask_yoy = (
            (andmed["Suund"] == suund)
            & (andmed["aasta"] == aasta)
            & andmed["kuu"].isin(uhised_kuud)
            & andmed["Piiripunkti tüüp"].isin(piirityybid)
        )

        for veerg, valitud in filtrid.items():
            if valitud:
                mask_yoy &= andmed[veerg].isin(valitud)

        return andmed.loc[
            mask_yoy, "Piiriületuste arv"
        ].sum()

    uus = tegelik_aastamaht(viimane)
    vana = tegelik_aastamaht(eelmine)

    return protsendimuutus(uus, vana)


# Uuendame YoY mõlemal liikumissuunal
sis_m["yoy"] = arvuta_yoy_uhiselt("Sisenemised")
val_m["yoy"] = arvuta_yoy_uhiselt("Väljumised")



# ------------------------------------------
# OSALISE KUU KASVUVÕRDLUSTE KONTROLL
# ------------------------------------------

# Kas valitud periood sisaldab osalist tegelikku kuud?
valikus_osaline_kuu = any(
    info["kuu"].year in aastad
    and info["kuu"].month in kuud
    for info in osalised_kuud.values()
)

# Arvestame ka olukorda, kus 2027 prognoosi
# võrreldakse 2026. aasta osaliste andmetega.
osaline_vordlusperioodis = any(
    info["kuu"].month in kuud
    and (
        info["kuu"].year in aastad
        or (
            naita_prognoosi
            and 2027 in aastad
            and info["kuu"].year == 2026
        )
    )
    for info in osalised_kuud.values()
)


if osaline_vordlusperioodis:

    if naita_prognoosi and 2027 in aastad:

        # Kasvuvõrdluses välistame osalise kuu
        # mõlemast võrreldavast aastast.
        osaliste_kuude_numbrid = {
            int(info["kuu"].month)
            for info in osalised_kuud.values()
            if int(info["kuu"].year) == 2026
        }

        kasvukuud = [
            kuu for kuu in kuud
            if kuu not in osaliste_kuude_numbrid
        ]

        for suund, moodikud in [
            ("Sisenemised", sis_m),
            ("Väljumised", val_m),
        ]:

            moodikud["muutus"] = None
            moodikud["cagr"] = None
            moodikud["yoy"] = None
            moodikud["muutus_12k"] = None

            if not kasvukuud:
                continue

            viimane = max(aastad)
            esimene = min(aastad)

            uus = aasta_maht_koos_prognoosiga(
                suund, viimane, kasvukuud
            )

            eelmine = aasta_maht_koos_prognoosiga(
                suund, viimane - 1, kasvukuud
            )

            if uus is not None and eelmine is not None:
                moodikud["yoy"] = protsendimuutus(
                    uus, eelmine
                )

            if len(set(aastad)) >= 2:

                vana = aasta_maht_koos_prognoosiga(
                    suund, esimene, kasvukuud
                )

                if vana is not None and uus is not None:

                    moodikud["muutus"] = protsendimuutus(
                        uus, vana
                    )

                    if vana > 0 and uus > 0:
                        moodikud["cagr"] = (
                            (uus / vana)
                            ** (1 / (viimane - esimene))
                            - 1
                        ) * 100

        st.info(
            "Kasvuvõrdlustes on osaline november 2026 "
            "mõlemast võrreldavast aastast välja jäetud. "
            "Üldmahud ja graafikud sisaldavad jätkuvalt "
            "valitud perioodi kõiki olemasolevaid andmeid. "
            "Viimase 12 kuu muutust ei kuvata, sest "
            "võrdlus ei hõlma 12 täielikku kuud."
        )

    
    else:

        # Ajalooliste aastate võrdlus:
        # kasutame ainult mõlemas aastas täielikke kuid.
        def uhised_taiskuud(aasta1, aasta2):
            tulem = (
                set(kuud)
                & set(saadaolevad_kuud.get(aasta1, set()))
                & set(saadaolevad_kuud.get(aasta2, set()))
            )

            for info in osalised_kuud.values():
                if info["kuu"].year in (aasta1, aasta2):
                    tulem.discard(int(info["kuu"].month))

            return sorted(tulem)

        def tegelik_maht(suund, aasta, kuude_valik):
            mask = (
                (andmed["Suund"] == suund)
                & (andmed["aasta"] == aasta)
                & andmed["kuu"].isin(kuude_valik)
                & andmed["Piiripunkti tüüp"].isin(piirityybid)
            )

            filtrid = {
                "Piiripunkt": piiripunktid,
                "Riikide grupp": riikide_grupid,
                "Kodakondsus": kodakondsused,
                "Sugu": sood,
                "Vanuserühm": vanused,
            }

            for veerg, valitud in filtrid.items():
                if valitud:
                    mask &= andmed[veerg].isin(valitud)

            return andmed.loc[
                mask, "Piiriületuste arv"
            ].sum()

        esimene = min(aastad)
        viimane = max(aastad)

        for suund, moodikud in [
            ("Sisenemised", sis_m),
            ("Väljumised", val_m),
        ]:

            moodikud["muutus"] = None
            moodikud["cagr"] = None
            moodikud["yoy"] = None
            moodikud["muutus_12k"] = None

            if esimene < viimane:
                kasvukuud = uhised_taiskuud(
                    esimene, viimane
                )

                if kasvukuud:
                    vana = tegelik_maht(
                        suund, esimene, kasvukuud
                    )
                    uus = tegelik_maht(
                        suund, viimane, kasvukuud
                    )

                    moodikud["muutus"] = protsendimuutus(
                        uus, vana
                    )

                    if vana > 0 and uus > 0:
                        moodikud["cagr"] = (
                            (uus / vana)
                            ** (1 / (viimane - esimene))
                            - 1
                        ) * 100

            # YoY: viimane valitud aasta vs eelmine aasta
            yoy_kuud = uhised_taiskuud(
                viimane - 1, viimane
            )

            if yoy_kuud:
                vana = tegelik_maht(
                    suund, viimane - 1, yoy_kuud
                )
                uus = tegelik_maht(
                    suund, viimane, yoy_kuud
                )

                moodikud["yoy"] = protsendimuutus(
                    uus, vana
                )

        st.info(
            "Kasvuvõrdlustes kasutatakse ainult mõlemas "
            "võrreldavas aastas täielikke kuid. "
            "2026. aasta osalist novembrit ja puuduvat "
            "detsembrit kasvunäitajatesse ei arvestata. "
            "Kogumahud ja graafikud jäävad muutmata."
        )



# ------------------------------------------
# KOMPAKTSED PÕHINÄITAJAD
# ------------------------------------------


# ------------------------------------------
# TEGELIKUD + PROGNOOSITUD MAHUD
# ------------------------------------------

sis_tegelik = sis_m["kokku"]
val_tegelik = val_m["kokku"]

sis_prognoos = 0
val_prognoos = 0

if naita_prognoosi:

    sis_prognoos = int(
        aktiivne_prognoos.loc[
            aktiivne_prognoos["Suund"] == "Sisenemised",
            "Prognoos"
        ].sum().round()
    )

    val_prognoos = int(
        aktiivne_prognoos.loc[
            aktiivne_prognoos["Suund"] == "Väljumised",
            "Prognoos"
        ].sum().round()
    )

sis_kokku = sis_tegelik + sis_prognoos
val_kokku = val_tegelik + val_prognoos

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

import streamlit as st

lipp = """
<svg xmlns="http://www.w3.org/2000/svg" width="36" height="24" viewBox="0 0 3 2">
  <rect width="3" height="2" fill="#fff"/>
  <rect width="3" height="0.6667" fill="#4891D9"/>
  <rect y="0.6667" width="3" height="0.6667" fill="#000"/>
</svg>
"""

col1, col2 = st.columns([1, 20], gap="small", vertical_alignment="center")

with col1:
    st.image(lipp, width=36)

with col2:
    st.subheader(
        "Eesti piiriületuste võrdlus sisenemised/väljumised | 2016–2027"
    )

# Kompaktsed väärtused mõõdikuriba jaoks
def lyhi_arv(arv):
    if abs(arv) >= 1_000_000:
        return f"{arv / 1_000_000:.2f}".replace(".", ",") + " mln"
    return vorminda_arv(arv)

# ------------------------------------------
# YOY MÕÕDIKU NIMETUS
# ------------------------------------------

# YoY selgitus vastavalt võrdluse aluseks olevatele kuudele
if osaline_vordlusperioodis and naita_prognoosi and 2027 in aastad:

    osaliste_kuude_numbrid = {
        int(info["kuu"].month)
        for info in osalised_kuud.values()
        if int(info["kuu"].year) == 2026
    }

    vordluskuude_arv = len(
        set(kuud) - osaliste_kuude_numbrid
    )

    yoy_silt = f"YoY ({vordluskuude_arv} võrreldavat kuud)"

elif osaline_vordlusperioodis:

    yoy_silt = "YoY (osaline kuu)"

elif naita_prognoosi and aastad and max(aastad) >= 2026:

    yoy_silt = "YoY (sh prognoos)"

else:

    yoy_silt = "YoY"

if osaline_vordlusperioodis:
    yoy_silt = "YoY (osaline kuu)"

with moodikute_koht.container():

    ppa_sisse, ppa_valja, ppa_kuu = ppa_andmeseis_tekstina()

    st.html(
        f"""
        <style>
        .sv-ppa-layout {{
            display: grid;
            grid-template-columns: minmax(0, 5fr) minmax(215px, 1.65fr);
            align-items: stretch;
            gap: 16px;
            width: 100%;
        }}

        .sv-ppa-layout .sv-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            width: 100%;
            min-width: 0;
        }}

        .sv-ppa-status {{
            border: 1px solid rgba(128, 128, 128, 0.24);
            border-radius: 10px;
            padding: 11px 14px;
            background: rgba(128, 128, 128, 0.045);
            min-width: 0;
        }}

        .sv-ppa-heading {{
            font-size: 12px;
            font-weight: 650;
            margin-bottom: 9px;
        }}

        .sv-ppa-row {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 8px;
            margin-top: 6px;
            font-size: 11px;
        }}

        .sv-ppa-row span {{
            color: var(--text-color, inherit);
            opacity: 0.7;
        }}

        .sv-ppa-row strong {{
            font-size: 12px;
            font-weight: 650;
            white-space: nowrap;
        }}

        .sv-ppa-month {{
            border-top: 1px solid rgba(128, 128, 128, 0.20);
            padding-top: 7px;
            margin-top: 9px;
        }}

        @media (max-width: 1050px) {{
            .sv-ppa-layout {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>

        <div class="sv-ppa-layout">

            <!-- VIIS OLEMASOLEVAT MÕÕDIKUT -->
            <div class="sv-metrics-grid">

                <div class="sv-metric">
                    <div class="sv-label">
                        Sisenemised
                        {'(koos prognoosiga)' if naita_prognoosi and sis_prognoos else ''}
                    </div>
                    <div class="sv-value">
                        {lyhi_arv(sis_kokku)}
                    </div>
                </div>

                <div class="sv-metric">
                    <div class="sv-label">
                        Väljumised
                        {'(koos prognoosiga)' if naita_prognoosi and val_prognoos else ''}
                    </div>
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
                    <div class="sv-label">{yoy_silt}</div>
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

            <!-- PPA ANDMETE SEIS -->
            <div class="sv-ppa-status">

                <div class="sv-ppa-heading">
                    📅 PPA tegelike andmete seis
                </div>

                <div class="sv-ppa-row">
                    <span>Sisenemised</span>
                    <strong>{ppa_sisse}</strong>
                </div>

                <div class="sv-ppa-row">
                    <span>Väljumised</span>
                    <strong>{ppa_valja}</strong>
                </div>

                <div class="sv-ppa-row sv-ppa-month">
                    <span>Viimane täielik kuu</span>
                    <strong>{ppa_kuu}</strong>
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
        if naita_prognoosi and 2027 in aastad:
            # Kasvuvõrdluses kasutatavate kuude arv
            osaliste_kuude_numbrid = {
                int(info["kuu"].month)
                for info in osalised_kuud.values()
                if int(info["kuu"].year) == 2026
            }

            if naita_prognoosi and 2027 in aastad:
                vordluskuud = set(kuud) - osaliste_kuude_numbrid
            else:
                vordluskuud = set(kuud)

            vordluskuude_arv = len(vordluskuud)

        
        # Võrreldavate kuude arv ja selgitus
        if aastad:
            esimene_aasta = min(aastad)
            viimane_aasta = max(aastad)

            if naita_prognoosi and viimane_aasta == 2027:
                vordluskuud = set(kuud)

                for info in osalised_kuud.values():
                    if info["kuu"].year == 2026:
                        vordluskuud.discard(int(info["kuu"].month))

                allika_selgitus = (
                    f"2027. aasta väärtused põhinevad "
                    f"{valitud_mudel} prognoosimudelil. "
                )
            else:
                vordluskuud = (
                    set(kuud)
                    & set(saadaolevad_kuud.get(esimene_aasta, set()))
                    & set(saadaolevad_kuud.get(viimane_aasta, set()))
                )

                for info in osalised_kuud.values():
                    if info["kuu"].year in (esimene_aasta, viimane_aasta):
                        vordluskuud.discard(int(info["kuu"].month))

                allika_selgitus = (
                    "Kasvuvõrdlus põhineb PPA tegelikel andmetel. "
                )

            vordluskuude_arv = len(vordluskuud)

            st.markdown(
                f"""
                <div style="
                    padding: 4px 14px 12px 14px;
                    font-size: 13px;
                    color: #7D8997;
                    line-height: 1.7;
                ">
                    {allika_selgitus}
                    Kasvuvõrdluse kuude arv:
                    <b>{vordluskuude_arv}</b>.
                    Võrreldakse samu kalendrikuusid ning osaline
                    november 2026 jäetakse vajaduse korral välja.
                    Kogumahud ja TOP 3 piiripunkti osakaal arvestavad
                    kõiki valitud perioodi olemasolevaid andmeid.
                </div>
                """,
                unsafe_allow_html=True
            )

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

        # None väärtused teisendame NaN-iks
        for veerg in ["Sisenemised", "Väljumised"]:
            vordlus[veerg] = pd.to_numeric(
                vordlus[veerg],
                errors="coerce"
            ).astype(float)

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

        # ------------------------------------------
# VÕRDLUSTABELI VORMINDAMINE
# ------------------------------------------

        tabel = vordlus.set_index("Mõõdik").copy().astype(object)

        # Vormindame väärtused enne kuvamist
        for moodik in tabel.index:

            for veerg in ["Sisenemised", "Väljumised"]:

                vaartus = tabel.loc[moodik, veerg]

                if pd.isna(vaartus):
                    tekst = "–"

                elif moodik == "TOP 3 piiripunkti osakaal":
                    tekst = f"{vaartus:.2f}%".replace(".", ",")

                else:
                    tekst = f"{vaartus:+.2f}%".replace(".", ",")

                tabel.loc[moodik, veerg] = tekst


        # Värvime kasvunäitajad
        def varvi_tabeli_vaartus(vaartus):

            if vaartus == "–":
                return "color: gray"

            if vaartus.startswith("-"):
                return "color: #D9534F; font-weight: 600"

            if vaartus.startswith("+"):
                return "color: #178939; font-weight: 600"

            return ""


        kujundatud_tabel = tabel.style.map(
            varvi_tabeli_vaartus,
            subset=pd.IndexSlice[
                [
                    "Muutus võrreldavatel aastatel",
                    "Keskmine aastane kasv (CAGR)",
                    "Viimase aasta muutus (YoY)",
                    "Viimase 12 kuu muutus",
                ],
                :
            ]
        )

        st.dataframe(
            kujundatud_tabel,
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
# B. KODAKONDSUSTE MAAILMAKAART – TOP 20
# ------------------------------------------

import unicodedata
import numpy as np

KODAKONDSUS_ISO3 = {
    'abw': 'ABW',
    'ad': 'AND',
    'ae': 'ARE',
    'af': 'AFG',
    'afg': 'AFG',
    'afganistan': 'AFG',
    'afghanistan': 'AFG',
    'ag': 'ATG',
    'ago': 'AGO',
    'ahvenamaa': 'ALA',
    'ai': 'AIA',
    'aia': 'AIA',
    'al': 'ALB',
    'ala': 'ALA',
    'aland islands': 'ALA',
    'alb': 'ALB',
    'albaania': 'ALB',
    'albania': 'ALB',
    'algeria': 'DZA',
    'alzeeria': 'DZA',
    'am': 'ARM',
    'ameerika samoa': 'ASM',
    'ameerika uhendriigid': 'USA',
    'american samoa': 'ASM',
    'and': 'AND',
    'andorra': 'AND',
    'angola': 'AGO',
    'anguilla': 'AIA',
    'antarctica': 'ATA',
    'antarktika': 'ATA',
    'antigua and barbuda': 'ATG',
    'antigua ja barbuda': 'ATG',
    'ao': 'AGO',
    'aq': 'ATA',
    'ar': 'ARG',
    'araabia uhendemiraadid': 'ARE',
    'arab republic of egypt': 'EGY',
    'are': 'ARE',
    'arg': 'ARG',
    'argentina': 'ARG',
    'argentine republic': 'ARG',
    'arm': 'ARM',
    'armeenia': 'ARM',
    'armenia': 'ARM',
    'aruba': 'ABW',
    'as': 'ASM',
    'aserbaidzaan': 'AZE',
    'asm': 'ASM',
    'at': 'AUT',
    'ata': 'ATA',
    'atf': 'ATF',
    'atg': 'ATG',
    'au': 'AUS',
    'aus': 'AUS',
    'austraalia': 'AUS',
    'australia': 'AUS',
    'austria': 'AUT',
    'aut': 'AUT',
    'aw': 'ABW',
    'ax': 'ALA',
    'az': 'AZE',
    'aze': 'AZE',
    'azerbaijan': 'AZE',
    'ba': 'BIH',
    'bahama': 'BHS',
    'bahamas': 'BHS',
    'bahrain': 'BHR',
    'bahrein': 'BHR',
    'bangladesh': 'BGD',
    'barbados': 'BRB',
    'bb': 'BRB',
    'bd': 'BGD',
    'bdi': 'BDI',
    'be': 'BEL',
    'bel': 'BEL',
    'belarus': 'BLR',
    'belau': 'PLW',
    'belgia': 'BEL',
    'belgium': 'BEL',
    'belize': 'BLZ',
    'ben': 'BEN',
    'benin': 'BEN',
    'bermuda': 'BMU',
    'bes': 'BES',
    'bf': 'BFA',
    'bfa': 'BFA',
    'bg': 'BGR',
    'bgd': 'BGD',
    'bgr': 'BGR',
    'bh': 'BHR',
    'bhr': 'BHR',
    'bhs': 'BHS',
    'bhutan': 'BTN',
    'bi': 'BDI',
    'bih': 'BIH',
    'bj': 'BEN',
    'bl': 'BLM',
    'blm': 'BLM',
    'blr': 'BLR',
    'blz': 'BLZ',
    'bm': 'BMU',
    'bmu': 'BMU',
    'bn': 'BRN',
    'bo': 'BOL',
    'bol': 'BOL',
    'boliivia': 'BOL',
    'bolivarian republic of venezuela': 'VEN',
    'bolivia, plurinational state of': 'BOL',
    'bonaire, sint eustatius and saba': 'BES',
    'bosnia and herzegovina': 'BIH',
    'bosnia ja hertsegoviina': 'BIH',
    'botswana': 'BWA',
    'bouvet island': 'BVT',
    'bouvet’ saar': 'BVT',
    'bq': 'BES',
    'br': 'BRA',
    'bra': 'BRA',
    'brasiilia': 'BRA',
    'brazil': 'BRA',
    'brb': 'BRB',
    'briti india ookeani ala': 'IOT',
    'briti neitsisaared': 'VGB',
    'british indian ocean territory': 'IOT',
    'british virgin islands': 'VGB',
    'brn': 'BRN',
    'brunei': 'BRN',
    'brunei darussalam': 'BRN',
    'bs': 'BHS',
    'bt': 'BTN',
    'btn': 'BTN',
    'bulgaaria': 'BGR',
    'bulgaria': 'BGR',
    'burkina faso': 'BFA',
    'burundi': 'BDI',
    'bv': 'BVT',
    'bvt': 'BVT',
    'bw': 'BWA',
    'bwa': 'BWA',
    'by': 'BLR',
    'bz': 'BLZ',
    'ca': 'CAN',
    'cabo verde': 'CPV',
    'caf': 'CAF',
    'cambodia': 'KHM',
    'cameroon': 'CMR',
    'can': 'CAN',
    'canada': 'CAN',
    'cayman islands': 'CYM',
    'cc': 'CCK',
    'cck': 'CCK',
    'cd': 'COD',
    'central african republic': 'CAF',
    'cf': 'CAF',
    'cg': 'COG',
    'ch': 'CHE',
    'chad': 'TCD',
    'che': 'CHE',
    'chile': 'CHL',
    'china': 'CHN',
    'chl': 'CHL',
    'chn': 'CHN',
    'christmas island': 'CXR',
    'ci': 'CIV',
    'civ': 'CIV',
    'ck': 'COK',
    'cl': 'CHL',
    'cm': 'CMR',
    'cmr': 'CMR',
    'cn': 'CHN',
    'co': 'COL',
    'cocos (keeling) islands': 'CCK',
    'cod': 'COD',
    'cog': 'COG',
    'cok': 'COK',
    'col': 'COL',
    'colombia': 'COL',
    'com': 'COM',
    'commonwealth of dominica': 'DMA',
    'commonwealth of the bahamas': 'BHS',
    'commonwealth of the northern mariana islands': 'MNP',
    'comoros': 'COM',
    'congo': 'COG',
    'congo, the democratic republic of the': 'COD',
    'cook islands': 'COK',
    'cooki saared': 'COK',
    'costa rica': 'CRI',
    "cote d'ivoire": 'CIV',
    'cpv': 'CPV',
    'cr': 'CRI',
    'cri': 'CRI',
    'croatia': 'HRV',
    'cu': 'CUB',
    'cub': 'CUB',
    'cuba': 'CUB',
    'curacao': 'CUW',
    'cuw': 'CUW',
    'cv': 'CPV',
    'cw': 'CUW',
    'cx': 'CXR',
    'cxr': 'CXR',
    'cy': 'CYP',
    'cym': 'CYM',
    'cyp': 'CYP',
    'cyprus': 'CYP',
    'cz': 'CZE',
    'cze': 'CZE',
    'czech republic': 'CZE',
    'czechia': 'CZE',
    'de': 'DEU',
    "democratic people's republic of korea": 'PRK',
    'democratic republic of sao tome and principe': 'STP',
    'democratic republic of timor-leste': 'TLS',
    'democratic socialist republic of sri lanka': 'LKA',
    'denmark': 'DNK',
    'deu': 'DEU',
    'dj': 'DJI',
    'dji': 'DJI',
    'djibouti': 'DJI',
    'dk': 'DNK',
    'dm': 'DMA',
    'dma': 'DMA',
    'dnk': 'DNK',
    'do': 'DOM',
    'dom': 'DOM',
    'dominica': 'DMA',
    'dominican republic': 'DOM',
    'dominikaani vabariik': 'DOM',
    'dz': 'DZA',
    'dza': 'DZA',
    'eastern republic of uruguay': 'URY',
    'ec': 'ECU',
    'ecu': 'ECU',
    'ecuador': 'ECU',
    'ee': 'EST',
    'eesti': 'EST',
    'eg': 'EGY',
    'egiptus': 'EGY',
    'egy': 'EGY',
    'egypt': 'EGY',
    'eh': 'ESH',
    'ekvatoriaal-guinea': 'GNQ',
    'el salvador': 'SLV',
    'elevandiluurannik': 'CIV',
    'equatorial guinea': 'GNQ',
    'er': 'ERI',
    'eri': 'ERI',
    'eritrea': 'ERI',
    'es': 'ESP',
    'esh': 'ESH',
    'esp': 'ESP',
    'est': 'EST',
    'estonia': 'EST',
    'eswatini': 'SWZ',
    'et': 'ETH',
    'eth': 'ETH',
    'ethiopia': 'ETH',
    'etioopia': 'ETH',
    'faari saared': 'FRO',
    'falkland islands (malvinas)': 'FLK',
    'falklandi saared': 'FLK',
    'faroe islands': 'FRO',
    'federal democratic republic of ethiopia': 'ETH',
    'federal democratic republic of nepal': 'NPL',
    'federal republic of germany': 'DEU',
    'federal republic of nigeria': 'NGA',
    'federal republic of somalia': 'SOM',
    'federated states of micronesia': 'FSM',
    'federative republic of brazil': 'BRA',
    'fi': 'FIN',
    'fidzi': 'FJI',
    'fiji': 'FJI',
    'filipiinid': 'PHL',
    'fin': 'FIN',
    'finland': 'FIN',
    'fj': 'FJI',
    'fji': 'FJI',
    'fk': 'FLK',
    'flk': 'FLK',
    'fm': 'FSM',
    'fo': 'FRO',
    'fr': 'FRA',
    'fra': 'FRA',
    'france': 'FRA',
    'french guiana': 'GUF',
    'french polynesia': 'PYF',
    'french republic': 'FRA',
    'french southern territories': 'ATF',
    'fro': 'FRO',
    'fsm': 'FSM',
    'ga': 'GAB',
    'gab': 'GAB',
    'gabon': 'GAB',
    'gabonese republic': 'GAB',
    'gambia': 'GMB',
    'gb': 'GBR',
    'gbr': 'GBR',
    'gd': 'GRD',
    'ge': 'GEO',
    'geo': 'GEO',
    'georgia': 'GEO',
    'germany': 'DEU',
    'gf': 'GUF',
    'gg': 'GGY',
    'ggy': 'GGY',
    'gh': 'GHA',
    'gha': 'GHA',
    'ghana': 'GHA',
    'gi': 'GIB',
    'gib': 'GIB',
    'gibraltar': 'GIB',
    'gin': 'GIN',
    'gl': 'GRL',
    'glp': 'GLP',
    'gm': 'GMB',
    'gmb': 'GMB',
    'gn': 'GIN',
    'gnb': 'GNB',
    'gnq': 'GNQ',
    'gp': 'GLP',
    'gq': 'GNQ',
    'gr': 'GRC',
    'grand duchy of luxembourg': 'LUX',
    'grc': 'GRC',
    'grd': 'GRD',
    'greece': 'GRC',
    'greenland': 'GRL',
    'grenada': 'GRD',
    'grl': 'GRL',
    'groonimaa': 'GRL',
    'gruusia': 'GEO',
    'gs': 'SGS',
    'gt': 'GTM',
    'gtm': 'GTM',
    'gu': 'GUM',
    'guadeloupe': 'GLP',
    'guam': 'GUM',
    'guatemala': 'GTM',
    'guernsey': 'GGY',
    'guf': 'GUF',
    'guinea': 'GIN',
    'guinea-bissau': 'GNB',
    'gum': 'GUM',
    'guy': 'GUY',
    'guyana': 'GUY',
    'gw': 'GNB',
    'gy': 'GUY',
    'haiti': 'HTI',
    'hashemite kingdom of jordan': 'JOR',
    'heard island and mcdonald islands': 'HMD',
    'heardi ja mcdonaldi saared': 'HMD',
    'hellenic republic': 'GRC',
    'hiina': 'CHN',
    'hispaania': 'ESP',
    'hk': 'HKG',
    'hkg': 'HKG',
    'hm': 'HMD',
    'hmd': 'HMD',
    'hn': 'HND',
    'hnd': 'HND',
    'holland': 'NLD',
    'holy see (vatican city state)': 'VAT',
    'honduras': 'HND',
    'hong kong': 'HKG',
    'hong kong special administrative region of china': 'HKG',
    'hongkong': 'HKG',
    'hongkongi erihalduspiirkond': 'HKG',
    'horvaatia': 'HRV',
    'hr': 'HRV',
    'hrv': 'HRV',
    'ht': 'HTI',
    'hti': 'HTI',
    'hu': 'HUN',
    'hun': 'HUN',
    'hungary': 'HUN',
    'iceland': 'ISL',
    'id': 'IDN',
    'ida-timor': 'TLS',
    'idn': 'IDN',
    'ie': 'IRL',
    'iirimaa': 'IRL',
    'iisrael': 'ISR',
    'il': 'ISR',
    'im': 'IMN',
    'imn': 'IMN',
    'in': 'IND',
    'ind': 'IND',
    'independent state of papua new guinea': 'PNG',
    'independent state of samoa': 'WSM',
    'india': 'IND',
    'indoneesia': 'IDN',
    'indonesia': 'IDN',
    'inglismaa': 'GBR',
    'io': 'IOT',
    'iot': 'IOT',
    'iq': 'IRQ',
    'ir': 'IRN',
    'iraak': 'IRQ',
    'iraan': 'IRN',
    'iran, islamic republic of': 'IRN',
    'iraq': 'IRQ',
    'ireland': 'IRL',
    'irl': 'IRL',
    'irn': 'IRN',
    'irq': 'IRQ',
    'is': 'ISL',
    'isl': 'ISL',
    'islamic republic of afghanistan': 'AFG',
    'islamic republic of iran': 'IRN',
    'islamic republic of mauritania': 'MRT',
    'islamic republic of pakistan': 'PAK',
    'island': 'ISL',
    'isle of man': 'IMN',
    'isr': 'ISR',
    'israel': 'ISR',
    'it': 'ITA',
    'ita': 'ITA',
    'itaalia': 'ITA',
    'italian republic': 'ITA',
    'italy': 'ITA',
    'jaapan': 'JPN',
    'jam': 'JAM',
    'jamaica': 'JAM',
    'japan': 'JPN',
    'je': 'JEY',
    'jeemen': 'YEM',
    'jersey': 'JEY',
    'jey': 'JEY',
    'jm': 'JAM',
    'jo': 'JOR',
    'jor': 'JOR',
    'jordaania': 'JOR',
    'jordan': 'JOR',
    'joulusaar': 'CXR',
    'jp': 'JPN',
    'jpn': 'JPN',
    'kaimanisaared': 'CYM',
    'kambodza': 'KHM',
    'kamerun': 'CMR',
    'kanada': 'CAN',
    'kariibi madalmaad': 'BES',
    'kasahstan': 'KAZ',
    'katar': 'QAT',
    'kaz': 'KAZ',
    'kazakhstan': 'KAZ',
    'ke': 'KEN',
    'keenia': 'KEN',
    'ken': 'KEN',
    'kenya': 'KEN',
    'kesk-aafrika vabariik': 'CAF',
    'kg': 'KGZ',
    'kgz': 'KGZ',
    'kh': 'KHM',
    'khm': 'KHM',
    'ki': 'KIR',
    'kingdom of bahrain': 'BHR',
    'kingdom of belgium': 'BEL',
    'kingdom of bhutan': 'BTN',
    'kingdom of cambodia': 'KHM',
    'kingdom of denmark': 'DNK',
    'kingdom of eswatini': 'SWZ',
    'kingdom of lesotho': 'LSO',
    'kingdom of morocco': 'MAR',
    'kingdom of norway': 'NOR',
    'kingdom of saudi arabia': 'SAU',
    'kingdom of spain': 'ESP',
    'kingdom of sweden': 'SWE',
    'kingdom of thailand': 'THA',
    'kingdom of the netherlands': 'NLD',
    'kingdom of tonga': 'TON',
    'kir': 'KIR',
    'kiribati': 'KIR',
    'km': 'COM',
    'kn': 'KNA',
    'kna': 'KNA',
    'komoorid': 'COM',
    'kongo dv': 'COD',
    'kongo vabariik': 'COG',
    'kookossaared': 'CCK',
    'kor': 'KOR',
    "korea, democratic people's republic of": 'PRK',
    'korea, republic of': 'KOR',
    'korgozstan': 'KGZ',
    'kosovo': 'XKX',
    'kp': 'PRK',
    'kr': 'KOR',
    'kreeka': 'GRC',
    'kupros': 'CYP',
    'kuuba': 'CUB',
    'kuveit': 'KWT',
    'kuwait': 'KWT',
    'kw': 'KWT',
    'kwt': 'KWT',
    'ky': 'CYM',
    'kyrgyz republic': 'KGZ',
    'kyrgyzstan': 'KGZ',
    'kz': 'KAZ',
    'la': 'LAO',
    'laane-sahara': 'ESH',
    'lao': 'LAO',
    "lao people's democratic republic": 'LAO',
    'laos': 'LAO',
    'lati': 'LVA',
    'latvia': 'LVA',
    'lb': 'LBN',
    'lbn': 'LBN',
    'lbr': 'LBR',
    'lby': 'LBY',
    'lc': 'LCA',
    'lca': 'LCA',
    'lebanese republic': 'LBN',
    'lebanon': 'LBN',
    'leedu': 'LTU',
    'lesotho': 'LSO',
    'li': 'LIE',
    'libeeria': 'LBR',
    'liberia': 'LBR',
    'libya': 'LBY',
    'lie': 'LIE',
    'liechtenstein': 'LIE',
    'liibanon': 'LBN',
    'liibua': 'LBY',
    'lithuania': 'LTU',
    'lk': 'LKA',
    'lka': 'LKA',
    'louna-aafrika vabariik': 'ZAF',
    'louna-georgia ja louna-sandwichi saared': 'SGS',
    'louna-korea': 'KOR',
    'louna-sudaan': 'SSD',
    'lr': 'LBR',
    'ls': 'LSO',
    'lso': 'LSO',
    'lt': 'LTU',
    'ltu': 'LTU',
    'lu': 'LUX',
    'luksemburg': 'LUX',
    'lux': 'LUX',
    'luxembourg': 'LUX',
    'lv': 'LVA',
    'lva': 'LVA',
    'ly': 'LBY',
    'ma': 'MAR',
    'mac': 'MAC',
    'macao': 'MAC',
    'macao special administrative region of china': 'MAC',
    'macau erihalduspiirkond': 'MAC',
    'madagascar': 'MDG',
    'madagaskar': 'MDG',
    'maf': 'MAF',
    'malaisia': 'MYS',
    'malawi': 'MWI',
    'malaysia': 'MYS',
    'maldiivid': 'MDV',
    'maldives': 'MDV',
    'mali': 'MLI',
    'malta': 'MLT',
    'mani saar': 'IMN',
    'mar': 'MAR',
    'maroko': 'MAR',
    'marshall islands': 'MHL',
    'marshalli saared': 'MHL',
    'martinique': 'MTQ',
    'mauritaania': 'MRT',
    'mauritania': 'MRT',
    'mauritius': 'MUS',
    'mayotte': 'MYT',
    'mc': 'MCO',
    'mco': 'MCO',
    'md': 'MDA',
    'mda': 'MDA',
    'mdg': 'MDG',
    'mdv': 'MDV',
    'me': 'MNE',
    'mehhiko': 'MEX',
    'mex': 'MEX',
    'mexico': 'MEX',
    'mf': 'MAF',
    'mg': 'MDG',
    'mh': 'MHL',
    'mhl': 'MHL',
    'micronesia, federated states of': 'FSM',
    'mikroneesia': 'FSM',
    'mk': 'MKD',
    'mkd': 'MKD',
    'ml': 'MLI',
    'mli': 'MLI',
    'mlt': 'MLT',
    'mm': 'MMR',
    'mmr': 'MMR',
    'mn': 'MNG',
    'mne': 'MNE',
    'mng': 'MNG',
    'mnp': 'MNP',
    'mo': 'MAC',
    'moldova': 'MDA',
    'moldova, republic of': 'MDA',
    'monaco': 'MCO',
    'mongolia': 'MNG',
    'mongoolia': 'MNG',
    'montenegro': 'MNE',
    'montserrat': 'MSR',
    'morocco': 'MAR',
    'mosambiik': 'MOZ',
    'moz': 'MOZ',
    'mozambique': 'MOZ',
    'mp': 'MNP',
    'mq': 'MTQ',
    'mr': 'MRT',
    'mrt': 'MRT',
    'ms': 'MSR',
    'msr': 'MSR',
    'mt': 'MLT',
    'mtq': 'MTQ',
    'mu': 'MUS',
    'mus': 'MUS',
    'mv': 'MDV',
    'mw': 'MWI',
    'mwi': 'MWI',
    'mx': 'MEX',
    'my': 'MYS',
    'myanmar': 'MMR',
    'myanmar (birma)': 'MMR',
    'mys': 'MYS',
    'myt': 'MYT',
    'mz': 'MOZ',
    'na': 'NAM',
    'nam': 'NAM',
    'namibia': 'NAM',
    'namiibia': 'NAM',
    'nauru': 'NRU',
    'nc': 'NCL',
    'ncl': 'NCL',
    'ne': 'NER',
    'nepal': 'NPL',
    'ner': 'NER',
    'netherlands': 'NLD',
    'new caledonia': 'NCL',
    'new zealand': 'NZL',
    'nf': 'NFK',
    'nfk': 'NFK',
    'ng': 'NGA',
    'nga': 'NGA',
    'ni': 'NIC',
    'nic': 'NIC',
    'nicaragua': 'NIC',
    'nigeeria': 'NGA',
    'niger': 'NER',
    'nigeria': 'NGA',
    'niu': 'NIU',
    'niue': 'NIU',
    'nl': 'NLD',
    'nld': 'NLD',
    'no': 'NOR',
    'nor': 'NOR',
    'norfolk': 'NFK',
    'norfolk island': 'NFK',
    'norra': 'NOR',
    'north macedonia': 'MKD',
    'northern mariana islands': 'MNP',
    'norway': 'NOR',
    'np': 'NPL',
    'npl': 'NPL',
    'nr': 'NRU',
    'nru': 'NRU',
    'nu': 'NIU',
    'nz': 'NZL',
    'nzl': 'NZL',
    'om': 'OMN',
    'omaan': 'OMN',
    'oman': 'OMN',
    'omn': 'OMN',
    'pa': 'PAN',
    'paapua uus-guinea': 'PNG',
    'pak': 'PAK',
    'pakistan': 'PAK',
    'palau': 'PLW',
    'palestiina': 'PSE',
    'palestiina alad': 'PSE',
    'palestine, state of': 'PSE',
    'pan': 'PAN',
    'panama': 'PAN',
    'papua new guinea': 'PNG',
    'paraguay': 'PRY',
    'pcn': 'PCN',
    'pe': 'PER',
    "people's democratic republic of algeria": 'DZA',
    "people's republic of bangladesh": 'BGD',
    "people's republic of china": 'CHN',
    'per': 'PER',
    'peru': 'PER',
    'peruu': 'PER',
    'pf': 'PYF',
    'pg': 'PNG',
    'ph': 'PHL',
    'philippines': 'PHL',
    'phl': 'PHL',
    'pitcairn': 'PCN',
    'pitcairni saared': 'PCN',
    'pk': 'PAK',
    'pl': 'POL',
    'plurinational state of bolivia': 'BOL',
    'plw': 'PLW',
    'pm': 'SPM',
    'pn': 'PCN',
    'png': 'PNG',
    'pohja-korea': 'PRK',
    'pohja-makedoonia': 'MKD',
    'pohja-mariaanid': 'MNP',
    'pol': 'POL',
    'poland': 'POL',
    'poola': 'POL',
    'portugal': 'PRT',
    'portuguese republic': 'PRT',
    'pr': 'PRI',
    'prantsuse guajaana': 'GUF',
    'prantsuse lounaalad': 'ATF',
    'prantsuse poluneesia': 'PYF',
    'prantsusmaa': 'FRA',
    'pri': 'PRI',
    'principality of andorra': 'AND',
    'principality of liechtenstein': 'LIE',
    'principality of monaco': 'MCO',
    'prk': 'PRK',
    'prt': 'PRT',
    'pry': 'PRY',
    'ps': 'PSE',
    'pse': 'PSE',
    'pt': 'PRT',
    'puerto rico': 'PRI',
    'pw': 'PLW',
    'py': 'PRY',
    'pyf': 'PYF',
    'qa': 'QAT',
    'qat': 'QAT',
    'qatar': 'QAT',
    're': 'REU',
    'republic of albania': 'ALB',
    'republic of angola': 'AGO',
    'republic of armenia': 'ARM',
    'republic of austria': 'AUT',
    'republic of azerbaijan': 'AZE',
    'republic of belarus': 'BLR',
    'republic of benin': 'BEN',
    'republic of bosnia and herzegovina': 'BIH',
    'republic of botswana': 'BWA',
    'republic of bulgaria': 'BGR',
    'republic of burundi': 'BDI',
    'republic of cabo verde': 'CPV',
    'republic of cameroon': 'CMR',
    'republic of chad': 'TCD',
    'republic of chile': 'CHL',
    'republic of colombia': 'COL',
    'republic of costa rica': 'CRI',
    "republic of cote d'ivoire": 'CIV',
    'republic of croatia': 'HRV',
    'republic of cuba': 'CUB',
    'republic of cyprus': 'CYP',
    'republic of djibouti': 'DJI',
    'republic of ecuador': 'ECU',
    'republic of el salvador': 'SLV',
    'republic of equatorial guinea': 'GNQ',
    'republic of estonia': 'EST',
    'republic of fiji': 'FJI',
    'republic of finland': 'FIN',
    'republic of ghana': 'GHA',
    'republic of guatemala': 'GTM',
    'republic of guinea': 'GIN',
    'republic of guinea-bissau': 'GNB',
    'republic of guyana': 'GUY',
    'republic of haiti': 'HTI',
    'republic of honduras': 'HND',
    'republic of iceland': 'ISL',
    'republic of india': 'IND',
    'republic of indonesia': 'IDN',
    'republic of iraq': 'IRQ',
    'republic of kazakhstan': 'KAZ',
    'republic of kenya': 'KEN',
    'republic of kiribati': 'KIR',
    'republic of latvia': 'LVA',
    'republic of liberia': 'LBR',
    'republic of lithuania': 'LTU',
    'republic of madagascar': 'MDG',
    'republic of malawi': 'MWI',
    'republic of maldives': 'MDV',
    'republic of mali': 'MLI',
    'republic of malta': 'MLT',
    'republic of mauritius': 'MUS',
    'republic of moldova': 'MDA',
    'republic of mozambique': 'MOZ',
    'republic of myanmar': 'MMR',
    'republic of namibia': 'NAM',
    'republic of nauru': 'NRU',
    'republic of nicaragua': 'NIC',
    'republic of north macedonia': 'MKD',
    'republic of palau': 'PLW',
    'republic of panama': 'PAN',
    'republic of paraguay': 'PRY',
    'republic of peru': 'PER',
    'republic of poland': 'POL',
    'republic of san marino': 'SMR',
    'republic of senegal': 'SEN',
    'republic of serbia': 'SRB',
    'republic of seychelles': 'SYC',
    'republic of sierra leone': 'SLE',
    'republic of singapore': 'SGP',
    'republic of slovenia': 'SVN',
    'republic of south africa': 'ZAF',
    'republic of south sudan': 'SSD',
    'republic of suriname': 'SUR',
    'republic of tajikistan': 'TJK',
    'republic of the congo': 'COG',
    'republic of the gambia': 'GMB',
    'republic of the marshall islands': 'MHL',
    'republic of the niger': 'NER',
    'republic of the philippines': 'PHL',
    'republic of the sudan': 'SDN',
    'republic of trinidad and tobago': 'TTO',
    'republic of tunisia': 'TUN',
    'republic of turkiye': 'TUR',
    'republic of uganda': 'UGA',
    'republic of uzbekistan': 'UZB',
    'republic of vanuatu': 'VUT',
    'republic of yemen': 'YEM',
    'republic of zambia': 'ZMB',
    'republic of zimbabwe': 'ZWE',
    'reu': 'REU',
    'reunion': 'REU',
    'ro': 'ROU',
    'roheneemesaared': 'CPV',
    'romania': 'ROU',
    'rootsi': 'SWE',
    'rou': 'ROU',
    'rs': 'SRB',
    'ru': 'RUS',
    'rumeenia': 'ROU',
    'rus': 'RUS',
    'russian federation': 'RUS',
    'rw': 'RWA',
    'rwa': 'RWA',
    'rwanda': 'RWA',
    'rwandese republic': 'RWA',
    'sa': 'SAU',
    'saalomoni saared': 'SLB',
    'saint barthelemy': 'BLM',
    'saint helena': 'SHN',
    'saint helena, ascension and tristan da cunha': 'SHN',
    'saint kitts and nevis': 'KNA',
    'saint kitts ja nevis': 'KNA',
    'saint lucia': 'LCA',
    'saint martin (french part)': 'MAF',
    'saint pierre and miquelon': 'SPM',
    'saint vincent and the grenadines': 'VCT',
    'saint vincent ja grenadiinid': 'VCT',
    'saint-barthelemy': 'BLM',
    'saint-martin': 'MAF',
    'saint-pierre ja miquelon': 'SPM',
    'saksamaa': 'DEU',
    'sambia': 'ZMB',
    'samoa': 'WSM',
    'san marino': 'SMR',
    'sao tome and principe': 'STP',
    'sao tome ja principe': 'STP',
    'sau': 'SAU',
    'saudi araabia': 'SAU',
    'saudi arabia': 'SAU',
    'sb': 'SLB',
    'sc': 'SYC',
    'sd': 'SDN',
    'sdn': 'SDN',
    'se': 'SWE',
    'seisellid': 'SYC',
    'sen': 'SEN',
    'senegal': 'SEN',
    'serbia': 'SRB',
    'seychelles': 'SYC',
    'sg': 'SGP',
    'sgp': 'SGP',
    'sgs': 'SGS',
    'sh': 'SHN',
    'shn': 'SHN',
    'si': 'SVN',
    'sierra leone': 'SLE',
    'singapore': 'SGP',
    'singapur': 'SGP',
    'sint maarten': 'SXM',
    'sint maarten (dutch part)': 'SXM',
    'sj': 'SJM',
    'sjm': 'SJM',
    'sk': 'SVK',
    'sl': 'SLE',
    'slb': 'SLB',
    'sle': 'SLE',
    'slovak republic': 'SVK',
    'slovakia': 'SVK',
    'slovakkia': 'SVK',
    'sloveenia': 'SVN',
    'slovenia': 'SVN',
    'slv': 'SLV',
    'sm': 'SMR',
    'smr': 'SMR',
    'sn': 'SEN',
    'so': 'SOM',
    'socialist republic of viet nam': 'VNM',
    'solomon islands': 'SLB',
    'som': 'SOM',
    'somaalia': 'SOM',
    'somalia': 'SOM',
    'soome': 'FIN',
    'south africa': 'ZAF',
    'south georgia and the south sandwich islands': 'SGS',
    'south sudan': 'SSD',
    'spain': 'ESP',
    'spm': 'SPM',
    'sr': 'SUR',
    'srb': 'SRB',
    'sri lanka': 'LKA',
    'ss': 'SSD',
    'ssd': 'SSD',
    'st': 'STP',
    'state of israel': 'ISR',
    'state of kuwait': 'KWT',
    'state of qatar': 'QAT',
    'stp': 'STP',
    'sudaan': 'SDN',
    'sudan': 'SDN',
    'sultanate of oman': 'OMN',
    'sur': 'SUR',
    'suriname': 'SUR',
    'suurbritannia': 'GBR',
    'suuria': 'SYR',
    'sv': 'SLV',
    'svaasimaa': 'SWZ',
    'svalbard and jan mayen': 'SJM',
    'svalbard ja jan mayen': 'SJM',
    'sveits': 'CHE',
    'svk': 'SVK',
    'svn': 'SVN',
    'swe': 'SWE',
    'sweden': 'SWE',
    'swiss confederation': 'CHE',
    'switzerland': 'CHE',
    'swz': 'SWZ',
    'sx': 'SXM',
    'sxm': 'SXM',
    'sy': 'SYR',
    'syc': 'SYC',
    'syr': 'SYR',
    'syrian arab republic': 'SYR',
    'sz': 'SWZ',
    'taani': 'DNK',
    'tadzikistan': 'TJK',
    'tai': 'THA',
    'taiwan': 'TWN',
    'taiwan, province of china': 'TWN',
    'tajikistan': 'TJK',
    'tansaania': 'TZA',
    'tanzania, united republic of': 'TZA',
    'tc': 'TCA',
    'tca': 'TCA',
    'tcd': 'TCD',
    'td': 'TCD',
    'tf': 'ATF',
    'tg': 'TGO',
    'tgo': 'TGO',
    'th': 'THA',
    'tha': 'THA',
    'thailand': 'THA',
    'the state of eritrea': 'ERI',
    'the state of palestine': 'PSE',
    'timor-leste': 'TLS',
    'tj': 'TJK',
    'tjk': 'TJK',
    'tk': 'TKL',
    'tkl': 'TKL',
    'tkm': 'TKM',
    'tl': 'TLS',
    'tls': 'TLS',
    'tm': 'TKM',
    'tn': 'TUN',
    'to': 'TON',
    'togo': 'TGO',
    'togolese republic': 'TGO',
    'tokelau': 'TKL',
    'ton': 'TON',
    'tonga': 'TON',
    'tr': 'TUR',
    'trinidad and tobago': 'TTO',
    'trinidad ja tobago': 'TTO',
    'tsaad': 'TCD',
    'tsehhi': 'CZE',
    'tsiili': 'CHL',
    'tt': 'TTO',
    'tto': 'TTO',
    'tun': 'TUN',
    'tuneesia': 'TUN',
    'tunisia': 'TUN',
    'tur': 'TUR',
    'turgi': 'TUR',
    'turkiye': 'TUR',
    'turkmenistan': 'TKM',
    'turks and caicos islands': 'TCA',
    'turks ja caicos': 'TCA',
    'tuv': 'TUV',
    'tuvalu': 'TUV',
    'tv': 'TUV',
    'tw': 'TWN',
    'twn': 'TWN',
    'tz': 'TZA',
    'tza': 'TZA',
    'u.a.e.': 'ARE',
    'ua': 'UKR',
    'ug': 'UGA',
    'uga': 'UGA',
    'uganda': 'UGA',
    'uhendkuningriik': 'GBR',
    'uhendriigid': 'USA',
    'uhendriikide hajasaared': 'UMI',
    'ukr': 'UKR',
    'ukraina': 'UKR',
    'ukraine': 'UKR',
    'um': 'UMI',
    'umi': 'UMI',
    'ungari': 'HUN',
    'union of the comoros': 'COM',
    'united arab emirates': 'ARE',
    'united kingdom': 'GBR',
    'united kingdom of great britain and northern ireland': 'GBR',
    'united mexican states': 'MEX',
    'united republic of tanzania': 'TZA',
    'united states': 'USA',
    'united states minor outlying islands': 'UMI',
    'united states of america': 'USA',
    'uruguay': 'URY',
    'ury': 'URY',
    'us': 'USA',
    'usa': 'USA',
    'usa neitsisaared': 'VIR',
    'usbekistan': 'UZB',
    'uus-kaledoonia': 'NCL',
    'uus-meremaa': 'NZL',
    'uy': 'URY',
    'uz': 'UZB',
    'uzb': 'UZB',
    'uzbekistan': 'UZB',
    'va': 'VAT',
    'valgevene': 'BLR',
    'vanuatu': 'VUT',
    'vat': 'VAT',
    'vatikan': 'VAT',
    'vc': 'VCT',
    'vct': 'VCT',
    've': 'VEN',
    'ven': 'VEN',
    'vene foderatsioon': 'RUS',
    'venemaa': 'RUS',
    'venezuela': 'VEN',
    'venezuela, bolivarian republic of': 'VEN',
    'vg': 'VGB',
    'vgb': 'VGB',
    'vi': 'VIR',
    'viet nam': 'VNM',
    'vietnam': 'VNM',
    'vir': 'VIR',
    'virgin islands of the united states': 'VIR',
    'virgin islands, british': 'VGB',
    'virgin islands, u.s.': 'VIR',
    'vn': 'VNM',
    'vnm': 'VNM',
    'vu': 'VUT',
    'vut': 'VUT',
    'wallis and futuna': 'WLF',
    'wallis ja futuna': 'WLF',
    'western sahara': 'ESH',
    'wf': 'WLF',
    'wlf': 'WLF',
    'ws': 'WSM',
    'wsm': 'WSM',
    'ye': 'YEM',
    'yem': 'YEM',
    'yemen': 'YEM',
    'yt': 'MYT',
    'za': 'ZAF',
    'zaf': 'ZAF',
    'zambia': 'ZMB',
    'zimbabwe': 'ZWE',
    'zm': 'ZMB',
    'zmb': 'ZMB',
    'zw': 'ZWE',
    'zwe': 'ZWE',
}

# PPA algandmetes kasutatakse sageli riikide ametlikke täisnimesid.
# Võtame esmalt täpse vastenduse ning alles siis proovime üldnimetust.
PPA_RIIGI_ALIASED = {
    "eesti vabariik": "EST",
    "vene fod eratsioon": "RUS",
    "venemaa foderatsioon": "RUS",
    "belgia kuningriik": "BEL",
    "soome vabariik": "FIN",
    "lati vabariik": "LVA",
    "leedu vabariik": "LTU",
    "poola vabariik": "POL",
    "saksamaa liitvabariik": "DEU",
    "prantsuse vabariik": "FRA",
    "itaalia vabariik": "ITA",
    "austria vabariik": "AUT",
    "rootsi kuningriik": "SWE",
    "norra kuningriik": "NOR",
    "taani kuningriik": "DNK",
    "hispaania kuningriik": "ESP",
    "madalmaade kuningriik": "NLD",
    "hollandi kuningriik": "NLD",
    "uhendkuningriik": "GBR",
    "hiina rahvavabariik": "CHN",
    "india vabariik": "IND",
    "korea vabariik": "KOR",
    "korea rahvademokraatlik vabariik": "PRK",
    "valgevene vabariik": "BLR",
    "ukraina": "UKR",
    "ameerika uhendriigid": "USA",
    "kanada": "CAN",
    "jaapani riik": "JPN",
    "turgi vabariik": "TUR",
    "tsehhi vabariik": "CZE",
    "slovaki vabariik": "SVK",
    "ungari": "HUN",
    "portugali vabariik": "PRT",
    "kreeka vabariik": "GRC",
    "iiri vabariik": "IRL",
    "sveitsi konfoederatsioon": "CHE",
    "luksemburgi suurhertsogiriik": "LUX",
    "rumeenia": "ROU",
    "bulgaaria vabariik": "BGR",
    "moldova vabariik": "MDA",
    "kasahstani vabariik": "KAZ",
    "usbekistani vabariik": "UZB",
    "aserbaidzaani vabariik": "AZE",
    "armeenia vabariik": "ARM",
    "gruusia": "GEO",
    "iisl endi vabariik": "ISL",
}

def normaliseeri_riik(vaartus):
    return " ".join("".join(
        c for c in unicodedata.normalize("NFKD", str(vaartus).casefold())
        if not unicodedata.combining(c)
    ).split())


# PPA ametlike kodakondsusnimetuste täiendavad vastendused

PPA_TAIENDAVAD_RIIGID = {
    "Suurbritannia ja Põhja-Iiri Ühendkuningriik": "GBR",
    "Iisraeli Riik": "ISR",
    "Madalmaade Kuningriik ~ Hollandi Kuningriik": "NLD",
    "Küprose Vabariik": "CYP",
    "Kõrgõstan (Kirgiisi Vabariik)": "KGZ",
    "Šveitsi Konföderatsioon": "CHE",
    "Filipiini Vabariik": "PHL",
    "Mehhiko Ühendriigid": "MEX",
    "Pakistani Islamivabariik": "PAK",
    "Iraani Islamivabariik": "IRN",
    "Tadžikistani Vabariik": "TJK",
    "Egiptuse Araabia Vabariik": "EGY",
    "Singapuri Vabariik": "SGP",
    "Bangladeshi Rahvavabariik": "BGD",
    "Iraagi Vabariik": "IRQ",
    "Jordaania Haɩmiidi Kuningriik": "JOR",
    "Sri Lanka Demokraatlik Sotsialistlik Vabariik": "LKA",
    "Saint Kitts ja Nevise Föderatsioon": "KNA",
    "Vietnami Sotsialistlik Vabariik": "VNM",
    "Liibanoni Vabariik": "LBN",
    "Süüria Araabia Vabariik": "SYR",
    "Myanmari Liidu Vabariik": "MMR",
    "Islandi Vabariik": "ISL",
    "Nepali Demokraatlik Liitvabariik": "NPL",
    "Kameruni Vabariik": "CMR",
    "Afganistani Islamivabariik": "AFG",
    "Venezuela Bolivari Vabariik": "VEN",
    "Uruguay Idavabariik": "URY",
    "Kuveidi Riik": "KWT",
    "Omaani Sultaniriik": "OMN",
}

PPA_RIIGI_ALIASED.update({
    normaliseeri_riik(nimi): iso3
    for nimi, iso3 in PPA_TAIENDAVAD_RIIGID.items()
})


PPA_UUED_RIIGID = {
    "Alžeeria Demokraatlik Rahvavabariik": "DZA",
    "Ecuadori Vabariik": "ECU",
    "El Salvadori Vabariik": "SLV",
    "Mauritiuse Vabariik": "MUS",
    "Dominica Ühendus": "DMA",
    "Hondurase Vabariik": "HND",
    "Bahreini Kuningriik": "BHR",
    "Jeemeni Vabariik": "YEM",
    "Tansaania Ühendvabariik": "TZA",
    "Boliivia Paljurahvuseline Riik": "BOL",
    "Sudaani Vabariik": "SDN",
    "Trinidadi ja Tobago Vabariik": "TTO",
    "Etioopia Demokraatlik Liitvabariik": "ETH",
    "Andorra Vürstiriik": "AND",
    "Senegali Vabariik": "SEN",
    "Cote d'Ivoire'i Vabariik": "CIV",
    "Mosambiigi Vabariik": "MOZ",
    "Kongo Demokraatlik Vabariik": "COD",
    "Katari Riik": "QAT",
    "Liibüa Riik": "LBY",
    "Benini Vabariik": "BEN",
    "Suur Liibüa Araabia Sotsialistlik Rahvad١mahirija": "LBY",
    "Bhutani Kuningriik": "BTN",
    "Brunei Darussalami Riik": "BRN",
    "Seišelli Vabariik": "SYC",
    "Maldiivi Vabariik": "MDV",
    "Madagaskari Vabariik": "MDG",
    "Liechtensteini Vürstiriik": "LIE",
    "Laose Demokraatlik Rahvavabariik": "LAO",
    "Monaco Vürstiriik": "MCO",
    "Mauritaania Islamivabariik": "MRT",
    "Gaboni Vabariik": "GAB",
    "Eritrea Riik": "ERI",
    "Bahama Ühendus": "BHS",
    "Nigeri Vabariik": "NER",
}

PPA_RIIGI_ALIASED.update({
    normaliseeri_riik(nimi): iso3
    for nimi, iso3 in PPA_UUED_RIIGID.items()
})


PPA_ERIJUHUD = {
    "Taiwan, Hiina provints (CHN)": "TWN",
    "Hongkong (Hiina RV)": "HKG",
    "Palestiina okupeeritud ala": "PSE",
    "British Nationals (Overseas)": "GBR",
    "British subjects": "GBR",
    "British Protected Persons": "GBR",
}

PPA_RIIGI_ALIASED.update({
    normaliseeri_riik(nimi): iso3
    for nimi, iso3 in PPA_ERIJUHUD.items()
})

def leia_iso3(kodakondsus):
    nimi = normaliseeri_riik(kodakondsus)
    vaste = PPA_RIIGI_ALIASED.get(nimi) or KODAKONDSUS_ISO3.get(nimi)
    if vaste:
        return vaste
    # Ainult kindlate üldiste riigivormide korral eemaldame lõpus tiitli.
    # Erandid, nagu Korea Vabariik, on ülal eraldi määratud.
    for lopp in (" vabariik", " kuningriik", " liitvabariik",
                 " suurhertsogiriik", " foderatsioon"):
        if nimi.endswith(lopp):
            alus = nimi[:-len(lopp)]
            if alus in {"korea", "kong o", "kongo", "dominikaani", "kesk aafrika"}:
                return None
            return KODAKONDSUS_ISO3.get(alus)
    return None

st.divider()
st.subheader("🌍 Kodakondsuste maailmakaart")

kaardi_suund = st.segmented_control(
    "Liikumissuund",
    options=["Sisenemised", "Väljumised"],
    default="Sisenemised",
    key="sv_kaardi_suund",
)

kaardi_ulatus = st.segmented_control(
    "Kuvatavad riigid",
    options=["TOP 20", "Kõik kaardistatavad"],
    default="TOP 20",
    key="sv_kaardi_ulatus",
)

kaardi_andmed = filtreeritud.loc[
    filtreeritud["Suund"] == kaardi_suund
]

kodakondsuste_summa = (
    kaardi_andmed.groupby("Kodakondsus", dropna=False)["Piiriületuste arv"]
    .sum().sort_values(ascending=False)
)

# Nimetaja on kogu valitud suuna piiriületuste arv, mitte TOP20 summa.
kaardi_kokku = float(kaardi_andmed["Piiriületuste arv"].sum())
kaardi_tabel = kodakondsuste_summa.reset_index()
kaardi_tabel["ISO3"] = kaardi_tabel["Kodakondsus"].map(
    leia_iso3
)

# Ühte ISO-riiki koonduvad võimalikud eri nimekujud.
kaardi_riigid = (
    kaardi_tabel.dropna(subset=["ISO3"])
    .groupby("ISO3", as_index=False)
    .agg({"Piiriületuste arv": "sum", "Kodakondsus": "first"})
    .sort_values("Piiriületuste arv", ascending=False)
)
if kaardi_ulatus == "TOP 20":
    kaardi_riigid = kaardi_riigid.head(20).copy()

if kaardi_kokku == 0 or kaardi_riigid.empty:
    st.info("Valitud filtritega kaardile kantavaid kodakondsusi ei ole.")
else:
    kaardi_riigid["Osakaal"] = (
        100 * kaardi_riigid["Piiriületuste arv"] / kaardi_kokku
    )
    kaardi_riigid["Arvutekst"] = kaardi_riigid["Piiriületuste arv"].map(
        lambda x: f"{int(x):,}".replace(",", " ")
    )
    varviskaala = (
        [[0.0, "#e6f4e8"], [0.35, "#8bd1a1"], [1.0, "#08753b"]]
        if kaardi_suund == "Sisenemised" else
        [[0.0, "#e4f1fb"], [0.35, "#91c8ec"], [1.0, "#125e9c"]]
    )
    joonis_kaart = go.Figure(go.Choropleth(
        locations=kaardi_riigid["ISO3"],
        z=kaardi_riigid["Osakaal"],
        locationmode="ISO-3",
        text=kaardi_riigid["Kodakondsus"],
        customdata=kaardi_riigid[["Arvutekst", "Osakaal"]].to_numpy(),
        hovertemplate=(
            "<b>%{text}</b><br>Piiriületusi: %{customdata[0]}"
            "<br>Osakaal valitud suunast: %{customdata[1]:.2f}%<extra></extra>"
        ),
        colorscale=varviskaala,
        zmin=0,
        marker_line_color="white",
        marker_line_width=0.3,
        colorbar=dict(title="Osakaal %", thickness=13, len=0.6),
    ))
    joonis_kaart.update_geos(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#bfc9d3",
        showland=True,
        landcolor="#e9edf1",
        showcountries=True,
        countrycolor="#ffffff",
        bgcolor="rgba(0,0,0,0)",
    )
    joonis_kaart.update_layout(
        margin=dict(l=5, r=5, t=10, b=5),
        height=540,
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(joonis_kaart, width="stretch")

    kaardistamata = kaardi_tabel.loc[
        kaardi_tabel["ISO3"].isna(), "Piiriületuste arv"
    ].sum()
    st.caption(
        f"Kaardil kuvatakse {kaardi_ulatus.lower()} riigid. "
        f"Osakaalu nimetaja on kõik {kaardi_suund.lower()} valitud filtritega. "
        f"Kaardistamata kodakondsuste piiriületusi: "
        f"{int(kaardistamata):,}. ".replace(",", " ")
        + "Kodakondsus ei tähenda tingimata päritolu- ega elukohariiki. "
        + ("Hallid riigid ei kuulu kuvatava TOP 20 hulka." if kaardi_ulatus == "TOP 20" else "Hallid riigid on kaardistamata või ilma valitud andmeteta.")
    )
    if kaardistamata:
        with st.expander("Kodakondsused, mida ei õnnestunud kaardile paigutada"):
            puuduvad = kaardi_tabel.loc[kaardi_tabel["ISO3"].isna(),
                ["Kodakondsus", "Piiriületuste arv"]].sort_values(
                "Piiriületuste arv", ascending=False)
            st.dataframe(puuduvad, hide_index=True, width="stretch")
            st.caption("Esimesed read näitavad kõige suurema mõjuga puuduvaid vastendusi; nende põhjal saab sõnastikku täiendada.")

# ------------------------------------------
# C. SISENEMISTE JA VÄLJUMISTE DÜNAAMIKA
# ------------------------------------------

st.divider()
st.subheader("Sisenemiste ja väljumiste dünaamika")

kuupohine = (
    filtreeritud.groupby(["Kuupäev", "Suund"])["Piiriületuste arv"]
    .sum().unstack("Suund", fill_value=0).sort_index()
)
for suund in ("Sisenemised", "Väljumised"):
    if suund not in kuupohine.columns:
        kuupohine[suund] = 0



fig_kuud = go.Figure()

for suund, varvus in [
    ("Sisenemised", "#178939"),
    ("Väljumised", "#2878B5")
]:

    # Täielike kuude joon.
    # Osalise kuu väärtus jääb eraldi markerina alles.
    joone_vaartused = kuupohine[suund].astype(float).copy()

    if suund in osalised_kuud:
        osaline_kuu = pd.Timestamp(
            osalised_kuud[suund]["kuu"]
        )

        if osaline_kuu in joone_vaartused.index:
            joone_vaartused.loc[osaline_kuu] = float("nan")

    fig_kuud.add_trace(
        go.Scatter(
            x=kuupohine.index,
            y=joone_vaartused,
            mode="lines",
            name=suund,
            line=dict(color=varvus, width=2.5),
            connectgaps=False,
        )
    )

    # Osalise kuu tegelik punkt
    if suund in osalised_kuud:

        info = osalised_kuud[suund]
        kuu = pd.Timestamp(info["kuu"])
        viimane_paev = pd.Timestamp(info["viimane_paev"])

        if kuu in kuupohine.index:

            maht = kuupohine.loc[kuu, suund]

            fig_kuud.add_trace(
                go.Scatter(
                    x=[kuu],
                    y=[maht],
                    mode="markers",
                    marker=dict(
                        color=varvus,
                        size=13,
                        symbol="circle-open",
                        line=dict(width=3, color=varvus)
                    ),
                    name=f"{suund} – osaline kuu",
                    showlegend=False,
                    hovertemplate=(
                        "<b>Osaline kuu – tegelikud andmed</b>"
                        f"<br>{suund}"
                        f"<br>Andmed kuni {viimane_paev:%d.%m.%Y}"
                        "<br>Piiriületusi: %{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )

            fig_kuud.add_annotation(
                x=kuu,
                y=maht,
                text=f"Osaline kuu<br>kuni {viimane_paev:%d.%m.%Y}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-55 if suund == "Sisenemised" else 55,
                font=dict(size=10, color=varvus),
                bgcolor="rgba(255,255,255,0.92)",
                bordercolor=varvus,
                borderwidth=1
            )



# ------------------------------------------
# A7/A9 PROGNOOSID DÜNAAMIKAGRAAFIKUL
# ------------------------------------------

if naita_prognoosi:

    for suund, varvus in [
        ("Sisenemised", "#178939"),
        ("Väljumised", "#2878B5")
    ]:

        p = (
            aktiivne_prognoos[
                aktiivne_prognoos["Suund"] == suund
            ]
            .groupby("Kuupäev", as_index=False)["Prognoos"]
            .sum()
            .sort_values("Kuupäev")
        )

        if not p.empty:

            fig_kuud.add_trace(
                go.Scatter(
                    x=p["Kuupäev"],
                    y=p["Prognoos"],
                    mode="lines+markers",
                    name=f"{suund} – prognoos {valitud_mudel}",
                    line=dict(
                        color=varvus,
                        width=2.5,
                        dash="dash"
                    ),
                    marker=dict(size=5),
                    hovertemplate=(
                        "%{x|%m.%Y}<br>"
                        "Prognoos: %{y:,.0f}"
                        "<extra></extra>"
                    )
                )
            )
# --- PPA SÜNDMUSTE TAUSTAKIHT (v1) ---
# Need kuupäevad on sündmuste käsitsi kontrollitud metaandmed,
# mitte Parquet-failist automaatselt laaditud tunnused.
# Sündmuse esinemine ajajoonel ei tõenda põhjuslikku mõju.

sv_sundmused = [
    # 2017–2020: kontrollitud sündmused. NaT ei võrdu "jätkuv".
    # Tähtajatu viisavabadus ja leevendused = algusmärgis;
    # täpselt piiritletud kontroll või peatatud e-viisa = ajavahemik.
    dict(nimi="Gruusia biomeetrilise passi viisavabadus", algus="2017-03-28", lopp=None,
         punktid=(), tyyp=None, kodakondsused=("Gruusia", "GEO"),
         kirjeldus="Viisavabadus jätkub tavapasside omanikele; erandid võivad kehtida muudele passiliikidele"),
    dict(nimi="Ukraina biomeetrilise passi viisavabadus", algus="2017-06-11", lopp=None,
         punktid=(), tyyp=None, kodakondsused=("Ukraina", "UKR"),
         kirjeldus="Viisavabadus on jätkuv õiguslik muudatus; näidatakse ainult algust"),
    dict(nimi="Peterburi ja Leningradi oblasti e-viisa süsteem", algus="2019-10-01", lopp="2020-03-18",
         punktid=("Narva", "Koidula", "Luhamaa", "Saatse"), tyyp="Maismaapiir",
         kirjeldus="Venemaa piirkondlik e-viisa; e-viisade väljastamine peatati 18.03.2020. See ei ole uue üleriigilise e-viisasüsteemi algus"),
    dict(nimi="COVID-19: ajutine kontroll maismaapiiril", algus="2020-03-17", lopp="2020-05-14",
         punktid=(), tyyp="Maismaapiir",
         kirjeldus="Ajutise piirikontrolli periood maismaapiiril. Muud reisipiirangud ei lõppenud selle kuupäevaga"),
    dict(nimi="COVID-19: ajutine kontroll õhu- ja merepiiril", algus="2020-03-17", lopp="2020-06-16",
         punktid=(), tyyp=None, tyyp_valikud=("Õhupiir", "Merepiir"),
         kirjeldus="Ajutise piirikontrolli periood õhu- ja merepiiril. Muud reisipiirangud kehtisid osaliselt edasi"),
    dict(nimi="Balti riikide vahelise liikumise leevendamine", algus="2020-05-15", lopp=None,
         punktid=("Ikla", "Valga", "Lilli", "Mõisaküla"), tyyp="Maismaapiir",
         kirjeldus="Balti mulli algus; tingimused muutusid hiljem (sh 2020. aasta septembris). Algusmärgis, mitte jätkuv vahemik"),
    dict(nimi="Euroopa riikidest Eestisse reisimise leevendamine", algus="2020-06-01", lopp=None,
         punktid=(), tyyp=None,
         kirjeldus="Leevenduste algus; tingimusi muudeti korduvalt, ühtset lõppkuupäeva ei ole"),
    dict(nimi="ABC-väravad Tallinnas ja Narvas", algus="2021-02-10", lopp=None,
         punktid=("Tallinna-1", "Narva-1"), tyyp=None,
         kirjeldus="Automaatse piirikontrolli väravate kasutuselevõtt"),
    dict(nimi="Ajutine Eesti–Läti piirikontroll", algus="2022-03-03", lopp="2022-05-24",
         punktid=("Ikla", "Valga-1", "Valga-2", "Valga-3"), tyyp="Maismaapiir",
         kirjeldus="Ajutine kontroll Eesti–Läti maismaapiiril"),
    dict(nimi="Saatse automaatne piirikontroll", algus="2023-04-19", lopp=None,
         punktid=("Saatse",), tyyp="Maismaapiir",
         kirjeldus="Automaatse piirikontrolli süsteemi kasutuselevõtt"),
    dict(nimi="Ivangorodi sõidukiliikluse sulgemine", algus="2024-02-01", lopp=None,
         punktid=("Narva-1",), tyyp="Maismaapiir",
         kirjeldus="Sõidukiliikluse piirang Narva–Ivangorodi suunal"),
    dict(nimi="Narva-1 lahtiolekuaja piirang", algus="2024-05-01", lopp="2026-06-14",
         punktid=("Narva-1",), tyyp="Maismaapiir",
         kirjeldus="Narva-1 piiripunkti tööaeg 7–23"),
    dict(nimi="Narva-1 ajutine täielik sulgemine", algus="2025-04-30", lopp="2025-05-02",
         punktid=("Narva-1",), tyyp="Maismaapiir",
         kirjeldus="Lühiajaline täielik sulgemine"),
    dict(nimi="Koidula ja Luhamaa öine sulgemine", algus="2026-02-24", lopp="2026-08-31",
         punktid=("Koidula", "Luhamaa"), tyyp="Maismaapiir",
         kirjeldus="Öine sulgemine, piiratud tööaeg"),
    dict(nimi="Narva-1 üleminek 12-tunnisele tööajale", algus="2026-06-15", lopp=None,
         punktid=("Narva-1",), tyyp="Maismaapiir",
         kirjeldus="Narva-1 tööaeg vähenes 12 tunnini"),
    dict(nimi="Kuressaare lennujaama ajutine sulgemine", algus="2026-08-10", lopp="2026-08-31",
         punktid=("Kuressaare-2", "Kuressaare"), tyyp="Õhupiir",
         kirjeldus="Lennujaama ajutine sulgemine"),
    dict(nimi="Piiripunktide 12-tunnine graafik", algus="2026-09-01", lopp=None,
         punktid=("Narva-1", "Koidula", "Luhamaa", "Narva raudtee", "Koidula raudtee"),
         tyyp="Maismaapiir", kirjeldus="Piiratud tööaja jätkumine määramata ajaks"),
]

sv_naita_sundmusi = st.toggle(
    "Näita ajaloolisi sündmusi", value=True, key="sv_naita_dynaamika_sundmusi",
    help="Õrnad taustaribad tähistavad sündmuste perioode, täpid üksikuid alguskuupäevi."
)

if sv_naita_sundmusi and not kuupohine.empty:
    sv_min_x = pd.Timestamp(kuupohine.index.min())
    sv_max_x = pd.Timestamp(kuupohine.index.max()) + pd.offsets.MonthEnd(1)
    sv_ymax = float(kuupohine[["Sisenemised", "Väljumised"]].max().max())
    # Kaitse tühi- ja nullmahu korral.
    sv_ymax = sv_ymax if sv_ymax > 0 else 1.0
    sv_marks_x, sv_marks_y, sv_marks_text = [], [], []
    sv_nimetused = []

    def sv_sundmus_sobib(s):
        # Kui kasutaja valis konkreetsed piiripunktid, näitame ainult neid puudutavaid sündmusi.
        # Ilma konkreetse punktivalikuta kontrollime piiripunkti tüüpi.
        if s.get("tyyp_valikud") and not any(
            t in piirityybid for t in s["tyyp_valikud"]
        ):
            return False
        if s["tyyp"] and s["tyyp"] not in piirityybid:
            return False
        sihtriigid = s.get("kodakondsused", ())
        if kodakondsused and sihtriigid:
            if not any(
                token.lower() in str(valik).lower()
                for token in sihtriigid
                for valik in kodakondsused
            ):
                return False
        if piiripunktid and s["punktid"]:
            return any(
                token.lower() in str(punkt).lower()
                for token in s["punktid"]
                for punkt in piiripunktid
            )
        return True

    for s in sv_sundmused:
        if not sv_sundmus_sobib(s):
            continue
        algus = pd.Timestamp(s["algus"])
        lopp = pd.Timestamp(s["lopp"]) if s["lopp"] else None
        # Valitud ajavahemikust täielikult väljas olevat sündmust ei näidata.
        if algus > sv_max_x or (lopp is not None and lopp < sv_min_x):
            continue
        sv_nimetused.append(s["nimi"])
        if lopp is not None:
            fig_kuud.add_vrect(
                x0=max(algus, sv_min_x), x1=min(lopp, sv_max_x),
                fillcolor="#8B97A5", opacity=0.10,
                line_width=0, layer="below"
            )
        else:
            fig_kuud.add_vline(
                x=algus, line_color="#8B97A5",
                line_dash="dot", line_width=1, opacity=0.55,
                layer="below"
            )
        # Plotly shape'idel pole hoverit; nähtavad õrnad markerid pakuvad lisainfot.
        sv_marks_x.append(min(max(algus, sv_min_x), sv_max_x))
        sv_marks_y.append(sv_ymax * 1.02)
        sv_marks_text.append(
            f"<b>{s['nimi']}</b><br>Algus: {s['algus']}"
            + (f"<br>Lõpp: {s['lopp']}" if s['lopp'] else "")
            + f"<br>{s['kirjeldus']}"
        )
    if sv_marks_x:
        fig_kuud.add_trace(go.Scatter(
            x=sv_marks_x, y=sv_marks_y, mode="markers",
            name="Sündmused", showlegend=True,
            marker=dict(symbol="diamond", size=8, color="#7D8997", opacity=0.75),
            text=sv_marks_text, hovertemplate="%{text}<extra></extra>",
            cliponaxis=False,
        ))
        fig_kuud.update_yaxes(autorange=True)
        st.caption(
            "◇ Sündmuse algus või ajalooline verstapost; hele taustriba näitab piiritletud perioodi. "
            "Liigu teemandikujulisele markerile, et näha kuupäevi ja kirjeldust. "
            "Sündmused ei tõenda põhjuslikku mõju."
        )


fig_kuud.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Piiriületuste arv",
    hovermode="x unified",
    template="plotly_white",
    height=470,
)

# X-telg vastab valitud aastatele.
# Ajaloolised sündmused ei venita enam telge.
if aastad:
    x_algus = pd.Timestamp(
        year=min(aastad), month=1, day=1
    ) - pd.Timedelta(days=15)

    x_lopp = pd.Timestamp(
        year=max(aastad), month=12, day=31
    ) + pd.Timedelta(days=15)

    fig_kuud.update_xaxes(
        type="date",
        range=[x_algus, x_lopp],
        autorange=False,
        tickformat="%b %Y",
        showgrid=True
    )


st.plotly_chart(fig_kuud, width="stretch")

# ------------------------------------------
# D. KUU / KVARTAL / NÄDALAPÄEV
# ------------------------------------------

st.divider()
st.subheader("📅 Hooajalisus ja perioodide võrdlus")

ajavaade = st.segmented_control(
    "Ajatase", ["Kuu", "Kvartal", "Nädalapäev"],
    default="Kuu", key="sv_ajavaade"
)

# Kuu filter jäetakse hooajalisuse võrdlusest välja.

# ------------------------------------------
# HOOAJALISUSE ANDMED – TEGELIKUD + PROGNOOS
# ------------------------------------------


# ------------------------------------------
# HOOAJALISUS: AINULT TÄIELIKUD TEGELIKUD KUUD
# ------------------------------------------

# Võtame kuude olemasolu kalendri aluseks,
# kuid eemaldame sellest osalised kuud.
hooaja_tais_kuud = {
    int(aasta): set(kuud_olemas)
    for aasta, kuud_olemas in saadaolevad_kuud.items()
}

for info in osalised_kuud.values():
    aasta = int(info["kuu"].year)
    kuu = int(info["kuu"].month)

    hooaja_tais_kuud.get(aasta, set()).discard(kuu)


# Kuu filter jäetakse hooajalisuse võrdlusest välja.
# Ülejäänud filtrid kehtivad.

hooaja_alus = andmed.loc[
    andmed["aasta"].isin(aastad)
    & andmed["Piiripunkti tüüp"].isin(piirityybid)
].copy()

for veerg, valitud in valikulised_filtrid.items():
    if valitud:
        hooaja_alus = hooaja_alus.loc[
            hooaja_alus[veerg].isin(valitud)
        ]


# Osalisi tegelikke kuid ei kasutata hooajalisuses
# täiskuu mahuna.
osaline_mask = pd.Series(
    False,
    index=hooaja_alus.index
)

for info in osalised_kuud.values():
    aasta = int(info["kuu"].year)
    kuu = int(info["kuu"].month)

    osaline_mask |= (
        (hooaja_alus["aasta"] == aasta)
        & (hooaja_alus["kuu"] == kuu)
    )

hooaja_alus = hooaja_alus.loc[
    ~osaline_mask
].copy()


# Ainult tegelike andmetega täielikud aastad
tais_tegelikud_aastad = sorted(
    aasta for aasta in aastad
    if hooaja_tais_kuud.get(aasta, set()) == set(range(1, 13))
)

# Prognoosid kuu- ja kvartalivaatele.
# Kasutame kogu prognoositabelit, sest hooajalisuse
# arvutamisel ei rakendata kuu filtrit.

if naita_prognoosi:

    hooaja_prognoos = prognoosid.loc[
        prognoosid["aasta"].isin(aastad)
        & prognoosid["Mudel"].eq(valitud_mudel)
        & prognoosid["Piiripunkti tüüp"].isin(piirityybid)
    ].copy()

    for veerg, valitud in valikulised_filtrid.items():
        if valitud:
            hooaja_prognoos = hooaja_prognoos.loc[
                hooaja_prognoos[veerg].isin(valitud)
            ]

    # Väldime tegelike kuude topeltarvestust
    hooaja_prognoos = hooaja_prognoos.loc[
        [
            kuu not in hooaja_tais_kuud.get(aasta, set())
            for aasta, kuu in zip(
                hooaja_prognoos["aasta"],
                hooaja_prognoos["kuu"]
            )
        ]
    ].copy()

    prognoositud_kuud = set(
        zip(
            hooaja_prognoos["aasta"],
            hooaja_prognoos["kuu"]
        )
    )

    # Kontrollime, kas kõik 12 kuud on kaetud
    # tegelike või prognoositud väärtustega.
    tais_aastad = sorted(
        aasta for aasta in aastad
        if all(
            kuu in hooaja_tais_kuud.get(aasta, set())
            or (aasta, kuu) in prognoositud_kuud
            for kuu in range(1, 13)
        )
    )

    hooaja_prognoos = hooaja_prognoos.rename(
        columns={"Prognoos": "Piiriületuste arv"}
    )

    hooaja_alus = pd.concat(
        [
            hooaja_alus,
            hooaja_prognoos
        ],
        ignore_index=True
    )

else:
    tais_aastad = tais_tegelikud_aastad

if ajavaade == "Nädalapäev" and not tais_tegelikud_aastad:
    st.info(
        "Nädalapäevade hooajalisus põhineb ainult täielikel "
        "tegelike andmetega aastatel. 2027. aasta prognoos "
        "on kuupõhine."
    )

elif ajavaade != "Nädalapäev" and not tais_aastad:
    st.info(
        "Vali vähemalt üks täielik kalendriaasta "
        "või prognoosiga kaetud aasta."
    )

elif ajavaade == "Nädalapäev":
    tais_aastad = tais_tegelikud_aastad
    sis_paev, val_paev = lae_paevased_andmed()

    # Kuu filter jääb välja nagu teistes hooajalisuse vaadetes.
    # Nullpäevad sisalduvad nimetajas kalendri alusel.
    suundade_paevad = []
    for suund, alus, arv_veerg in [
        ("Sisenemised", sis_paev, "Piiriületajate arv"),
        ("Väljumised", val_paev, "Piirilt lahkujate arv"),
    ]:
        paeva_mask = (
            alus["aasta"].isin(tais_aastad)
            & alus["Piiripunkti tüüp"].isin(piirityybid)
        )
        for veerg, valitud in valikulised_filtrid.items():
            if valitud:
                paeva_mask &= alus[veerg].isin(valitud)

        koond = (
            alus.loc[paeva_mask]
            .groupby(["aasta", "nadalapaev"], observed=True)[arv_veerg]
            .sum()
        )
        koond = koond.reindex(
            pd.MultiIndex.from_product(
                [tais_aastad, range(1, 8)],
                names=["aasta", "nadalapaev"],
            ),
            fill_value=0,
        ).rename("Arv").reset_index()
        koond["Suund"] = suund
        suundade_paevad.append(koond)

    paevade_koond = pd.concat(suundade_paevad, ignore_index=True)

    # Arvutame iga täisaasta 365/366 kalendripäeva ja nädalapäevade arvu.
    kalendri_ridu = []
    for aasta in tais_aastad:
        kalender = pd.date_range(f"{aasta}-01-01", f"{aasta}-12-31", freq="D")
        loendus = (
            pd.Series(kalender.dayofweek + 1)
            .value_counts().reindex(range(1, 8), fill_value=0)
        )
        for paev in range(1, 8):
            kalendri_ridu.append((aasta, paev, int(loendus[paev]), len(kalender)))
    kalender_df = pd.DataFrame(
        kalendri_ridu,
        columns=["aasta", "nadalapaev", "Paevi", "Aastas_paevi"],
    )
    paevade_koond = paevade_koond.merge(
        kalender_df, on=["aasta", "nadalapaev"], validate="many_to_one"
    )
    paevade_koond["Paeva_keskmine"] = (
        paevade_koond["Arv"] / paevade_koond["Paevi"]
    )
    aasta_maht = paevade_koond.groupby(["Suund", "aasta"])["Arv"].transform("sum")
    aasta_paevakeskmine = aasta_maht / paevade_koond["Aastas_paevi"]
    paevade_koond["Indeks"] = (
        paevade_koond["Paeva_keskmine"]
        / aasta_paevakeskmine.where(aasta_paevakeskmine > 0) * 100
    )

    # Keskmine absoluutarv põhineb kõigi valitud aastate vastavate
    # nädalapäevade kogusummal / nende kalendripäevade arvul.
    graafiku_data = (
        paevade_koond.groupby(["Suund", "nadalapaev"], as_index=False)
        .agg(Indeks=("Indeks", "mean"),
             Kogusumma=("Arv", "sum"), Kalendripaevad=("Paevi", "sum"))
    )
    graafiku_data["Keskmine_arv"] = (
        graafiku_data["Kogusumma"] / graafiku_data["Kalendripaevad"]
    )

    def nadalapaeva_moodikud(suund):
        x = graafiku_data.loc[
            graafiku_data["Suund"] == suund, "Keskmine_arv"
        ]
        keskmine = float(x.mean()) if not x.empty else None
        peak = float(x.max() / keskmine) if keskmine and keskmine > 0 else None
        return keskmine, peak

    sis_avg, sis_peak = nadalapaeva_moodikud("Sisenemised")
    val_avg, val_peak = nadalapaeva_moodikud("Väljumised")
    c1, c2, c3 = st.columns([1, 1, 1.15])
    with c1:
        st.metric("Keskmine sisenemine päevas",
                  vorminda_arv(round(sis_avg)) if sis_avg is not None else "–")
    with c2:
        st.metric("Keskmine väljumine päevas",
                  vorminda_arv(round(val_avg)) if val_avg is not None else "–")
    with c3:
        st.markdown("**Peak / Avg ratio**")
        st.markdown(
            f"<span style='color:#178939'>S: <b>{sis_peak:.2f}×</b></span>"
            if sis_peak is not None else "S: –",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color:#2878B5'>V: <b>{val_peak:.2f}×</b></span>"
            if val_peak is not None else "V: –",
            unsafe_allow_html=True,
        )

    paevanimed = ["Esmaspäev", "Teisipäev", "Kolmapäev", "Neljapäev",
                  "Reede", "Laupäev", "Pühapäev"]
    fig_hooaeg = go.Figure()
    for suund, varvus in [("Sisenemised", "#178939"),
                          ("Väljumised", "#2878B5")]:
        d = graafiku_data.loc[
            graafiku_data["Suund"] == suund
        ].set_index("nadalapaev").reindex(range(1, 8))
        fig_hooaeg.add_trace(go.Scatter(
            x=paevanimed, y=d["Indeks"],
            customdata=d["Keskmine_arv"].to_numpy().reshape(-1, 1),
            name=suund, mode="lines+markers",
            line=dict(color=varvus, width=3), marker=dict(size=8),
            hovertemplate=(
                "%{x}<br>Hooajalisuse indeks: %{y:.1f}"
                "<br>Keskmine päevas: %{customdata[0]:,.0f}"
                "<extra>%{fullData.name}</extra>"
            ),
        ))
    fig_hooaeg.add_hline(
        y=100, line_dash="dash", line_color="gray",
        annotation_text="Aasta keskmine päevatase = 100"
    )
    fig_hooaeg.update_layout(
        xaxis_title="Nädalapäev", yaxis_title="Hooajalisuse indeks",
        template="plotly_white", hovermode="x unified", height=430,
        legend=dict(orientation="h", y=1.12), margin=dict(t=65),
    )
    st.plotly_chart(fig_hooaeg, width="stretch")
    st.caption(
        f"Nädalapäevade võrdlus põhineb täisaastatel "
        f"{min(tais_aastad)}–{max(tais_aastad)}. "
        "Indeks on igal aastal normaliseeritud selle aasta keskmise "
        "päevase piiriületuste arvu suhtes. Nulliga kalendripäevad "
        "on arvestatud. Kuu filter seda plokki ei mõjuta."
    )
else:
    hooaja_alus = hooaja_alus.loc[hooaja_alus["aasta"].isin(tais_aastad)]
    hooaja_kuud = (
        hooaja_alus.groupby(["Suund", "aasta", "kuu"])["Piiriületuste arv"]
        .sum()
    )
    # Täielikud aastasisesed kalendrikuu read, sh nullkuud.
    hooaja_indeksirida = pd.MultiIndex.from_product(
        [["Sisenemised", "Väljumised"], tais_aastad, range(1, 13)],
        names=["Suund", "aasta", "kuu"]
    )
    hooaja_kuud = (
        hooaja_kuud.reindex(hooaja_indeksirida, fill_value=0)
        .rename("Arv").reset_index()
    )

    if ajavaade == "Kuu":
        hooaeg = hooaja_kuud.rename(columns={"kuu": "Periood"}).copy()
        vaartused = list(range(1, 13))
        sildid = [kuude_nimed[k] for k in vaartused]
        perioodi_nimi = "kuus"
    else:
        hooaja_kuud["Periood"] = ((hooaja_kuud["kuu"] - 1) // 3 + 1)
        hooaeg = (
            hooaja_kuud.groupby(["Suund", "aasta", "Periood"], as_index=False)["Arv"]
            .sum()
        )
        vaartused = [1, 2, 3, 4]
        sildid = ["Q1", "Q2", "Q3", "Q4"]
        perioodi_nimi = "kvartalis"

    # Indeks põhineb iga aasta oma keskmisel perioodimahul.
    aasta_keskmine = hooaeg.groupby(["Suund", "aasta"])["Arv"].transform("mean")
    hooaeg["Indeks"] = (
        hooaeg["Arv"] / aasta_keskmine.where(aasta_keskmine > 0) * 100
    )

    graafiku_data = (
        hooaeg.groupby(["Suund", "Periood"], as_index=False)
        .agg(Indeks=("Indeks", "mean"), Keskmine_arv=("Arv", "mean"))
    )

    # Need mõõdikud põhinevad ABSOLUUTARVUDEL, mitte indeksil.
    def perioodi_moodikud(suund):
        x = graafiku_data.loc[
            graafiku_data["Suund"] == suund, "Keskmine_arv"
        ].dropna()
        keskmine = float(x.mean()) if not x.empty else None
        peak = (float(x.max()) / keskmine) if keskmine and keskmine > 0 else None
        return keskmine, peak

    sis_avg, sis_peak = perioodi_moodikud("Sisenemised")
    val_avg, val_peak = perioodi_moodikud("Väljumised")

    c1, c2, c3 = st.columns([1, 1, 1.15])
    with c1:
        st.metric(
            f"Keskmine sisenemine {perioodi_nimi}",
            vorminda_arv(round(sis_avg)) if sis_avg is not None else "–"
        )
    with c2:
        st.metric(
            f"Keskmine väljumine {perioodi_nimi}",
            vorminda_arv(round(val_avg)) if val_avg is not None else "–"
        )
    with c3:
        st.markdown("**Peak / Avg ratio**")
        st.markdown(
            f"<span style='color:#178939'>S: <b>{sis_peak:.2f}×</b></span>"
            if sis_peak is not None else "S: –",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color:#2878B5'>V: <b>{val_peak:.2f}×</b></span>"
            if val_peak is not None else "V: –",
            unsafe_allow_html=True,
        )

    fig_hooaeg = go.Figure()
    for suund, varvus in [("Sisenemised", "#178939"),
                         ("Väljumised", "#2878B5")]:
        d = graafiku_data.loc[
            graafiku_data["Suund"] == suund
        ].set_index("Periood").reindex(vaartused)
        fig_hooaeg.add_trace(go.Scatter(
            x=sildid, y=d["Indeks"],
            customdata=d["Keskmine_arv"].to_numpy().reshape(-1, 1),
            name=suund, mode="lines+markers",
            line=dict(color=varvus, width=3), marker=dict(size=8),
            hovertemplate=(
                "%{x}<br>Hooajalisuse indeks: %{y:.1f}"
                "<br>Keskmine perioodimaht: %{customdata[0]:,.0f}"
                "<extra>%{fullData.name}</extra>"
            ),
        ))
    fig_hooaeg.add_hline(
        y=100, line_dash="dash", line_color="gray",
        annotation_text="Aasta keskmine = 100"
    )
    fig_hooaeg.update_layout(
        xaxis_title="Kuu" if ajavaade == "Kuu" else "Kvartal",
        yaxis_title="Hooajalisuse indeks",
        template="plotly_white", hovermode="x unified", height=430,
        legend=dict(orientation="h", y=1.12),
        margin=dict(t=65),
    )
    
    st.plotly_chart(fig_hooaeg, width="stretch")

    # ------------------------------------------
    # HOOAJALISUSE SELGITUS
    # ------------------------------------------

    prognoosiaastad = sorted(
        set(tais_aastad) - set(tais_tegelikud_aastad)
    )

    if prognoosiaastad:

        st.caption(
            f"Võrdlus põhineb täisaastatel "
            f"{min(tais_aastad)}–{max(tais_aastad)}. "
            f"Aastate {', '.join(map(str, prognoosiaastad))} "
            f"puhul kasutatakse osaliselt või täielikult "
            f"{valitud_mudel} prognoosi. "
            "Hooajalisuse indeks normaliseeritakse "
            "iga aasta keskmise suhtes. "
            "Keskmised mahud ja Peak/Avg põhinevad "
            "tegelikel ning prognoositud piiriületustel. "
            "Kuu filter seda plokki ei mõjuta."
        )

    else:

        st.caption(
            f"Võrdlus põhineb tegelike andmetega täisaastatel "
            f"{min(tais_aastad)}–{max(tais_aastad)}. "
            "Kõik perioodid on iga aasta sees normaliseeritud. "
            "Keskmised mahud ja Peak/Avg põhinevad "
            "tegelikel piiriületustel. "
            "Kuu filter seda plokki ei mõjuta."
        )


# ------------------------------------------
# E. SISENEMISTE JA VÄLJUMISTE KUINE ERINEVUS
# ------------------------------------------

st.divider()

st.divider()
st.subheader("Sisenemiste ja väljumiste kuine erinevus")

# Tegelike andmete põhjal arvutatud erinevus
erinevus_tegelik = kuupohine.copy()

erinevus_tegelik["Erinevus"] = (
    erinevus_tegelik["Sisenemised"]
    - erinevus_tegelik["Väljumised"]
)

fig_erinevus = go.Figure()


if not erinevus_tegelik.empty:

    # Leiame osalised kuud ja nende viimased
    # tegelike andmete kuupäevad.
    osaliste_kuude_info = {}

    for suund, info in osalised_kuud.items():
        kuu = pd.Timestamp(info["kuu"])
        viimane_paev = pd.Timestamp(info["viimane_paev"])

        osaliste_kuude_info.setdefault(kuu, {})[
            suund
        ] = viimane_paev

    hover_tekstid = []
    mustrid = []

    for kuu in erinevus_tegelik.index:

        kuu = pd.Timestamp(kuu).to_period("M").to_timestamp()

        if kuu in osaliste_kuude_info:

            info = osaliste_kuude_info[kuu]

            sisse = info.get("Sisenemised")
            valja = info.get("Väljumised")

            kuupaevad = []

            if sisse is not None:
                kuupaevad.append(
                    f"Sisenemised kuni {sisse:%d.%m.%Y}"
                )

            if valja is not None:
                kuupaevad.append(
                    f"Väljumised kuni {valja:%d.%m.%Y}"
                )

            hover_tekstid.append(
                "<b>Osaline kuu – tegelikud andmed</b>"
                + "<br>"
                + "<br>".join(kuupaevad)
            )

            mustrid.append("/")

        else:
            hover_tekstid.append(
                "Täielik kuu – tegelikud andmed"
            )

            mustrid.append("")

    fig_erinevus.add_trace(
        go.Bar(
            x=erinevus_tegelik.index,
            y=erinevus_tegelik["Erinevus"],

            marker_color=[
                "#178939" if x >= 0 else "#D9534F"
                for x in erinevus_tegelik["Erinevus"]
            ],

            marker_pattern_shape=mustrid,

            customdata=hover_tekstid,

            hovertemplate=(
                "<b>%{x|%B %Y}</b>"
                "<br>Erinevus: %{y:+,.0f}"
                "<br>%{customdata}"
                "<extra></extra>"
            ),
            width=20 * 24 * 60 * 60 * 1000,

            name="Tegelik erinevus"
        )
    )

# Valitud mudeli prognoositud erinevus
if naita_prognoosi and not aktiivne_prognoos.empty:

    prog_koond = (
        aktiivne_prognoos
        .groupby(["Kuupäev", "Suund"])["Prognoos"]
        .sum()
        .unstack("Suund", fill_value=0)
        .sort_index()
    )

    # Puuduva suuna korral ei eelda me nullprognoosi
    if {"Sisenemised", "Väljumised"}.issubset(
        prog_koond.columns
    ):

        prog_koond = prog_koond.loc[
            [
                kuu.month not in saadaolevad_kuud.get(
                    kuu.year, set()
                )
                for kuu in prog_koond.index
            ]
        ].copy()
  
        prog_koond["Erinevus"] = (
            prog_koond["Sisenemised"]
            - prog_koond["Väljumised"]
        )

        
# Prognoositud erinevus – positiivsed ja negatiivsed eraldi
for tingimus, varvus, nimetus in [
    (prog_koond["Erinevus"] >= 0, "#178939", "Positiivne"),
    (prog_koond["Erinevus"] < 0, "#D9534F", "Negatiivne"),
]:

    osa = prog_koond.loc[tingimus].copy()

    if osa.empty:
        continue

    fig_erinevus.add_trace(
        go.Bar(
            x=osa.index,
            y=osa["Erinevus"],
            marker_color=varvus,
            marker_pattern_shape=".",
            name=f"Prognoositud erinevus ({valitud_mudel}) – {nimetus.lower()}",
            width=20 * 24 * 60 * 60 * 1000,
            hovertemplate=(
                "<b>%{x|%m.%Y}</b>"
                "<br>Prognoositud erinevus: %{y:+,.0f}"
                "<extra></extra>"
            ),
        )
    )


# Osalise kuu nähtav märgistus
for info in osalised_kuud.values():

    kuu = pd.Timestamp(info["kuu"])
    viimane_paev = pd.Timestamp(info["viimane_paev"])

    if kuu not in erinevus_tegelik.index:
        continue

    vaartus = float(erinevus_tegelik.loc[kuu, "Erinevus"])

    fig_erinevus.add_annotation(
        x=kuu,
        y=vaartus,
        text=f"Osaline kuu<br>kuni {viimane_paev:%d.%m.%Y}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-50,
        font=dict(size=11),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="rgba(128,128,128,0.4)",
        borderwidth=1
    )

    break

fig_erinevus.add_hline(
    y=0,
    line_color="gray",
    line_width=1
)

fig_erinevus.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Sisenemised − väljumised",
    template="plotly_white",
    height=420,
    hovermode="x unified",
    barmode="overlay"
)


# ------------------------------------------
# KUISE ERINEVUSE X-TELJE VAADE
# ------------------------------------------

erinevuse_kuupaevad = list(erinevus_tegelik.index)

if naita_prognoosi and not prog_koond.empty:
    erinevuse_kuupaevad.extend(
        prog_koond.index.tolist()
    )

if erinevuse_kuupaevad:

    x_algus = (
        pd.Timestamp(min(erinevuse_kuupaevad))
        - pd.Timedelta(days=20)
    ).strftime("%Y-%m-%d")

    x_lopp = (
        pd.Timestamp(max(erinevuse_kuupaevad))
        + pd.Timedelta(days=35)
    ).strftime("%Y-%m-%d")

    fig_erinevus.update_xaxes(
        type="date",
        range=[x_algus, x_lopp],
        autorange=False,
        tickformat="%b %Y"
    )

st.plotly_chart(fig_erinevus, width="stretch")

if osalised_kuud:
    viimane_paev = max(
        info["viimane_paev"]
        for info in osalised_kuud.values()
    )

    st.caption(
        f"PPA tegelikud andmed ulatuvad {viimane_paev:%d.%m.%Y}. "
        "Viimane kuu on osaline. "
        "Tulevaste kuude väärtused põhinevad valitud "
        "A7/A9 prognoosimudelil, kui prognoos on sisse lülitatud."
    )


# ------------------------------------------
# F. PIIRIPUNKTIDE VÕRDLUS – HEATMAP
# ------------------------------------------

st.divider()
st.subheader("Piiripunktide võrdlus – heatmap")

hc1, hc2 = st.columns([1, 1])
with hc1:
    heat_suund = st.segmented_control(
        "Heatmap'i suund", ["Sisenemised", "Väljumised"],
        default="Sisenemised", key="sv_heat_suund"
    )
with hc2:
    heat_tyyp = st.segmented_control(
        "Heatmap'i väärtus", ["Arv", "Osakaal aastas (%)"],
        default="Arv", key="sv_heat_tyyp"
    )

# ------------------------------------------
# HEATMAP – TEGELIKUD + PROGNOOSID
# ------------------------------------------

heat_tegelik = filtreeritud.loc[
    filtreeritud["Suund"] == heat_suund,
    ["Kuupäev", "aasta", "kuu", "Piiripunkt",
     "Piiriületuste arv"]
].copy()

heat_osad = [heat_tegelik]

if naita_prognoosi:

    heat_prognoos = aktiivne_prognoos.loc[
        aktiivne_prognoos["Suund"] == heat_suund,
        ["Kuupäev", "aasta", "kuu", "Piiripunkt",
         "Prognoos"]
    ].copy()

    # Eemaldame prognoosist kuud, mille kohta
    # tegelikud andmed on juba olemas.
    if not heat_prognoos.empty:

        tegelike_kuude_mask = heat_prognoos.apply(
            lambda r: r["kuu"] in saadaolevad_kuud.get(
                r["aasta"], set()
            ),
            axis=1
        )

        heat_prognoos = heat_prognoos.loc[
            ~tegelike_kuude_mask
        ].copy()

        heat_prognoos = heat_prognoos.rename(
            columns={"Prognoos": "Piiriületuste arv"}
        )

        heat_osad.append(heat_prognoos)

heat_alus = pd.concat(
    heat_osad,
    ignore_index=True
)

heat_top = (
    heat_alus.groupby("Piiripunkt")["Piiriületuste arv"]
    .sum().sort_values(ascending=False).head(18).index.tolist()
)
if not heat_top:
    st.info("Valitud filtritega pole piiripunktide andmeid.")
else:
    heat = (
        heat_alus.loc[heat_alus["Piiripunkt"].isin(heat_top)]
        .groupby(["Piiripunkt", "aasta"])["Piiriületuste arv"]
        .sum().unstack("aasta", fill_value=0)
    )
    heat = heat.reindex(index=heat_top[::-1],
                        columns=sorted(aastad), fill_value=0)
    if heat_tyyp == "Osakaal aastas (%)":
        # Nimetaja: kogu valitud suuna vastava aasta maht (kõik piiripunktid).
        aasta_kogus = (
            heat_alus.groupby("aasta")["Piiriületuste arv"].sum()
            .reindex(heat.columns, fill_value=0)
        )
        kuvatav = heat.div(aasta_kogus.replace(0, np.nan), axis=1) * 100
        suffix = "%"
        colorbar_title = "Osakaal %"
    else:
        kuvatav = heat
        suffix = ""
        colorbar_title = "Piiriületusi"

    fig_heat = go.Figure(go.Heatmap(
        z=kuvatav.to_numpy(),
        x=[str(x) for x in kuvatav.columns],
        y=kuvatav.index.tolist(),
        customdata=heat.to_numpy().reshape((*heat.shape, 1)),
        colorscale=(
            [[0, "#edf6ee"], [0.45, "#83caa2"], [1, "#0b7741"]]
            if heat_suund == "Sisenemised" else
            [[0, "#edf5fd"], [0.45, "#86bbdd"], [1, "#125e9c"]]
        ),
        colorbar=dict(title=colorbar_title, thickness=14),
        hovertemplate=(
            "%{y} · %{x}<br>Väärtus: %{z:,.2f}" + suffix +
            "<br>Piiriületusi: %{customdata[0]:,.0f}<extra></extra>"
        ),
        xgap=2, ygap=2,
    ))
    fig_heat.update_layout(
        xaxis_title="Aasta",
        xaxis_type="category",
        yaxis_title="Piiripunkt",
        height=max(510, 26 * len(heat_top) + 120),
        margin=dict(l=10, r=10, t=25, b=35),
    )
    st.plotly_chart(fig_heat, width="stretch")


st.caption(
    "PPA tegelikud andmed ulatuvad 18.11.2026-ni. "
    "November 2026 on osaline kuu ja viimane täielik kuu "
    "on oktoober 2026. Alates detsembrist 2026 "
    "kasutatakse valitud A7/A9 prognoosimudeli tulemusi, "
    "kui prognoos on sisse lülitatud. "
    "Prognoos ei asenda ega dubleeri olemasolevaid tegelikke andmeid."
)

