# file: document_typo_checker.py
import streamlit as st
import difflib
import json
import csv
import docx2txt
import pdfplumber
import tempfile
from pathlib import Path
import re

KBBI_CSV_PATH = Path("data/kbbi.csv")


def load_kbbi_csv(csv_path):
    kbbi_words = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kbbi_words.add(row['kata'].strip().lower())
    return kbbi_words


def extract_text_from_upload(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix == ".pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join([page.extract_text() or '' for page in pdf.pages])
    elif suffix in [".doc", ".docx"]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        return docx2txt.process(tmp_path)
    elif suffix == ".txt":
        return uploaded_file.read().decode('utf-8')
    return ""


def tokenize(text):
    words = re.findall(r"\b\w+\b", text)
    return words


def find_typos(words, kbbi_words):
    typos = {}
    for word in set(words):
        if len(word) <= 3:
            continue  # skip short words
        if word.isupper():
            continue  # skip acronyms or abbreviations
        if word[0].isupper() and word[1:].islower():
            continue  # skip proper nouns

        lower_word = word.lower()
        if lower_word not in kbbi_words:
            suggestions = difflib.get_close_matches(lower_word, kbbi_words, n=3, cutoff=0.8)
            typos[word] = suggestions
    return typos


def highlight_typos(text, typos):
    def replacement(match):
        word = match.group(0)
        if word in typos:
            return f"<mark style='background-color: #ffdddd'>{word}</mark>"
        return word

    highlighted = re.sub(r"\b\w+\b", replacement, text)
    return highlighted


def main():
    st.title("🔍 Pemeriksa Typo & Saran Kata (KBBI)")
    st.markdown("Upload dokumen berformat **PDF, Word, atau TXT** untuk diperiksa.")

    uploaded_doc = st.file_uploader("📄 Upload Dokumen", type=["pdf", "doc", "docx", "txt"])

    if uploaded_doc:
        if not KBBI_CSV_PATH.exists():
            st.error(f"File KBBI tidak ditemukan di: {KBBI_CSV_PATH}")
            return

        kbbi_words = load_kbbi_csv(KBBI_CSV_PATH)
        doc_text = extract_text_from_upload(uploaded_doc)
        tokens = tokenize(doc_text)
        typos = find_typos(tokens, kbbi_words)

        st.subheader("📑 Teks Dokumen")
        highlighted = highlight_typos(doc_text, typos)
        st.markdown(highlighted, unsafe_allow_html=True)

        st.subheader("❌ Kata Tidak Dikenal & Saran")
        if not typos:
            st.success("✅ Tidak ditemukan kesalahan ejaan!")
        else:
            for typo, suggestions in sorted(typos.items()):
                st.markdown(f"- **{typo}** → Saran: `{', '.join(suggestions) if suggestions else 'Tidak ada saran'}`")


if __name__ == '__main__':
    main()
