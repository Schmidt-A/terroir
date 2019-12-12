import re
import string

import PyPDF2 as pypdf

# spain = 8 to 15
START_PAGE = 14
END_PAGE = 35  # 14+1


class StateTracker(object):

    WINE_NAME_NEXT = 1
    NEW_WINERY = 2
    PARSING_WINES = 3

    def __init__(self):
        self.parsed_first_spanish = False
        self.curr_winery = None
        self.state = self.NEW_WINERY

class Booth(object):

    def __init__(self, name, num):
        self.name = name
        self.num = num
        self.country = None
        self.wines_raw = []
        self.wines = []

class Wine(object):

    def __init__(self, name):
        self.name = name
        self.rating = 0.0

booths = []

with open('wine_festival_guide.pdf', 'rb') as pdf_file:
    reader = pypdf.PdfFileReader(pdf_file)
    st = StateTracker()

    for i in range(START_PAGE, END_PAGE):
        page = reader.getPage(i)
        page_text = page.extractText()
        lines = page_text.split('\n')

        for line in lines:
            # First spanish wine parses out with "Booth" at the beginning
            if not line.startswith('Booth') and not st.parsed_first_spanish:
                continue
            if not st.parsed_first_spanish:
                st.parsed_first_spanish = True
                # This line starts with 'Booth' so just get rid of it
                line = line[5:]

            # Useless lines
            if 'REPRESENTED BY' in line:
                continue

            # Get winery state management
            if st.state == st.NEW_WINERY:
                if len(line) < 1:
                    continue
                if not re.match(r'\d', line[0]):
                    continue
                try:
                    num, name = line.split(' ', 1)
                except:
                    continue
                winery = Booth(name, num)
                booths.append(winery)
                st.curr_winery = winery
                st.state = st.PARSING_WINES
                continue

            if st.curr_winery:
                wine_ids_split = re.split(r'(\d{5,7})', line)

                for entry in wine_ids_split:
                    # Get rid of whitespace
                    entry = entry.strip()
                    # Get rid of crap that winds up in the wine names that we don't want
                    if 'NEW' in entry:
                        entry = entry.replace('NEW', '')
                    if 'Booth' in entry:
                        entry = entry.replace('Booth', '')

                    # We're splitting on MLCC numbers, wine names always come after this,
                    # so set state = getting a wine name
                    if re.match(r'\d{5,7}', entry):
                        st.state = st.WINE_NAME_NEXT
                        continue

                    if st.state == st.WINE_NAME_NEXT:
                        st.state = st.PARSING_WINES
                        if '...' in entry:
                            st.state = st.NEW_WINERY
                            entry = entry.replace('.', '')
                            entry = entry.strip()

                        while re.search(r'\d+$', entry):
                            entry = entry.rstrip(string.digits)
                            entry = entry.strip()
                        st.curr_winery.wines_raw.append(entry)

                    # last line, set curr_winery to false when done
                    if st.state == st.NEW_WINERY:
                        st.curr_winery = None

for booth in booths:
    print(booth.num, booth.name)
    for wine in booth.wines_raw:
        print(wine)
