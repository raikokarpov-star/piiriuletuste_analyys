import streamlit as st
import pandas as pd

# ---------------------------------
# LEHE SEADISTUSED
# ---------------------------------

st.set_page_config(
    page_title="Eesti piiriületuste analüüs",
    page_icon="🇪🇪",
    layout="wide"
)

st.title("Eesti piiriületuste analüüs")
st.caption("Piiriületuste dünaamiline analüüs 2021–2026")

# ---------------------------------
# ANDMETE LAADIMINE
# ---------------------------------

@st.cache_data
def lae_andmed():
    return pd.read_parquet("piiriuletused.parquet")

df = lae_andmed()

# ---------------------------------
# FILTRID
# ---------------------------------

st.sidebar.header("Filtrid")

# Piiripunkti tüüp
piiri_tyyp = st.sidebar.selectbox(
    "Piiripunkti tüüp",
    ["Kõik", "Maismaapiir", "Õhupiir"]
)

# Piiripunktide valik vastavalt tüübile
# Piiripunktide valik vastavalt tüübile

# Jätame merepiiri välja
maismaa_ja_ohu = df[
    df["Piiripunkti tüüp"].isin(
        ["Maismaapiir", "Õhupiir"]
    )
]

if piiri_tyyp == "Kõik":
    punktid = sorted(
        maismaa_ja_ohu["Piiripunkt"].dropna().unique()
    )
else:
    punktid = sorted(
        maismaa_ja_ohu.loc[
            maismaa_ja_ohu["Piiripunkti tüüp"] == piiri_tyyp,
            "Piiripunkt"
        ].dropna().unique()
    )

valitud_punktid = st.sidebar.multiselect(
    "Piiripunkt",
    options=punktid,
    default=punktid
)

# Aastad
aastad = sorted(df["aasta"].unique())

valitud_aastad = st.sidebar.multiselect(
    "Aasta",
    options=aastad,
    default=aastad
)

# Kuud
kuud = list(range(1, 13))

valitud_kuud = st.sidebar.multiselect(
    "Kuu",
    options=kuud,
    default=kuud
)

# Kodakondsuse filter
kodakondsused = sorted(
    df["Kodakondsus"].dropna().unique()
)

valitud_kodakondsused = st.sidebar.multiselect(
    "Kodakondsus",
    options=kodakondsused,
    default=kodakondsused
)

# Vanuserühma filter
vanuseruhmad = sorted(
    df["Vanuserühm"].dropna().unique()
)

valitud_vanuseruhmad = st.sidebar.multiselect(
    "Vanuserühm",
    options=vanuseruhmad,
    default=vanuseruhmad
)

# Riikide gruppide filter
riikide_grupid = sorted(
    df["Riikide grupp"].dropna().unique()
)

valitud_riikide_grupid = st.sidebar.multiselect(
    "Riikide grupp",
    options=riikide_grupid,
    default=riikide_grupid
)

# ---------------------------------
# ANDMETE FILTREERIMINE
# ---------------------------------

filtreeritud = df[
    (df["Piiripunkti tüüp"].isin(
        ["Maismaapiir", "Õhupiir"]
        if piiri_tyyp == "Kõik"
        else [piiri_tyyp]
    ))
    & (df["Piiripunkt"].isin(valitud_punktid))
    & (df["aasta"].isin(valitud_aastad))
    & (df["kuu"].isin(valitud_kuud))
    & (df["Kodakondsus"].isin(valitud_kodakondsused))
    & (df["Riikide grupp"].isin(valitud_riikide_grupid))
    & (df["Vanuserühm"].isin(valitud_vanuseruhmad))
]

# ---------------------------------
# TULEMUSED
# ---------------------------------

st.subheader("Ülevaade")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Piiriületuste arv",
        f"{len(filtreeritud):,}".replace(",", " ")
    )

with col2:
    st.metric(
        "Valitud piiripunkte",
        len(valitud_punktid)
    )

