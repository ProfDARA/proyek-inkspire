import csv

def save_to_csv(data: dict, filename: str):
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['kata', 'definisi'])
        for kata, definisi in sorted(data.items()):
            writer.writerow([kata, definisi])
    print(f"✅ Disimpan ke {filename} (format CSV)")
