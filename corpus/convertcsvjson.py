import csv, json

# Baca CSV
with open("readability_dataset100k.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

# Simpan ke JSON
with open("output.json", "w", encoding="utf-8") as jsonfile:
    json.dump(data, jsonfile, ensure_ascii=False, indent=2)

print("Selesai ekspor ke output.json")