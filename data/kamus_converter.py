# file: parse_kbbi_pdf.py
import pdfplumber
import re
import json
from pathlib import Path

def parse_kbbi_pdf(pdf_path, output_json):
    kbbi_dict = {}
    current_word = None
    current_def = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            # Hilangkan nomor halaman dan header huruf
            lines = [
                l.strip() for l in text.split("\n")
                if not re.match(r"^\d+$", l.strip()) and len(l.strip()) > 0
            ]
            
            for line in lines:
                # Deteksi kata baru (diawali huruf, spasi, lalu jenis kata: n, a, v, adv, pron, dsb.)
                match = re.match(r"^([a-zA-ZÀ-ÿ\-]+)\s+([navkp]\w*)\s+(.*)", line)
                if match:
                    # Simpan entri sebelumnya
                    if current_word:
                        kbbi_dict[current_word] = " ".join(current_def).strip()
                    
                    current_word = match.group(1).lower()
                    current_def = [match.group(2) + " " + match.group(3)]
                else:
                    # Tambahkan ke definisi entri aktif
                    if current_word:
                        current_def.append(line)
        
        # Simpan entri terakhir
        if current_word:
            kbbi_dict[current_word] = " ".join(current_def).strip()

    # Simpan ke JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(kbbi_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ Berhasil mengekstrak {len(kbbi_dict)} entri ke {output_json}")

if __name__ == "__main__":
    parse_kbbi_pdf("KBBI.pdf", "kbbi.json")

