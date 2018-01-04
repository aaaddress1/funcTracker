'''
	@file:			funcTracker.py
	@author:		aaaddress1@chroot.org
	@repository: 	https://github.com/aaaddress1/funcTracker
'''
from idautils import *
from idaapi import *
from idc import *
import re
MAXDEEPCOUNT = 5
pattCall = re.compile('call[\x20\t]+(.+)')

def guessFuncName(guessAddr, deepCount = 0):
	currGuessNm = ''
	if deepCount > MAXDEEPCOUNT: return currGuessNm # tooooooo deep, stop it!
	
	(startea, endea) = Chunks(guessAddr).next() # function range
	print '%s - %s@%x' % ('\t' * deepCount,GetFunctionName(startea), startea)
	
	for head in Heads(startea, endea):
		opcode = GetDisasm(head)
		matcher = pattCall.match(opcode)
		
		if not matcher:
			continue
			
		funcName = matcher.group(1)
		print '\t' * (deepCount + 1) + 'call ' + funcName
		
		if not 'sub_' in funcName:
			currGuessNm += '|%s\n' % funcName 
			
		else:
			subFuncAddr = LocByName(funcName) # sub function address
			currGuessNm += guessFuncName(subFuncAddr, deepCount + 1)
	
	currGuessNm = re.sub(r"ds:|__imp_", "", currGuessNm)
	return currGuessNm

	
class funcTrackerHandler(idaapi.action_handler_t):	
    def __init__(self):
        idaapi.action_handler_t.__init__(self)

    def activate(self, ctx):
		funcName = GetFunctionName(get_screen_ea())
		funcStrt = LocByName(funcName)
		print 'checking... function %s@%x' % (funcName, funcStrt)
		guessName = guessFuncName(funcStrt)
		set_cmt(funcStrt, guessName, True)
		return 1

    def update(self, ctx):
        return idaapi.AST_ENABLE_FOR_FORM if ctx.form_type == idaapi.BWN_DISASM else idaapi.AST_DISABLE_FOR_FORM


class funcTrackerPlugin(idaapi.plugin_t):
	flags = idaapi.PLUGIN_UNL
	wanted_hotkey = help = comment = ""

	wanted_name = "Function Tracker"
	act_name = "funcTracker:handler"

	def init(self):
		print '''
		  ___                             
		 /                                
		(___       ___  ___               
		|    |   )|   )|                  
		|    |__/ |  / |__                
										  
		  __                              
		 /|                 /             
		( |  ___  ___  ___ (     ___  ___ 
		  | |   )|   )|    |___)|___)|   )
		  | |    |__/||__  | \  |__  |     
		
		v1.0, powered by aaaddress1@chroot.org
		'''
		if idaapi.register_action(idaapi.action_desc_t(
				self.act_name, 					# Name. Acts as an ID. Must be unique.
				"Function Tracker",   			# Label. That's what users see.
				funcTrackerHandler(), 			# Handler. Called when activated, and for updating
				None,	            			# Shortcut (optional)
				"Trace WTF in this function :)",# Tooltip (optional)
				0)):         					# Icon ID (optional)
			print "Action registered. Attaching to menu."

			class Hooks(idaapi.UI_Hooks):
				def finish_populating_tform_popup(self, form, popup):
					if idaapi.get_tform_type(form) == idaapi.BWN_DISASM:
						idaapi.attach_action_to_popup(form, popup, self.act_name, None)

			self.lazyHooks = Hooks()
			self.lazyHooks.act_name = self.act_name
			self.lazyHooks.hook()
	
		return idaapi.PLUGIN_KEEP
		
	def run(self, arg):
		pass

	def term(self):
		pass

def PLUGIN_ENTRY():
	return funcTrackerPlugin()