import re
from typing import List, Dict
from collections import defaultdict
import string

def levehnsteinDistance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Inisialisasi Baris dan Kolom Pertama
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,        # Deletion
                dp[i][j - 1] + 1,        # Insertion
                dp[i - 1][j - 1] + cost  # Substitution
            )
    return dp[m][n]

# cek tipe reduplikasi dari kata
def isReduplicate(word: str) -> str:
    # kasus kata berulang (anak-anak)
    if re.fullmatch(r'(\w+)-\1', word):
        return "pure"
    elif re.fullmatch(r'\w+-\w+', word):
        part1, part2 = word.split('-')
        # ada imbuhan awal
        if part1[1:] == part2:
            return "derived_first"     
        # ada imbuhan akhir  
        elif part1 == part2[:-1]:
            return "derived_last"       
        # ada imbuhan awal dan akhir  
        elif part1[1:] == part2[:-1]:
            return "derived_first_last"    
        else:
            return "none" 
    else:
        return "none"


def reduplicationSimiliarity(sentence1: str, sentence2: str) -> float:  
    # filter kata yang berulang dari kalimat
    def extractReduplicatedWords(sent):
        words = sent.lower().split()
        return [
            (word, isReduplicate(word.strip(string.punctuation)))
            for word in words
            if isReduplicate(word.strip(string.punctuation)) != "none"
        ]

    rWord1 = extractReduplicatedWords(sentence1)
    rWord2 = extractReduplicatedWords(sentence2)

    min_len = min(len(rWord1), len(rWord2))
    if min_len == 0:
        return 1.0 if len(rWord1) == len(rWord2) else 0.0

    match = 0
    for i in range(min_len):
        _, type1 = rWord1[i]
        _, type2 = rWord2[i]
        if type1 == type2:
            match += 1

    return match / max(len(rWord1), len(rWord2))


# Menghitung ukuran kemiripan leksikal antar dua kalimat dengan levehnstein distance
def lexicalSimiliarity(sentence1: str, sentence2: str) -> float:
    max_len = max(len(sentence1), len(sentence2))
    if max_len == 0:
        return 1.0  # identik
    dist = levehnsteinDistance(sentence1, sentence2)
    return 1 - dist / max_len

# Baca file txt dan kelompokkan kalimat berdasarkan bahasa sebagai dict
def readFromFile(filename: str) -> Dict[str, List[str]]:
    langSentencesDict = defaultdict(list)
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if ',' not in line:
                continue
            # buat pemetaan kode bahasa dengan kalimatnya
            code, sentence = line.strip().split(',', 1)
            langSentencesDict[code.strip()].append(sentence.strip())
    return langSentencesDict

# Analisis kesamaan dengan hanya reduplikasi
def analyzeSimiliarity(langSentencesDict: Dict[str, List[str]], referenceLang='ID'):
    results = {}
    refLangSentences = langSentencesDict.get(referenceLang)
    if not refLangSentences:
        raise ValueError(f"Tidak ada kalimat untuk bahasa referensi '{referenceLang}'")

    for code, sentences in langSentencesDict.items():
        # abaikan bahasa referensi
        if code == referenceLang:
            continue
        # dictionary untuk menyimpan hasil ukuran kemiripan dari tiap kalimat per satu bahasa
        sentencesResult = []
        for i in range(len(refLangSentences)):
            # hitung ukuran kemiripan leksikal dan struktural untuk tiap kalimat berkesuaian dari setiap bahasa dengan bahasa Indonesia
            lexical = lexicalSimiliarity(refLangSentences[i], sentences[i])
            structural = reduplicationSimiliarity(refLangSentences[i], sentences[i])
            sentencesResult.append({
                "Lexical": round(lexical, 3),
                "Structural": round(structural, 3),
            })
        results[code] = sentencesResult
    return results

if __name__ == "__main__":
    filename = input("Masukkan nama file teks (dalam .txt): ").strip()
    try:
        langSentencesDict = readFromFile(filename)
        results = analyzeSimiliarity(langSentencesDict, referenceLang="ID")

        for lang in results:
            print(f"\nHasil untuk {lang}:")
            for i, entry in enumerate(results[lang]):
                print(f"Kalimat {i+1}: {entry}")
    except FileNotFoundError:
        print(f"[ERROR] File '{filename}' tidak ditemukan.")
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan: {e}")