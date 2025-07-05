# treti_projekt
Třetí projekt na Python Akademii Engeto
# Popis projektu
Tento script slouží k extrahování výsledků parlamentních voleb v roce 2017. Odkaz k prohlédnutí najdete [zde](https://https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ).
# Instalace knihoven
Knihovny, které jsou použity v kódu jsou uložené v souboru requirements.txt.
Pro instalaci doporučuji použít nové virtuální prostředí a s naistalovaným manažerem spustit následovně:

**$ pip3 --version**   *# ověřím verzi manažeru*

**$ pip3 install -r requirements.txt**        *# nainstalujeme knihovny*
# Spuštění projektu
Spuštění souboru main.py v rámci příkazového řádku požaduje dva povinné argumenty.

main.py <odkaz_uzemniho_celku> <nazev_souboru.csv>

Následně se vám stáhnou výsledky jako soubor s příponou .csv.
# Ukázka projektu
1. argument `https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100`

2. argument `vysledky_Praha.csv`

Spuštění programu:

`python main.py 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100' vysledky_Praha.csv`

Průběh stahování:

`STAHUJI DATA Z VYBRANÉHO URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100`

`UKLÁDÁM DATA DO SOUBORU: vysledky_Praha.csv`

`UKONČUJI PROGRAM`

Částečný výstup:

`Kód obce;Název obce;Voliči v seznamu;Vydané obálky;Platné hlasy;...`

`500054;Praha 1;21 556;14 167;14 036;2 770;9;13;657;12;1;774;392;514;41;6;241;14;44;2 332;5;0;12;2 783;1 654;1;7;954;3;133;11;2;617;34`

`500224;Praha 10;79 964;52 277;51 895;8 137;40;34;3 175;50;17;2 334;2 485;1 212;230;15;1 050;35;67;9 355;9;8;30;6 497;10 856;37;53;2 398;12;477;69;53;2 998;162`

`...`
