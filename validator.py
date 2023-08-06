####################################################################################
#                                                                                  #
# validator.py -- module with input validation functions                           #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/6/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################


####################################################################################
# Globals                                                                          #
####################################################################################

# Validator result booleans 
PASS = True
FAIL = False

# List of terminal commands
commandCallbacks = [ 
                "exit"        ,
                "help"        ,
                "clear"       ,
                "comports"    ,
                "ping"        ,
                "connect"     ,
                "ignite"      ,
                "flash"       ,
                "sensor"      ,
                "dual-deploy" 
]

# Display Constants
TERMINAL_PROMPT              = "ZCC> "
UNRECOGNIZED_COMMAND_MESSAGE = "Error: Unsupported command"


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		parseArgs                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		runs basic checks on command inputs and outputs a                          #
#       boolean indicating if the user input passes the                            #
#       checks                                                                     #
#                                                                                  #
####################################################################################
def parseArgs(
             Args,          # function arguments
			 max_num_Args,  # maximum number of function arguments
             Args_dic,      # dictionary of supported inputs
             command_type,  # indicates if command has subcommands
             ):

	##############################################################################
	# Local Variables                                                            #
	##############################################################################


	# subcommand support
	if ( command_type == 'subcommand' ):
		subcommand_func = True
	else:
		subcommand_func = False


	##############################################################################
	# Input Tests                                                                #
	##############################################################################

	# No Subcommands/Options
	if ( subcommand_func ):
		if ( len(Args) == 0 ): # no subcommand
			print( 'Error: No subcommand supplied. Valid ' +
                   'subcommands include: ' )
			for subcommand in Args_dic:
				print( '\t' + subcommand )
			print()
			return FAIL
		subcommand = Args[0]
	else:
		if ( len(Args) == 0 ): # no options
			print( 'Error: No options supplied. Valid ' +
                   'options include: ' )
			for option in Args_dic:
				print( '\t' + option + '\t' + Args_dic[option] ) 
			print()
			return FAIL
		user_option = Args[0]

	# Too Many Inputs
	if ( len(Args) > max_num_Args ): 
		print( 'Error: To many inputs.' )
		return FAIL

	# Unrecognized Subcommand
	if ( subcommand_func ):
		if ( not (subcommand in Args_dic) ): 
			print('Error: Unrecognized subcommand. Valid ' +
                  'subcommands include: ')
			for subcommand in Args_dic:
				print( '\t' + subcommand )
			print()
			return FAIL
		num_options = len( Args_dic[subcommand] )
		# No option supplied after subcommand
		if ( (len(Args) == 1) and (num_options != 0) ):
			print( 'Error: No options supplied. Valid ' +
                   'options include: ' )
			for option in Args_dic[subcommand]:
				print( '\t' + option + '\t' + 
                       Args_dic[subcommand][option] ) 
			print()
			return FAIL
		# Subcommand valid, exit if subcommand has no options
		if ( num_options == 0 ):
			return PASS
		else: 
			# Organize user options into a list
			user_options = []
			for arg in Args[1:]:
				if ( '-' in arg ):
					user_options.append(arg)

	# Unrecognized Option	
	if ( subcommand_func ): #subcommand supported
		for user_option in user_options:	
			if ( not(user_option in Args_dic[subcommand]) ): 
				print( 'Error: Unrecognized option. Valid ' +
                       'options include: ')
				for option in Args_dic[subcommand]:
					print( '\t' + option + '\t' + 
                           Args_dic[subcommand][option] ) 
				print()
				return FAIL
	else: # subcommand not supported 
		if ( not(user_option in Args_dic) ): 
			print( 'Error: Unrecognized option. Valid ' +
                   'options include: ' )
			for option in Args_dic:
				print( '\t' + option + '\t' + Args_dic[option] ) 
			print()
			return FAIL

	# User input passes all checks	
	return PASS
## parseArgs ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		parseInput                                                                 #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		checks user input against command list options                             #
#                                                                                  #
####################################################################################
def parseInput( userin ): 

    # Get rid of any whitespace
    userin.strip()

    # Split the input into commands and arguments
    userin = userin.split() 
    try:
        userCommand = userin[0]
        CommandArgs = userin[1:] 
    except TypeError:
        print( UNRECOGNIZED_COMMAND_MESSAGE )
        userin = input( TERMINAL_PROMPT )
        parseInput(userin)

    # Check if user input corresponds to a function
    for command in commandCallbacks: 
        if userCommand == command:
           return userin

    # User input doesn't correspond to a command
    print( UNRECOGNIZED_COMMAND_MESSAGE )
    userin = input( TERMINAL_PROMPT )
    return parseInput(userin)
## parseInput ##


##################################################################################
# END OF FILE                                                                    #
##################################################################################