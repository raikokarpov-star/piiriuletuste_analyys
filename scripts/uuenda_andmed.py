
from pathlib import Path
from datetime import date
import calendar
import pandas as pd
import argparse
import os
import shutil
from datetime import datetime

# ------------------------------------------
# ASUKOHAD JA SEADISTUS
# ------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
ANDMEKAUST = ROOT / "streamlit_andmed"
KONTROLLKAUST = ROOT / "_uuenduse_kontroll"

AASTA = 2026

TUNNUSED = [
    "Sugu",
    "Vanuserühm",
    "Riikide grupp",
    "Kodakondsus",
    "Piiripunkti tüüp",
    "Piiripunkt",
]

ALLIKAD = {
    "Sisenemised": {
        "url": (
            "https://opendata.smit.ee/ppa/csv/"
            "piiriyletused_isikud_sisse_2026.csv"
        ),
        "arv": "Piiriületajate arv",
        "kuu_fail": "sisenemised_2016_2026.parquet",
        "paeva_fail": "sisenemised_paevad_2016_2026.parquet",
    },
    "Väljumised": {
        "url": (
            "https://opendata.smit.ee/ppa/csv/"
            "piiriyletused_isikud_valja_2026.csv"
        ),
        "arv": "Piirilt lahkujate arv",
        "kuu_fail": "valjumised_2016_2026.parquet",
        "paeva_fail": "valjumised_paevad_2016_2026.parquet",
    },
}


# ------------------------------------------
# ABIFUNKTSIOONID
# ------------------------------------------

def valmiskuu(aasta, kuu, viimane_kuupaev):
    """Kuu peab olema lõppenud ja allikas peab katma kuu lõpu."""

    viimane_paev = date(
        aasta,
        kuu,
        calendar.monthrange(aasta, kuu)[1]
    )

    return (
        viimane_kuupaev >= viimane_paev
        and date.today() > viimane_paev
    )


def yhenda_ajalugu(vana, uus, arv):
    """Säilitame varasemad aastad ja asendame 2026 tervikuna."""

    ajalugu = vana.loc[
        vana["aasta"] < AASTA
    ].copy()

    tulemus = pd.concat(
        [ajalugu, uus],
        ignore_index=True
    )

    # Säilitame olemasoleva andmestruktuuri
    tulemus = tulemus[vana.columns.tolist()]

    tulemus["aasta"] = tulemus["aasta"].astype("int16")
    tulemus["kuu"] = tulemus["kuu"].astype("int8")

    for veerg in ["paev", "nadalapaev", "nadal"]:
        if veerg in tulemus.columns:
            tulemus[veerg] = tulemus[veerg].astype("int8")

    for veerg in TUNNUSED:
        tulemus[veerg] = tulemus[veerg].astype("category")

    tulemus[arv] = tulemus[arv].astype("int64")

    kuupaevaveerg = (
        "Piiriületuse kpv"
        if "Piiriületuse kpv" in tulemus.columns
        else "Kuupäev"
    )

    tulemus[kuupaevaveerg] = (
        pd.to_datetime(tulemus[kuupaevaveerg])
        .astype("datetime64[us]")
    )

    return tulemus.sort_values(
        [kuupaevaveerg, *TUNNUSED]
    ).reset_index(drop=True)


def kontrolli_tulemus(vana, uus, tulemus, arv, oodatud):
    """Kontrollime ajalugu, struktuuri ja kogumahtu."""

    if tulemus.columns.tolist() != vana.columns.tolist():
        raise ValueError("Veergude struktuur on muutunud")

    if tulemus.isna().any().any():
        raise ValueError("Uues andmestikus on puuduvaid väärtusi")

    if (tulemus[arv] < 0).any():
        raise ValueError("Andmestikus on negatiivseid koguseid")

    vana_ajalugu = vana.loc[
        vana["aasta"] < AASTA, arv
    ].sum()

    uus_ajalugu = tulemus.loc[
        tulemus["aasta"] < AASTA, arv
    ].sum()

    if vana_ajalugu != uus_ajalugu:
        raise ValueError("Ajalooliste andmete maht muutus")

    uus_aasta = tulemus.loc[
        tulemus["aasta"] == AASTA, arv
    ].sum()

    if uus_aasta != oodatud:
        raise ValueError(
            f"2026 kogusumma ei klapi: {uus_aasta} != {oodatud}"
        )


