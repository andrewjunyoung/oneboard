import sys
from collections import Counter

def check_duplicates(filename, *tokens):
   with open(filename, 'r', encoding='utf-8') as f:
       lines = [line.strip() for line in f if line.strip()]

   keys = [line.split('\t')[0] for line in lines]
   dict_ = {line.split('\t')[0]: line.split('\t')[1] for line in lines}
   modified_keys = keys[:]

   target = tokens[0]
   for n in tokens[1:]:
       print(n, target)
       modified_keys = [key.replace(f'.{n}.', f'.{target}.') for key in modified_keys]

   counts = Counter(modified_keys)
   duplicates = [k for k, v in counts.items() if v > 1]

   if len(duplicates) > 0:
       print(f"New duplicates created: {len(duplicates)}")
       for dup in duplicates:
           print(f"  {dup}")
           print(dict_.get(dup))
       return True
   else:
       print("No new duplicates")
       return False

if __name__ == "__main__":
   if len(sys.argv) < 4:
       print("Usage: python script.py <filename> <n1> <n2> [n3] ...")
       sys.exit(1)

   filename = sys.argv[1]
   tokens = sys.argv[2:]
   check_duplicates(filename, *tokens)
