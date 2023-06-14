import json
import io
import os
from hashlib import sha256
from operator import add
from math import log
import numpy.random as rand
import random
import sys


def harm(n):
    if n == 0:
        return 0.0
    h = 1.0
    for i in range(2, n + 1):
        h += 1 / i
    return h


def walk(bc, a: int, b: int):
    count = 0
    l = len(bc[str(a)][0]["extra_hashes"])
    while a != b:
        count += 1
        new_a = -1
        extra_hashes = bc[str(a)][0]["extra_hashes"]
        # shuffled = extra_hashes
        # random.shuffle(shuffled)
        # for h in shuffled:
        #     if int(h[0]) >= b:
        #         new_a = int(h[0])
        #         break
        for h in extra_hashes:
            if int(h[0]) >= b and (new_a == -1 or int(h[0]) < new_a):
                new_a = int(h[0])
        if new_a != -1:
            a = new_a
        else:
            a -= 1
    return count, l


def num_links(bc):
    n = len(bc)
    links = [0 for _ in range(n)]
    for i in range(n):
        extra_hashes = bc[str(i)][0]["extra_hashes"]
        for h in extra_hashes:
            links[int(h[0])] += 1
    return links

dr = sys.argv[1]
folders = os.listdir(f"{dr}")
folders.sort(key=lambda x: (int(x.split("_")[0]), int(x.split("_")[1])))
for folder in folders:
    s = 0
    est = 0
    i = 0
    for ff in os.listdir(f"{dr}/{folder}"):
        i += 1
        f = io.open(f"{dr}/{folder}/{ff}", "r")
        bc = json.load(f)
        q = len(bc) - 1
        l = len(bc[str(q)][0]["extra_hashes"])
        if sys.argv[4] == "r":
            for j in range(100):
                b = random.randint(0, q - 1)
                a = random.randint(0, q - 1)
                # if a == b:
                #     a += 1
                if a < b:
                    temp = a
                    a = b
                    b = a
                c, _ = walk(bc, a, b)
                # print(f"{a} | {b} | {a - b} | {l}")
                est += log(q/3, l) / 100
                s += c / 100
        else:
            c, _ = walk(bc, q, 0)
            est += log(q, l)
            s += c
        # jumps = 0
        # pr = (harm(q) - harm(l))/q
        # left = 1 - pr
        # for j in range(1, q):
        #     jumps += j * pr
        #     pr = left * (harm(q) - harm(l))/(q - j)
        #     left = left - pr
        # est += jumps
        # est += log(q)
    print(f"{folder}: {s / i} | {est / i}")

n = int(sys.argv[2])
k = int(sys.argv[3])

links = [0 for _ in range(n + 1)]
files = os.listdir(f"{dr}/{n}_{k}")
for ff in files:
    f = io.open(f"{dr}/{n}_{k}/{ff}", "r")
    links = list(map(add, links, num_links(json.load(f))))
links = [x / len(files) for x in links]
for (i, l) in enumerate(links):
    # d = harm(100) - harm(i)
    print(f"{i}: {l} | {k * (harm(n - 1) - harm(i)) if i > k else k * (harm(n - 1) - harm(k) + 1) - i}")
    # print(f"{i}: {l / ((harm(n - 1) - harm(i)) if i < n - 1 else 1)} | {k * (harm(n - 1) - harm(i)) if i > k else k * (harm(n - 1) - harm(k) + 1) - i}")
    # print(f"{i}: {l}")

# 3 * l / (harm(k*i+1) - harm(i))

def extra_hashes(i: int):
    xs = [hex(3456)]
    n = 20
    for j in range(1, n):
        xs.append(sha256((xs[j - 1] + str(j)).encode('utf-8')).hexdigest())
    rand.seed(sum(map(lambda x: int(x, 16), xs)) % 2 ** 32)

    dist = [1/((i - j) * harm(i - 1)) for j in range(1, i)]

    indices = rand.choice(range(i - 1), size=20, replace=False, p=dist)
    # indices = [int(xs[0], 16) % (i - n)]
    # module = i - n + 1
    # for j in range(1, n):
    #     n_ = int(xs[j], 16) % module
    #     try:
    #         k = indices.index(n_)
    #         indices.append(module - 1)
    #     except:
    #         indices.append(n_)
    #     module += 1
    return sorted(indices)