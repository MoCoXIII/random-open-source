import random

results = []

def avgRatio():
    return sum([h/(h+t) for h, t in results]) / len(results)

while True:
    heads = 0
    tails = 0
    while not heads > tails:
        if random.randint(0, 1) == 0:
            heads += 1
        else:
            tails += 1
    results.append((heads, tails))
    input(f"{avgRatio()}\n{avgRatio()*4}")
