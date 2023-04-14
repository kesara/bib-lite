from flask import Flask, jsonify, request
from urllib.parse import quote
from waitress import serve
import json
import sqlite3
import os


BASE_URL = 'https://devbox.amsl.com'
SQLITE_DB = os.environ['SQLITE_DB']
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'try /get/<document_id> and /search/<query>'


@app.route('/get/<document_id>')
def get(document_id):
    conn = sqlite3.connect(SQLITE_DB)
    with conn:
        result = conn.execute('SELECT * FROM docs WHERE doc_id = ?;',
                              (document_id,))
        doc = result.fetchone() 
        if doc:
            return jsonify({
                'document_id': doc[0],
                'title': doc[1],
                'target': doc[2],
                'absatract': doc[3],
                'date': doc[4],
                'authors': json.loads(doc[5])})
        else:
            return jsonify({'error': 'Document not found'}), 404


@app.route('/search/<query>')
def search(query):
    offset = int(request.values.get('offset', 0))
    limit = int(request.values.get('limit', 100))

    conn = sqlite3.connect(SQLITE_DB)
    with conn:
        result = conn.execute(f'''
SELECT doc_id, title, abstract, '{BASE_URL}/get/' || doc_id AS document_url
FROM docs
WHERE
    doc_id MATCH ? OR
    title  MATCH ? OR
    abstract MATCH ? OR
    authors MATCH ?
ORDER BY rank
LIMIT ?
OFFSET ?;''',
                              (query, query, query, query, limit, offset))
        docs = result.fetchall()
        if len(docs) == limit:
            no = offset + limit
            q = quote(query)
            url = f'{BASE_URL}/search/{q}?limit={limit}&offset={no}'
            return jsonify({
                'documents': docs,
                'next_results': url})
        else:
            return jsonify({'documents': docs})
    return jsonify({'error': 'An error while trying to query database.'})


if __name__ == '__main__':
    serve(app, listen='*:80')
