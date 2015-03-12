#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Semcor Toolkit for Python

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
import sys
import argparse
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

multi_semcor_aligned = ["br-a01", "br-a11", "br-a12", "br-a13", "br-a14", "br-b13", "br-b20", "br-c01", "br-c02", "br-c04", "br-d01", "br-d02", "br-d03", "br-e01", "br-e04", "br-e23", "br-e24", "br-e27", "br-e28", "br-e29", "br-e30", "br-f03", "br-f10", "br-f14", "br-f15", "br-f16", "br-f19", "br-f22", "br-f23", "br-f24", "br-f25", "br-f43", "br-g11", "br-g12", "br-g14", "br-g15", "br-g16", "br-g17", "br-g18", "br-g21", "br-g22", "br-g23", "br-g39", "br-g43", "br-h01", "br-h13", "br-h14", "br-h16", "br-h17", "br-h18", "br-h21", "br-j01", "br-j03", "br-j04", "br-j05", "br-j10", "br-j17", "br-j22", "br-j23", "br-j29", "br-j30", "br-j31", "br-j33", "br-j34", "br-j35", "br-j37", "br-j38", "br-j41", "br-j42", "br-j52", "br-j53", "br-j55", "br-j57", "br-j58", "br-j60", "br-k01", "br-k02", "br-k03", "br-k05", "br-k08", "br-k10", "br-k11", "br-k13", "br-k15", "br-k18", "br-k19", "br-k21", "br-k22", "br-k24", "br-k26", "br-k29", "br-l08", "br-l10", "br-l11", "br-l12", "br-l14", "br-l16", "br-l18", "br-m01", "br-m02", "br-n05", "br-n09", "br-n12", "br-n15", "br-n17", "br-n20", "br-p01", "br-p07", "br-p09", "br-p10", "br-p12", "br-p24", "br-r04", "br-r06", "br-r07", "br-r08"]

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

def gen_text(only_multi_semcor=False):
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
				if only_multi_semcor:
					all_files = [ x for x in all_files if os.path.splitext(os.path.basename(x))[0] in multi_semcor_aligned ]
				print("Processing %s file(s) ..." % len(all_files))
				for file_name in all_files:
					convert_file(file_name, semcor_txt, semcor_raw, semcor_tag)

def sk_to_ss():
	"""Update sensekey in tag file to synsetID (offset-pos)"""
	all_sk = set()
	print("Reading tag file ...")
	with open(SEMCOR_TAG, 'r') as semcor_tag:
		lines = [ x.split() for x in semcor_tag.readlines() ]
	for line in lines:
		sk = line[3]
		scloc = sk.find(';')
		if scloc > -1:
			sk = sk[:scloc] # only consider the first sensekey
		all_sk.add(sk)
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

def multi_semcor():
	gen_text(True)
	sk_to_ss()

def main():
	parser = argparse.ArgumentParser(description="Semcor Python Toolkit")
	parser.add_argument('action', choices=['fix', 'gen', 'ms', 'msall', 'ss', 'all'], help='''Task to perform 
	(fix: Fix Semcor XML data | 
	gen: Generate Semcor text | 
	ms: generate Multi-Semcor data | 
	msall: Fix Semcor XML data and then generate Multi-Semcor profile  | 
	ss: Convert sensekey in tag file into synsetID |
	all: all of the above
	''')
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-v", "--verbose", action="store_true")
	group.add_argument("-q", "--quiet", action="store_true")

	if len(sys.argv) == 1:
		# User didn't pass any value in, show help
		parser.print_help()
	else:
		args = parser.parse_args()
		task_maps = { 
			'fix' : (fix_data,),
			'ss'  : (sk_to_ss,),
			'gen' : (gen_text,),
			'ms'  : (multi_semcor,),
			'msall'  : (fix_data, multi_semcor,),
			'all' : (fix_data, gen_text, sk_to_ss)
		}
		for task in task_maps[args.action]:
			task()
	pass

if __name__ == "__main__":
	main()
	print("All done!")
