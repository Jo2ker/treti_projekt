"""
main.py: třetí projekt do Engeto Online Python Akademie

author: Tomáš Snětivý
email: jo2ker@seznam.cz
"""

import sys
import requests
from bs4 import BeautifulSoup
import csv


# spouštěcí argumenty
if len(sys.argv) != 3:
   print("Chyba: Nezadali jste správný počet argumentů.")
   print(f"Použití: python {sys.argv[0]} <URL> <nazev_souboru.csv>")
   sys.exit(1)

url = sys.argv[1]
csv_filename = sys.argv[2]

def ziskat_kod_nazev_obci_z_html(url):
    """
    Stáhne HTML stránku zadané URL, a z ní extrahuje seznam kódů a názvů obcí.

    Použití:
    kod_obci, nazvy_obci = ziskat_kod_nazev_obci_z_html(url)

    Args:
        url (str): URL adresu stránky, ze které se má získat data.

    Returns:
        tuple: dvojice seznamů (kod_obci, nazvy_obci)
            - kod_obci (list of str): seznam kódů obcí jako textových řetězců
            - nazvy_obci (list of str): seznam názvů obcí jako textových řetězců
    """
    odpoved = requests.get(url)
    if odpoved.status_code != 200:
        print(f"Chyba při načítání stránky {url}")
        return []
    soup = BeautifulSoup(odpoved.text, 'html.parser')
    kod_obci = []
    nazvy_obci = []

    cisla_td = soup.find_all('td', class_='cislo')
    for td in cisla_td:
        a = td.find('a')
        if a:
            kod_obci.append(a.text.strip())
    nazvy_td = soup.find_all('td', class_='overflow_name')
    for td in nazvy_td:
        nazvy_obci.append(td.text.strip())
    
    return kod_obci, nazvy_obci

def ziskat_relativni_url(url):
    """
    Stáhne HTML stránku zadané URL a extrahuje relativní odkazy na stránky s parametry ps311 a xobec.

    Použití:
    relativni_url = ziskat_relativni_url(url)

    Args:
        url (str): URL adresa stránky, kterou se načítá.

    Returns:
        - relativni_url (list of str): Seznam relativních URL fragmentů odpovídajících kritériím.
    """
    odpoved = requests.get(url)
    if odpoved.status_code != 200:
        print(f"Chyba při načítání stránky {url}")
        return []

    soup = BeautifulSoup(odpoved.text, 'html.parser')
    relativni_url = []
    for td in soup.find_all('td', class_='cislo'):
        a = td.find('a', href=True)
        if a:
            href = a['href']
            if href.startswith('ps311') and 'xobec=' in href:
                relativni_url.append(href)
    
    return relativni_url

relativni_url = ziskat_relativni_url(url)

def extrahuj_data_z_odkazu_list(relativni_url):
    """
    Na základě seznamu relativních URL načte detailní stránky a extrahuje data.

    Pro každý odkaz:
    - Připojí ho k základní URL a načte stránku.
    - Získá tři hlavní hodnoty z elementů s třídou 'td.cislo' s atributy 'headers' 'sa2', 'sa3', 'sa6'.
    - Získá tabulky uvnitř prvního a druhého divu s ID odvozeným od '#inner > div:nth-child(1)'
      a '#inner > div:nth-child(2)', z nich extrahuje data z určitých řádků a buněk.

    Výsledek:
    - Vrací seznam seznamů, kde každý podseznam obsahuje extrahovaná data z jednoho odkazu.

    Args:
        relativni_url (list of str): Seznam relativních URL fragmentů k jednotlivým stránkám.

    Returns:
        vsechny_data (list of list of str): Souhrnná data z každé stránky jako seznam seznamů řetězců.
    """
    relativni_url = ziskat_relativni_url(url)
    vsechny_data = []

    for odkaz in relativni_url:
        plny_odkaz = 'https://www.volby.cz/pls/ps2017nss/' + odkaz
        odp = requests.get(plny_odkaz)
        if odp.status_code != 200:
            continue
        soup = BeautifulSoup(odp.text, 'html.parser')
        data = []

        # extrahuj hlavni data
        for header_value in ['sa2', 'sa3', 'sa6']:
            td = soup.find('td', class_='cislo', attrs={'headers': header_value})
            if td:
                text = td.get_text(strip=True).replace('\xa0', ' ').replace('&nbsp;', ' ')
                data.append(text)

        # extrahování data z tabulek
        div1 = soup.select_one('#inner > div:nth-child(1)')
        if div1:
            table1 = div1.select_one('table')
            if table1:
                trs = table1.find_all('tr')
                for i in range(2, min(17, len(trs))):
                    tds = trs[i].find_all('td')
                    if len(tds) >= 3:
                        v = tds[2].get_text(strip=True)
                        if any(c.isdigit() for c in v):
                            data.append(v)

        div2 = soup.select_one('#inner > div:nth-child(2)')
        if div2:
            table2 = div2.select_one('table')
            if table2:
                trs = table2.find_all('tr')
                for i in range(2, min(16, len(trs))):
                    tds = trs[i].find_all('td')
                    if len(tds) >= 3:
                        v = tds[2].get_text(strip=True)
                        if any(c.isdigit() for c in v):
                            data.append(v)

        # odstraňování \xa0
        data = [item.replace('\xa0', ' ') for item in data]
        vsechny_data.append(data)
    
    return vsechny_data

