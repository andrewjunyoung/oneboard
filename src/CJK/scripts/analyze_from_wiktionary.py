import argparse
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
import threading
import random

def parse_composition(html):
    composition_pattern = re.compile(r'composition.*?</i>\s*<span[^>]*>(.*?)</span>', re.DOTALL | re.IGNORECASE)
    match = composition_pattern.search(html)
    if match:
        composition_span = match.group(1)
        soup_comp = BeautifulSoup(composition_span, 'html.parser')
        return soup_comp.get_text()
    return None

print_lock = threading.Lock()
seen_chars = {}
decomposition_steps = {}
seen_lock = threading.Lock()

strokes = {  # cant change
    # -
    "一": ".-", "㇀": ".-",
    # /
    "丿": "./", "㇒": "./",
    # '
    "丶": ".\\", "乀": ".\\", "㇏": ".\\",
    # l
    "丨": ".l",
    "亅": ".lA",
    # S with hook
    "乙": ".sF", "乚": ".sI", "𠃋": ".sK", "㇇": ".sM", "𠄌": ".sO",
    "㇂": ".sG", "乛": ".sJ", "𠃌": ".sL", "㇉": ".sN", "㇈": ".sP",
    "⺄": ".sH",
    # S without hook
    "𠃍": ".sA", "𠃊": ".sB", "ㄣ": ".sC", "㇍": ".sD",
    # Z-able
    "㇡": ".sE",
}
shapes = {
    # 2
    "二": ".2", "⺀": ".2B", "冫": ".2_", "丷": ".2|","刂": "._2", "リ": ".2D",
    # 3
    "彡": "./3", "三": ".-3", "𫶧": ".3",  # triplication
    "氵": ".3_", "氺": ".|3", "水": ".3E",  # same
    # 4
    "覀": ".-4", "四": ".o8", "灬": ".4", "皿": ".nhA", "罒": ".nhB", "西": ".-4",
    # 5
    "五": ".-5", "𫝀": ".5",
    # 6
    "亠": ".6",
    # 7
    "匕": ".7A", "七": ".7B",
    # 8
    "八": ".8",
    # 9
    "夕": ".9A", "九": ".9B", "夂": "./xA", "夊": "./xA",
    # 0
    "十": ".+A", "𬺰": ".+B",
    "女": ".y",
    "片": ".k", "爿": ".k", "尢": ".k", "兂": ".k",  # Wan?
    "丆": ".rA", "𠂆": ".rB","厂": ".rC", "𠂇": ".r|",

    "末": ".-m", "未": ".im",
    "申": ".bl", "甲": ".bi",

    # a
    "人": ".a", "𠆢": ".a|", "亻": ".a_", "儿": ".|a",
    "𠂉": ".aA", "入": ".aB",  "癶": ".aC",
    # q
    "大": ".qB", "火": ".qA",
    # b
    "日": ".b", "⺜": ".b|", "曰": ".bB",
    # c
    "匚": ".c0",
    "コ": ".c", "ユ": ".c", "⺕": ".c-",
    # d
    "厶": ".d", "龴": ".d|",
    # e (semantic - beasts)
    "犭": ".e_", "豸": ".e`_",
    "豕": ".e", "𧰨": ".|e",
    "犬": ".e",
    "巳": ".eA",
    # f
    "卜": ".fA", "⺊": ".fB", "𰀁": ".-+A", "干": ".-+B", "𰀁": ".fC",
    # m
    "木": ".m", "朩": ".m",
    # n
    "冂": ".nA", "⺈": ".n|A", "冖": ".n|B", "勹": ".nB", "⺆": ".nC", "門": ".nD", "𠘨": ".nE",
    "几": ".nF", "门": ".\\nD`",
    "口": ".o", "囗": ".o0",
    # g
    "月": ".gA", "⺝": ".g_", "肉": ".gB", "⺼": ".gC", "目": ".gi",

    "貝": ".gi8`", "贝": ".gi8",  # simp
    # h
    "卄": ".h", "艹": ".h|",
    "䒑": ".h|B",
    "廾": ".hC", "丌": ".hD",  # same strokes
    "⻀": ".h|D",
    # i
    "工": ".i",
    # j
    "扌": ".j_", "手": ".jC", "于": ".jB",
    # p
    "尸": ".pA", "戶": ".ip",
    "力": ".pB", "刀": ".pC",
    # t
    "土": ".t", "𤣩": ".-t_", "王": ".-t", "龶": ".-t|",
    # u
    "田": ".u", "凵": ".u",
    "囬": ".u",  # equivalent to o0o
    # w
    "小": ".w", "𭕄": ".w|A", "⺌": ".w|B",
    "𧘇": ".|w",
    "心": ".wA", "忄": ".wA_",
    # x
    "乂": ".x", "㐅": ".x",
    "又": ".xB",
    "戈": ".xA/\\", "弋": ".xA\\\\",
    # z
    "了": ".z1", "𠄐": ".z2",
}
non_obvious_derivations = {
    "羽": ".cc",
    "耒": ".i-m",  # 2m
    "聿": ".c-f",
    "臣": ".rlc6",
    "虫": ".od",
    "阝": ".zl", # because "卩": ".sl",
    "骨": ".nsng",
    "𭃂": ".cl",
    "母": ".ss3", "毋": ".ss+",  # ss
    "北": ".2l7",
    "𦣝": ".clcl",  # eh
    "巿": ".-nl", "帀": ".-ni",
}
obvious_greedy_derivations = {  # to avoid bullshit with wiktionary
    "亾": ".a.s",
    "耂": ".t./",
    "百": ".r.b",
    "化": ".a.f",
    "民": ".p.x",
    "具": ".gi.8",
    "长": "./-d",
    "是": ".b-fa",
    "黾": ".obs", "黽": ".obs`",
    "殳": ".n.x",
    "ス": ".s\\",
    "业": ".4.-",
    "山": ".l.u",
    "我": "./fx\\",
    "斤": ".r.r",
    "方": ".6p",
    "止": ".f6",
    "比": ".77",
    "氏": ".r.x",
    "瓦": ".-ss\\",
    "由": ".nt",
    "疒": ".\\r2",
    "示": ".2w", "礻": ".2w",
    "竹": ".alal", "𥫗": ".alal|",
    "糸": ".sdw", "糹": ".sdw_", "纟": ".sdw_",
    "耳": ".r3l",
    "臼": ".r-c", "𦥑": ".r-c",
    "艮": ".c-v",  # cv
    "虍": ".fr7",
    "言": ".4o", "訁": ".4o",
    "身": "./g-/",
    "车": ".-s+",  "車": ".-s+`",
    "辰": ".r2w",
    "辵": ".3af", "辶": ".3af",
    "金": ".af", "釒": ".af", "钅": ".af",
    "隹": ".a6f-",
    "雨": ".-nl4", "⻗": ".-nl4|",  # n4
    "非": ".3ll3",
    "革": ".h-o+",
    "飞": ".s2", "飛": ".s2`",
    "食": ".aic-v", "飠": ".aic-v_`",  # ac
    "马": ".ss-", "馬": ".ss-`",
    "髟": ".r3d3",
    "斗": ".3l",
    "鱼": ".nn-", "魚": ".nn-`",
    "鸟": ".n\\s-", "鳥": ".n\\s-`",
    "鹵": ".fox4",   # f4
    "黑": ".4t4",
    "鼎": ".4kk",
    "齿": ".f6ua", "齒": ".f6ua`", # fu
    "龙": ".k/\\", "龍": ".k/\\`",
    "龰": ".fa",
    "及": ".za",
    "免": ".noa",
    "皮": ".rlx",
    "戊": ".rx",
    "𢆶": ".dd",
    "𠫝": ".d3",
    "鹿": ".\\r477",
}
problematic_components = {
    "㇯": ".iziz",
    "𣦵": ".fn-",
    "𥬥": ".a\\a\\gi",
    "𦙍": "./sdg",
    "𭔰": ".-oh+\\",
    "𠔾": "./n2",
    "宅": ".in/7",
    "毛": "./-7",
    "𥘈": ".723",
    "𡕩": ".ox8",
    "肃": ".c+4",
    "𭥴": ".4+",
    "𠁁": ".*A",
    "亞": ".*A",
    "丱": ".*B",
}

