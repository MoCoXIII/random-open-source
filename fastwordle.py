import re

# wordle solver utility
# needs wordlist.txt to be filled with a list of valid words, each word in a new line.
# it then asks you to provide information about the wordle, and returns a list of valid words
# or if there are more than 20 (customizable) valid words, it provides you with words that are NOT it, but can provide more information

wordList = list(open("wordlist.txt", "r").read().split("\n"))
all_letters = "abcdefghijklmnopqrstuvwxyz"
print(".- anything\n.a fixed letter\n!abcde letters elsewhere\n;abcde letters not included")
instructions = str(input("Instructions: "))


def instructionsToLetters(instructions):
    return re.findall(r"([.!;])([^.!;]+)", instructions)


letters = instructionsToLetters(instructions)


def get_valids(letters, noDoubles=False):
    anyways = {}
    valids = []
    for word in wordList:
        valid = True
        letter_counts = {char: word.count(char) for char in all_letters}
        if noDoubles:
            for letter_count in letter_counts.values():
                if letter_count >= 2:
                    valid = False
                    break
        for letter in all_letters:
            anyways[letter] = 0
        for index, (marker, chars) in enumerate(letters):
            if marker == '.':
                current_letter = word[index]
                if current_letter != chars and not chars == '-':
                    valid = False
                    break
                elif current_letter == chars:
                    anyways[chars] += 1
            elif marker == '!':
                for char in chars:
                    anyways[char] += 1
                for char in chars:
                    if char == word[index]:
                        valid = False
                        break
                if not all(char in word for char in chars):
                    valid = False
                    break
            elif marker == ";":
                for char in chars:
                    if char in word and letter_counts[char] > anyways[char]:
                        valid = False
                        break
        if valid:
            valids.append(word)
    return valids


valids = get_valids(letters)
oldValids = valids
if len(valids) > 20:
    previousLetters = ""
    for match in letters:
        for letter in match[1]:
            if letter != "-":
                previousLetters += letter
    newInstructions = f";{previousLetters}"
    print(f"More than 20 possible words, guess more letters! Used letters: {previousLetters}")
    newLetters = instructionsToLetters(newInstructions)
    valids = get_valids(newLetters, noDoubles=True)
if len(valids) == 0:
    print("Oh, no more pure words left. Here's the rest:")
    valids = oldValids

idx = 0
for word in valids:
    idx += 1
    print(word, end=" " if idx % 20 != 0 else "\n")
