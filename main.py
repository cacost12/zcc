####################################################################################
#                                                                                  #
# zcc.py -- main terminal program. Contains main program                           #
#            loop and global objects                                               #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 7/30/2023                                                                  #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard
import serial
import serial.tools.list_ports
import sys
import time

# Setup project directory structure
sys.path.insert( 0, './commands')
sys.path.insert( 0, './objects' )

# General Project
import commands        
from   config import * 
import ZAVDevice

# Commands
import clear
import comports
import connect
import exitCommand
import flash
import helpCommand
import ignite
import sensor
import dualDeploy


####################################################################################
# Global Variables                                                                 #
####################################################################################

# List of terminal commands
command_callbacks = { 
                "exit"       : exitCommand.exitFunc             ,
                "help"       : helpCommand.helpFunc             ,
                "clear"      : clear.clearConsole               ,
                "comports"   : comports.comports                ,
                "ping"       : commands.ping                    ,
                "connect"    : connect.connect                  ,
                "ignite"     : ignite.ignite                    ,
                "flash"      : flash.flash                      ,
                "sensor"     : sensor.sensor                    ,
                "dual-deploy": dualDeploy.dual_deploy
                }

# Display Constants
TERMINAL_PROMPT              = "ZCC> "
UNRECOGNIZED_COMMAND_MESSAGE = "Error: Unsupported command"


####################################################################################
# Procedures                                                                       #
####################################################################################


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
    for command in command_callbacks: 
        if userCommand == command:
           return userin

    # User input doesn't correspond to a command
    print( UNRECOGNIZED_COMMAND_MESSAGE )
    userin = input( TERMINAL_PROMPT )
    return parseInput(userin)
## parseInput ##


####################################################################################
# Application Entry Point                                                          #
####################################################################################
if __name__ == '__main__':
    
    # Initialize Serial Port Object
    zavDevice = ZAVDevice.ZAVDevice()

    # Look for possible connections
    avail_ports = serial.tools.list_ports.comports()
    for port_num, port in enumerate( avail_ports ):
        if ( 'CP2102' in port.description ):
            # Connect
            port_num = port.device
            connect_args  = [ '-p', port_num]
            connect.connect( connect_args, zavDevice )
            
    # Display command prompt
    while( True ):
        # Command prompt
        userin         = input( TERMINAL_PROMPT )

        # Parse command
        userin_clean   = parseInput( userin )
        userCommand    = userin_clean[0]
        userArgs       = userin_clean[1:]

        # Execute Command
        zavDevice.execute_command( command_callbacks[userCommand], userArgs )

## main ##


####################################################################################
# END OF FILE                                                                      #
####################################################################################