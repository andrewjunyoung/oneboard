import sys

subs = {}
overrides = {("讠", "訁")}

def load_tokens(tokens_file):
   with open(tokens_file, "r") as file:
       lines = file.readlines()
       for line in lines:
           splitline = line.split("\t")
           char = splitline[0]
           new_token = splitline[2].strip("\n")
           subs[char] = new_token
   print(subs)

composition = {
"⿰": "_",
"⿲": "__",
"⿱": "|",
"⿳": "||",
"⿴": ")",
"⿵": ")",
"⿷": ")",
"⿶": ")",
"⿸": ")",
"⿹": ")",
"⿺": "_",
"⿻": ")",
}


def reanalyze(s: str):
    analyses = s.split("|")
    char = analyses[0].split("→")[0]
    analysis = analyses[0].split("→")[1]
    for n, item in enumerate(analyses):
        if n == 0:
            continue
        sub_char = item.split("→")[0].strip(" ")
        sub_analysis = item.split("→")[1].strip(" ")
        if (sub_char, sub_analysis) in overrides:
            continue
        analysis = analysis.replace(sub_char, sub_analysis)
    return analysis


def main(input_path, output_path, restructure=False):
    output_lines = []
    with open(input_path, 'r') as file:
        lines = file.readlines()

    for n, line in enumerate(lines):
        splits = line.split("\t")
        if splits[0] in ["裏", "䦟"]:
            output_lines.append(f"skip: {line}")
            continue
        try:
            reanalysis = splits[3].strip("\n")
            raw_reanalysis = reanalyze(reanalysis)
            reanalysis = raw_reanalysis
            for sub in subs.keys():
                if (sub, subs[sub]) in overrides:
                    print("sub", n)
                    output_lines.append(f"sub: {line}")
                    continue
                reanalysis = reanalysis.replace(sub, subs[sub])
            for sub in composition.keys():
                reanalysis = reanalysis.replace(sub, composition[sub])

            if " /" in reanalysis or "(" in reanalysis:
                print("/(", n, reanalysis)
                output_lines.append(f"/(: {line}")
                continue
            if restructure:
                line = [reanalysis.strip(" "), splits[0]]
            else:
                line = [
                    splits[0],
                    reanalysis,
                    raw_reanalysis,
                    splits[3],
                ]
            new_line = "\t".join(line)
            output_lines.append(new_line)
        except:
            print("no changes:", line)
            output_lines.append(f"no changes: {line}")

    with open(output_path, "w") as file:
        for output_line in output_lines:
            file.write(output_line + "\n")


if __name__ == "__main__":
   if len(sys.argv) < 2:
       print("Usage: python script.py <input_file> [-r]")
       sys.exit(1)

   input_file = sys.argv[1]
   output_file = "tmp.txt"
   restructure = False

   for arg in sys.argv[2:]:
       if arg == "-r":
           restructure = True
       elif not arg.startswith("-"):
           output_file = arg

   load_tokens("tokens.txt")
   main(input_file, output_file, restructure)
