#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
pySemcor toolkit
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
import argparse

from chirptext import Counter, TextReport, header
from chirptext.texttaglib import TaggedDoc
from yawlib import SynsetID
from pysemcor.semcorxml import fix_3rada, xml2json
from pysemcor.semcorxml import FileSet, SemcorXML

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))
SEMCOR_ORIG = os.path.abspath('./data/3rada')
SEMCOR_FIXED = os.path.abspath('./data/3rada_fixed')
SEMCOR_JSON = os.path.abspath('./data/3rada_json')
SEMCOR_TTL = os.path.abspath('./data/3rada_ttl')


# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------

def fix(args):
    fix_3rada(SEMCOR_ORIG, SEMCOR_FIXED)


def to_json(args):
    sc = SemcorXML(SEMCOR_FIXED)
    sc_json = FileSet(SEMCOR_JSON)
    for f in sc.files:
        xml2json(f, sc, sc_json)


def to_ttl(args):
    ''' Convert fixed XML to TTL '''
    sc = SemcorXML(SEMCOR_FIXED)
    scttl = FileSet(SEMCOR_TTL)
    sc.convert_to_ttl(scttl, limit=args.limit, with_nonsense=False)


def list_unksense(args):
    header("List unknown sensekeys in Semcor")
    ttl = SemcorXML(SEMCOR_TTL)
    unk = Counter()
    sids = Counter()
    c = Counter()
    out = TextReport() if not args.out else TextReport(args.out)
    for f in ttl.files[:args.limit] if args.limit else ttl.files:
        doc = TaggedDoc.from_json_file(ttl.files.abspath(f))
        for s in doc:
            for concept in s.concepts:
                try:
                    sid = SynsetID.from_string(concept.tag)
                    sids.count((sid, concept.clemma))
                    c.count("Known instances")
                except:
                    sid = None
                    unk.count((concept.tag, concept.clemma))
                    c.count("Unknown instances")
    out.header("Known concepts")
    out.writeline("\t".join(("synsetID", "lemma", "count")))
    for k, v in sids.sorted_by_count():
        sid, lemma = k
        out.writeline("\t".join((str(sid), lemma, str(v))))
    out.header("Unknown concepts")
    out.writeline("\t".join(("sensekey", "lemma", "count")))
    for k, v in unk.sorted_by_count():
        sk, lemma = k
        out.writeline("\t".join((sk, lemma, str(v))))
    out.header("Total")
    out.writeline("Known: {}".format(len(sids)))
    out.writeline("Unknown: {}".format(len(unk)))
    c.summarise(out)


def config_logging(args):
    ''' Override root logger's level '''
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------

def main():
    '''Main entry of pysemcor
    '''

    # It's easier to create a user-friendly console application by using argparse
    # See reference at the top of this script
    parser = argparse.ArgumentParser(description="pySemcor toolkit", add_help=False)
    parser.set_defaults(func=None)

    # Optional argument(s)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    tasks = parser.add_subparsers(help="Task to be done")

    fix_task = tasks.add_parser('fix', parents=[parser], help='Fix 3rada dataset')
    fix_task.set_defaults(func=fix)

    json_task = tasks.add_parser('json', parents=[parser], help='Convert XML to JSON')
    json_task.set_defaults(func=to_json)

    ttl_task = tasks.add_parser('ttl', parents=[parser], help='Convert fixed 3rada dataset to TTL')
    ttl_task.add_argument('-n', '--limit', type=int, help='Only parse top K files', default=None)
    ttl_task.set_defaults(func=to_ttl)

    list_unksense_task = tasks.add_parser('unk', parents=[parser], help='List unknown senses')
    list_unksense_task.add_argument('-n', '--limit', type=int, help='Only parse top K files', default=None)
    list_unksense_task.add_argument('-o', '--out', help='Output file', default=None)
    list_unksense_task.set_defaults(func=list_unksense)

    # Main script
    args = parser.parse_args()
    config_logging(args)
    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()
    pass


if __name__ == "__main__":
    main()
