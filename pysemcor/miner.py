# -*- coding: utf-8 -*-

'''
Semcor data miner
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

import logging

from chirptext import header, Counter

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Application logic
# -------------------------------------------------------------------------------

def mine_rdf_values(sc, limit=None):
    ot_values = set()
    rdf_counter = Counter()
    rdf_with_key_counter = Counter()
    for f in sc.files if not limit else sc.files[:limit]:
        for sj in sc.iterparse(f):
            for t in sj['tokens']:
                if 'rdf' in t:
                    l = t['lemma'] if 'lemma' in t else t.text
                    r = t['rdf']
                    sk = t['sk'] if 'sk' in t else ''
                    item = (l, r, sk)
                    rdf_counter.count(item)
                    if sk:
                        rdf_with_key_counter.count(item)
                if 'ot' in t:
                    ot_values.add(t['ot'])
    header("RDF values")
    for k, v in rdf_counter.sorted_by_count():
        print("{}: {}".format(k, v))
    header("RDF values (with valid keys)")
    for k, v in rdf_with_key_counter.sorted_by_count():
        print("{}: {}".format(k, v))
    header("OT values")
    for o in ot_values:
        print(o)
