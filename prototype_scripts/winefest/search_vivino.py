from difflib import SequenceMatcher
import json
import pprint
import requests

algolia_url = 'https://9takgwjuxl-dsn.algolia.net/1/indexes/WINES_prod/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.32.1&x-algolia-application-id=9TAKGWJUXL&x-algolia-api-key=60c11b2f1068885161d95ca068d3a6ae'

headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'hungry for wine 0.1'
}

def get_algolia_json(wine):
    payload = {
        'params': 'query={}&hitsPerPage=6'.format(wine)
    }
    r = requests.post(algolia_url, json.dumps(payload), headers=headers)
    return json.loads(r.content.decode('utf-8'))

def get_and_record_vivino_data(winelist_file):
    result_set = []

    with open(winelist_file, 'r') as winelist:
        for wine in winelist:

            # Preparing the data in a format that algolia endpoint likes better
            wine = wine.strip()
            # Keep track of original wine name
            orig_name = wine
            wine = wine.replace('-', ' ')
            print('Searching for ID for {}...'.format(wine))
            result = get_algolia_json(wine)

            # This algolia search interface doesn't like long search strings, so
            # we'll try stripping down the wine name and see if we can get anything
            # if no hits come back for the original name
            try:
                if len(result['hits']) < 1:
                    print('No hit, retrying with shorter names...')
                    wine_words = wine.split(' ')[:-1]
                    while len(result['hits']) < 1 and len(wine_words) > 1:
                        wine = ' '.join(wine_words)
                        print('Searching for ID for {}...'.format(wine))
                        result = get_algolia_json(wine)
                        wine_words = wine.split(' ')[:-1]

                if len(result['hits']) > 0:
                    print(
                        'Collecting data for {} (successful query was {})'.format(
                            orig_name, wine))
                    #wine_data = Wine(orig_name, result['hits'][0])
                    #wines.append(wine_data)
                    result_set.append(
                        {
                            'wine_fest_name': orig_name,
                            'vivino_data': result['hits'][0]
                    })
                else:
                    result_set.append(
                        {
                            'wine_fest_name': orig_name,
                            'vivino_data': None
                    })
            except KeyError:
                result_set.append(
                    {
                        'wine_fest_name': orig_name,
                        'vivino_data': None
                })

    print('Writing to results file')
    with open('{}.search_results'.format(winelist_file), 'w') as outfile:
        json.dump(result_set, outfile)

#get_and_record_vivino_data('all.txt')
get_and_record_vivino_data('bison_names.txt')

