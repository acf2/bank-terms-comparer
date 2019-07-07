#!/usr/bin/env python3.5

# Ad hoc bank terms comparer.
# Probably could be done better.
#
# it needs requests and scrapy
# pdf-diff must be accessible in PATH


import os
import sys
import requests
from scrapy.selector import Selector
import json
from hashlib import sha256
#import pdf_diff # Better use it from commandline


image_viewer = 'feh'
pdf_viewer = 'evince'


bank_info = {
    'rocketbank': {
        'terms': 'rocketbank_terms.pdf',
        'terms_template': 'rocketbank_terms_no_%s.pdf',
        'diff_file': 'rocketbank_diff.png',
    },
    'tinkoff': {
        'terms': 'tinkoff_terms.pdf',
        'terms_template': 'tinkoff_terms_no_%s.pdf',
        'diff_file': 'tinkoff_diff.png'
    }
}


def download_rocketbank_terms(filename):
    site = 'https://rocketbank.ru'

    path_docs = '/docs/terms-of-service'

    r = requests.get(site + path_docs)
    path_json = Selector(text=r.text).xpath('//head//link[@as="fetch" and @rel="preload"]/@href').extract()[0]

    r2 = requests.get(site + path_json)
    path_pdf = json.loads(r2.text)['data']['content']['meta']['currentFile']['publicURL']

    r3 = requests.get(site + path_pdf)
    with open(filename, 'wb') as terms:
        terms.write(r3.content) # content is just raw bytes


def download_tinkoff_terms(filename):
    address = 'https://static.tinkoff.ru/documents/docs/terms_of_integrated_banking_services.pdf'

    r = requests.get(address)
    with open(filename, 'wb') as terms:
        terms.write(r.content)


def get_sha256(filename):
    hashfunc = sha256()
    with open(filename, 'rb') as f:
        hashfunc.update(f.read())
    return hashfunc.hexdigest()


def get_edition_number(bank):
    if not os.path.isfile(bank_info[bank]['terms_template'] % 1):
        return None
    i = 1
    while os.path.isfile(bank_info[bank]['terms_template'] % (i + 1)):
        i += 1
    return i


def does_terms_differ(bank, download_function):
    if not bank in bank_info:
        raise Exception('Unknown bank name')

    download_function(bank_info[bank]['terms'])
    current_edition = get_edition_number(bank)
    if current_edition is None:
        os.rename(bank_info[bank]['terms'], bank_info[bank]['terms_template'] % 1)
        return True
    old_terms = bank_info[bank]['terms_template'] % current_edition
    if get_sha256(bank_info[bank]['terms']) == get_sha256(old_terms):
        os.remove(bank_info[bank]['terms'])
        return False
    os.system('pdf-diff -f png %s %s > %s' % (old_terms, bank_info[bank]['terms'], bank_info[bank]['diff_file']))
    os.rename(bank_info[bank]['terms'], bank_info[bank]['terms_template'] % (current_edition + 1))
    return True


def open_diff_for(bank):
    if not bank in bank_info:
        raise Exception('Unknown bank name')

    if not os.path.isfile(bank_info[bank]['diff_file']):
        os.system('%s %s' % (pdf_viewer, bank_info[bank]['terms_template'] % get_edition_number(bank)))
        return
    os.system('%s %s' % (image_viewer, bank_info[bank]['diff_file']))
    return


def main(argv):
    for bank in bank_info:
        if bank == 'rocketbank':
            downloader = download_rocketbank_terms
        elif bank == 'tinkoff':
            downloader = download_tinkoff_terms
        else:
            raise Exception('Unknown bank name')

        if does_terms_differ(bank, downloader):
            open_diff_for(bank)


if __name__ == '__main__':
    exit(main(sys.argv))
