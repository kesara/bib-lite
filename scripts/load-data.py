import json
import os
import sqlite3
import sys
import yaml

if len(sys.argv) != 3:
    print(f'Usage: {sys.argv[0]} sqlite_db data_dir')
    sys.exit(1)

sqlite_db = sys.argv[1]
data_dir = sys.argv[2]
conn = sqlite3.connect(sqlite_db)
with conn:
    conn.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(
                        doc_id, title, target, abstract, date, authors);''')


for root, dirs, files in os.walk(data_dir):
    for file in files:
        file_path = os.path.join(root, file)
        with open(file_path, 'r') as f:
            file_contents = f.read()
            data = yaml.safe_load(file_contents)

            doc_id = str(data['id'])
            authors = []
            print(f'loading {doc_id}')
            if not 'contributor' in data.keys():
                print(f'ignoring {doc_id}')
                # ignore these for now
                continue
            for author in data['contributor']:
                if 'person' in author.keys():
                    try:
                        fullname = str(author['person']['name']['completename']['content'])
                    except KeyError:
                        fullname = ''
                    try:
                        initials = str(author['person']['name']['given']['formatted_initials']['content'])
                    except KeyError:
                        initials = ''
                    try:
                        surname = str(author['person']['name']['surname']['content'])
                    except KeyError:
                        surname = ''
                    authors.append({
                        'fullname': fullname,
                        'initials': initials,
                        'surname': surname,
                        })
            try:
                abstract = str(data['abstract'][0]['content'])
            except KeyError:
                abstract = ''
            try:
                title = str(data['title'][0]['content'])
            except KeyError:
                title = ''
            try:
                target = str(data['link'][0]['content'])
            except KeyError:
                target = ''
            try:
                date = str(data['date'][0]['value'])
            except KeyError:
                date = ''

            authors_json = json.dumps({'authors': authors})


            with conn:
                try:
                    conn.execute(
                        'INSERT INTO docs VALUES (?, ?, ?, ?, ?, ?);',
                        (doc_id, title, target, abstract, date, authors_json))
                    conn.commit()
                    print(f'{doc_id} loaded')
                except sqlite3.IntegrityError:
                    print(f'{doc_id} is already loaded')
