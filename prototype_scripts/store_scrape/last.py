links_list = []
format_str = '<a href="{url}">{name}</a>'

lines = [line.rstrip('\n') for line in open('bison_urls.txt')]

for line in lines:
    tokens = line.split('/')
    name_raw = tokens[4]
    name = name_raw.replace('-', ' ').title()
    format_str = f'<a href="{line}">{name}</a>'
    print(format_str)
