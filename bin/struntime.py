# Runtime helper functions for Subterra
import re
from stexcept import *

# Hacky init function to gather a local reference to the execute function and avoid circular imports -_-
def initRuntime(execfunc):
	global execute
	execute = execfunc

# Subroutine registry, as well as wrapper for subroutine-related methods
class Subroutines(dict):
	# Registers a new Subroutine instance to this registry, and returns it
	def createSubroutine(self, id, rt, op, impid=-1, allowinv=False):
		if not allowinv and id < 0: raise STInvalidSubrtIdError()
		return self.Subroutine(self, id, rt, op, impid)

	# Consumes the next subroutine reference or definition and returns the correct Subroutine instance, or throws a syntax error if it can't
	def consumeSubroutine(self, tokens, imports, anonid=-9, forceImported=False):
		o = next(tokens)

		if forceImported or o == '.':
			i,s = o if forceImported else next(tokens),next(tokens)

			if not i.isdigit(): raise STSyntaxError(i)
			if not s.isdigit(): raise STSyntaxError(s)

			if len(imports) <= int(i): raise STImportRefError(i)
			if int(s) not in imports[int(i)].subrt: raise STReferenceError(s)

			r = imports[int(i)].subrt[int(s)]
			r.impid = int(i)
			return r
		elif o.isdigit():
			if int(o) not in self: raise STReferenceError(int(o))
			return self[int(o)]
		else:
			if o not in '{[(': raise STSyntaxError(o)
			return self.createSubroutine(anonid, next(tokens), o, allowinv=True)

	def copy(self):
		new = Subroutines()

		for key in self:
			new[key] = self[key]

		return new

	class Subroutine(object):
		def __init__(self, reg, id, rt, op, impid=-1):
			self.id = id
			self.rt = rt
			self.op = op
			self.impid = impid
			reg[id] = self

# Import list, as well as wrapper for import-related methods
class Imports(list):
	# Creates a new Import instance for the given file or path and imports it (unless noImport is set to True)
	@staticmethod
	def createImport(file=None, path=None, noImport=False):
		if file is None: file = Imports.fileToString(path+'.sbtr')

		return Imports.Import(file)

	# Reads the file at a given path into a string, as well as stripping it of comments
	@staticmethod
	def fileToString(path):
		try:
			with open(path) as f:
				return re.sub('~.*\n', '\n', f.read())
		except FileNotFoundError:
			raise STFileNotFoundError(path)

	def copy(self):
		new = Imports()

		for key in self:
			new[key] = self[key]

		return new

	# Container class for a single imported file
	class Import(object):
		def __init__(self, file):
			self.file = file
			self.isImported = False

		def doImport(self, depth, imports):
			if self.isImported: return

			self.subrt,self.imports = Subroutines(),Imports()
			execute(-6, depth+1, self.file, subrt=self.subrt, imports=self.imports, impid=len(imports))
			imports.append(self)

			self.isImported = True

# Return the appropriate stack based on the subroutine's opening character
def getNewStack(old, subo):
	if subo == '{': return old
	if subo == '[': return old.copy()
	if subo == '(': return []

# Clean all None from the stack
def cleanStack(stack):
	while None in stack: stack.remove(None)
