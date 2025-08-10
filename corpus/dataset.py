import pandas as pd
import os

# Konfigurasi: nama file dan format kolomnya
file_configs = {
    "ind_mixed_2012_10K-co_n.txt": {"columns": ["col1", "col2", "col3", "col4"], "sep": r"\s+"},
    "ind_mixed_2012_10K-co_s.txt": {"columns": ["col1", "col2", "col3", "col4"], "sep": r"\s+"},
    "ind_mixed_2012_10K-inv_so.txt": {"columns": ["col1", "col2"], "sep": r"\s+"},
    "ind_mixed_2012_10K-inv_w.txt": {"columns": ["col1", "col2", "col3"], "sep": r"\s+"},
    "ind_mixed_2012_10K-meta.txt": {"columns": ["id", "key", "value"], "sep": "\t"},
    "ind_mixed_2012_10K-sentences.txt": {"columns": ["id", "sentence"], "sep": "\t"},
    "ind_mixed_2012_10K-sources.txt": {"columns": ["id", "url", "date"], "sep": "\t"},
    "ind_mixed_2012_10K-words.txt": {"columns": ["id", "word", "freq"], "sep": r"\s+"}
}

excel_filename = "corpus_combined.xlsx"
csv_filename = "corpus_combined.csv"

with pd.ExcelWriter(excel_filename) as writer:
    all_dataframes = []
    
    for fname, cfg in file_configs.items():
        if not os.path.exists(fname):
            print(f"⚠️ File tidak ditemukan: {fname}")
            continue

        try:
            # Baca file sesuai separator yang ditentukan
            df = pd.read_csv(fname, sep=cfg["sep"], header=None, names=cfg["columns"], engine="python")
        except Exception as e:
            print(f"❌ Error membaca {fname}: {e}")
            continue

        # Simpan di Excel (sheet name dibatasi 31 karakter)
        sheet_name = os.path.splitext(fname)[0][-31:]
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Tambahkan kolom sumber file untuk gabungan CSV
        df["source_file"] = fname
        all_dataframes.append(df)

    # Gabungkan semua dataframe untuk CSV
    combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
    combined_df.to_csv(csv_filename, index=False, encoding="utf-8")

print(f"✅ Data tersimpan ke Excel: {excel_filename}")
print(f"✅ Data tersimpan ke CSV: {csv_filename}")
