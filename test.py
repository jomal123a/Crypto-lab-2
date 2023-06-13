import json
import io


def walk(bc, a: int, b: int):
    count = 0
    while a != b:
        count += 1
        new_a = -1
        extra_hashes = bc[str(a)][0]["extra_hashes"]
        for h in extra_hashes:
            if int(h[0]) == b:
                return count
            if int(h[0]) > b:
                new_a = int(h[0])
                break
            count += 1
        if new_a != -1:
            a = new_a
        else:
            a -= 1


f = io.open("100_20.json", "r")
bc = json.load(f)
print(walk(bc, 100, 0))
