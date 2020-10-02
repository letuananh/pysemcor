# -*- coding: utf-8 -*-

''' Convert Semcor into TTL SQLite

Latest version can be found at https://github.com/letuananh/pysemcor

:copyright: (c) 2017 Le Tuan Anh <tuananh.ke@gmail.com>
:license: MIT, see LICENSE for more details.
'''

import logging
from texttaglib import TTLSQLite
from texttaglib import ttl
from pysemcor import SemcorXML


db = TTLSQLite('data/semcor.ttl.db')
brown1 = db.ensure_corpus(name='brown1')
brown2 = db.ensure_corpus(name='brown2')
brownv = db.ensure_corpus(name='brownv')
corpuses = {'brown1': brown1,
            'brown2': brown2,
            'brownv': brownv}
try:
    semxml = SemcorXML(root='data/3rada_ttl')
except:
    print("Did you convert Semcor to TTL by using `python main.py ttl`?")
    exit()
logger = logging.getLogger(__name__)

all_files = semxml.files
# all_files = ['brown1/tagfiles/br-b13.json']
for idx, fn in enumerate(all_files):
    corpus = corpuses[fn[:6]]
    doc_ttl = ttl.Document.from_json_file(semxml.files.abspath(fn))
    doc_obj = db.doc.select_single('name=?', (doc_ttl.name,))
    if doc_obj is not None:
        logger.warning("Doc {} exists. Cannot import".format(doc_ttl.name))
    else:
        print("Importing {} into {} ({}/{})".format(doc_ttl.name, corpus.name, idx + 1, len(semxml.files)))
        # create the doc
        doc_obj = db.ensure_doc(name=doc_ttl.name, corpus=corpus)
        for sent in doc_ttl:
            # clear ID
            sent.ID = None
            sent.docID = doc_obj.ID
            db.save_sent(sent)

print("Done!")
