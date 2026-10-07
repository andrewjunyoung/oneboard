#!/usr/bin/env python3
from collections import Counter
import unicodedata
import string

def analyze_char_frequencies(file_path):
    char_counter = Counter()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        for char in content:
            # Skip numbers, ASCII letters, and punctuation
            if char.isdigit() or char in string.ascii_letters or char in string.punctuation:
                continue
            # Skip whitespace and control characters
            if char.isspace() or unicodedata.category(char)[0] == 'C':
                continue
            char_counter[char] += 1

    # Sort by frequency (descending)
    sorted_chars = char_counter.most_common()

    print("Character frequency ranking:")
    print("Rank | Character | Count")
    print("-" * 25)

    for rank, (char, count) in enumerate(sorted_chars, 1):
        # Show readable representation for special characters
        display_char = repr(char) if char in '\n\t\r ' else char
        print(f"{rank:4d} | {display_char:9s} | {count:5d}")

    print(f"\nTotal unique characters: {len(sorted_chars)}")
    print(f"Total characters in file: {sum(char_counter.values())}")

if __name__ == "__main__":
    analyze_char_frequencies("data/char_db.csv")
