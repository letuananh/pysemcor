#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for semcor
Latest version can be found at https://github.com/letuananh/pysemcor

References:
    Python unittest documentation:
        https://docs.python.org/3/library/unittest.html
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 0257 - Python Docstring Conventions:
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
import unittest

from chirptext import header
from pysemcor.semcorxml import FileSet, SemcorXML
from pysemcor.semcorxml import fix_3rada, fix_token_text, xml2json
from pysemcor.miner import mine_rdf_values


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')
SEMCOR_ORIG = os.path.abspath('./data/3rada')
SEMCOR_FIXED = os.path.abspath('./data/3rada_fixed')
SEMCOR_JSON = os.path.abspath('./data/3rada_json')
SEMCOR_TTL = os.path.abspath('./data/3rada_ttl')


# -------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------

class TestMain(unittest.TestCase):

    def test_fileset(self):
        files = FileSet(SEMCOR_ORIG)
        files.add_all('brown1/tagfiles')
        self.assertEqual(len(files), 103)  # brown1
        files.add_all('brown2/tagfiles')
        self.assertEqual(len(files), 186)  # brown1 + brown2
        files.add_all('brownv/tagfiles')
        self.assertEqual(len(files), 352)  # brown1 + brown2 + brownv

    def test_3rada(self):
        sc = SemcorXML(SEMCOR_ORIG)
        self.assertEqual(len(sc.files), 352)

    def test_fix_token(self):
        self.assertEqual(fix_token_text("Y ' all"), "Y'all")

    def test_rdf(self):
        sc = SemcorXML(SEMCOR_FIXED)
        mine_rdf_values(sc, limit=1)

    def test_fix_3rada(self):
        header("Test fix original 3rada dataset")
        fix_3rada(SEMCOR_ORIG, SEMCOR_FIXED)

    def test_xml2json(self):
        header("Test fixed 3rada to JSON")
        sc = SemcorXML(SEMCOR_FIXED)
        sc_json = FileSet(SEMCOR_JSON)
        for f in sc.files:
            xml2json(f, sc, sc_json)

    def test_parse_xml(self):
        sc = SemcorXML(SEMCOR_FIXED)
        for s in sc.iter_ttl(limit=1, with_nonsense=False):
            jttl = s.to_json()
            self.assertTrue(s.text)
            self.assertTrue(s.tokens)
            self.assertIsNotNone(s.concepts)
            if not s.concepts:
                logger.warning("Nonsense sentence: {}".format(jttl))

    def test_xml_to_ttl(self):
        header("Test fixed 3rada to TTL format")
        sc = SemcorXML(SEMCOR_FIXED)
        scttl = FileSet(SEMCOR_TTL)
        sc.convert_to_ttl(scttl, limit=1, with_nonsense=False)


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
