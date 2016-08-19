# Exception classes for Subterra
class STException(Exception):
	def __init__(self, type, error, traceback, parenttb=[]):
		self.type = type
		self.error = error
		self.traceback = parenttb

		if traceback is None: self.traceback = None
		elif isinstance(traceback, list): self.traceback.extend(traceback)
		else: self.traceback.append(traceback)

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
