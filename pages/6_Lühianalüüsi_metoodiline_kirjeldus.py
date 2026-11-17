
import streamlit as st

st.title("Metoodiline kirjeldus")

# ---------------------------------
# 1. SISSEJUHATUS JA PROBLEEMI PÜSTITUS
# ---------------------------------

st.subheader("1. Sissejuhatus ja probleemi püstitus")

st.markdown("**Teema tutvustus**")

st.write("""
Piiriületusega seotud probleemid sõltuvad suuresti sellest, kas tegemist on Euroopa Liidu (edaspidi EL) sisepiiriga (Schengeni ala) või välispiiriga. Välispiiril on olulisteks probleemideks ebaseaduslik ränne, piiriülene kuritegevus, salakaubandus ja julgeolekuohud. **Politsei- ja Piirivalveameti** (edaspidi PPA) peamine ülesanne on piirikontrolli teostamisel tõkestada **seadusevastast piiriületamist**, **ebaseaduslikku rännet** ning **piiriülest kuritegevust**, tagades sellega riikliku sisejulgeoleku ja ennetades võimalikke ohte.

Ebaseadusliku rände tugevaks kujundajaks on jätkuv **geopoliitiline ebastabiilsus**, **muutuv julgeolekukeskkond** ning **Euroopa riikide demograafilised ja tööturuvajadused**. Venemaa täiemahuline sõda Ukrainas jätkub ning konfliktid Lähis-Idas, mitmel pool Aafrikas ja mujal maailmas põhjustavad rahvaste sundrännet. Kõikidest mõjuteguritest hoolimata vähenesid 2025. aastal mitmed ELi rändesurvet iseloomustavad näitajad (EMN Eesti, 2026): langesid nii esmakordsete rahvusvahelise kaitse taotluste arv kui ka ELi välispiiridel tuvastatud ebaseaduslike piiriületuste arv.

Eesti rändeolukorda mõjutas 2025. aastal jätkuvalt Venemaa sõda Ukrainas ja sellest tulenevad piirangud Venemaa ja Valgevene kodanikele. Esmakordsete tähtajaliste elamislubade arv langes ligikaudu veerandi võrra võrreldes 2024. aastaga.

Hoolimata heitlikust **geopoliitilisest olukorrast** saabus kolmandate riikide kodanikke Euroopa Liitu ebaseaduslikke rändeteid pidi oluliselt vähem kui kahel varasemal aastal. Peamiseks sisenemiskohaks oli Kesk-Vahemere rändetee, mille kaudu registreeriti üle kolmandiku kõigist teatatud ebaseadusliku rände juhtumitest. Kõige sagedamini ületasid Euroopa Liidu piiri Bangladeshi (13%), Egiptuse (10%) ja Afganistani (9%) kodanikud (EMN Eesti, 2026).

Eeltoodud arengud näitavad, et riigipiiri ületamisega seotud olukord ei sõltu üksnes üldisest rändesurvest, vaid seda mõjutavad ka **geopoliitilised sündmused**, **riikidevahelised suhted** ning **riigisisesed korralduslikud ja õiguslikud meetmed**. Nende tegurite mõju võib väljenduda piiriületuste koguarvu muutumises, kuid samuti piiriületuste ajalises jaotuses, kodakondsuste struktuuris ning piiripunktide kasutamise intensiivsuses. Seetõttu ei anna üksnes piiriületuste koguarvu jälgimine piisavat ülevaadet Eesti riigipiiril toimuvatest muutustest ega võimalda hinnata, millised piiripunktid võivad vajada piiriturvalisuse tagamisel suuremat tähelepanu.

Sellest tulenevalt on **oluline analüüsida** kolmandate riikide kodanike piiriületuste dünaamikat ja struktuuri Eestis, võttes arvesse nii **geopoliitiliste sündmuste** kui ka **Eesti siseriiklike korralduslike meetmete võimalikku mõju**.
""")

st.markdown("**Uurimisprobleem**")

st.write("""
Kuidas kajastuvad geopoliitilised sündmused ja Eesti siseriiklikud korralduslikud meetmed kolmandate riikide kodanike piiriületuste mahus ja struktuuris Eesti riigipiiril ning kuidas võimaldab piiriületuste dünaamika ja struktuuri analüüs tuvastada piiriturvalisuse seisukohalt suuremat tähelepanu vajavaid piiripunkte?
""")

