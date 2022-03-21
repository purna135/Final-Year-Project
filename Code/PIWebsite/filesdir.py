import os

path = "uploadeddata\\"

files = [f for r, d, f in os.walk(path)]
for f in files:
    for x in f:
        print(x)