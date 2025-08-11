import csv
import re
import pandas as pd

# ------------------------------------------------------------------------------------------
# --- fungsi load daftar kata formal ---
def load_formal_words(filepath):
    with open(filepath, encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

# --- fungsi cek ragam formal / tidak formal ---
def detect_ragam(sentence, formal_words_set):
    words = re.findall(r'\b\w+\b', sentence.lower())
    if any(word not in formal_words_set for word in words):
        return "tidak formal"
    return "formal"

# ------------------------------------------------------------------------------------------
def load_word_list(filepath):
    with open(filepath, encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

def has_prepositions_conjunctions(sentence, prepositions_set, conjunctions_set):
    words = re.findall(r'\b\w+\b', sentence.lower())
    
    found_prepositions = [w for w in words if w in prepositions_set]
    found_conjunctions = [w for w in words if w in conjunctions_set]
    
    has_any = bool(found_prepositions or found_conjunctions)
    
    return has_any, found_conjunctions, found_prepositions

# ------------------------------------------------------------------------------------------
def check_punctuation(sentence):
    if not sentence:
        return False
    start_capital = sentence[0].isupper()
    end_punct = sentence.strip()[-1] in ".?!:;" or sentence.strip()[-1] in ['”', '"', "'"]
    # Jika tanda kutip atau apostrof di akhir, cek karakter sebelumnya
    if not end_punct and sentence.strip()[-1] in ['”', '"', "'"]:
        stripped = sentence.strip().rstrip('”"\'')
        if stripped and stripped[-1] in ".?!:;":
            end_punct = True
    return start_capital and end_punct

def count_syllables_id(word):
    vowels = "aiueoAIUEO"
    count = 0
    prev_char_vowel = False
    for c in word:
        if c in vowels:
            if not prev_char_vowel:
                count += 1
            prev_char_vowel = True
        else:
            prev_char_vowel = False
    return max(count, 1)

# --- fungsi hitung readability (Flesch Reading Ease modifikasi bahasa Indonesia) ---
def flesch_reading_ease_id(sentence):
    words = re.findall(r'\b\w+\b', sentence)
    word_count = len(words)
    syllable_count = sum(count_syllables_id(w) for w in words)
    sentence_count = 1  # karena input satu kalimat
    if word_count == 0:
        return 0
    score = 206.835 - (65 * (syllable_count / word_count)) - (word_count / sentence_count)
    return round(score, 2)


def calc_avg_word_freq(sentence, freq_set):
    words = re.findall(r'\b\w+\b', sentence.lower())
    found = [w for w in words if w in freq_set]
    return len(found) / len(words) if words else 0

def categorize_word_freq(avg_freq):
    if avg_freq >= 0.8:
        return "mudah"
    elif avg_freq >= 0.5:
        return "sedang"
    else:
        return "sulit"



# ------------------------------------------------------------------------------------------
# MAIN
input_file = "ind_mixed-tufs4_2012_100K-sentences.txt"
output_file = "hasil_readability.csv"

# Load file daftar kata
formal_words_set = load_formal_words("formal_words.txt")
prepositions_set = load_word_list("prepositions.txt")
conjunctions_set = load_word_list("conjunctions.txt")
freq_set = load_word_list("frequency.txt")

rows = []
with open(input_file, encoding="utf-8") as f:
    for line in f:
        if "\t" not in line:
            continue
        s_id, sentence = line.strip().split("\t", 1)

        ragam = detect_ragam(sentence, formal_words_set)
        has_prep_conj = has_prepositions_conjunctions(sentence, prepositions_set, conjunctions_set)
        punct_ok = check_punctuation(sentence)
        score = flesch_reading_ease_id(sentence)

        rows.append({
            "s_id": s_id,
            "sentence": sentence,
            "ragam": ragam,
            "punya_preposisi_konjungsi": has_prep_conj,
            "punctuation_ok": punct_ok,
            "readability_score": score
        })

# Simpan ke CSV
df = pd.DataFrame(rows)
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Data berhasil disimpan ke {output_file}")