st.markdown("**Alaprobleem**")

st.write("""
Kui hästi kajastab piiriületusandmetes registreeritud kodakondsus isikute tegelikku kodakondsuslikku tausta ning milliseid piiranguid seab võimalik mitmikkodakondsus piiriületuste struktuuri ja julgeolekuriskide hindamisele?
""")

st.write("""
**Uurimistöö eesmärk**

Uurimistöö eesmärk on analüüsida Politsei- ja Piirivalveameti piiriületusandmete põhjal kolmandate riikide kodanike piiriületuste **dünaamikat ja struktuuri Eesti riigipiiril aastatel 2021–2025**. Analüüs keskendub Eestisse **siseneval suunal** toimunud piiriületustele, mida vaadeldakse kahes lõikes: maismaapiiri ja õhupiiri kaudu toimunud piiriületused. Eesmärk on tuvastada piiriületustes toimunud olulisemad muutused ning hinnata nende võimalikku seost geopoliitiliste sündmuste ja Eesti siseriiklike korralduslike meetmetega. Lisaks koostatakse ajalooliste andmete põhjal piiriületuste **prognoos aastateks 2026–2027**, et hinnata võimalikke edasisi arengusuundi ja tuvastada piiriturvalisuse seisukohalt tähelepanu väärivaid muutusi.
""")

# ---------------------------------
# 2. UURIMISTÖÖ METOODIKA
# ---------------------------------

st.subheader("2. Uurimistöö metoodika")

st.write("""
Uurimistöös kasutatakse **kvantitatiivset sekundaarandmete analüüsi meetodit**. Analüüsi aluseks on Politsei- ja Piirivalveameti avaandmed Eesti riigipiiri ületuste kohta. Aastate 2021–2025 andmeid kasutatakse piiriületuste ajaloolise dünaamika ja struktuuri analüüsimiseks. 2026. aasta jaanuari–oktoobri tegelikke andmeid kasutatakse prognoosimudelite valideerimiseks ja prognooside koostamiseks. 2026. aasta novembrit ja detsembrit ning 2027. aastat käsitletakse prognoosiperioodina.

Andmeid töödeldakse Pythoni abil ning analüüsitakse statistiliste meetodite ja visualiseerimise kaudu, et kirjeldada piiriületuste ajalist dünaamikat ja struktuuri ning võrrelda muutusi erinevate tunnuste ja piiripunktide lõikes.
""")

st.markdown("**Andmeallikad ja andmestiku kirjeldus**")

st.write("""
Analüüsi aluseks on PPA kodulehel avaldatud isikute piiriületusandmed Eesti siseneval suunal aastatest 2021–2026. Andmed sisaldavad muu hulgas piiriületuse kuupäeva, piiripunkti, kodakondsust, riikide gruppi, sugu, vanuserühma ja piiriületuse suunda.

Andmed kajastavad registreeritud piiriületusi, mitte unikaalsete isikute arvu. Seetõttu võib sama isik andmestikus esineda mitmel korral, kui ta ületab riigipiiri korduvalt.

Algandmed imporditi CSV-failidest Pandase teegi abil Jupyter Notebooki ning ühendati ühtseks andmestikuks. Ajaloolise analüüsi jaoks kasutati aastaid 2021–2025. Prognoosimudelite koostamiseks ja hindamiseks kasutati lisaks 2026. aasta jaanuari–oktoobri tegelikke andmeid.
""")

st.markdown("**Andmete töötlemine ja analüüs**")