with col3:
    st.metric(
        "Valitud aastaid",
        len(valitud_aastad)
    )

st.write("Filtreeritud andmestiku mõõtmed:", filtreeritud.shape)

# ---------------------------------
# AJALINE ANALÜÜS
# ---------------------------------

st.divider()

st.subheader("Piiriületuste muutumine ajas")

# Koondame andmed aasta ja kuu kaupa
graafiku_andmed = (
    filtreeritud
    .groupby(
        ["aasta", "kuu", "Piiripunkt"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Loome kuupäeva veeru
graafiku_andmed["Kuupäev"] = pd.to_datetime(
    graafiku_andmed["aasta"].astype(str)
    + "-"
    + graafiku_andmed["kuu"].astype(str)
    + "-01"
)

# Joonistame graafiku
import plotly.express as px

fig = px.line(
    graafiku_andmed,
    x="Kuupäev",
    y="Piiriületuste arv",
    color="Piiripunkt",
    markers=True,
    title="Piiriületused kuude lõikes"
)

fig.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Piiriületuste arv",
    hovermode="x unified",
    legend_title="Piiripunkt"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------------------------
# PIIRIPUNKTIDE VÕRDLUS AASTATE LÕIKES
# ---------------------------------

st.divider()

st.subheader("Piiripunktide võrdlus aastate lõikes")

# Koondame piiriületused aasta ja piiripunkti kaupa
aastate_andmed = (
    filtreeritud
    .groupby(
        ["aasta", "Piiripunkt"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Aastate võrdlus tulpdiagrammil
fig_aastad = px.bar(
    aastate_andmed,
    x="aasta",
    y="Piiriületuste arv",
    color="Piiripunkt",
    barmode="group",
    title="Piiriületused piiripunktide ja aastate lõikes",
    text_auto=".2s"
)

fig_aastad.update_layout(
    xaxis_title="Aasta",
    yaxis_title="Piiriületuste arv",
    legend_title="Piiripunkt",
    hovermode="x unified"
)

st.plotly_chart(
    fig_aastad,
    use_container_width=True
)

# ---------------------------------
# MUUTUSTE ANALÜÜS
# ---------------------------------

st.divider()

st.subheader("Piiriületuste muutused aastate lõikes")

# Koondame andmed piiripunktide ja aastate kaupa
muutuste_tabel = (
    filtreeritud
    .groupby(
        ["Piiripunkt", "aasta"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Sorteerime andmed
muutuste_tabel = muutuste_tabel.sort_values(
    ["Piiripunkt", "aasta"]
)

# Arvutame absoluutse muutuse
muutuste_tabel["Absoluutne muutus"] = (
    muutuste_tabel
    .groupby("Piiripunkt")["Piiriületuste arv"]
    .diff()
)

# Arvutame protsentuaalse muutuse
muutuste_tabel["Muutus %"] = (
    muutuste_tabel
    .groupby("Piiripunkt")["Piiriületuste arv"]
    .pct_change() * 100
)

# Vormindame tulemused
muutuste_tabel["Muutus %"] = (
    muutuste_tabel["Muutus %"].round(1)
)

# Kuvame tabeli
st.dataframe(
    muutuste_tabel,
    use_container_width=True,
    hide_index=True
)

st.subheader("TOP 10 kodakondsust")

# Koondame piiriületused kodakondsuse ja riikide grupi järgi
kodakondsuste_koond = (
    filtreeritud
    .groupby(
        ["Kodakondsus", "Riikide grupp"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Leiame 10 kõige arvukamat kodakondsust
top10_kodakondsused = (
    kodakondsuste_koond
    .sort_values("Piiriületuste arv", ascending=False)
    .head(10)
)

# Horisontaalne tulpdiagramm
fig_top10 = px.bar(
    top10_kodakondsused,
    x="Piiriületuste arv",
    y="Kodakondsus",
    color="Riikide grupp",
    orientation="h",
    text_auto=".2s",
    title="10 kõige arvukamat kodakondsust"
)

fig_top10.update_layout(
    xaxis_title="Piiriületuste arv",
    yaxis_title="Kodakondsus",
    yaxis={"categoryorder": "total ascending"},
    legend_title="Riikide grupp"
)

st.plotly_chart(
    fig_top10,
    use_container_width=True
)

# Andmetabel koos riikide grupiga
st.dataframe(
    top10_kodakondsused,
    use_container_width=True,
    hide_index=True
)

st.subheader("Piiriületused riikide gruppide järgi")

st.subheader("Riikide gruppide dünaamika ajas")

# Koondame piiriületused aasta, kuu ja riikide grupi järgi
riikide_grupid = (
    filtreeritud
    .groupby(
        ["aasta", "kuu", "Riikide grupp"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Loome kuupäeva telje jaoks
riikide_grupid["Kuupäev"] = pd.to_datetime(
    dict(
        year=riikide_grupid["aasta"],
        month=riikide_grupid["kuu"],
        day=1
    )
)

# Joondiagramm
fig_grupid = px.line(
    riikide_grupid,
    x="Kuupäev",
    y="Piiriületuste arv",
    color="Riikide grupp",
    markers=True,
    title="Piiriületuste muutus riikide gruppide lõikes"
)

fig_grupid.update_layout(
    xaxis_title="Aeg",
    yaxis_title="Piiriületuste arv",
    legend_title="Riikide grupp",
    hovermode="x unified"
)

st.plotly_chart(
    fig_grupid,
    use_container_width=True
)

# ---------------------------------
# HOOAJALISUSE ANALÜÜS
# ---------------------------------

st.divider()

st.subheader("Piiriületuste hooajalisus")

st.info(
    """
    **Mis on hooajalisuse indeks?**

    Hooajalisuse indeks näitab, kui palju erineb konkreetse kuu
    piiriületuste arv sama aasta keskmisest kuisest piiriületuste arvust.

    - 100 = aasta keskmine
    - Üle 100 = keskmisest aktiivsem kuu
    - Alla 100 = keskmisest vaiksem kuu

    Näiteks indeks 120 tähendab, et piiriületusi oli 20% rohkem
    kui selle aasta keskmisel kuul.
    """
)

# Kasutame piiritüübi, piiripunkti ja aasta filtreid,
# kuid mitte kuu filtrit.
hooajalisuse_alus = df[
    (df["Piiripunkti tüüp"].isin(
        ["Maismaapiir", "Õhupiir"]
        if piiri_tyyp == "Kõik"
        else [piiri_tyyp]
    ))
    & (df["Piiripunkt"].isin(valitud_punktid))
    & (df["aasta"].isin(valitud_aastad))
    & (df["Kodakondsus"].isin(valitud_kodakondsused))
    & (df["Riikide grupp"].isin(valitud_riikide_grupid))
    & (df["Vanuserühm"].isin(valitud_vanuseruhmad))
].copy()

# Kontrollime viimase kuu täielikkust
viimane_kpv = df["Piiriületuse kpv"].max()

kuud_arvutuseks = list(range(1, 13))

if pd.notna(viimane_kpv) and viimane_kpv.day < viimane_kpv.days_in_month:
    # Osalist viimast kuud hooajalisuse arvutusse ei kaasa
    hooajalisuse_alus = hooajalisuse_alus[
        ~(
            (hooajalisuse_alus["aasta"] == viimane_kpv.year)
            & (hooajalisuse_alus["kuu"] == viimane_kpv.month)
        )
    ]

    if viimane_kpv.year in valitud_aastad:
        kuud_arvutuseks = [
            kuu for kuu in range(1, 13)
            if kuu != viimane_kpv.month
        ]

# Koondame tegelikud piiriületused
hooajalisus = (
    hooajalisuse_alus
    .groupby(
        ["aasta", "kuu", "Piiripunkt"],
        observed=True
    )
    .size()
    .reset_index(name="Piiriületuste arv")
)

# Lisame ka kuud, kus piiriületusi ei toimunud
indeks = pd.MultiIndex.from_product(
    [
        valitud_aastad,
        valitud_punktid,
        range(1, 13)
    ],
    names=["aasta", "Piiripunkt", "kuu"]
)

hooajalisus = (
    hooajalisus
    .set_index(["aasta", "Piiripunkt", "kuu"])
    .reindex(indeks, fill_value=0)
    .reset_index()
)

# Eemaldame viimase osalise kuu
if pd.notna(viimane_kpv) and viimane_kpv.day < viimane_kpv.days_in_month:
    hooajalisus = hooajalisus[
        ~(
            (hooajalisus["aasta"] == viimane_kpv.year)
            & (hooajalisus["kuu"] == viimane_kpv.month)
        )
    ]

# Arvutame aasta keskmise kuise piiriületuste arvu
hooajalisus["Aasta keskmine"] = (
    hooajalisus
    .groupby(
        ["aasta", "Piiripunkt"],
        observed=True
    )["Piiriületuste arv"]
    .transform("mean")
)

# Arvutame hooajalisuse indeksi
hooajalisus["Hooajalisuse indeks"] = (
    hooajalisus["Piiriületuste arv"]
    / hooajalisus["Aasta keskmine"]
    * 100
).round(1)

# Kuu nimetused
kuu_nimed = {
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
    12: "Detsember"
}

hooajalisus["Kuu"] = hooajalisus["kuu"].map(kuu_nimed)

# Valime aastad, mida soovime võrrelda
hooajalisuse_aastad = st.multiselect(
    "Võrdle aastaid",
    options=sorted(hooajalisus["aasta"].unique()),
    default=sorted(hooajalisus["aasta"].unique())[-3:]
)

hooajalisuse_graafik = hooajalisus[
    hooajalisus["aasta"].isin(hooajalisuse_aastad)
]

# Hooajalisuse graafikud eraldi aastate kaupa
st.subheader("Hooajalisuse võrdlus")

if not hooajalisuse_aastad:
    st.warning("Vali vähemalt üks aasta.")

else:
    y_max = hooajalisuse_graafik["Hooajalisuse indeks"].max()
    y_max = ((y_max // 20) + 1) * 20

    veerud = st.columns(len(hooajalisuse_aastad))

    for veerg, aasta in zip(veerud, hooajalisuse_aastad):

        aasta_andmed = hooajalisuse_graafik[
            hooajalisuse_graafik["aasta"] == aasta
        ]

        fig_hooajalisus = px.line(
            aasta_andmed,
            x="Kuu",
            y="Hooajalisuse indeks",
            color="Piiripunkt",
            markers=True,
            category_orders={
                "Kuu": list(kuu_nimed.values())
            }
        )

        fig_hooajalisus.add_hline(
            y=100,
            line_dash="dash",
            annotation_text="Aasta keskmine (100)"
        )

        fig_hooajalisus.update_layout(
            title=str(aasta),
            xaxis_title="Kuu",
            yaxis_title="Hooajalisuse indeks",
            legend_title="Piiripunkt",
            hovermode="x unified",
            yaxis=dict(range=[0, y_max]),
            margin=dict(l=40, r=20, t=50, b=40)
        )

        with veerg:
            st.plotly_chart(
                fig_hooajalisus,
                use_container_width=True
            )

    
# Hooajalisuse tabel
st.subheader("Hooajalisuse andmetabel")

st.dataframe(
    hooajalisus[
        [
            "Piiripunkt",
            "aasta",
            "Kuu",
            "Piiriületuste arv",
            "Aasta keskmine",
            "Hooajalisuse indeks"
        ]
    ],
    use_container_width=True,
    hide_index=True
)
