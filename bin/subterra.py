# Subterra Interpreter v1.0
import os, sys, random
from stexcept import *
from stparser import tokenGenerator
from struntime import *

# Execute a subroutine
def execute(id, depth, routine, stack=None, subrt=None, imports=None, impid=-1, shouldret=True):
	qex = lambda r, ret=None: execute(r.id, depth+1, r.rt, getNewStack(stack, r.op), subrt.copy(), imports.copy(), r.impid, ret if ret is not None else r.op != '{')
	if stack is None: stack = []
	if subrt is None: subrt = Subroutines()
	if imports is None: imports = Imports()

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
				if t == '/': stack += [stack.pop(-2)//stack.pop()]
				if t == '%': stack += [stack.pop(-2)%stack.pop()]
				if t == 'r': stack += [random.randrange(stack.pop())]

				# Stack operations
				if t == '$': stack.pop()
				if t == '&': stack += [stack.pop()]*2
				if t == 'b': stack.insert(0, stack.pop())
				if t == 't': stack += [stack.pop(0)]
				if t == '@': stack.reverse()
				if t == 's': stack += [len(stack)]
				if t == 'e': stack.clear()

				# IO/String operations
				if t == 'p': print(stack.pop(),end='')
				if t == 'c': print(chr(stack.pop()),end='')
				if t == 'i':
					i = input()
					stack += [ord(c) for c in i[::-1]]+[len(i)]
				if t == '"':
					i = next(tokens)
					stack += [ord(c) for c in i[::-1]]+[len(i)]
				if t == '\\':
					stack += [ord(next(tokens))]

				# Conditionals/Loops
				if t == '=': stack += [int(stack.pop(-2) == stack.pop())]
				if t == '!': stack += [int(stack.pop(-2) != stack.pop())]
				if t == '<': stack += [int(stack.pop(-2) < stack.pop())]
				if t == '>': stack += [int(stack.pop(-2) > stack.pop())]
				if t == '?':
					r = subrt.consumeSubroutine(tokens, imports, -2)

					if stack.pop():
						stack += [qex(r)]
						ifsuccess = True
					else: ifsuccess = False
				if t == ':':
					if last != '?': raise STSyntaxError(t)
					r = subrt.consumeSubroutine(tokens, imports, -3)

					if not ifsuccess:
						stack += [qex(r)]
				if t == 'w':
					c = subrt.consumeSubroutine(tokens, imports, -4)
					r = subrt.consumeSubroutine(tokens, imports, -5)

					while qex(c, True): stack += [qex(r)]

				# Import system
				if t == 'm':
					path = ''
					for i in range(stack.pop()): path += chr(stack.pop())

					Imports.createImport(path=path).doImport(depth+1, imports)
				if t == '.':
					r = subrt.consumeSubroutine(tokens, imports, forceImported=True)

					stack += [execute(r.id, depth+1, r.rt, getNewStack(stack, r.op), imports[r.impid].subrt, imports[r.impid].imports, r.impid)]

				# Subroutines
				if t in '{[(':
					subrt.createSubroutine(stack.pop(), next(tokens), t, impid)
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
	try:
		if len(sys.argv) < 2: raise STCommandLineError('Expected path, got none')

		os.chdir(os.path.dirname(sys.argv[1]))
		prog = Imports.fileToString(sys.argv[1])
		if not prog: exit()

		initRuntime(execute)
		execute(-1, 0, prog)

		shouldPause = True
		if len(sys.argv) > 2:
			if sys.argv[2] != '-np': raise STCommandLineError('Expected -np, got '+sys.argv[2])
			shouldPause = False
		if shouldPause: input('\n\nPress ENTER to continue...')
	except KeyboardInterrupt:
		exit()
	except STException as e:
		e.printStackTrace()