def renumber_keys(d):
   items = list(d.items())
   return {key: f".{i+1}" for i, (key, value) in enumerate(items)}

stop_chars = {
    **strokes,
    **shapes,
    **non_obvious_derivations,
    # **obvious_greedy_derivations,
    **problematic_components
}
# stop_chars = renumber_keys(stop_chars)
print(stop_chars)

composition = {
    "0" : ["⿸","⿵","⿴","⿶","⿷","⿸","⿹","⿺"],
    "||": "⿳",
    "|" : "⿱",
    "__": "⿲",
    "." : "⿻",
    "_" : "⿰",
}
dont_print = set()#dont_print.union(stack)

def fetch_char_composition(char):
    with seen_lock:
        if char in seen_chars:
            return seen_chars[char]

    url = f"https://en.wiktionary.org/wiki/{char}"
    try:
        resp = requests.get(url)
        composition = parse_composition(resp.text)
        with seen_lock:
            seen_chars[char] = composition
        return composition
    except Exception as e:
        with seen_lock:
            seen_chars[char] = None
        return None

def decompose_char(char, steps=None, is_root=True):
    cache[char] = "seen"

    if steps is None:
        steps = []

    if char in stop_chars:
        return stop_chars[char], char

    composition = fetch_char_composition(char)
    if not composition:
        return char, char

    steps.append(f"{char} → {composition}")

    components = re.findall(r'[^\u2ff0-\u2fff]', composition)
    decomposed_components = []
    tree_components = []

    for component in components:
        if component != char and component not in stop_chars:
            decomp_result, tree_result = decompose_char(component, steps, False)
            decomposed_components.append(decomp_result)
            tree_components.append(tree_result)
        else:
            decomp_result = stop_chars.get(component, component)
            decomposed_components.append(decomp_result)
            tree_components.append(component)

    structure = composition
    tree_structure = composition

    for i, component in enumerate(components):
        if component != char:
            structure = structure.replace(component, decomposed_components[i], 1)
            tree_structure = tree_structure.replace(component, tree_components[i], 1)

    combining_chars = re.findall(r'[\u2ff0-\u2fff]', composition)
    if combining_chars:
        combiner = combining_chars[0]
        if len(tree_components) >= 1:
            tree_structure = f"{combiner}({','.join(tree_components)})"

        structure = ''.join(c for c in structure if c not in dont_print)

    with seen_lock:
        decomposition_steps[char] = steps.copy()

    return structure, tree_structure

