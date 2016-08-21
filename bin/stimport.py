# Import utilities for Subterra
import os, re, imp
from struntime import Subroutine, PySubroutine
from stexcept import *

# Set the location of the standard library folder
def setStdLibLoc(path):
	global stdlibloc
	stdlibloc = path

# Convert a file to a string
def stringFromFile(path):
	try:
		with open(path) as f:
			return re.sub('~.*\n', '\n', f.read())
	except FileNotFoundError:
		raise STFileNotFoundError(path)

# Import a .sbtr/.stpy file into the given namespace
def doImport(depth, stack, data):
	i,path = stack.pop(),''.join([chr(stack.pop()) for i in range(stack.pop())]).replace('.','/')

	if os.path.exists(path+'.stpy'):
		doSTPYImport(i,path+'.stpy',depth,data)
	elif os.path.exists(path+'.sbtr'):
		return doSBTRImport(i,path+'.sbtr',depth,data)
	elif os.path.exists(stdlibloc+path+'.stpy'):
		doSTPYImport(i,stdlibloc+path+'.stpy',depth,data)
	elif os.path.exists(stdlibloc+path+'.sbtr'):
		return doSBTRImport(i,stdlibloc+path+'.sbtr',depth,data)
	else: raise STFileNotFoundError(path)

# Import a .stpy file
# Used for libraries only, not main program execution!
def doSTPYImport(i, path, depth, data):
	imported = imp.load_source(os.path.splitext(os.path.basename(path))[0], path)
	data['imports'][i] = {}

	for key in imported.data:
		data['imports'][i][key] = PySubroutine(key, imported.data[key]['oncall'], imported.data[key]['type'])

# Import a .stbr file
def doSBTRImport(i, path, depth, data):
	try:
		prog = stringFromFile(path)
	except STFileNotFoundError:
		prog = stringFromFile(stdlibloc+path)

	impr = Subroutine(-1, prog, '(')
	data['imports'][i] = {-1:impr,'imports':{}}

	return i, impr