st.write("""
Andmete töötlemisel kontrolliti nende kvaliteeti, andmetüüpe ja puuduvaid väärtusi. Eemaldati korduvat teavet sisaldav veerg ning kategooriliste tunnuste andmetüübid muudeti mälukasutuse vähendamiseks. Selle tulemusena vähenes andmestiku mälukasutus 831 MiB-lt 220 MiB-ni ehk ligikaudu 73,5%.

Ajalise analüüsi võimaldamiseks loodi kuupäeva põhjal aasta, kuu, päeva, nädalapäeva ja nädala tunnused. Analüüsiks moodustati koondandmestikud, mis võimaldasid võrrelda piiriületusi kodakondsuse, riikide grupi, soo, vanuserühma ja piiripunktide lõikes. Piiripunktide hooajalisuse hindamiseks arvutati hooajalisuse indeks. Töödeldud andmestik salvestati Parquet-vormingus.

Prognoosimiseks koostati eraldi andmestik, milles käsitleti ainult maismaa- ja õhupiiri ületusi. Tegelikult esinenud tunnuste kombinatsioonidele loodi aastate ja kuude kalender ning puuduvate kuiste vaatluste piiriületuste arvuks määrati null. 2026. aasta tegelikud andmed hõlmasid jaanuari–oktoobrit; novembrit ja detsembrit käsitleti prognoosiperioodina.

Lisaks loodi kaheksa sündmuste ja korralduslike meetmetega seotud tunnust, mis kirjeldasid piiripunktide lahtiolekut, ajutist piirikontrolli, sõidukipiiranguid ja automaatsete kontrollisüsteemide kasutuselevõttu. Tunnuste väärtused arvutati sündmuste kehtivusaja põhjal kuude lõikes, et võimaldada prognoosimudelitel arvestada piiripunktide töökorralduse muutustega.

Prognoosimudelite hindamisel kasutati ajalist tagasitestimist (rolling-origin backtesting), mille puhul treeningandmed pärinesid alati prognoositavale perioodile eelnenud ajast. Selline lähenemine võimaldab hinnata mudelite prognoosivõimet erinevatel ajaperioodidel ning aitab vältida tulevikuinfo sattumist mudeli treeningandmetesse.
""")

# ---------------------------------
# ANDMESTIKU KLASSIFIKATSIOONI KONTROLL
# ---------------------------------

st.markdown("**Andmestiku klassifikatsiooni järjepidevuse kontroll**")

st.write("""
Lisaks kontrolliti PPA andmestikus kasutatava tunnuse „Riikide grupp“ ajalist klassifikatsiooni, võrreldes seda riikide ametliku Euroopa Liidu ja Schengeni liikmesuse ajalooga. Kontrollimisel ilmnesid Bulgaaria, Rumeenia ja Horvaatia puhul ajalised lahknevused.

Bulgaaria ja Rumeenia puhul esines 2025. aasta alguses paralleelselt mitu riikide grupi kategooriat. Mõlema riigi esimesed Schengeni kategooria kirjed ilmusid 28. märtsil 2025. Kuni 14. maini 2025 esinesid andmestikus paralleelselt kategooriad „EL/EMP/CH“ ja „Schengen, EL/EMP/CH“. Erinevused puudutasid Bulgaaria puhul 766 ja Rumeenia puhul 1460 piiriületust. Alates 2025. aasta juunist erinevusi enam ei esinenud.

Horvaatia puhul ilmnes vastupidine olukord. PPA andmestikus esines kategooria „Schengen, EL/EMP/CH“ juba alates 11. augustist 2021, kuigi Horvaatia liitus Schengeni alaga 1. jaanuaril 2023. Varasema klassifikatsiooniga oli seotud kokku 556 piiriületust.

Tulemused osutavad PPA riikide grupi ajalise klassifikatsiooni ebajärjekindlusele võrreldes ametliku Schengeni liikmesuse ajalooga. Bulgaaria ja Rumeenia puhul ilmneb hilisem üleminek Schengeni kategooriasse, Horvaatia puhul aga varasem üleminek. Tegemist on erinevustega ametliku liikmesuse põhjal koostatud kontrollreegli ja lähteandmestiku klassifikatsiooni vahel, mitte tõendiga algandmete ebaõigsuse kohta. Kõik kolm riiki olid kogu vaadeldava perioodi jooksul EL-i liikmesriigid ning nende kodanikke ei käsitleta uurimistöös kolmandate riikide kodanikena.
""")