def fetch_char(char):
    try:
        result, tree = decompose_char(char)
        steps = decomposition_steps.get(char, [])
        steps_str = " | ".join(steps) if steps else "No steps"
        output = f"{char}\t{result}\t{tree}\t{steps_str}"
    except Exception as e:
        output = f"{char}\tError: {e}\t\t"

    with print_lock:
        print(output)


cache = dict()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Input file with tab-separated data')
    parser.add_argument('-o', '--offset', help='Char to start recursion at')
    parser.add_argument('--stop-chars', help='Char to stop recursion at')
    parser.add_argument('-n', '--num-samples', type=int, help='Number of samples to process (default: all)')
    parser.add_argument('-r', '--random', action='store_true', help='Randomize sample selection')
    args = parser.parse_args()

    if args.stop_chars:
        for char in args.stop_chars:
            stop_chars[char] = char

    with open(args.file, "r", encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    all_chars = [line.split('\t')[1] for line in lines if len(line.split('\t')) >= 2]

    if args.num_samples is None:
        n_samples = len(all_chars)
    else:
        n_samples = min(args.num_samples, len(all_chars))

    offset = 0
    if args.offset is not None:
        offset = int(args.offset)

    if args.random:
        chars = random.sample(all_chars, n_samples)
    else:
        chars = all_chars[offset:(offset+n_samples)]

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_char, chars)

if __name__ == "__main__":
    main()
