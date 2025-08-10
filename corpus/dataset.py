import pandas as pd
import os

# Konfigurasi: nama file, jumlah kolom, dan nama kolom
file_configs = {
    "ind_mixed_2012_10K-co_n.txt": (4, ["col1", "col2", "col3", "col4"]),
    "ind_mixed_2012_10K-co_s.txt": (4, ["col1", "col2", "col3", "col4"]),
    "ind_mixed_2012_10K-inv_so.txt": (2, ["col1", "col2"]),
    "ind_mixed_2012_10K-inv_w.txt": (3, ["col1", "col2", "col3"]),
    "ind_mixed_2012_10K-meta.txt": (3, ["id", "key", "value"]),
    "ind_mixed_2012_10K-sentences.txt": (2, ["id", "sentence"]),
    "ind_mixed_2012_10K-sources.txt": (3, ["id", "url", "date"]),
    "ind_mixed_2012_10K-words.txt": (3, ["id", "word", "freq"])
}

excel_filename = "corpus_combined.xlsx"
csv_filename = "corpus_combined.csv"

def read_file_manual(fname, num_cols, col_names):
    rows = []
    with open(fname, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=num_cols - 1)  # pastikan kolom terakhir ambil semua sisa teks
            # Kalau kolom kurang, tambahkan None
            while len(parts) < num_cols:
                parts.append(None)
            rows.append(parts)
    return pd.DataFrame(rows, columns=col_names)

with pd.ExcelWriter(excel_filename) as writer:
    all_dataframes = []
    
    for fname, (num_cols, col_names) in file_configs.items():
        if not os.path.exists(fname):
            print(f"⚠️ File tidak ditemukan: {fname}")
            continue
        
        try:
            df = read_file_manual(fname, num_cols, col_names)
        except Exception as e:
            print(f"❌ Error membaca {fname}: {e}")
            continue

        # Simpan di Excel
        sheet_name = os.path.splitext(fname)[0][-31:]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Tambahkan kolom nama file
        df["source_file"] = fname
        all_dataframes.append(df)

    combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
    combined_df.to_csv(csv_filename, index=False, encoding="utf-8")

print(f"✅ Data tersimpan ke Excel: {excel_filename}")
print(f"✅ Data tersimpan ke CSV: {csv_filename}")
