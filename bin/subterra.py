# Subterra Interpreter v1.3
import os, sys, random
from stparser import tokenGenerator
from stexcept import *
from stimport import *
from struntime import *

# Execute a subroutine
def execute(sub, depth=0, stack=None, data=None, impid=-1):
	# Initialize default parameters
	if stack is None: stack = Stack()
	if data is None: data = {sub.id:sub,"imports":{}}

	# Helper functions
	out = lambda o: print(o,end='')
	strin = lambda i: [stack.pushall([ord(c) for c in i[::-1]]),stack.push(len(i))]
	exct = lambda r: execute(r, depth+1, r.getStack(stack), data.copy(), impid)
	ret = lambda: None if sub.type == '{' or not stack else stack.pop()

	try:
		# Run subroutines imported from .stpy files
		if isinstance(sub, PySubroutine):
			stack.push(sub.inner(stack, data))
			return ret()

		# Main parsing loop
		tokens,last,ifsuccess = tokenGenerator(sub.inner),'',False
		for token in tokens:
			if last != '?': ifsuccess = False

			# Numbers/Math
			if token.isdigit(): stack.push(token)
			if token == '+': stack.push(stack.pop(-2)+stack.pop())
			if token == '-': stack.push(stack.pop(-2)-stack.pop())
			if token == '*': stack.push(stack.pop(-2)*stack.pop())
			if token == '/': stack.push(stack.pop(-2)//stack.pop())
			if token == '%': stack.push(stack.pop(-2)%stack.pop())
			if token == 'r': stack.push(random.randrange(stack.pop()))

			# Stack operations
			if token == '$': stack.pop()
			if token == '&': stack.push(stack[-1])
			if token == 'b': stack.insert(0, stack.pop())
			if token == 't': stack.push(stack.pop(0))
			if token == '@': stack.reverse()
			if token == 's': stack.push(len(stack))
			if token == 'e': stack.clear()

			# IO and strings
			if token == 'p': out(stack.pop())
			if token == 'c': out(chr(stack.pop()))
			if token == 'i': strin(input())
			if token in '"\'': strin(next(tokens))
			if token == '\\': stack.push(ord(next(tokens)))

			# Conditionals, comparison and loops
			if token == '=': stack.push(stack.pop(-2) == stack.pop())
			if token == '!': stack.push(stack.pop(-2) != stack.pop())
			if token == '<': stack.push(stack.pop(-2) < stack.pop())
			if token == '>': stack.push(stack.pop(-2) > stack.pop())
			if token == '?':
				r = consumeSubroutine(tokens, data, -2)

				ifsuccess = stack.pop()
				if ifsuccess:
					stack.push(exct(r))
			if token == ':':
				if last != '?': raise STSyntaxError(token)
				r = consumeSubroutine(tokens, data, -3)

				if not ifsuccess:
					stack.push(exct(r))
			if token == 'w':
				c = consumeSubroutine(tokens, data, -4)
				r = consumeSubroutine(tokens, data, -5)

				while True:
					stack.push(exct(c))
					if not stack.pop(): break
					stack.push(exct(r))

			# Import system
			if token == 'm':
				imp = doImport(depth, stack, data)
				if imp is not None: execute(imp[1], depth+1, data=data['imports'][imp[0]], impid=imp[0])
			if token == '.':
				s,i = stack.pop(),stack.pop()
				if i not in data['imports']: raise STImportRefError(i)
				if s not in data['imports'][i]: raise STReferenceError('%s:%s'%(i,s))
				imp = data['imports'][i]

				execute(imp[s], depth+1, imp[s].getStack(stack), imp.copy(), i)

			# Subroutines
			if token in '{[(':
				i = stack.pop()
				data[i] = Subroutine(i, next(tokens), token)
			if token == '#':
				i = stack.pop()
				if i not in data: raise STReferenceError(i)
				exct(data[i])

			last = token
		return ret()
	except tuple(exceptionMap) as e:
		handleException(e, sub, depth, token, impid)

# Main entry point
if __name__ == '__main__':
	try:
		if len(sys.argv) < 2: raise STCommandLineError('Expected path, got none')

		# Setting up working directories, getting main file, etc.
		with open(sys.argv[1]) as f:
			prog = stringFromFile(file=f)
			if not prog: exit()

			setStdLibLoc(os.path.dirname(sys.argv[0])+'/../lib/')
			os.chdir(os.path.dirname(os.path.realpath(f.name)))

		# Execute main file
		execute(Subroutine(-1, prog, '('))

		# If '-p' is added to command line arguments, pause at the end of execution
		if len(sys.argv) > 2:
			if sys.argv[2] != '-p': raise STCommandLineError('Expected -p, got '+sys.argv[2])
			input('\n\nPress ENTER to continue...')
	except KeyboardInterrupt:
		exit()
	except STException as e:
		e.printStackTrace()
