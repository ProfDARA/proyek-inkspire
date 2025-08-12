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

def find_prepositions_conjunctions(sentence, prepositions_set, conjunctions_set):
    words = re.findall(r'\b\w+\b', sentence.lower())
    found_prepositions = [w for w in words if w in prepositions_set]
    found_conjunctions = [w for w in words if w in conjunctions_set]
    return found_prepositions, found_conjunctions

# ------------------------------------------------------------------------------------------
def check_punctuation(sentence):
    if not sentence:
        return False
    start_capital = sentence[0].isupper()
    end_punct = sentence.strip()[-1] in ".?!:;" or sentence.strip()[-1] in ['”', '"', "'"]
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

# --- fungsi hitung readability ---
def flesch_reading_ease_id(sentence):
    words = re.findall(r'\b\w+\b', sentence)
    word_count = len(words)
    syllable_count = sum(count_syllables_id(w) for w in words)
    sentence_count = 1
    if word_count == 0:
        return 0
    score = 206.835 - (65 * (syllable_count / word_count)) - (word_count / sentence_count)
    return round(score, 2)

def categorize_readability(score):
    if score >= 60:
        return "mudah"
    elif score >= 30:
        return "sedang"
    else:
        return "sulit"

# --- fitur tambahan ---
def count_affixed_words(words):
    prefixes = ("me", "di", "ke", "se", "ber", "ter", "per")
    suffixes = ("kan", "an", "i")
    affixed = [w for w in words if w.startswith(prefixes) or w.endswith(suffixes)]
    return len(affixed)

def count_reduplication(words):
    return sum(1 for w in words if "-" in w or re.match(r'^(\w+)\1$', w))

def calc_hard_word_ratio(words, freq_set):
    if not words:
        return 0
    hard_count = sum(1 for w in words if w not in freq_set)
    return hard_count / len(words)
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model paraphrase
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os

# Path absolut ke folder model
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

model_path = r"E:/Dicoding/Projekt_Inkspire/corpus/modelparaprase"

tokenizer = T5Tokenizer.from_pretrained(model_path)  # slow tokenizer
model = T5ForConditionalGeneration.from_pretrained(model_path).to("cuda")

text = "parafrase: Dia juga bilang bahwa ramuan ini juga pernah diterbitkan di sebuah majalah."
input_ids = tokenizer.encode(text, return_tensors="pt").to("cuda")

output = model.generate(input_ids, max_length=64, num_beams=4)
print(tokenizer.decode(output[0], skip_special_tokens=True))

# ------------------------------------------------------------------------------------------
# MAIN
input_file = "ind_mixed-tufs4_2012_100K-sentences.txt"
output_file = "hasil_readability.csv"

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

        words = re.findall(r'\b\w+\b', sentence.lower())

        ragam = detect_ragam(sentence, formal_words_set)
        found_preps, found_conjs = find_prepositions_conjunctions(sentence, prepositions_set, conjunctions_set)
        punct_ok = check_punctuation(sentence)
        score = flesch_reading_ease_id(sentence)
        readability_level = categorize_readability(score)

        word_count = len(words)
        unique_word_count = len(set(words))
        avg_syllables_per_word = sum(count_syllables_id(w) for w in words) / word_count if word_count else 0
        hard_word_ratio = calc_hard_word_ratio(words, freq_set)
        affixed_word_ratio = count_affixed_words(words) / word_count if word_count else 0
        reduplication_count = count_reduplication(words)

        rows.append({
            "s_id": s_id,
            "sentence": sentence,
            "ragam": ragam,
            "prepositions": ", ".join(found_preps),
            "conjunctions": ", ".join(found_conjs),
            "punctuation_ok": punct_ok,
            "readability_score": score,
            "readability_level": readability_level,
            "word_count": word_count,
            "unique_word_count": unique_word_count,
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
            "hard_word_ratio": round(hard_word_ratio, 3),
            "affixed_word_ratio": round(affixed_word_ratio, 3),
            "reduplication_count": reduplication_count,
            "suggested_sentence": auto_rewrite_sentence(sentence)
        })

# Simpan ke CSV
df = pd.DataFrame(rows)
df.to_csv(output_file, index=False, encoding="utf-8")
print(f"Data berhasil disimpan ke {output_file}")