r"""TotalGood module: natural language processing, artifical intelligence, and web applications.

This module exports all functions from tg.utils.

Additional utilities can be found in the submodules:
	ai_ngrams
	basic_arguments
	compose_email
	csv2model
	fdacsvprocessing
	finance
	herding_metric
	mail
	nlp
	recipeprocessing
	regex_patterns
	stockquote
	tagim
	utils

TODO:
	Built-in doctests
"""

from tg.utils import *

#import sys
#_names = sys.builtin_module_names

# __all__ = ["ai_ngrams",
#            "basic_arguments",
#            "compose_email",
#            "csv2model",
#            "fdacsvprocessing",
#            "finance",
#            "herding_metric",
#            "mail",
#            "nlp",
#            "prepro",
#            "recipeprocessing",
#            "regex_patterns",
#            "stockquote",
#            "tagim",]

def _get_exports_list(module):
    try:
        return list(module.__all__)
    except AttributeError:
        return [n for n in dir(module) if n[0] != '_']

#sys.modules['tg.utils'] = tg.utils
from tg.utils import * #(curdir, pardir, sep, pathsep, defpath, extsep, altsep, devnull)

#del _names

