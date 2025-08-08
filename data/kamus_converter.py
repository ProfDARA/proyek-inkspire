# file: parse_kbbi_pdf_to_json.py
import re
import json
import csv
import pdfplumber
from pathlib import Path

def parse_kbbi_text(ocr_text: str) -> dict:
    entries = {}
    current_word = None
    current_def = []

    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

    for line in lines:
        match = re.match(r"^([a-zA-Z\-]+)\s+([navakp]\w*)\s+(.+)$", line)
        if match:
            if current_word:
                entries[current_word] = " ".join(current_def).strip()
            current_word = match.group(1).lower()
            current_def = [match.group(2) + " " + match.group(3)]
        else:
            if current_word:
                current_def.append(line)

    if current_word:
        entries[current_word] = " ".join(current_def).strip()

    return entries

def extract_text_from_pdf(pdf_path: str) -> str:
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)

def save_to_json(data: dict, filename: str):
    sorted_data = dict(sorted(data.items()))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Disimpan ke {filename} ({len(sorted_data)} entri, sudah urut abjad)")

def save_to_csv(data: dict, filename: str):
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['kata', 'definisi'])
        for kata, definisi in sorted(data.items()):
            writer.writerow([kata, definisi])
    print(f"✅ Disimpan ke {filename} (format CSV)")

if __name__ == "__main__":
    pdf_file = "KBBI.pdf"
    json_output = "kbbi.json"
    csv_output = "kbbi.csv"

    raw_text = extract_text_from_pdf(pdf_file)
    kbbi_dict = parse_kbbi_text(raw_text)

    save_to_json(kbbi_dict, json_output)
    save_to_csv(kbbi_dict, csv_output)