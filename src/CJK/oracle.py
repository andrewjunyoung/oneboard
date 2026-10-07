#!/usr/bin/env python3
import pandas as pd
import argparse
import sys
import csv
import re

def compress_duplications(s):
    s = re.sub(r'(.{2,})\1\1', r'\g<1>"', s)
    s = re.sub(r'(.{2,})\1', r'\g<1>2', s)
    return s

def load_char_db():
    return pd.read_csv("data/char_db.csv")


def show_longest_keys(dict_path, n=10):
    entries = []
    with open(dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                key = parts[0]
                length = len(re.sub(r'[A-Z]', '', key))
                entries.append((length, key, parts[1]))

    all_keys = {e[1]: e[2] for e in entries}

    def make_prefix(key):
        non_caps = re.sub(r'[A-Z]', '', key)
        if len(non_caps) <= 6:
            return None
        prefix = non_caps[:3]
        m = re.search(r'[^A-Z][A-Z]*$', key)
        if not m:
            return None
        return prefix + "'" + m.group()

    entries.sort(reverse=True)
    for length, key, char in entries[:n]:
        prefix = make_prefix(key)
        clash = ""
        if prefix:
            clashing = [(k, v) for k, v in all_keys.items() if k != key and make_prefix(k) == prefix]
            if clashing:
                clash = " ⚠ clashes with " + ", ".join(f"{k}({v})" for k, v in clashing)
        print(f"{key}({char})\t({length}){' → ' + prefix if prefix else ''}{clash}")


def load_stroke_encodings():
    encodings = {}
    with open('data/stroke_encodings.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            strokes = row['strokes'].strip()
            char = row['char'].strip()
            if strokes and char:
                if strokes not in encodings:
                    encodings[strokes] = []
                encodings[strokes].append(char)
    return encodings


def apply_character_swaps(encoding):
    return encoding.replace('l', '\\').replace('i', 'l').replace('j', '/')


def prompt_user_choice(char, current_encoding, new_encoding_options):
    print(f"\n🔥 CLASH DETECTED for char: '{char}'")
    print(f"Current encoding: '{current_encoding}'")
    print("New encoding options:")

    options = []
    for i, option in enumerate(new_encoding_options, 1):
        print(f"  {i}. {option}")
        options.append(option)

    while True:
        try:
            user_input = input("\nChoose option number (1-{}) or enter custom encoding in quotes: ".format(len(options))).strip()

            if user_input.startswith('"') and user_input.endswith('"'):
                return user_input[1:-1]
            elif user_input.startswith("'") and user_input.endswith("'"):
                return user_input[1:-1]

            choice_num = int(user_input)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(options)}, or a quoted string.")
        except ValueError:
            print("Please enter a valid number or quoted string.")


def greedy_encode(strokes, encodings, char="", current_encoding="", interactive=False):
    if not strokes:
        return ""

    result = ""
    i = 0
    strokes = apply_character_swaps(strokes)
    while i < len(strokes):
        found_match = False
        for length in range(len(strokes) - i, 0, -1):
            substring = strokes[i:i+length]
            if substring in encodings:
                matches = encodings[substring]
                if len(matches) == 1:
                    result += matches[0]
                else:
                    unique_matches = list(set(matches))
                    if len(unique_matches) == 1:
                        result += unique_matches[0]
                    else:
                        if interactive and char and current_encoding:
                            chosen_encoding = prompt_user_choice(char, current_encoding, unique_matches)
                            result += chosen_encoding
                        else:
                            result += "(" + "/".join(unique_matches) + ")"
                i += length
                found_match = True
                break

        if not found_match:
            result += strokes[i]
            i += 1

    return result


def gen_tokens(interactive=False):
    encodings = load_stroke_encodings()
    print(f"Loaded {len(encodings)} stroke encodings")

    tokens_df = pd.read_csv('data/token_db.csv')

    new_encodings = []
    mismatches = []
    for idx, row in tokens_df.iterrows():
        strokes = str(row['strokes']) if pd.notna(row['strokes']) else ""
        old_encoding = str(row['encoding']) if pd.notna(row['encoding']) else ""
        char = str(row['character']) if 'character' in row and pd.notna(row['character']) else f"Row {idx}"

        temp_encoding = greedy_encode(strokes, encodings)

        if interactive and "(" in temp_encoding and ")" in temp_encoding and old_encoding != temp_encoding:
            new_encoding = greedy_encode(strokes, encodings, char, current_encoding=old_encoding, interactive=True)
        else:
            new_encoding = temp_encoding

        new_encodings.append(new_encoding)
        if old_encoding != new_encoding:
            mismatches.append(old_encoding)
        else:
            mismatches.append("")

    tokens_df['encoding'] = new_encodings
    tokens_df['mismatch'] = mismatches

    tokens_df.to_csv('show_me.csv', index=False)
    print(f"\nSaved results to show_me.csv with {len(tokens_df)} rows")

    mismatch_count = sum(1 for m in mismatches if m != "")
    matches = len(tokens_df) - mismatch_count
    print(f"Exact matches: {matches}/{len(tokens_df)} ({matches/len(tokens_df)*100:.1f}%)")

    print("\nDifferences:")
    for i, mismatch in enumerate(mismatches):
        if mismatch != "":
            print(f"Row {i}: Expected '{mismatch}' -> Actual '{new_encodings[i]}'")

    return tokens_df


def update_encoding(tokens_path, use_strokes=False):
    char_df = load_char_db()
    tokens_df = pd.read_csv(tokens_path)

    column_name = "strokes" if use_strokes == "true" else "encoding"
    char_to_code = dict(zip(tokens_df["character"], tokens_df[column_name]))

    def replace_chars(composition):
        if pd.isna(composition):
            return composition
        result = ""
        for char in composition:
            next_char = str(char_to_code.get(char, char))
            result += "." + next_char
        return result

    char_df["retokenized"] = char_df["composition"].apply(replace_chars)

    no_steps_mask = char_df["decomposition"] == "No steps"
    for idx, row in char_df[no_steps_mask].iterrows():
        char = row["character"]
        if char in char_to_code:
            char_df.loc[idx, "encoding"] = "." + str(char_to_code[char])

    mask = ~pd.isna(char_df["retokenized"])
    char_df.loc[mask, "encoding"] = char_df.loc[mask, "retokenized"]

    char_df.to_csv("data/char_db.csv", index=False)

    return char_df


def list_dupes(dict_path, ignore_variants=False):
    encoding_to_chars = {}

    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    encoding = parts[0]
                    character = parts[1]

                    if encoding not in encoding_to_chars:
                        encoding_to_chars[encoding] = []
                    encoding_to_chars[encoding].append(character)
    except FileNotFoundError:
        print(f"Error: Dictionary file '{dict_path}' not found")
        return
    except Exception as e:
        print(f"Error reading dictionary file: {e}")
        return

    duplicates_found = False
    for encoding, chars in encoding_to_chars.items():
        if len(chars) > 1:
            duplicates_found = True
            print(f"Encoding '{encoding}': {', '.join(chars)}")

    if not duplicates_found:
        print("No characters found with the same encoding")


def gen_dict(exclude_s=False, exclude_t=False):
    filtered_rows = []

    with open('data/char_db.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['encoding'] and row['encoding'].strip():
                filtered_rows.append(row)

    seen_compositionless_encodings = set()
    compositionless_encodings_with_duplicates = set()
    initial_dict = {}
    for row in filtered_rows:
        encoding = row['encoding']\
                .strip()\
                .replace("V", "")\
                .replace("A", "")\
                .replace("B", "")\
                .replace(".", "")

        if exclude_s and 'T' in encoding:
            continue
        if exclude_t and 'S' in encoding:
            continue

        if exclude_s:
            encoding = encoding.replace('S', '')
        if exclude_t:
            encoding = encoding.replace('T', '')

        if len(encoding) > 1:
            encoding = encoding[0] + encoding[1:]\
                    .replace(")", "")\
                    .replace("|", "")\
                    .replace("_", "")
            if encoding[1:] in seen_compositionless_encodings:
                compositionless_encodings_with_duplicates.add(encoding[1:])
                print(encoding)
            else:
                seen_compositionless_encodings.add(encoding[1:])

        if encoding not in initial_dict:
            initial_dict[encoding] = []
        initial_dict[encoding].append(row['character'])

    final_dict = {}
    for encoding, characters in initial_dict.items():
        final_encoding = encoding
        if len(encoding) > 1 and encoding[1:] not in compositionless_encodings_with_duplicates:
            final_encoding = encoding[1:]

        if final_encoding not in final_dict:
            final_dict[final_encoding] = []
        final_dict[final_encoding].extend(characters)

    with open('output/dict.txt', 'w', encoding='utf-8') as f:
        total_entries = 0
        for encoding, characters in final_dict.items():
            for character in characters:
                f.write(f"{compress_duplications(encoding)}\t{character}\t名詞\n")
                total_entries += 1

    print(f"Generated dict.txt with {total_entries} entries")


def gen_prefix_dict():
    entries = []
    with open('output/dict.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                entries.append(parts)

    prefix_map = {}

    def insert(entry, length):
        key = entry[0]
        prefix = key[:length]
        if prefix not in prefix_map:
            prefix_map[prefix] = entry
            return
        existing = prefix_map[prefix]
        if existing[0] == key:
            prefix_map[key] = entry
            return
        del prefix_map[prefix]
        insert(existing, len(prefix) + 1)
        insert(entry, len(prefix) + 1)

    for entry in entries:
        insert(entry, 1)

    with open('output/smol_dict.txt', 'w', encoding='utf-8') as f:
        total = 0
        for prefix, entry in prefix_map.items():
            tag = entry[2] if len(entry) > 2 else '名詞'
            f.write(f"{prefix}\t{entry[1]}\t{tag}\n")
            total += 1

    print(f"Generated smol_dict.txt with {total} entries")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", help="Command to run (gen-dict, list-dupes, gen-tokens)")
    parser.add_argument("-t", action="store_true", help="Only include traditional characters")
    parser.add_argument("-s", action="store_true", help="Only include simplified characters")
    parser.add_argument(
        "--tokens",
        help="Path to token_db.csv",
        default="data/token_db.csv"
    )
    parser.add_argument("--use-strokes", help="Use the character's strokes as the code")
    parser.add_argument("-d", "--dict", help="Path to dictionary file", default="output/dict.txt")
    parser.add_argument("--ignore-variants", action="store_true", help="Ignore traditional/simplified variants when listing duplicates")
    parser.add_argument("-i", "--interactive", action="store_true", help="Enable interactive mode for encoding clashes")
    parser.add_argument("-n", type=int, default=10)

    args = parser.parse_args()

    if args.command == "gen-dict":
        gen_dict(exclude_s=args.s, exclude_t=args.t)
        gen_prefix_dict()
    elif args.command == "show-dupes":
        list_dupes(args.dict, args.ignore_variants)
    elif args.command == "gen-tokens":
        result_df = gen_tokens(args.interactive)
        return result_df
    elif args.command == "show-longest":
        show_longest_keys(args.dict, args.n)
    elif args.command == "update-encoding":
        result_df = update_encoding(args.tokens, args.use_strokes)
        print(result_df[["character", "composition", "retokenized"]].head(20))
        return result_df
    else:
        char_df = load_char_db()
        print(f"Loaded {len(char_df)} characters")
        print(char_df.head(20))
        return char_df


if __name__ == "__main__":
    main()