# ---------------------------------
# KLASSIFIKATSIOONI VISUAALNE KONTROLL
# ---------------------------------
with st.expander("Vaata Bulgaaria, Rumeenia ja Horvaatia klassifikatsiooni graafikut", expanded=False):
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    andmed = st.session_state["andmed_df"]
    uuritavad = {
        "Bulgaaria Vabariik": ("Bulgaaria", "2025-01-01"),
        "Rumeenia": ("Rumeenia", "2025-01-01"),
        "Horvaatia Vabariik": ("Horvaatia", "2023-01-01"),
    }
    varvid = {"EL/EMP/CH": "#E69F00", "Schengen, EL/EMP/CH": "#178939"}
    kontroll = andmed.loc[
        andmed["Kodakondsus"].isin(uuritavad),
        ["Kodakondsus", "Riikide grupp", "aasta", "kuu"]
    ].copy()
    kuude_kaupa = (kontroll.groupby(
        ["Kodakondsus", "aasta", "kuu", "Riikide grupp"], observed=True
    ).size().reset_index(name="Piiriületusi"))
    kuude_kaupa["Kuupäev"] = pd.to_datetime(dict(
        year=kuude_kaupa["aasta"], month=kuude_kaupa["kuu"], day=1
    ))

    joonis = make_subplots(
        rows=3, cols=1,
        subplot_titles=[v[0] for v in uuritavad.values()],
        shared_xaxes=True, vertical_spacing=0.10
    )
    for rida, (kodakondsus, (nimi, kuupaev)) in enumerate(uuritavad.items(), 1):
        for kategooria, varv in varvid.items():
            osa = kuude_kaupa.loc[
                (kuude_kaupa["Kodakondsus"] == kodakondsus)
                & (kuude_kaupa["Riikide grupp"] == kategooria)
            ].sort_values("Kuupäev")
            joonis.add_trace(go.Bar(
                x=osa["Kuupäev"], y=osa["Piiriületusi"],
                name=kategooria, legendgroup=kategooria,
                marker_color=varv, showlegend=(rida == 1),
                hovertemplate="%{x|%m.%Y}<br>Piiriületusi: %{y:,}<extra></extra>"
            ), row=rida, col=1)
        # Kuupäev antakse stringina, et Plotly datetime-telje vertikaaljoon töötaks.
        joonis.add_vline(
            x=kuupaev, line_dash="dash", line_color="#D62728",
            line_width=2, row=rida, col=1
        )

    joonis.update_layout(
        title="Lähteandmestiku klassifikatsioon vs ametlik Schengeniga liitumine",
        height=910, barmode="group", legend_title="PPA riikide grupp",
        margin=dict(l=45, r=25, t=85, b=50)
    )
    joonis.update_xaxes(tickformat="%Y", title_text="Aeg", row=3, col=1)
    joonis.update_yaxes(title_text="Piiriületusi")
    st.plotly_chart(joonis, width="stretch")
    st.caption(
        "Punane katkendjoon tähistab Schengeni liikmesuse algust. "
        "Graafik kasutab kogu PPA andmestikku, mitte külgribal valitud filtreid. "
        "Riikide grupi klassifikatsioon ei muuda nende riikide ELi kodakondsust."
    )

st.markdown("**Uurimise piirangud**")

st.write("""
**1. Piiriületusandmete piirangud.**

Piiriületuste arv kajastab registreeritud piiriületusi, kuid ei näita iseenesest kõiki sisenemiskatseid ega juhtumeid, kus isikule sisenemist ei võimaldatud. Seetõttu ei saa üksnes nende andmete põhjal hinnata, kui palju on konkreetsed meetmed Eestisse sisenemist takistanud.

**2. Põhjuslike seoste hindamise piirangud.**

Geopoliitiliste sündmuste ja korralduslike meetmete ajaline kokkulangevus piiriületuste muutustega ei tõenda iseenesest põhjuslikku seost. Tulemuste tõlgendamisel tuleb arvestada ka teiste võimalike mõjuteguritega.

**3. Kodakondsuse kui julgeolekuriski hindamise tunnuse piirangud.**

Kodakondsus on oluline tunnus piiriületuste struktuuri analüüsimisel, kuid see ei pruugi kajastada isiku kogu kodakondsuslikku tausta ega võimalikke riiklikke seoseid. Mitmikkodakondsuse ja kodakondsuse omandamise erinevate praktikate levik võib piirata üksnes registreeritud kodakondsusel põhineva riskihindamise täpsust. Seetõttu tuleb piiriületuste analüüsimisel arvestada, et kodakondsus ei ole iseseisvalt piisav alus isiku või piiripunkti julgeolekuriski hindamiseks.

**4. Prognoosimudelite piirangud.**

Prognoosimudelid põhinevad ajaloolistel andmetel ja neis kasutatud tunnustel. Geopoliitilised sündmused, ootamatud piirangud ja muud järsud muutused võivad prognoositäpsust mõjutada. Samuti sõltub väliseid tunnuseid kasutavate mudelite prognoosivõime sellest, kas prognoosiperioodi kohta on olemas piisavalt usaldusväärne ja õigel ajal teada olnud info.
""")


