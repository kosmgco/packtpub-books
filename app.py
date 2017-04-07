#!/usr/bin/env python
# coding: utf-8
__author__ = 'scdev1003'

import re
import os
import json
from qiniu import Auth
from qiniu import BucketManager
from flask import Flask, jsonify, request

ak = os.environ["QINIUAK"]
sk = os.environ["QINIUSK"]

q = Auth(ak, sk)

bucket = BucketManager(q)
app = Flask(__name__)

@app.route('/')
def index():
    callback = request.args.get('callback', '')
    bucket_name = 'packtpub-books'
    res = bucket.list(bucket_name)
    books = {}
    for item in res[0].get('items', []):
        key = '.'.join(item.get('key', '').split('.')[0:-1])
        name = re.search(r'^\d{4}\/\d{2}\/\d{2}\/(.*)$', key).group(1)
        date = re.search(r'^(\d{4}\/\d{2}\/\d{2})\/.*$', key).group(1)
        if books.get(date, None) == None:
            books.update({date: {}})
            books[date]["keys"] = []
        books[date].update({'name': name})
        books[date]["domain"] = 'packtpub.ooops.me'
        books[date]["keys"].append(item.get('key', ''))
    return callback + "(%s)" %json.dumps(books, ensure_ascii=False)


if __name__ == '__main__':
    app.run()
