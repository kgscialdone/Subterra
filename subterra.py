# Subterra Interpreter v1.0
import sys, re

# Syntax definitions
validinst = '+-*/%$&bt@se=!<>?:wpci"\'\\{[(#dm.'
tokensep = ' \n\t|;'

# Exception classes
class STException(Exception):
	def __init__(self, type, error, traceback, parenttb=[]):
		self.type = type
		self.error = error
		self.traceback = parenttb

		if isinstance(traceback, list): self.traceback.extend(traceback)
		else: self.traceback.append(traceback)

class STSyntaxError(STException):
	def __init__(self, error):
		super().__init__('SyntaxError', 'Unexpected token '+str(error), [])

class STInvalidEscSeqError(STException):
	def __init__(self, error):
		super().__init__('InvalidEscSeqError', 'Invalid escape sequence \\'+str(error), [])

class STInvalidSubrtIdError(STException):
	def __init__(self, error):
		super().__init__('InvalidSubrtIdError', 'Subroutine ids must be positive', [])

class STReferenceError(STException):
	def __init__(self, error):
		super().__init__('ReferenceError', 'No subroutine with id '+str(error), [])

class STImportRefError(STException):
	def __init__(self, error):
		super().__init__('ImportRefError', 'No import with id '+str(error), [])

class STEmptyStackError(STException):
	def __init__(self):
		super().__init__('EmptyStackError', 'Attempt to pop from empty stack', [])

class STRecursionDepthError(STException):
	def __init__(self):
		super().__init__('RecursionDepthError', 'Maximum recursion depth exceeded', [])

class STEndOfRoutineError(STException):
	def __init__(self):
		super().__init__('EndOfRoutineError', 'Unexpected EOR', [])

# Get the traceback info for the given data
def getTraceback(id, depth, token, routine, impid=-1):
	origid = id
	if id == -1: id = '(main)'
	if id == -2: id = '(anon ? block)'
	if id == -3: id = '(anon : block)'
	if id == -4: id = '(anon w cond)'
	if id == -5: id = '(anon w block)'
	if id == -6: id = '(import %s)'%impid
	if id == -9: id = '(unknown)'
	if impid != -1 and origid != -6: id = '%s:%s'%(impid,id)

	if origid in [-1,-6]: routine = ''
	elif '\n' in routine: routine = ', routine:\n\t\t'+'\n\t\t'.join(routine.split('\n'))
	else: routine = ', routine: %s'%routine

	return 'at subroutine id %s, depth %s, token %s%s'%(id,depth,token,routine)

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

# Consumes the next subroutine reference or definition, or throws a syntax error if it can't
def consumeSubroutine(tokens, subrt, imports, anonid=-9, forceImported=False):
	o = next(tokens)

	if forceImported or o == '.':
		i,s = o if forceImported else next(tokens),next(tokens)

		if not i.isdigit(): raise STSyntaxError(i)
		if not s.isdigit(): raise STSyntaxError(s)

		if len(imports) <= int(i): raise STImportRefError(i)
		if int(s) not in imports[int(i)][1]: raise STReferenceError(s)

		return tuple(list(imports[int(i)][1][int(s)])+[int(i)])
	elif o.isdigit():
		if int(o) not in subrt: raise STReferenceError(int(o))
		return subrt[int(o)]
	else:
		if o not in '{[(': raise STSyntaxError(o)
		return (anonid, next(tokens), o)

# Get the proper stack given the opening character of the subroutine
getSubrtStack = lambda s,o: s if o == '{' else s.copy() if o == '[' else []

# Get the proper import id for the given subroutine tuple
getImpId = lambda r, i: i if len(r) < 4 else r[3]

# Clear the stack of 'None' objects
def cleanStack(s):
	while None in s: s.remove(None)

# Import and prep a file to be run as Subterra code
def importFile(path):
	with open(path) as f:
		return re.sub('~.*\n', '\n', f.read())
		return ''.join([s for s in re.sub('~.*\n', '\n', f.read()).splitlines(True) if s.strip()])