# ---------------------------------
# 3. ANALÜÜS JA TULEMUSED
# ---------------------------------

st.subheader("3. Analüüs ja tulemused")

st.markdown("**3.1 Piiriületuste dünaamika**")

st.write("""
Aastatel 2021–2025 suurenes kolmandate riikide kodanike registreeritud
Eestisse sisenemiste arv 25,2%, samal ajal kui kõigi riikide gruppide
piiriületuste arv suurenes 69,1%.

See erinevus näitab, et üldise piiriületuste mahu kasv ei tähenda
samaväärset kasvu kolmandate riikide kodanike seas. Seetõttu tuleb
piiriületuste dünaamikat hinnata eraldi riikide gruppide ja piiripunktide
lõikes, mitte piirduda riikliku koguarvuga.

Piiripunktide võrdluses ilmnesid märkimisväärsed muutused. Näiteks
Narva-1 piiripunktis vähenes registreeritud sisenemiste arv
aastatel 2024–2025 ligikaudu 40,3% ehk 196 816 piiriületuse võrra.

Sellised muutused viitavad vajadusele jälgida piiripunktide
töökoormuse ümberjaotumist ning võrrelda dünaamikat ka hooajaliste
ja töökorralduslike teguritega.
""")

st.markdown("**3.2 Piiriületuste struktuur**")

st.write("""
Piiriületuste struktuuri analüüs näitas, et eri kodakondsustega
isikute sisenemiste mahud, ajalised muutused ja kasutatavad
piiripunktid võivad märkimisväärselt erineda.

Kodakondsuste võrdluses väärivad täiendavat tähelepanu näiteks
Serbia ja Iisraeli kodanike piiriületuste mahu kasv ning
maismaapiiri kasutamise osakaal.

Soolise ja vanuselise struktuuri analüüs võimaldab täiendavalt
kirjeldada piiriületuste koosseisu ning jälgida, kas muutused
piiripunktides puudutavad erinevaid rahvastikurühmi sarnaselt
või erinevalt.

Oluline on eristada piiriületuste arvu isikute arvust:
üks inimene võib vaadeldaval perioodil piiri ületada korduvalt.

Registreeritud kodakondsus kirjeldab andmestikus esitatud
kodakondsust, kuid ei võimalda tuvastada inimese võimalikku
mitmikkodakondsust. Seetõttu ei saa üksnes kodakondsuste ja
piiripunktide kasutusmustrite põhjal teha järeldusi
isikute julgeolekuriski kohta.
""")

st.markdown(
    "**3.3 Geopoliitiliste sündmuste ja korralduslike meetmete võimalik seos**"
)

st.write("""
Piiriületuste ajalises dünaamikas esinevaid muutusi tuleb
tõlgendada koos geopoliitilise olukorra ning Eesti riigipiiril
rakendatud korralduslike ja õiguslike meetmetega.

Vaadeldavat perioodi mõjutasid muu hulgas Venemaa täiemahuline
sõda Ukrainas, Venemaa ja Valgevene kodanikele kehtestatud
piirangud ning piiripunktide töökorralduse muudatused.

Prognoosimudelite jaoks loodi kaheksa sündmuste ja korralduslike
meetmetega seotud tunnust. Need kirjeldavad muu hulgas
piiripunktide lahtiolekut, ajutist piirikontrolli,
sõidukipiiranguid ja automaatsete kontrollisüsteemide
kasutuselevõttu.

Tunnused võimaldavad analüüsida, kas teadaolevate sündmuste
ja meetmete kehtivusperioodid langevad ajaliselt kokku
piiriületuste mahu muutustega.

Samas ei tõenda ajaline kokkulangevus põhjuslikku seost.
Näiteks võib piiriületuste vähenemine olla seotud mitme
samaaegselt toimiva teguriga, mida kasutatav andmestik
ei võimalda üksteisest täielikult eristada.

Seetõttu käsitletakse tuvastatud muutusi täiendavat
uurimist vajavate tähelepanekutena, mitte tõendina
konkreetse meetme otsesest mõjust.
""")

