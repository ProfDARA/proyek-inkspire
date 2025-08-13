import requests
from bs4 import BeautifulSoup
import csv
import re

BASE_URL = "https://repositori.untidar.ac.id/index.php?p=show_detail&id={}"  
OUTPUT_FILE = "untidar_scrape_perkalimat3.csv"

fields = ["No", "Kalimat", "Judul", "Penulis", "Fakultas", "Prodi"]

results = []

for doc_id in range(15000, 20000):
    url = BASE_URL.format(doc_id)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[SKIP] ID {doc_id} - error: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        judul = soup.select_one(
            "body div.result-search.pb-5 section.container.mt-8 div div div.flex-1.p-0.px-md-4 blockquote h4"
        ).get_text(strip=True)
    except AttributeError:
        judul = None

    try:
        penulis = soup.select_one(
            "body div.result-search.pb-5 section.container.mt-8 div div div.flex-1.p-0.px-md-4 blockquote footer a"
        ).get_text(strip=True)
    except AttributeError:
        penulis = None

    try:
        fakultas_prodi = soup.select_one(
            "body div.result-search.pb-5 section.container.mt-8 div div div.flex-1.p-0.px-md-4 dl dd:nth-child(24) div"
        ).get_text(strip=True)
        if "-" in fakultas_prodi:
            fakultas, prodi = [x.strip() for x in fakultas_prodi.split("-", 1)]
        else:
            fakultas, prodi = fakultas_prodi, None
    except AttributeError:
        fakultas, prodi = None, None

    try:
        abstrak = soup.select_one(
            "body div.result-search.pb-5 section.container.mt-8 div div div.flex-1.p-0.px-md-4 p.text-grey-darker"
        ).get_text(" ", strip=True)
    except AttributeError:
        abstrak = None

    if abstrak:
        kalimat_list = [kal.strip() for kal in re.split(r'(?<=[.!?])\s+', abstrak) if kal.strip()]
        for idx, kalimat in enumerate(kalimat_list, start=1):
            results.append([idx, kalimat, judul, penulis, fakultas, prodi])
        print(f"[OK] ID {doc_id} - {len(kalimat_list)} kalimat diambil")
    else:
        print(f"[EMPTY] ID {doc_id} tidak ada abstrak")

with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    writer.writerows(results)

print(f"Scraping selesai. Data tersimpan di {OUTPUT_FILE}")
