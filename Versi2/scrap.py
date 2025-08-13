import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://repositori.untidar.ac.id/index.php?p=show_detail&id={}"  # ID akan diganti dalam loop

# File CSV output
OUTPUT_FILE = "untidar_scrape_abstrak2.csv"

# Header CSV
fields = ["ID", "Judul", "Penulis", "Abstrak", "Info_24"]

results = []

for doc_id in range(13000, 16000):
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
        abstrak = soup.select_one(
            "body div.result-search.pb-5 section.container.mt-8 div div div.flex-1.p-0.px-md-4 p.text-grey-darker"
        ).get_text(" ", strip=True)
    except AttributeError:
        abstrak = None

    try:
        info_24 = soup.select_one(
            "body div.result-search.pb-5 section.container.mt-8 div div div.flex-1.p-0.px-md-4 dl dd:nth-child(24) div"
        ).get_text(strip=True)
    except AttributeError:
        info_24 = None

    results.append([doc_id, judul, penulis, abstrak, info_24])
    print(f"[OK] ID {doc_id} berhasil diambil")

# Simpan ke CSV
with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    writer.writerows(results)

print(f"Scraping selesai. Data tersimpan di {OUTPUT_FILE}")