st.markdown("**3.4 Piiriületuste prognoos aastateks 2026–2027**")

st.write("""
Piiriületuste edasise dünaamika hindamiseks koostati ja
võrreldi erinevaid prognoosimudeleid, sealhulgas
A7 SARIMAX-mudelit ja A9 mudelit.

Mudelite hindamisel kasutati ajalist tagasitestimist,
mille korral mudelid treeniti ainult prognoositavale
perioodile eelnenud andmetel.

A7 mudeli 46-kuulise tagasitestimise tulemuseks oli
keskmine absoluutviga (MAE) 15 838,66 piiriületust
ja kaalutud absoluutne protsentviga (WAPE) 18,12%.

A9 mudeli 18-kuulise treeningaknaga katse WAPE oli 26,45%.
Neid tulemusi ei saa siiski automaatselt käsitleda
mudelite lõpliku järjestusena, kui hindamisperioodid
või prognoositingimused erinevad.

Tulemused näitavad, et keerukama mudeli kasutamine
ei taga iseenesest väiksemat prognoosiviga.

2026. aasta jaanuari–oktoobri registreeritud sisenemised
on tegelikud andmed. Novembrit ja detsembrit ning
2027. aastat käsitletakse prognoosiperioodina.

Prognoose saab kasutada piiripunktide võimalike
koormusmuutuste jälgimiseks, kuid need ei kirjelda
kindlalt tulevikus realiseeruvaid piiriületuste mahtusid.
""")

# ---------------------------------
# 4. ARUTELU JA KOKKUVÕTE
# ---------------------------------

st.subheader("4. Arutelu ja kokkuvõte")

st.markdown("**4.1 Tulemuste tõlgendamine**")

st.write("""
Uurimistöö tulemused osutavad, et Eesti riigipiiril
registreeritud sisenemiste koguarv ei anna üksinda
piisavat ülevaadet kolmandate riikide kodanike
piiriületuste dünaamikast ja struktuurist.

Kolmandate riikide kodanike piiriületuste kasv erines
märkimisväärselt kõigi riikide gruppide kogukasvust.
Samuti ilmnesid üksikute piiripunktide lõikes
suured muutused, mida riiklik kogunäitaja võib varjata.

Narva-1 piiripunktis toimunud oluline vähenemine
näitab, miks piiripunktide töökoormust tuleb hinnata
eraldi ning võrrelda seda varasemate perioodidega.

Geopoliitilised sündmused ja riigisisesed korralduslikud
meetmed annavad muutuste tõlgendamiseks olulise tausta.
Samas ei võimalda kirjeldav andmeanalüüs määrata,
millise osa muutusest põhjustas konkreetne sündmus
või piirang.
""")

st.markdown("**4.2 Vastus uurimisprobleemile**")

st.write("""
Geopoliitilised sündmused ja Eesti siseriiklikud
korralduslikud meetmed võivad piiriületusandmetes
kajastuda nii sisenemiste koguarvu muutumisena kui ka
erinevustena kodakondsuste, piiripunktide ja
ajaperioodide lõikes.

Piiriületuste dünaamika ja struktuuri analüüs
võimaldab tuvastada piiripunkte, kus esinevad
ebatavaliselt suured muutused, koormuse
ümberjaotumine või prognoosist kõrvalekaldumised.

Sellised tähelepanekud annavad aluse täiendavaks
kontrolliks ning töökorralduslike otsuste kaalumiseks,
kuid ei tõenda iseenesest julgeolekuohu olemasolu.
""")

st.markdown("**4.3 Vastus alaprobleemile**")

