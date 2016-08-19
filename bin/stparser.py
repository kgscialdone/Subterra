# Parsing functions for Subterra
from stexcept import *

# Syntax definitions
validinst = '+-*/%r$&bt@se=!<>?:wpci"\'\\{[(#dm.'
tokensep = ' \n\t|;'

# Simple token generator
def tokenGenerator(routine):
	token,routine = '',list(routine)

	while routine:
		c = routine.pop(0)

		if c.isdigit():
			if token and not token.isdigit(): yield token; token = ''
			token += c
		else:
			if c not in validinst+tokensep: raise STSyntaxError(c)
			if token: yield token; token = ''
			if c in tokensep: continue

			yield c
			if c == '\\':
				yield routine.pop(0)
			elif c == '{':
				yield getNested(routine,'{','}')
			elif c == '[':
				yield getNested(routine,'[',']')
			elif c == '(':
				yield getNested(routine,'(',')')
			elif c == '"':
				yield getQuoted(routine, '"')
			elif c == "'":
				yield getQuoted(routine, "'")
	if token: yield token

# Chunk everything between matching brackets together into one token
def getNested(i,op,cl):
	nestlevel,token = 0,''
	while i:
		c = i.pop(0)

		if c == op: nestlevel += 1
		if c == cl:
			nestlevel -= 1
			if nestlevel < 0: break

		token += c
	if nestlevel >= 0: raise STEndOfRoutineError()
	return token

# Chunk everything inside a quoted string into one token
def getQuoted(i,q):
	token,end = '',False
	while i:
		c = i.pop(0)

		if c == '\\':
			lt,e = token,i.pop(0);

			if e in '\\\'"': token += e
			if e == 'a': token += '\a'
			if e == 'b': token += '\b'
			if e == 'f': token += '\f'
			if e == 'n': token += '\n'
			if e == 'r': token += '\r'
			if e == 't': token += '\t'
			if e == 'v': token += '\v'
			if lt == token: raise STInvalidEscSeqError(e)

			continue
		if c == q: end = True; break
		token += c
	if not end: raise STEndOfRoutineError()
	return token
