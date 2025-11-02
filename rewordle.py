import re

wordlist = open("wordlist.txt").read()

# wordle solver implementation using regex
# requires wordlist.txt to be a list of valid words seperated by any regex word boundary (\b)

def find_words(f, orange, rest):
    lookaheads = ""
    musts = ""
    orange_dict = {c: 0 for c, n in orange}
    for c, n in orange:
        orange_dict[c] += int(n or 1)
    for c, n in orange_dict.items():
        comma = True
        if c in f:
            f = f.replace(c, "")
            comma = False
        must = fr"(?=(?:[^{c} \n]*?{c})"
        if n:
            if comma:
                must += "{" + str(n) + ",}?"
            else:
                must = fr"(?!(?:.*[{c}])"
                must += "{" + str(n + 1) + "}"
        musts += must
        musts += ")"
    rest_dict = {l: 0 for l in rest}
    for l in rest:
        rest_dict[l] += 1
    for l in rest_dict.keys():
        if l in f:
            f = f.replace(l, "")
            musts += fr"(?!(?:.*[{l}])"
            musts += "{" + str(rest_dict[l] + 1) + "})"
    lookaheads += musts
    lookaheads += fr"(?=[^{f} \n]+?\b)" if f else ""  # forbidden letters
    pattern = fr"\b{lookaheads}{rest}{r"\w*?\b" if r"\b" not in rest else ""}"
    print(pattern)
    results = re.findall(pattern, wordlist)
    result_string = "\n".join(results)
    res = [tup[1] for tup in re.findall(r"\b(?!.*(.).*\1)([^ \n]+)\b", result_string)]
    return results, res


letters = ""
f = ""
done = False
while not done:
    f += str(input(f"New Grey ({f}): "))
    letters += f
    oranges = str(input("Orange (<letter>[count]): "))
    for r in re.findall(r"\w", oranges):
        letters += r
    orange = re.findall(r"(\w)(\d*)", oranges)
    green = str(input("Word (!x, for [^x]): "))
    for r in re.findall(r"\w", green):
        letters += r
    rest = re.sub(r"!(.+?),", r"[^\1]", green)
    if not rest:
        rest = "."

    results, res = find_words(f, orange, rest)

    if len(results) > 20:
        pat = fr"\b(?!.*(.).*\1)([^{letters} \n]+)\b"
        print(pat, end=" ")
        res = [tup[1] for tup in re.findall(pat, wordlist)]
        if len(res) != 0:
            print("applied")
            results = res
        else:
            print("tried")

    print("All results:")
    for i, result in enumerate(results):
        print(f"{result}", end="\n" if (i + 1) % 20 == 0 else " ")
    print("\nWithout Duplicates:")
    for i, result in enumerate(res):
        print(f"{result}", end="\n" if (i + 1) % 20 == 0 else " ")
    print()
