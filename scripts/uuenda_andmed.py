
from pathlib import Path
from datetime import date, datetime
from urllib.error import HTTPError
import argparse
import calendar
import os
import shutil

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANDMEKAUST = ROOT / "streamlit_andmed"
KONTROLLKAUST = ROOT / "_uuenduse_kontroll"
VARUKOOPIAD = ROOT / "_uuenduse_varukoopiad"

ALGUSAASTA = 2026
LOPPAASTA = 2027

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
        "suund": "sisse",
        "arv": "Piiriületajate arv",
        "kuu_fail": "sisenemised_2016_2026.parquet",
        "paeva_fail": "sisenemised_paevad_2016_2026.parquet",
    },
    "Väljumised": {
        "suund": "valja",
        "arv": "Piirilt lahkujate arv",
        "kuu_fail": "valjumised_2016_2026.parquet",
        "paeva_fail": "valjumised_paevad_2016_2026.parquet",
    },
}


def lae_csv(info, aasta):
    url = (
        "https://opendata.smit.ee/ppa/csv/"
        f"piiriyletused_isikud_{info['suund']}_{aasta}.csv"
    )

    try:
        df = pd.read_csv(url, sep=None, engine="python")
    except HTTPError as e:
        if e.code == 404 and aasta > ALGUSAASTA:
            print(f"{aasta}: CSV pole veel avaldatud")
            return None
        raise

    vajalikud = ["Piiriületuse kpv", *TUNNUSED]

    if df.empty or not set(vajalikud).issubset(df.columns):
        raise ValueError(f"{aasta}: CSV on tühi või veerud erinevad")

    if df[vajalikud].isna().any().any():
        raise ValueError(f"{aasta}: CSV sisaldab puuduvaid väärtusi")

    df["Piiriületuse kpv"] = pd.to_datetime(
        df["Piiriületuse kpv"],
        format="%d-%m-%Y",
        errors="raise"
    )

    if not df["Piiriületuse kpv"].dt.year.eq(aasta).all():
        raise ValueError(f"{aasta}: CSV sisaldab vale aasta kuupäevi")

    if df["Piiriületuse kpv"].max().date() > date.today():
        raise ValueError(f"{aasta}: CSV sisaldab tulevikukuupäevi")

    df["aasta"] = df["Piiriületuse kpv"].dt.year
    df["kuu"] = df["Piiriületuse kpv"].dt.month
    df["paev"] = df["Piiriületuse kpv"].dt.day
    df["nadalapaev"] = df["Piiriületuse kpv"].dt.dayofweek
    df["nadal"] = df["Piiriületuse kpv"].dt.isocalendar().week.astype(int)

    print(
        f"{aasta}: {len(df):,} piiriületust; "
        f"viimane päev {df['Piiriületuse kpv'].max().date()}"
    )

    return df


def koonda_paevad(df, arv):
    grupid = [
        "Piiriületuse kpv",
        "aasta",
        "kuu",
        "paev",
        "nadalapaev",
        "nadal",
        *TUNNUSED,
    ]

    tulemus = (
        df.groupby(grupid, observed=True, dropna=False)
        .size()
        .reset_index(name=arv)
    )

    if int(tulemus[arv].sum()) != len(df):
        raise ValueError("Päevapõhiste andmete kogusumma ei klapi")

    return tulemus