st.write("""
PPA andmestikus registreeritud kodakondsus on
kasulik piiriületuste struktuuri kirjeldamiseks,
kuid selle põhjal ei saa kindlaks teha isiku
kõiki võimalikke kodakondsusi.

Kui inimesel on mitu kodakondsust, ei pruugi
ühes piiriületuskirjes esitatud kodakondsus
kajastada tema kogu kodakondsuslikku tausta.

Seetõttu ei võimalda kasutatav andmestik hinnata
mitmikkodakondsuse tegelikku levimust ega selle
võimalikku seost piiriületuste mustritega.

Registreeritud kodakondsus ei ole iseseisvalt
piisav alus julgeolekuriski määramiseks.
""")

st.markdown("**4.4 Praktilised soovitused**")

st.markdown("""
1. **Jälgida piiriületusi piiripunktide kaupa.**
   Riikliku koguarvu kõrval tuleb regulaarselt analüüsida
   üksikute piiripunktide sisenemiste mahtu, muutust
   ja osakaalu.

2. **Võrrelda muutusi teadaolevate sündmuste ja meetmetega.**
   Oluliste kõrvalekallete korral tuleb kontrollida
   piiripunktide töökorraldust, piirangute kehtivust,
   hooajalisust ja muid võimalikke mõjutegureid.

3. **Kasutada prognoose töökoormuse seire abivahendina.**
   Tegelike sisenemiste ja prognooside erinevusi
   tuleks jälgida samade riikide gruppide,
   piiritüüpide ja piiripunktide lõikes.
   Suuremad kõrvalekalded võivad viidata
   täiendava analüüsi vajadusele.
""")

st.markdown("**4.5 Kokkuvõttev järeldus**")

st.write("""
Uurimistöö peamine järeldus on, et piiriületuste
koguarvu jälgimisest ei piisa Eesti riigipiiril
toimuvate muutuste mõistmiseks.

Piiriületuste ajalise dünaamika, kodakondsusliku
struktuuri, piiripunktide kasutamise ja prognooside
ühine analüüs loob parema aluse tähelepanu vajavate
muutuste varajaseks tuvastamiseks.

Analüüsi tulemused võivad toetada piirikontrolli
töökorralduse ja ressursside planeerimist,
kuid nende põhjal ei saa üksi teha järeldusi
ebaseadusliku rände, konkreetsete isikute
või piiripunktide julgeolekuriski kohta.
""")


# ---------------------------------
# 5. TEHISARU KASUTAMINE
# ---------------------------------

st.subheader("5. Tehisaru kasutamine")

st.write("""
**Tehisaru** kasutati projekti käigus abivahendina **Pythoni** päringute koostamisel ja selgitamisel, andmemudeli ülesehituse arutamisel, andmekvaliteedi kontrollide kavandamisel, analüüsivõimaluste leidmisel ning dokumentatsiooni struktureerimisel ja sõnastamisel.

Tehisaru kasutati ka prognoosimudelite metoodika arutamisel ja võimalike lahenduste hindamisel. Tehisaru väljundeid ei käsitletud automaatselt õigete tulemustena. Pythoni lahendusi kontrolliti tegelike andmete ja mõõdikute tulemuste põhjal ning vajadusel parandati. Eriti oluline oli kontroll olukordades, kus tulemus sõltus andmemudeli seostest, tabelite kategoriseerimisest või konkreetse välja tähendusest.

Lõplikud analüütilised tulemused ja järeldused põhinevad projekti andmetel ja autori tehtud analüüsil, mitte tehisaru genereeritud tulemustel.
""")

# ---------------------------------
# 6. KASUTATUD KIRJANDUS
# ---------------------------------

st.subheader("6. Kasutatud kirjandus")

st.write("""
1. Rändepoliitika aastaraport, 2026 (EMN Eesti). [Võrgumaterjal] Leitav: https://www.emn.ee/wp-content/uploads/2026/09/EMN_Randeraport-2026_A4_web_final.pdf

2. Politsei- ja Piirivalveamet (2026). *Ränne ja kodakondsus*, *Piir ja meri*. [Võrgumaterjal] Leitav: https://www.politsei.ee/et/
""")
