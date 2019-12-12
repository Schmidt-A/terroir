import csv
from difflib import SequenceMatcher
import json
import pprint

class Wine(object):

    def __init__(self, wine_fest_name, result=None):
        self.wine_fest_name = wine_fest_name
        if result is not None:
            self.vivino_name = result['name']
            # This is the internal integer ID that vivino uses to track a wine.
            # Their api endpoints require it. I haven't used them here because
            # everything we needed came back from the algolia endpoint, but
            # I wanted to keep tabs on it for future work
            self.vivino_id = result['id']
            if result['winery'] is not None:
                self.winery = result['winery']['name']
            else:
                self.winery = ''
            self.rating = result['statistics']['ratings_average']
            self.num_ratings = result['statistics']['ratings_count']

            # Calculate similarity between the returned Vivino wine name and
            # what we originally searched for.
            # Wine fest strings have winery name included so add winery name
            # to vivino result in order to have similtude be less skewed if
            # winery name isn't present
            if self.winery not in self.vivino_name:
                similtude_vivino_name = self.winery + ' ' + self.vivino_name
            else:
                similtude_vivino_name = self.vivino_name
            self.match_confidence = SequenceMatcher(
                None, self.wine_fest_name, similtude_vivino_name).ratio()

        else:
            self.vivino_name = ''
            self.vivino_id = -1
            self.winery = ''
            self.rating = 0.0
            self.num_ratings = 0
            self.match_confidence = 0.0

parsed_wines = []

def parse_results_file(fname):
    with open(fname, 'r') as f:
        data = json.load(f)
        for record in data:
            # record['vivino_data'] will be None if we didn't find anything
            wine_data = Wine(record['wine_fest_name'], record['vivino_data'])
            parsed_wines.append(wine_data)

print('Parsing wine list files...')
parse_results_file('spanish.txt.search_results')
parse_results_file('all.txt.search_results')
print('... Done.')

print('Writing parsed results to CSV file...')
with open('wine_fest_vivino.csv', 'w') as csvfile:
    fieldnames = [
        'wine_fest_name',
        'vivino_name',
        'winery',
        'rating',
        'num_ratings',
        'match_confidence'
    ]

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for entry in parsed_wines:
        writer.writerow({
            'wine_fest_name': entry.wine_fest_name,
            'vivino_name': entry.vivino_name,
            'winery': entry.winery,
            'rating': entry.rating,
            'num_ratings': entry.num_ratings,
            'match_confidence': entry.match_confidence
        })
print('...Done.')
