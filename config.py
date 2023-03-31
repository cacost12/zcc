####################################################################################
#                                                                                  #
# config.py -- Contains sdec global configuration parameters                       #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 12/29/2022                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
import sys


####################################################################################
# Global Variables                                                                 #
####################################################################################

# Command Line Arguments
cmd_args = sys.argv

# Debug configuration, true for debug timeout settings
if ( 'debug' in cmd_args ):
    sdr_debug = True 
    print( 'SDEC Running in DEBUG mode' )
else:
    sdr_debug = False


###################################################################################
# END OF FILE                                                                     # 
###################################################################################