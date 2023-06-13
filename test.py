import json
import io

f = io.open("100_20.json", "r")
bc = json.load(f)
print(len(bc))
