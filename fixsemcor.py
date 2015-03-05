#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Fix 3rada's version
@author: Le Tuan Anh
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2015, pySemCor"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
import lxml
from lxml import etree
import xml.etree.ElementTree as ET
from chirptext.leutile import *
from collections import namedtuple
from bs4 import BeautifulSoup
import nltk

TokenInfo = namedtuple("TokenInfo", ['text', 'sk'])

SEMCOR_ROOT=os.path.expanduser('./data/3rada')
DATA_DIR_1=os.path.join(SEMCOR_ROOT, 'brown1', 'tagfiles')
DATA_DIR_2=os.path.join(SEMCOR_ROOT, 'brown2', 'tagfiles')
DATA_DIR_V=os.path.join(SEMCOR_ROOT, 'brownv', 'tagfiles')
DATA_DIRS = [ DATA_DIR_1, DATA_DIR_2, DATA_DIR_V ]

SEMCOR_FIXED_ROOT = os.path.expanduser('./data/3rada_fixed')
DATA_DIR_1_FIXED =os.path.join(SEMCOR_FIXED_ROOT, 'brown1')
DATA_DIR_2_FIXED =os.path.join(SEMCOR_FIXED_ROOT, 'brown2')
DATA_DIR_V_FIXED =os.path.join(SEMCOR_FIXED_ROOT, 'brownv')
OUTPUT_DIRS = {
	#DATA_DIR_1 : DATA_DIR_1_FIXED
	#,DATA_DIR_2 : DATA_DIR_2_FIXED
	#,DATA_DIR_V : DATA_DIR_V_FIXED
	DATA_DIR_1 : SEMCOR_FIXED_ROOT
	,DATA_DIR_2 : SEMCOR_FIXED_ROOT
	,DATA_DIR_V : SEMCOR_FIXED_ROOT
}
# XML_DIR = os.path.expanduser('./data/')
XML_DIR = SEMCOR_FIXED_ROOT
SEMCOR_RAW = os.path.expanduser('./data/semcor_wn30.raw')
SEMCOR_TAG = os.path.expanduser('./data/semcor_wn30.tag')
SS_SK_MAP = os.path.expanduser('./data/sk_map_ss.txt')
SK_NOTFOUND = os.path.expanduser('./data/sk_notfound.txt')
SEMCOR_TXT = os.path.expanduser('./data/semcor_wn30.txt')

def fix_malformed_xml_file(filepathchunks, postfix='.xml'):
	file_name = filepathchunks[1]
	input_file_path = os.path.join(*filepathchunks)
	output_dir = OUTPUT_DIRS[filepathchunks[0]]
	output_file_path = os.path.join(output_dir, file_name + postfix)
	
	print('Fixing the file: %s ==> %s' % (input_file_path ,output_file_path))
	soup = BeautifulSoup(open(input_file_path).read())
	
	# Create output dir if needed
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	
	with open(output_file_path, 'w') as output_file:
		output_file.write(soup.prettify())

def convert_file(file_name, semcor_txt, semcor_raw=None, semcor_tag=None):
	#print('Loading %s' %file_name)

	tree = etree.iterparse(file_name)
	for event, element in tree:
		if event == 'end' and element.tag == 's':
			fcode = os.path.basename(file_name)
			fcode = os.path.basename(fcode)[:-4] if fcode.endswith('.xml') else fcode
			scode = fcode + '-' + str(element.get('snum'))
			#print("Found a sentence (length = %s) - sid = %s" % (len(element), scode,) )
			
			# Generate TAB file with tags
			tokens = []
			for token in element:
				if token.tag == 'wf':
					lemma = StringTool.strip(token.get('lemma'))
					lexsn = StringTool.strip(token.get('lexsn'))
					sk = lemma + '%' + lexsn if lemma and lexsn else ''
					sk = StringTool.strip(sk.replace('\t', ' ').replace('|', ' '))
					text = StringTool.strip(token.text.replace('\t', ' ').replace('|', ' '))
					tokens.append(TokenInfo(text, sk))
				elif token.tag == 'punc':
					tokens.append(TokenInfo(token.text.strip(), ''))
			element.clear()
			
			tokens_text = '\t'.join([ x.text + '|' + x.sk for x in tokens])
			semcor_txt.write(tokens_text + '\n')
			
			# Generate raw file
			if semcor_raw:
				sentence_text = ' '.join([ x.text for x in tokens ])
				sentence_text = sentence_text.replace(" , , ", ", ")
				sentence_text = sentence_text.replace(' , ', ', ').replace('`` ', ' “').replace(" ''", '”')
				sentence_text = sentence_text.replace(' ! ', '! ').replace(" 'll ", "'ll ").replace(" 've ", "'ve ")			
				sentence_text = sentence_text.replace(" 's ", "'s ")			
				sentence_text = sentence_text.replace(" 'm ", "'m ")			
				sentence_text = sentence_text.replace(" ' ", "' ")			
				sentence_text = sentence_text.replace(" ; ", "; ")			
				sentence_text = sentence_text.replace("( ", "(")			
				sentence_text = sentence_text.replace(" )", ")")			
				sentence_text = sentence_text.replace(" n't ", "n't ")			
				sentence_text = sentence_text.replace("Never_mind_''", "Never_mind_”")			
				sentence_text = sentence_text.replace("327_U._S._114_''", "327_U._S._114_”")			
				sentence_text = sentence_text.replace("``", "“")			
				sentence_text = sentence_text.replace("''", "”")			
				if sentence_text[-2:] in (' .', ' :', ' ?', ' !'):
					sentence_text = sentence_text[:-2] + sentence_text[-1]
				sentence_text = sentence_text.strip()
				
				# Generate mapping file
				if semcor_tag:
					cfrom = 0
					cto = len(sentence_text)
					stags = []
					strace = []
					previous_token = ''
					for token in tokens:
						tokentext = token.text.replace('``', '“').replace("''", '”')
						if ',' == tokentext and ',' == previous_token:
							print("WARNING: Duplicate punc (,) at %s" % ("('%s', %d)" % (scode, cfrom),))
							continue
						strace.append("looking for '%s' from '%s' - %s" % (tokentext, cfrom, "('%s', %d)" % (scode, cfrom)))
						tokenfrom = sentence_text.find(tokentext, cfrom)
						if cfrom == 0 and tokenfrom != 0:
							print("WARNING: Sentence starts at %s instead of 0 - sid = %s [sent[0] is |%s|]" % (tokenfrom, scode, sentence_text[0]))
						if tokenfrom == -1:
							print("WARNING: Token not found (%s) in %s from %s |%s|" % (tokentext, scode, cfrom, sentence_text))
							for msg in strace[-4:]:
								print(msg)
							return
						else:
							cfrom = tokenfrom + len(tokentext)
							if token.sk:
								stags.append((scode, tokenfrom, cfrom,token.sk,tokentext,))
						# Finished processing this token
						previous_token = tokentext
					if cfrom != cto:
						print("WARNING: Sentence length is expected to be %s but found %s lasttoken=|%s| (sid = %s)" % (cto, cfrom, tokentext, scode))
						print("Debug info: %s" % (stags,))
					for tag in stags:
						semcor_tag.write('\t'.join([ str(x) for x in tag]) + '\n')
				# Done!
				semcor_raw.write(scode + '\t')
				semcor_raw.write(sentence_text + '\n')
	
