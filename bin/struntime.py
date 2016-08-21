# Data structure stuff for Subterra
from stexcept import *

# A single subroutine
class Subroutine:
	def __init__(self, id, inner, type):
		self.id = id
		self.inner = inner
		self.type = type

	def getStack(self, old):
		if self.type == '{': return old
		if self.type == '[': return Stack(old)
		if self.type == '(': return Stack()
		raise STSyntaxError(self.type)

# A subroutine imported from a .stpy file (used purely for type differentiation)
class PySubroutine(Subroutine): pass

# Subterra stack implementation
# Doesn't accept None, implicitly converts to int
# Use push instead of append, and pushall instead of extend
class Stack(list):
	push = lambda _, i: _.append(int(i)) if i is not None else None
	pushall = lambda _, l: [_.push(i) for i in l]

# Get the id of the next subroutine in the token list
def consumeSubroutine(tokens, data, anonid=-9):
	o = next(tokens)

	if o.isdigit():
		if int(o) in data: return data[int(o)]
		raise STReferenceError(int(o))
	else:
		if o not in '{[(': raise STSyntaxError(o)
		return Subroutine(anonid, next(tokens), o)
