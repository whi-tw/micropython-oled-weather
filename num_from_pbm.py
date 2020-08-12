char_mapping = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "."]
all = []
for char in char_mapping:
    with open("pbm/numerals/{}.pbm".format(char), 'rb') as f:
        f.readline()  # Magic number
        f.readline()  # Creator comment
        width, height = [int(v) for v in f.readline().split()]
        data = bytearray(f.read())
        all+=[data, width, height]

print(all)