def koonda_kuud(df, arv):
    # Võtame ainult allikas kaetud, juba lõppenud kuud.
    valmis = []

    for aasta, osa in df.groupby("aasta"):
        viimane = osa["Piiriületuse kpv"].max().date()

        for kuu in range(1, 13):
            kuupaev = date(
                int(aasta),
                kuu,
                calendar.monthrange(int(aasta), kuu)[1]
            )

            if viimane >= kuupaev and date.today() > kuupaev:
                valmis.append((int(aasta), kuu))

    kuud = pd.MultiIndex.from_frame(
        df[["aasta", "kuu"]]
    )

    df = df.loc[
        kuud.isin(pd.MultiIndex.from_tuples(
            valmis, names=["aasta", "kuu"]
        ))
    ].copy()

    df["Kuupäev"] = (
        df["Piiriületuse kpv"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    grupid = [
        "Kuupäev", "aasta", "kuu", *TUNNUSED
    ]

    tulemus = (
        df.groupby(grupid, observed=True, dropna=False)
        .size()
        .reset_index(name=arv)
    )

    if int(tulemus[arv].sum()) != len(df):
        raise ValueError("Kuupõhiste andmete kogusumma ei klapi")

    print("Täielikud kuud:", valmis)

    return tulemus


def yhenda_ajalugu(vana, uus, arv):
    # 2016–2025 säilivad muutumatuna.
    ajalugu = vana.loc[
        vana["aasta"] < ALGUSAASTA
    ].copy()

    tulemus = pd.concat(
        [ajalugu, uus],
        ignore_index=True
    )

    tulemus = tulemus[vana.columns.tolist()]

    tulemus["aasta"] = tulemus["aasta"].astype("int16")
    tulemus["kuu"] = tulemus["kuu"].astype("int8")

    for veerg in ("paev", "nadalapaev", "nadal"):
        if veerg in tulemus.columns:
            tulemus[veerg] = tulemus[veerg].astype("int8")

    for veerg in TUNNUSED:
        tulemus[veerg] = tulemus[veerg].astype("category")

    tulemus[arv] = tulemus[arv].astype("int64")

    kp = (
        "Piiriületuse kpv"
        if "Piiriületuse kpv" in tulemus.columns
        else "Kuupäev"
    )

    tulemus[kp] = (
        pd.to_datetime(tulemus[kp])
        .astype("datetime64[us]")
    )

    return tulemus.sort_values(
        [kp, *TUNNUSED]
    ).reset_index(drop=True)


def sama_sisu(vana, uus):
    if len(vana) != len(uus):
        return False

    if vana.columns.tolist() != uus.columns.tolist():
        return False

    veerud = vana.columns.tolist()

    a = vana.sort_values(veerud).reset_index(drop=True)
    b = uus.sort_values(veerud).reset_index(drop=True)

    try:
        pd.testing.assert_frame_equal(
            a,
            b,
            check_dtype=False,
            check_categorical=False
        )
        return True
    except AssertionError:
        return False


def tootle_suund(nimi, info):
    print(f"\n{'=' * 55}")
    print("TÖÖTLEN:", nimi)

    aasta_now = date.today().year

    if aasta_now > LOPPAASTA:
        raise ValueError(
            f"Lisa enne {aasta_now}. aastat uue aasta tugi"
        )

    osad = {}

    for aasta in range(ALGUSAASTA, aasta_now + 1):
        df = lae_csv(info, aasta)

        if df is not None:
            osad[aasta] = df

    if ALGUSAASTA not in osad:
        raise ValueError("2026. aasta lähtefail puudub")

    arv = info["arv"]

    vana_paev = pd.read_parquet(
        ANDMEKAUST / info["paeva_fail"]
    )

    vana_kuu = pd.read_parquet(
        ANDMEKAUST / info["kuu_fail"]
    )

    for aasta, df in osad.items():
        vana_osa = vana_paev.loc[
            vana_paev["aasta"] == aasta
        ]

        if not vana_osa.empty:
            vana_summa = int(vana_osa[arv].sum())

            if len(df) < vana_summa:
                raise ValueError(
                    f"{nimi} {aasta}: kogumaht vähenes "
                    f"{vana_summa} -> {len(df)}"
                )

            vana_viimane = (
                vana_osa["Piiriületuse kpv"].max().date()
            )

            uus_viimane = (
                df["Piiriületuse kpv"].max().date()
            )

            if uus_viimane < vana_viimane:
                raise ValueError(
                    f"{nimi} {aasta}: viimane kuupäev liikus tagasi"
                )

    # Kui 2027 CSV puudub, ei tohi juba avaldatud
    # 2027 andmeid kogemata ära kustutada.
    aastad_failis = set(
        vana_paev.loc[
            vana_paev["aasta"] >= ALGUSAASTA,
            "aasta"
        ].astype(int)
    )

    if not aastad_failis.issubset(osad.keys()):
        raise ValueError(
            f"{nimi}: mõne juba avaldatud aasta CSV puudub"
        )

    df = pd.concat(
        list(osad.values()),
        ignore_index=True
    )

    uus_paev = koonda_paevad(df, arv)
    uus_kuu = koonda_kuud(df, arv)

    paevad = yhenda_ajalugu(
        vana_paev, uus_paev, arv
    )

    kuud = yhenda_ajalugu(
        vana_kuu, uus_kuu, arv
    )

    # Ajalugu peab säilima täpselt.
    for vana, uus in [
        (vana_paev, paevad),
        (vana_kuu, kuud),
    ]:
        vana_ajalugu = vana.loc[
            vana["aasta"] < ALGUSAASTA
        ]

        uus_ajalugu = uus.loc[
            uus["aasta"] < ALGUSAASTA
        ]

        if not sama_sisu(vana_ajalugu, uus_ajalugu):
            raise ValueError(
                f"{nimi}: ajaloolised andmed muutusid"
            )

    print("Päevapõhiseid ridu:", len(paevad))
    print("Kuupõhiseid ridu:", len(kuud))
    print("Valideerimine: KORRAS")

    return {
        info["paeva_fail"]: paevad,
        info["kuu_fail"]: kuud,
    }


def avalda_failid(muudetud):
    if not muudetud:
        print("Andmed pole muutunud. Avaldamist pole vaja.")
        return

    VARUKOOPIAD.mkdir(parents=True, exist_ok=True)

    varukoopia = (
        VARUKOOPIAD
        / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )

    varukoopia.mkdir()

    for fail in muudetud:
        shutil.copy2(
            ANDMEKAUST / fail,
            varukoopia / fail
        )

    try:
        for fail in muudetud:
            ajutine = ANDMEKAUST / f"{fail}.tmp"

            shutil.copy2(
                KONTROLLKAUST / fail,
                ajutine
            )

            os.replace(
                ajutine,
                ANDMEKAUST / fail
            )

            print("AVALDATUD:", fail)

    except Exception:
        for fail in muudetud:
            (ANDMEKAUST / f"{fail}.tmp").unlink(
                missing_ok=True
            )

            shutil.copy2(
                varukoopia / fail,
                ANDMEKAUST / fail
            )

        raise

    print("Avaldamine lõpetatud")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--publish",
        action="store_true"
    )

    args = parser.parse_args()

    tulemused = {}

    for nimi, info in ALLIKAD.items():
        tulemused.update(
            tootle_suund(nimi, info)
        )

    # Valideerime kõik enne ühegi faili muutmist.
    KONTROLLKAUST.mkdir(parents=True, exist_ok=True)

    muudetud = []

    for fail, df in tulemused.items():
        vana = pd.read_parquet(ANDMEKAUST / fail)

        if sama_sisu(vana, df):
            print("MUUTUMATU:", fail)
            continue

        tee = KONTROLLKAUST / fail
        df.to_parquet(tee, index=False)

        kontroll = pd.read_parquet(tee)

        if not sama_sisu(df, kontroll):
            raise ValueError(
                f"Salvestatud fail ei klapi: {fail}"
            )

        muudetud.append(fail)
        print("MUUTUNUD:", fail)

    print(f"\nMuudetud faile: {len(muudetud)}")

    if args.publish:
        avalda_failid(muudetud)
    else:
        print("Kontrollrežiim: originaalfaile ei muudetud")


if __name__ == "__main__":
    main()
