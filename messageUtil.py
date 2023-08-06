####################################################################################
#                                                                                  #
# messageUtil.py -- module with general console message printing helper functions  #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/6/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		display_help_info                                                          #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		displays a command's help info from its doc file                           #
#                                                                                  #
####################################################################################
def display_help_info( command ):
	with open ("doc/" + command ) as file:
		doc_lines = file.readlines()
	print()
	for line in doc_lines:
		print( line, end='' )
	print()
## display_help_info ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		error_msg                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		displays a general software failure error message                          #
#                                                                                  #
####################################################################################
def error_msg():
	print( "Something went wrong. Report this issue to " + 
              "the Zenith development team" )	
## error_msg ##


##################################################################################
# END OF FILE                                                                    #
##################################################################################