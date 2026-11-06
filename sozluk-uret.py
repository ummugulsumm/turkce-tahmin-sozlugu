"""Tahmin sözlüğünü üretir: kaynak/tr_TR.dic, kaynak/tr_TR.aff ve ek-kelimeler.txt dosyalarından words.json yazar.

Kullanım: python3 sozluk-uret.py [kaynak klasörü] [çıktı dosyası]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHABET = set("abcçdefgğhıijklmnoöprsştuüvyz")
LENGTHS = (4, 5, 6)
WORD_SUFFIXES = {"lar", "ler", "mak", "mek"}


def read_rules(path):
    rules = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0] != "SFX":
            continue
        _, flag, strip, add, condition = parts[:5]
        if strip == "0" and condition == ".":
            rules[flag].append(add.split("/")[0])
    return rules


def expand(path, rules):
    # Sözlük kesik parçalar da tutar (fındı+k). Gövde ancak çoğul veya mastar eki alıyorsa kelime sayılır.
    forms = set()
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        stem, _, flags = line.split("\t")[0].partition("/")
        if stem != stem.lower() or len(stem) > max(LENGTHS) or not flags:
            continue
        suffixes = {suffix for flag in flags.split(",") for suffix in rules.get(flag, ())}
        if suffixes & WORD_SUFFIXES:
            suffixes.add("")
        for suffix in suffixes:
            word = stem + suffix
            if len(word) in LENGTHS and set(word) <= ALPHABET:
                forms.add(word)
    return forms


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "kaynak"
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "words.json"
    forms = expand(source / "tr_TR.dic", read_rules(source / "tr_TR.aff"))
    forms |= set((ROOT / "ek-kelimeler.txt").read_text(encoding="utf-8").split())
    words = {str(n): "".join(sorted(w for w in forms if len(w) == n)) for n in LENGTHS}
    output.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    for n in LENGTHS:
        print(n, "harfli:", len(words[str(n)]) // n)


if __name__ == "__main__":
    main()
