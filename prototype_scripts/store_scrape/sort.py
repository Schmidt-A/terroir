with open('wine_cleaned.txt') as f:
    lines = sorted(f.readlines())

with open('wine_sorted.txt', 'w') as f:
    f.writelines(lines)
