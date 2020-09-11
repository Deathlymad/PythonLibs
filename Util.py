import re


def is_valid_regex(regexString):
	is_valid = None
	try:
		re.compile('[')
		is_valid = True
	except re.error:
		is_valid = False
	return is_valid