"""Lehekesksed filtrid PPA analüüsilehtede jaoks (app.py külgribast sõltumatud)."""
import streamlit as st

KOLMANDAD = "3.riik"

def gruppide_loend(df):
    return sorted(g for g in df["Riikide grupp"].dropna().astype(str).unique() if g != "Puudub")

def vali_grupp(df, key, koik=True):
    grupid = gruppide_loend(df)
    opts = (["Kõik riikide grupid"] if koik else []) + grupid
    vaikimisi = KOLMANDAD if KOLMANDAD in opts else next((x for x in opts if "kolmand" in x.lower()), opts[0])
    return st.selectbox("Riikide grupp", opts, index=opts.index(vaikimisi), key=f"{key}_grupp")

def grupi_mask(df, grupp):
    if grupp == "Kõik riikide grupid":
        return df["Riikide grupp"].astype(str).isin(gruppide_loend(df))
    return df["Riikide grupp"].astype(str).eq(grupp)

def vali_kodakondsus(df, grupp, key):
    nimed = sorted(df.loc[grupi_mask(df, grupp), "Kodakondsus"].dropna().astype(str).unique().tolist())
    return st.selectbox("Kodakondsus", ["Kõik kodakondsused"] + nimed, key=f"{key}_kodakondsus")

def vali_aastad(df, key, kaasa_2026=False):
    opts = sorted(int(a) for a in df["aasta"].dropna().unique() if 2021 <= int(a) <= (2026 if kaasa_2026 else 2025))
    defaults = opts if kaasa_2026 else [a for a in opts if a <= 2025]
    return st.multiselect("Aastad", options=opts, default=defaults, key=f"{key}_aastad")

def vali_piiripunkt(df, key):
    opts = sorted(df["Piiripunkt"].dropna().astype(str).unique().tolist())
    return st.selectbox("Piiripunkt", ["Kõik piiripunktid"] + opts, key=f"{key}_punkt")

def vali_piirityyp(key):
    return st.selectbox("Piiritüüp", ["Kõik", "Maismaapiir", "Õhupiir"], key=f"{key}_tyyp")

def filtreeri(df, grupp="Kõik riikide grupid", kodakondsus="Kõik kodakondsused", punkt="Kõik piiripunktid", tyyp="Kõik", aastad=None):
    mask = grupi_mask(df, grupp) & df["Piiripunkti tüüp"].isin(["Maismaapiir", "Õhupiir"])
    if kodakondsus != "Kõik kodakondsused":
        mask &= df["Kodakondsus"].astype(str).eq(kodakondsus)
    if punkt != "Kõik piiripunktid":
        mask &= df["Piiripunkt"].astype(str).eq(punkt)
    if tyyp != "Kõik":
        mask &= df["Piiripunkti tüüp"].eq(tyyp)
    if aastad is not None:
        mask &= df["aasta"].isin(aastad)
    return df.loc[mask]
