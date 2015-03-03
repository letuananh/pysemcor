#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
pySemCor: Python library for processing SemCor
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

class SemCor:
	pass

class SemCorTXT:
	def __init__(self, data_path='./data/3rada/'):
		"""Create an instance of SemCorTXT
		
		data_path -- a path to data folder (by default is './data/3rada/')
		Inside that folder we should find 3 folders brown1, brown2 & brownv.
		"""
		self.data_path = data_path

class SemCorSQLite:
	def __init__(self, db_path='./data/semcor.db'):
		"""Create an instance of SemCorSQLite.
		
		Arguments:
		db_path -- should point to a SQLite DB file (default to './data/semcor.db')
		"""
		self.db_path = db_path


def main():
	print("Semcor-models is a library, not an application.")
	pass

if __name__ == "__main__":
	main()
