# file: parse_kbbi_filtered.py
import re
import json
import csv
import pdfplumber
from pathlib import Path

def read_reference_words(filepath: str) -> set:
    with open(filepath, 'r', encoding='utf-8') as f:
        return set(word.strip().lower() for word in f if word.strip())

def normalize_word(word: str) -> str:
    return re.sub(r"^[0-9]+", "", word.lower())

def parse_kbbi_text(ocr_text: str) -> dict:
    entries = {}
    current_word = None
    current_def = []

    lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

    for line in lines:
        match = re.match(r"^([a-zA-Z0-9\-]+)\s+([navakp]\w*)\s+(.+)$", line)
        if match:
            if current_word:
                normalized = normalize_word(current_word)
                entries[normalized] = " ".join(current_def).strip()
            current_word = match.group(1)
            current_def = [match.group(2) + " " + match.group(3)]
        else:
            if current_word:
                current_def.append(line)

    if current_word:
        normalized = normalize_word(current_word)
        entries[normalized] = " ".join(current_def).strip()

    return entries

def extract_text_from_pdf(pdf_path: str) -> str:
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            width = page.width
            mid_x = width / 2

            left_bbox = (0, 0, mid_x, page.height)
            right_bbox = (mid_x, 0, width, page.height)

            left_text = page.within_bbox(left_bbox).extract_text() or ''
            right_text = page.within_bbox(right_bbox).extract_text() or ''

            full_text.extend([left_text, right_text])

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
    ref_words_file = "text_kamus.txt"

    ref_words = read_reference_words(ref_words_file)
    raw_text = extract_text_from_pdf(pdf_file)
    all_entries = parse_kbbi_text(raw_text)

    filtered_entries = {k: v for k, v in all_entries.items() if k in ref_words}

    save_to_json(filtered_entries, json_output)
    save_to_csv(filtered_entries, csv_output)