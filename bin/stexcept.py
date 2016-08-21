# Exception classes for Subterra
class STException(Exception):
	def __init__(self, type, error, traceback, parenttb=[]):
		self.type = type
		self.error = error
		self.traceback = parenttb

		if traceback is None: self.traceback = None
		elif isinstance(traceback, list): self.traceback.extend(traceback)
		else: self.traceback.append(traceback)

	@staticmethod
	def fromExisting(old, type=None, error=None, traceback=None):
		new = STException(
			type if type is not None else old.type,
			error if error is not None else old.error,
			traceback if traceback is not None else old.traceback)
		return new

	def printStackTrace(self):
		print('\n'+self.type+': '+self.error)

		if self.traceback is not None:
			print('Traceback (most recent last):')
			for line in self.traceback[::-1]:
				print('\t'+line)
			print(self.type+': '+self.error+' (==END==)')

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

class STCommandLineError(STException):
	def __init__(self, error):
		super().__init__('CommandLineError', error, None)

class STFileNotFoundError(STException):
	def __init__(self, error):
		super().__init__('FileNotFoundError', 'File does not exist: \'%s\''%error, [])

# Get the traceback info for the given data
def getTraceback(sub, depth, token, impid=-1):
	id,rt = idMap.get(sub.id,sub.id),sub.inner
	if impid != -1:
		if sub.id != -6: id = '%s:%s'%(impid,id)
		else: id = id%impid

	if sub.id in [-1,-6] or impid != -1: rt = ''
	elif '\n' in rt: rt = ', routine:\n\t\t'+'\n\t\t'.join(rt.split('\n'))
	else: rt = ', routine: %s'%rt

	return 'at %s, depth %s, token %s%s'%(id,depth,token,rt)

# Exception handler for STException/anything in exceptionMap
# *tbargs is the argument list for getTraceback
def handleException(e, *tbargs):
	if isinstance(e, STException):
		raise STException(e.type, e.error, getTraceback(*tbargs), e.traceback)
	else:
		if not isinstance(e, RuntimeError) or 'maximum recursion depth exceeded' in str(e):
			raise STException.fromExisting(exceptionMap[type(e)](), traceback=getTraceback(*tbargs))
		raise

# Map of builtin exception types to their overriden types
# STException is included for easy try...except syntax
exceptionMap = {
	IndexError: STEmptyStackError,
	RuntimeError: STRecursionDepthError,
	StopIteration: STEndOfRoutineError,
	STException: None
}

# Map of subroutine ids to traceback aliases
idMap = {
	-1: '(main)',
	-2: '(anon ? block)',
	-3: '(anon : block)',
	-4: '(anon w cond)',
	-5: '(anon w block)',
	-6: '(import %s)',
	-9: '(unknown)',
}