def fix_data():
	t = Timer()
	c = Counter()
	for data_dir in DATA_DIRS:
		all_files = [ (data_dir, x) for x in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, x)) ]
		for a_file in all_files:
			fix_malformed_xml_file(a_file)
			c.count('file')

def gen_text():
	with open(SEMCOR_TAG, 'w') as semcor_tag:
		with open(SEMCOR_RAW, 'w') as semcor_raw:
			with open(SEMCOR_TXT, 'w') as semcor_txt:
				semcor_raw.write('# SemCor-WordNet30 Tab version - Prepared by Le Tuan Anh, <tuananh.ke@gmail.com>\n')
				semcor_raw.write('# Latest version can be downloaded at https://github.com/letuananh/pysemcor\n')
				semcor_raw.write('#\n')
				semcor_txt.write('# SemCor\' raw text - Prepared by Le Tuan Anh, <tuananh.ke@gmail.com>\n')
				semcor_txt.write('# Latest version can be downloaded at https://github.com/letuananh/pysemcor\n')
				semcor_txt.write('#\n')
				all_files = [ os.path.join(XML_DIR, x) for x in os.listdir(XML_DIR) if os.path.isfile(os.path.join(XML_DIR, x)) ]
				for file_name in all_files:
					convert_file(file_name, semcor_txt, semcor_raw, semcor_tag)

def sk_to_ss():
	"""Update sensekey in tag file to synsetID (offset-pos)"""
	all_sk = set()
	print("Reading tag file ...")
	with open(SEMCOR_TAG, 'r') as semcor_tag:
		lines = [ x.split() for x in semcor_tag.readlines() ]
	for line in lines:
		all_sk.add(line[3])
	print(len(all_sk))
	
	print("Loading WordNet ...")
	from nltk.corpus import wordnet as wn
	all_sk_notfound = set()
	with open(SS_SK_MAP, 'w') as mapfile:
		for sk in all_sk:
			try:
				if sk not in all_sk_notfound:
					ss = wn.lemma_from_key(sk).synset()
					sid = '%s-%s' % (ss.offset(), ss.pos())
					mapfile.write('%s\t%s\n' % (sk, sid))
			except nltk.corpus.reader.wordnet.WordNetError:
				all_sk_notfound.add(sk)
			except ValueError:
				print("Invalid sk: %s" % (sk,))
				all_sk_notfound.add('[INVALID]\t' + sk)
	with open(SK_NOTFOUND, 'w') as notfoundfile:
		for sk in all_sk_notfound:
			notfoundfile.write(sk)
			notfoundfile.write('\n')
	print("Map file has been created")	

def main():
	print("Fix SemCor 3rada")
	print('-'*40)
	if len(sys.argv) == 2:
		if sys.argv[1] == 'fixdata':
			fix_data()
		elif sys.argv[1] == 'gentext':
			gen_text()
		elif sys.argv[1] == 'ss':
			sk_to_ss()
		elif sys.argv[1] == 'all':
			fix_data()
			gen_text()
	else:
		print("""Usage:
	python fixsemcor.py [command]
Command list:
	fixdata: Fix 3rada XML malform
	gentext: Generate SemCor TXT files
	ss: Convert sensekey in tag file into synsetID
	all    : All of the above
""")

if __name__ == "__main__":
	main()
	print("All done!")