# ------------------------------------------
# ÜHE LIIKUMISSUUNA TÖÖTLUS
# ------------------------------------------

def tootle_suund(suund, info):

    print(f"\n{'=' * 55}")
    print("TÖÖTLEN:", suund)

    df = pd.read_csv(
        info["url"],
        sep=None,
        engine="python"
    )

    vajalikud = ["Piiriületuse kpv", *TUNNUSED]

    if df.empty:
        raise ValueError(f"{suund}: CSV on tühi")

    if not set(vajalikud).issubset(df.columns):
        raise ValueError(f"{suund}: CSV veerud ei klapi")

    if df[vajalikud].isna().any().any():
        raise ValueError(f"{suund}: CSV sisaldab puuduvaid väärtusi")

    df["Piiriületuse kpv"] = pd.to_datetime(
        df["Piiriületuse kpv"],
        format="%d-%m-%Y",
        errors="raise"
    )

    if not df["Piiriületuse kpv"].dt.year.eq(AASTA).all():
        raise ValueError("CSV sisaldab vale aasta andmeid")

    viimane = df["Piiriületuse kpv"].max().date()

    if viimane > date.today():
        raise ValueError("CSV sisaldab tulevikukuupäevi")

    df["aasta"] = df["Piiriületuse kpv"].dt.year
    df["kuu"] = df["Piiriületuse kpv"].dt.month
    df["paev"] = df["Piiriületuse kpv"].dt.day
    df["nadalapaev"] = df["Piiriületuse kpv"].dt.dayofweek
    df["nadal"] = df["Piiriületuse kpv"].dt.isocalendar().week.astype(int)

    arv = info["arv"]

    # ------------------------------------------
    # PÄEVAPÕHINE KOOND
    # ------------------------------------------

    paeva_grupid = [
        "Piiriületuse kpv",
        "aasta",
        "kuu",
        "paev",
        "nadalapaev",
        "nadal",
        *TUNNUSED,
    ]

    uus_paev = (
        df.groupby(
            paeva_grupid,
            observed=True,
            dropna=False
        )
        .size()
        .reset_index(name=arv)
    )

    if uus_paev[arv].sum() != len(df):
        raise ValueError("Päevapõhine summa ei klapi CSV-ga")

    # ------------------------------------------
    # KUUPÕHINE KOOND
    # ------------------------------------------

    valmis_kuud = [
        kuu for kuu in range(1, 13)
        if valmiskuu(AASTA, kuu, viimane)
    ]

    df_kuud = df.loc[
        df["kuu"].isin(valmis_kuud)
    ].copy()

    df_kuud["Kuupäev"] = (
        df_kuud["Piiriületuse kpv"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    kuu_grupid = [
        "Kuupäev",
        "aasta",
        "kuu",
        *TUNNUSED,
    ]

    uus_kuu = (
        df_kuud.groupby(
            kuu_grupid,
            observed=True,
            dropna=False
        )
        .size()
        .reset_index(name=arv)
    )

    if uus_kuu[arv].sum() != len(df_kuud):
        raise ValueError("Kuupõhine summa ei klapi CSV-ga")

    # ------------------------------------------
    # AJALOO ÜHENDAMINE
    # ------------------------------------------

    vana_paev = pd.read_parquet(
        ANDMEKAUST / info["paeva_fail"]
    )

        # ------------------------------------------
    # ANDMETE VÄHENEMISE KAITSE
    # ------------------------------------------

    vana_2026 = vana_paev[
        vana_paev["aasta"] == AASTA
    ]

    vana_viimane = (
        vana_2026["Piiriületuse kpv"].max().date()
    )

    vana_kogus = int(
        vana_2026[arv].sum()
    )

    uus_kogus = len(df)

    if viimane < vana_viimane:
        raise ValueError(
            f"{suund}: allika viimane kuupäev "
            f"liikus tagasi ({vana_viimane} -> {viimane})"
        )

    if uus_kogus < vana_kogus:
        raise ValueError(
            f"{suund}: andmete kogumaht vähenes "
            f"({vana_kogus} -> {uus_kogus})"
        )

    print("\nANDMETE VÄHENEMISE KONTROLL")
    print("Vana viimane kuupäev:", vana_viimane)
    print("Uus viimane kuupäev:", viimane)
    print("Vana 2026 kogus:", vana_kogus)
    print("Uus 2026 kogus:", uus_kogus)
    print("Tulemus: KORRAS")

    vana_kuu = pd.read_parquet(
        ANDMEKAUST / info["kuu_fail"]
    )

    paevad = yhenda_ajalugu(
        vana_paev, uus_paev, arv
    )

    kuud = yhenda_ajalugu(
        vana_kuu, uus_kuu, arv
    )

    kontrolli_tulemus(
        vana_paev, uus_paev, paevad,
        arv, len(df)
    )

    kontrolli_tulemus(
        vana_kuu, uus_kuu, kuud,
        arv, len(df_kuud)
    )

    print("CSV ridu:", len(df))
    print("Päevapõhiseid ridu:", len(paevad))
    print("Kuupõhiseid ridu:", len(kuud))
    print("Viimane tegelik päev:", viimane)
    print("Täielikud kuud:", valmis_kuud)
    print("Valideerimine: KORRAS")

    return {
        info["paeva_fail"]: paevad,
        info["kuu_fail"]: kuud,
    }



def avalda_failid(tulemused):
    """
    Avaldab valideeritud failid.
    Enne asendamist tehakse varukoopiad.
    Vea korral taastatakse vanad failid.
    """

    varukoopia = (
        ROOT
        / "_uuenduse_varukoopiad"
        / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )
    varukoopia.mkdir(parents=True, exist_ok=False)

    # Kõik neli uut faili peavad olemas olema.
    for fail in tulemused:
        uus = KONTROLLKAUST / fail
        vana = ANDMEKAUST / fail

        if not uus.is_file() or not vana.is_file():
            raise FileNotFoundError(
                f"Puuduv fail: {fail}"
            )

    # Teeme kõigist originaalidest varukoopiad.
    for fail in tulemused:
        shutil.copy2(
            ANDMEKAUST / fail,
            varukoopia / fail
        )

    print("\nVARUKOOPIAD:", varukoopia)

    try:
        for fail in tulemused:
            uus = KONTROLLKAUST / fail
            siht = ANDMEKAUST / fail
            ajutine = ANDMEKAUST / f"{fail}.tmp"

            shutil.copy2(uus, ajutine)
            os.replace(ajutine, siht)

            print("AVALDATUD:", fail)

    except Exception:
        print("AVALDAMINE EBAÕNNESTUS. Taastan varukoopiad.")

        for fail in tulemused:
            ajutine = ANDMEKAUST / f"{fail}.tmp"
            ajutine.unlink(missing_ok=True)

            shutil.copy2(
                varukoopia / fail,
                ANDMEKAUST / fail
            )

        raise

    print("\nKÕIK NELI FAILI AVALDATUD")


# ------------------------------------------
# PÕHIPROTSESS – KONTROLLREŽIIM
# ------------------------------------------


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--publish",
        action="store_true",
        help="Avalda kontrollitud andmed Streamliti andmekausta"
    )

    args = parser.parse_args()

    tulemused = {}

    for suund, info in ALLIKAD.items():
        tulemused.update(
            tootle_suund(suund, info)
        )

    KONTROLLKAUST.mkdir(
        parents=True,
        exist_ok=True
    )

    for fail, df in tulemused.items():

        tee = KONTROLLKAUST / fail

        df.to_parquet(
            tee,
            index=False
        )

        uuesti = pd.read_parquet(tee)

        arv = (
            "Piiriületajate arv"
            if "Piiriületajate arv" in df.columns
            else "Piirilt lahkujate arv"
        )

        if (
            len(uuesti) != len(df)
            or uuesti[arv].sum() != df[arv].sum()
            or uuesti.columns.tolist() != df.columns.tolist()
        ):
            raise ValueError(
                f"Salvestamise kontroll ebaõnnestus: {fail}"
            )

        print("KONTROLLITUD:", fail)

    print("\nKÕIK NELI FAILI VALIDEERITUD")

    if args.publish:
        avalda_failid(tulemused)
    else:
        print("Kontrollrežiim: originaalfaile ei muudetud.")


if __name__ == "__main__":
    main()
