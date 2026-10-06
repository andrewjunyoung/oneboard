import re
import argparse
from collections import Counter

def count_chinese_chars(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()

    #chars = re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text)
    chars = re.findall(r'[a-z0-9/\\=-]', text)
    return Counter(chars).most_common()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="File to analyze")
    parser.add_argument("-n", type=int, help="Show top n characters")
    args = parser.parse_args()

    char_counts = count_chinese_chars(args.filename)
    if args.n:
        char_counts = char_counts[:args.n]

    for char, count in char_counts:
        print(f"{char}: {count}")
