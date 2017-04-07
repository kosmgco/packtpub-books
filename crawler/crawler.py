#!/usr/bin/env python
# coding: utf-8

import re
import os
import requests
from qiniu import Auth, put_data
from datetime import datetime
from bs4 import BeautifulSoup

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}

ak, sk = os.environ["QINIUAK"], os.environ["QINIUSK"]
email, password = '', ''

q = Auth(ak, sk)


def login():
    url = 'https://www.packtpub.com/'
    res = session.get(url, timeout=30, verify=False)
    soup = BeautifulSoup(res.content, 'html5lib')
    form_id = soup.find('input', {'name': 'form_build_id'}).get('value', '')
    data = {
        'email': email,
        'password': password,
        'op': 'Login',
        'form_build_id': form_id,
        'form_id': 'packt_user_login_form'
    }
    res = session.post(url, data=data, timeout=30, verify=False)


def download_book():
    free_book_url = 'https://www.packtpub.com/packt/offers/free-learning'
    res = session.get(free_book_url, timeout=30, verify=False)
    soup = BeautifulSoup(res.content, 'html5lib')
    book_id = soup.find('a', {'class': 'twelve-days-claim'})
    author = ''
    description = soup.find('div', {'class': 'dotd-main-book-summary'}).find_all('div')[2].get_text().strip()
    book_id = re.search(r'/.*?/(.*?)/\d+', book_id.get('href', '')).group(1)
    title = re.subn(r'\s+', '_', soup.find('div', {'class': 'dotd-title'}).get_text().strip())[0]
    # pdf
    title_pdf = title + '.pdf'
    download_url = 'https://www.packtpub.com/ebook_download/{book_id}/pdf'.format(book_id=book_id)
    content = session.get(download_url, timeout=30, verify=False)
    print content.headers.get('Content-Type', '')
    if 'application/pdf' in content.headers.get('Content-Type', ''):
        upload_to_qiniu(title_pdf, content.content, author, description)

    # epub
    download_url = 'https://www.packtpub.com/ebook_download/{book_id}/epub'.format(book_id=book_id)
    title_epub = title + '.epub'
    content = session.get(download_url, timeout=30, verify=False)
    print content.headers.get('Content-Type', '')
    if 'application/epub+zip' in content.headers.get('Content-Type', ''):
        upload_to_qiniu(title_epub, content.content, author, description)

    # mobi
    download_url = 'https://www.packtpub.com/ebook_download/{book_id}/epub'.format(book_id=book_id)
    title_mobi = title + '.mobi'
    content = session.get(download_url, timeout=30, verify=False)
    print content.headers.get('Content-Type', '')
    if 'application/epub+zip' in content.headers.get('Content-Type', ''):
        upload_to_qiniu(title_mobi, content.content, author, description)

    # code
    download_url = 'https://www.packtpub.com/code_download/' + book_id
    title_code = title + '.zip'
    content = session.get(download_url, timeout=30, verify=False)
    print content.headers.get('Content-Type', '')
    if 'application/zip' in content.headers.get('Content-Type', ''):
        upload_to_qiniu(title_code, content.content, author, description)


def upload_to_qiniu(title, content, author, description):
    bucket = 'packtpub-books'
    key = datetime.now().strftime('%Y/%m/%d/') + title
    token = q.upload_token(bucket, key, 3600)
    ret, info = put_data(token, key, content)
    print ret, info


if __name__ == '__main__':
    login()
    download_book()
