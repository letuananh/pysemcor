# -*- coding: utf-8 -*-

'''
Semcor data in XML format
Latest version can be found at https://github.com/letuananh/pysemcor

References:
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, pysemcor"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import logging
import json

from lxml import etree
from bs4 import BeautifulSoup

from chirptext import FileHelper
from chirptext.leutile import StringTool
from chirptext import ttl
from yawlib import SynsetID
from yawlib.helpers import get_wn

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
wn = get_wn()


# -------------------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------------------

class TokenInfo:

    def __init__(self, text, **kwargs):
        self.text = text
        self.__data = dict(kwargs)

    def __contains__(self, key):
        return key in self.__data

    def __getitem__(self, key):
        return self.__data[key]

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __setitem__(self, key, value):
        self.__data[key] = value

    @property
    def data(self):
        return self.__data.items()

    @property
    def lemma(self):
        return self['lemma'] if 'lemma' in self else self.text

    def to_json(self):
        data = dict(self.__data)
        data['text'] = self.text
        return data

    def __repr__(self):
        return "{}:{}".format(self.text, self.__data)

    def __str__(self):
        return "{}:{}".format(self.text, self.__data)


class FileSet(object):

    def __init__(self, root):
        self.root = root
        self.__files = []

    @property
    def root(self):
        return self.__root

    @root.setter
    def root(self, value):
        self.__root = FileHelper.abspath(value)

    def add_all(self, path):
        folderpath = os.path.join(self.root, path)
        files = FileHelper.get_child_files(folderpath)
        for f in files:
            self.add(os.path.join(path, f))

    def add(self, path):
        self.__files.append(path)

    def __getitem__(self, idx):
        return self.__files[idx]

    def __len__(self):
        return len(self.__files)

    def abspaths(self):
        return [os.path.join(self.root, p) for p in self]

    def abspath(self, path):
        return path if os.path.isabs(path) else os.path.join(self.root, path)


class SemcorXML(object):

    def __init__(self, root):
        self.files = FileSet(root)
        self.files.add_all('brown1/tagfiles')
        self.files.add_all('brown2/tagfiles')
        self.files.add_all('brownv/tagfiles')

    @property
    def root(self):
        return self.files.root

    def iterparse(self, path):
        tree = etree.iterparse(self.files.abspath(path), events=('start', 'end'))
        filename = 'n/a'
        para = 'n/a'
        for event, element in tree:
            if event == 'start':
                if element.tag == 'context':
                    filename = element.get('filename')
                elif element.tag == 'p':
                    para = element.get('pnum')
            if event == 'end':
                if element.tag == 's':
                    # found a sentence
                    snum = element.get('snum')
                    tokens = []
                    for token in element:
                        token_data = dict(token.attrib)
                        token_data['tag'] = token.tag
                        text = fix_token_text(token.text)
                        if token.tag == 'wf':
                            # create sensekey
                            lemma = StringTool.strip(token.get('lemma'))
                            lexsn = StringTool.strip(token.get('lexsn'))
                            sk = lemma + '%' + lexsn if lemma and lexsn else ''
                            sk = StringTool.strip(sk.replace('\t', ' ').replace('|', ' '))
                            if sk:
                                token_data['sk'] = sk
                            tokens.append(TokenInfo(text, **token_data))
                        elif token.tag == 'punc':
                            tokens.append(TokenInfo(text, **token_data))
                    element.clear()
                    s = {'para': para,
                         'filename': filename,
                         'snum': snum,
                         'sid': "{}-{}-{}".format(filename, para, snum),
                         'tokens': tokens}
                    yield s
                elif element.tag == 'p':
                    para = 'n/a'
                    element.clear()
                elif element.tag == 'context':
                    filename = 'n/a'
                    element.clear()

    def iter_ttl(self, limit=None, with_nonsense=True):
        sk_map = {}
        # Convert sentence by sentence to TTL
        with wn.ctx() as wnctx:
            for f in self.files[:limit] if limit else self.files:
                for sj in self.iterparse(f):
                    s = to_ttl(sj, with_nonsense=with_nonsense, sk_map=sk_map, wnctx=wnctx)
                    yield s

    def convert_to_ttl(self, ttlset, limit=None, with_nonsense=True):
        sk_map = {}
        with wn.ctx() as wnctx:
            for f in self.files[:limit] if limit else self.files:
                xml2ttl(f, self, ttlset, with_nonsense=with_nonsense, sk_map=sk_map, wnctx=wnctx)


# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------

def xml2json(inpath, scxml, scjson):
    new_name = FileHelper.getfilename(inpath) + ".json"
    dir_name = os.path.dirname(inpath)
    outpath = scjson.abspath(os.path.join(dir_name, new_name))
    if os.path.isfile(outpath):
        print("SKIPPED: {} (output file exists)".format(outpath))
        return
    else:
        print("Generating: {} => {}".format(inpath, outpath))
    dirpath = os.path.dirname(outpath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with open(outpath, 'wt') as outfile:
        for sj in scxml.iterparse(inpath):
            sj['tokens'] = [t.to_json() for t in sj['tokens']]
            outfile.write(json.dumps(sj))
            outfile.write("\n")


def xml2ttl(inpath, scxml, scttl, with_nonsense=True, sk_map=None, wnctx=None):
    ''' convert all semcor files in XML format to ttl format '''
    new_name = FileHelper.getfilename(inpath) + ".json"
    dir_name = os.path.dirname(inpath)
    outpath = scttl.abspath(os.path.join(dir_name, new_name))
    if os.path.isfile(outpath):
        print("SKIPPED: {} (output file exists)".format(outpath))
        return
    else:
        print("Generating: {} => {}".format(inpath, outpath))
    dirpath = os.path.dirname(outpath)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    with open(outpath, 'wt') as outfile:
        for sj in scxml.iterparse(inpath):
            s = to_ttl(sj, with_nonsense=with_nonsense, sk_map=sk_map, wnctx=wnctx)
            outfile.write(json.dumps(s.to_json()))
            outfile.write("\n")


def to_ttl(sent, with_nonsense=True, sk_map=None, wnctx=None):
    tokens = sent['tokens']
    text = detokenize(tokens)
    s = ttl.Sentence(text=text, ident=sent['sid'])
    s.import_tokens((t.text for t in tokens))
    for tinfo, tk in zip(tokens, s):
        for k, v in tinfo.data:
            if (k, v) == ('tag', 'wf') or k == 'sk':
                continue
            if k == 'lemma':
                tk.lemma = v
            elif k == 'pos':
                tk.pos = v
            else:
                tk.new_tag(label=v, tagtype=k)
        # if sensekey exists, add it as a concept
        lemma = tinfo.lemma
        sk = fix_sensekey(tinfo.get('sk'))
        rdf = tinfo.get('rdf')
        if sk and (with_nonsense or not is_nonsense(lemma, sk, rdf)):
            sensetag = sk
            if sk_map is not None and sk in sk_map:
                sensetag = sk_map[sk]
            elif wnctx is not None:
                # try to determine synsetID
                ss = wnctx.senses.select_single('sensekey=?', (sk,))
                if ss is not None:
                    sid = str(SynsetID.from_string(ss.synsetid))
                    if sk_map is not None:
                        sk_map[sk] = sid
                        sensetag = sid
                else:
                    # sensekey not found
                    logger.warning("There is no synsetID with sensekey={} | rdf={}".format(sk, rdf))
            s.new_concept(clemma=lemma, tag=sensetag, tokens=(tk,))
    return s


KNOWN_KEYS = {"n't%4:02:00::": "not%4:02:00::"}


def fix_sensekey(sk):
    return KNOWN_KEYS[sk] if sk in KNOWN_KEYS else sk


NONSENSE = [('person%1:03:00::', 'person'),
            ('group%1:03:00::', 'group'),
            ('location%1:03:00::', 'location')]


def is_nonsense(lemma, sk, rdf):
    return ((sk, rdf) in NONSENSE) or lemma == 'be'


def fix_token_text(tk):
    tk = StringTool.strip(tk).replace('\t', ' ').replace('|', ' ').replace('_', ' ')
    tk = tk.replace(" ' nuff", " 'nuff")
    tk = tk.replace("Ol ' ", "Ol' ")
    tk = tk.replace("O ' ", "O' ")
    tk = tk.replace("ma ' am", "ma'am")
    tk = tk.replace("Ma ' am", "Ma'am")
    tk = tk.replace("probl ' y", "probl'y")
    tk = tk.replace("ai n't", "ain't")
    tk = tk.replace("holdin '", "holdin'")
    tk = tk.replace("hangin '", "hangin'")
    tk = tk.replace("dryin ' ", "dryin' ")
    tk = tk.replace("Y ' all", "Y'all")
    tk = tk.replace("y ' know", "y'know")
    tk = tk.replace("c ' n", "c'n")
    tk = tk.replace("l ' identite", "l'identite")
    tk = tk.replace("Rue de L ' Arcade", "Rue de l'Arcade")
    tk = tk.replace("p ' lite", "p'lite")
    tk = tk.replace("rev ' rend", "rev'rend")
    tk = tk.replace("coup d ' etat", "coup d'etat")
    tk = tk.replace("t ' gethuh", "t'gethuh")
    tk = tk.replace('``', "“")
    tk = tk.replace("''", "”")
    tk = tk.replace(" ,", ",")
    tk = tk.replace("( ", "(")
    tk = tk.replace(" )", ")")
    tk = tk.replace(" ”", "”")
    tk = tk.replace(" 's", "'s")
    tk = tk.replace("o '", "o'")
    tk = tk.replace("s ' ", "s' ")
    tk = tk.replace(" , ", ", ")
    # tk = tk.replace(" ' ", "' ")
    return tk


def detokenize(tokens):
    sentence_text = ' '.join([x.text for x in tokens])
    sentence_text = sentence_text.replace(" , , ", ", ")
    sentence_text = sentence_text.replace(' , ', ', ').replace('“ ', '“').replace(' ”', '”')
    sentence_text = sentence_text.replace(' ! ', '! ').replace(" 'll ", "'ll ").replace(" 've ", "'ve ").replace(" 're ", "'re ").replace(" 'd ", "'d ")
    sentence_text = sentence_text.replace(" 's ", "'s ")
    sentence_text = sentence_text.replace(" 'm ", "'m ")
    sentence_text = sentence_text.replace(" ' ", "' ")
    sentence_text = sentence_text.replace(" ; ", "; ")
    sentence_text = sentence_text.replace("( ", "(")
    sentence_text = sentence_text.replace(" )", ")")
    sentence_text = sentence_text.replace(" n't ", "n't ")
    # sentence_text = sentence_text.replace("Never_mind_''", "Never_mind_”")
    # sentence_text = sentence_text.replace("327_U._S._114_''", "327_U._S._114_”")
    # sentence_text = sentence_text.replace("``", "“")
    # sentence_text = sentence_text.replace("''", "”")
    sentence_text = sentence_text.replace("  ", " ")
    if sentence_text[-2:] in (' .', ' :', ' ?', ' !'):
        sentence_text = sentence_text[:-2] + sentence_text[-1]
    sentence_text = sentence_text.strip()
    return sentence_text


def fix_3rada(root, output_dir):
    ds_3rada = SemcorXML(root)
    for f in ds_3rada.files:
        inpath = os.path.join(ds_3rada.root, f)
        outpath = os.path.join(output_dir, f + ".xml")
        fix_malformed_xml_file(inpath, outpath)


def fix_malformed_xml_file(inpath, outpath):
    if os.path.isfile(outpath):
        print("SKIPPED: {} (output file exists)".format(outpath))
        return
    print('Fixing the file: %s ==> %s' % (inpath, outpath))
    with open(inpath) as infile:
        soup = BeautifulSoup(infile.read(), 'lxml')
    # create output dir if needed
    outdir = os.path.dirname(outpath)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    with open(outpath, 'w') as outfile:
        outfile.write(soup.prettify())
