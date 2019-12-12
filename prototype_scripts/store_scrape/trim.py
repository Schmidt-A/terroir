unique = set(open('wine_urls.txt').readlines())

with open('wine_cleaned.txt', 'w') as f:
    f.writelines(set(unique))