# Execute a subroutine
def execute(id, depth, routine, stack=[], subrt={}, imports=[], impid=-1, shouldret=True):
	qex = lambda r, ret=None: execute(r[0], depth+1, r[1], getSubrtStack(stack, r[2]), subrt.copy(), imports.copy(), getImpId(r, impid), ret if ret is not None else r[2] != '{')
	# print(routine,'\n---------------------------------------')

	token,last,ifsuccess = '','',False
	try:
		try:
			tokens = tokenGenerator(routine)
			for t in tokens:
				token = t
				if last != '?': ifsuccess = False
				cleanStack(stack)

				# Numbers/Math
				if t.isdigit(): stack += [int(t)]
				if t == '+': stack += [stack.pop(-2)+stack.pop()]
				if t == '-': stack += [stack.pop(-2)-stack.pop()]
				if t == '*': stack += [stack.pop(-2)*stack.pop()]
				if t == '/': stack += [stack.pop(-2)/stack.pop()]
				if t == '%': stack += [stack.pop(-2)%stack.pop()]

				# Stack operations
				if t == '$': stack.pop()
				if t == '&': stack += [stack.pop()]*2
				if t == 'b': stack.insert(0, stack.pop())
				if t == 't': stack += [stack.pop(0)]
				if t == '@': stack = stack[::-1]
				if t == 's': stack += [len(stack)]
				if t == 'e': stack = []

				# IO/String operations
				if t == 'p': print(stack.pop(),end='')
				if t == 'c': print(chr(stack.pop()),end='')
				if t == 'i':
					i = input()
					for c in i[::-1]: stack += [ord(c)]
					stack += [len(i)]
				if t == '"':
					i = next(tokens)
					for c in i[::-1]: stack += [ord(c)]
					stack += [len(i)]
				if t == '\\':
					stack += [ord(next(tokens))]

				# Conditionals/Loops
				if t == '=': stack += [int(stack.pop(-2) == stack.pop())]
				if t == '!': stack += [int(stack.pop(-2) != stack.pop())]
				if t == '<': stack += [int(stack.pop(-2) < stack.pop())]
				if t == '>': stack += [int(stack.pop(-2) > stack.pop())]
				if t == '?':
					r = consumeSubroutine(tokens, subrt, imports, -2)

					if stack.pop():
						stack += [qex(r)]
						ifsuccess = True
					else: ifsuccess = False
				if t == ':':
					if last != '?': raise STSyntaxError(t)
					r = consumeSubroutine(tokens, subrt, imports, -3)

					if not ifsuccess:
						stack += [qex(r)]
				if t == 'w':
					c = consumeSubroutine(tokens, subrt, imports, -4)
					r = consumeSubroutine(tokens, subrt, imports, -5)

					while qex(c, True): stack += [qex(r)]

				# Import system
				if t == 'm':
					path = ''
					for i in range(stack.pop()): path += chr(stack.pop())

					imsub,imim = {},[]
					execute(-6, depth+1, importFile(path+'.sbtr'), [], imsub, imim, len(imports))
					imports.append((imim,imsub))
				if t == '.':
					r = consumeSubroutine(tokens, subrt, imports, forceImported=True)

					stack += [execute(r[0], depth+1, r[1], getSubrtStack(stack, r[2]), imports[r[3]][1], imports[r[3]][0], r[3])]

				# Subroutines
				if t in '{[(':
					id_ = stack.pop();
					if id_ < 0: raise STInvalidSubrtIdError()
					subrt[id_] = (id_, next(tokens), t)
				if t == '#':
					id_ = stack.pop()
					if id_ not in subrt: raise STReferenceError(id_)

					stack += [qex(subrt[id_])]
				if t == 'd': stack += [depth]

				last = t
			if shouldret and stack: return stack.pop()
		except IndexError as e:
			raise STEmptyStackError()
		except RuntimeError as e:
			if 'maximum recursion depth exceeded' in str(e): raise STRecursionDepthError()
			raise
		except StopIteration:
			raise STEndOfRoutineError()
	except STException as e:
		raise STException(e.type, e.error, getTraceback(id,depth,token,routine,impid), e.traceback)

if __name__ == '__main__':
	prog = importFile(sys.argv[1])
	if not prog: exit()

	try:
		execute(-1, 0, prog, subrt={-1:(prog,True)})
	except KeyboardInterrupt:
		exit()
	except STException as e:
		print('\n'+e.type+': '+e.error)
		print('Traceback (most recent last):')
		for line in e.traceback[::-1]:
			print('\t'+line)
		print(e.type+': '+e.error+' (==END==)')
		# raise #NOTE: for debugging, should be commented/removed
