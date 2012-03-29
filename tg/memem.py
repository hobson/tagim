#!/usr/bin/python
# searches through a directory tree to try to find text written by you about you (journals)
# in the future it may organize notes and journal entries (text files) into a picture of your life (life line, memoir, knowledge base about you)
# import tidbits of knowledge that you might want to know include:
#   where you were (fine grained hourly detail would be nice)
#   who your spouse or date was
#   who you talked to or met
#   what you were doing or saw
#   anything interesting you said
#   anything interesting people close to you said
#   anything interesting anyone said
#   facts that a novelist would care and write about: what clothes you were wearing, what was in your pockets, what was in your purse or backpack, what was on your mind, any unusual wound or scar (emotional or otherwise) and how it came about, the lies you told, the people you helped, the people you hurt, the things you gave, the things you wished for, your dreams, your accomplishments, scolding or praise from your parents, inventions, ideas, philosophical development, religious involvement/development, scientific/cultural contribution

import os, fnmatch, re



if pats.match():
return True
def relocate(regex, root=os.curdir):
	"""
	Locate all files matching supplied filename regular expression in and below
	supplied directory path or filename or full path name.
	Returns an iterator (this is a generator function)
	Usage: iter=relocate(regex, base_path=current_directory)
	TODO:
	1. allow regex to be a list of regexes that match [full_path_name, path_name, file_name]
	2. allow regex to be a dict, or list of tuples, indicating which part of full path should be matched
	"""
	r = re.compile(regex)
	for path, dirs, files in os.walk(os.path.abspath(root)):
		for fpn in files:
			if r.match(fpn):
				yield os.path.join(path, filename)

def locate(pattern, root=os.curdir):
	'''Locate all files matching supplied filename pattern in and below
	supplied root directory.'''
	for path, dirs, files in os.walk(os.path.abspath(root)):
		for filename in fnmatch.filter(files, pattern):
			yield os.path.join(path, filename)


for xml in relocate(r'^$'):