def extrahovat_data_zahlavi(relativni_url):
    """
    Načte stránku dle relativní URL a extrahuje hlavní záhlaví a názvy stran, 
    poté vše zapíše do souboru 'Vysledky_Praha.csv' ve formátu CSV s kódováním UTF-8 s BOM.

    Args:
        relativni_url (list of str): Seznam relativních URL fragmentů, přičemž se používá první element.

    Returns:
        data_zahlavi (list of str): Seznam obsahující názvy hlaviček a hodnoty pro CSV zápis.
    """
    plny_odkaz = 'https://www.volby.cz/pls/ps2017nss/' + relativni_url[0]
    odpoved = requests.get(plny_odkaz)
    soup = BeautifulSoup(odpoved.text, 'html.parser')

    data_zahlavi = ["Kód obce", "Název obce"]

    # extrahuj hodnoty #sa2, #sa3, #sa6
    for idx, id_name in enumerate(['sa2', 'sa3', 'sa6']):
        elem = soup.find(id=id_name)
        if elem:
            val = elem.get_text(strip=True).replace('\xa0', ' ')
        else:
            val = ''
        if idx == 0:
            val = 'Voliči v seznamu'
        elif idx == 1:
            val = 'Vydané obálky'
        elif idx == 2:
            val = 'Platné hlasy'
        data_zahlavi.append(val)
    # Názvy stran z první tabulky
    tab1 = soup.select_one('#inner > div:nth-of-type(1) > table')
    nazvy_stran = []
    if tab1:
        for tr in tab1.find_all('tr')[2:]:
            td_name = tr.find('td', class_='overflow_name')
            if td_name:
                nazvy_stran.append(td_name.get_text(strip=True))
    # Názvy stran z druhé tabulky
    tab2 = soup.select_one('#inner > div:nth-of-type(2) > table')
    if tab2:
        for tr in tab2.find_all('tr')[2:]:
            td_name = tr.find('td', class_='overflow_name')
            if td_name:
                nazvy_stran.append(td_name.get_text(strip=True))
    data_zahlavi.extend(nazvy_stran)

    # zápis hlavičky
    with open('vysledky_Praha.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(data_zahlavi)
    return data_zahlavi

kod_obci, nazvy_obci = ziskat_kod_nazev_obci_z_html(url)
vsechny_data = extrahuj_data_z_odkazu_list(relativni_url)

def pripravi_seznam_radku(kod_obci, nazvy_obci, vsechny_data):
    """
    Přípraví řádky pro zápis do CSV souboru.

    Funkce:
    - Pro každý index vytvoří řádek, který obsahuje:
        * kód obce
        * název obce
        * data z 'vsechny_data' odpovídajícího indexu
    - Uloží všechny řádky do souboru 'vysledky_Praha.csv' ve formátu CSV s kódováním UTF-8 s BOM.

    Args:
        kod_obci (list of str): seznam kódů obcí.
        nazvy_obci (list of str): seznam názvů obcí.
        vsechny_data (list of list of str): seznam datových řádků (každý je seznam hodnot).

    Returns:
        radky (list of list of str): seznam všech sestavených řádků, které byly zapsány do souboru.
    """
    radky = []
    for i in range(len(kod_obci)):
        radek = ([kod_obci[i], nazvy_obci[i]] + vsechny_data[i])
        radky.append(radek)
    
    # Zápis řádků do souboru .csv
    with open('vysledky_Praha.csv', 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(radky)
    return radky

if __name__ == "__main__":

    print("STAHUJI DATA Z VYBRANÉHO URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100")
    ziskat_kod_nazev_obci_z_html(url)
    ziskat_relativni_url(url)
    extrahuj_data_z_odkazu_list(relativni_url)
    extrahovat_data_zahlavi(relativni_url)
    print("UKLÁDÁM DATA DO SOUBORU: vysledky_Praha.csv") 
    pripravi_seznam_radku(kod_obci, nazvy_obci, vsechny_data)
    print("UKONČUJI PROGRAM")