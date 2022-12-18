#################################################################################### 
#                                                                                  # 
# hw_commands.py -- module with general command line functions with hardware       # 
#                   oriented functionality                                         #
#                                                                                  #
# Author: Colton Acosta                                                            # 
# Date: 12/18/2022                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
#################################################################################### 


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard imports
import sys
import os
import time

# Project imports
import sensor_conv
import commands


####################################################################################
# Global Variables                                                                 #
####################################################################################

default_timeout = 5 # 1 second timeout

# Controller identification codes
controller_codes = [ 
                  b'\x01', # Engine Controller, Rev 3.0
                  b'\x02', # Valve Controller , Rev 2.0 
                  b'\x03', # Engine Controller, Rev 4.0 
				  b'\x04'  # Flight Computer,   Rev 1.0
                   ]

# Controller Names
controller_names = [
                   "Liquid Engine Controller (L0002 Rev 3.0)",
                   "Valve Controller (L0005 Rev 2.0)"        ,
                   "Liquid Engine Controller (L0002 Rev 4.0)",
				   "Flight Computer (A0002 Rev 1.0)"
                   ]

# Controller descriptions from identification codes
controller_descriptions = {
                  b'\x01': "Liquid Engine Controller (L0002 Rev 3.0)",
                  b'\x02': "Valve Controller (L0005 Rev 2.0)"        ,
                  b'\x03': "Liquid Engine Controller (L0002 Rev 4.0)",
				  b'\x04': "Flight Computer (A0002 Rev 1.0)"
                          }

# Lists of sensors on each controller
controller_sensors = {
                  # Engine Controller rev 4.0
                  controller_names[2]: {
						   "pt0": "Pressure Transducer 0",
						   "pt1": "Pressure Transducer 1",
						   "pt2": "Pressure Transducer 2",
						   "pt3": "Pressure Transducer 3",
						   "pt4": "Pressure Transducer 4",
						   "pt5": "Pressure Transducer 5",
						   "pt6": "Pressure Transducer 6",
						   "pt7": "Pressure Transducer 7",
						   "tc ": "Theromcouple         ",
						   "lc ": "Load Cell            "            
                           },
				  # Flight Computer rev 1.0
				  controller_names[3]: {
						   "accX" : "Accelerometer X       ",
                           "accY" : "Accelerometer Y       ",
                           "accZ" : "Accelerometer Z       ",
                           "gryoX": "Gryoscope X           ",
                           "gryoY": "Gryoscope Y           ",
                           "gryoZ": "Gryoscope Z           ",
                           "magX" : "Magnetometer X        ",
                           "magY" : "Magnetometer Y        ",
                           "magZ" : "Magnetometer Z        ",
                           "imut" : "IMU Die Temperature   ",
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature"
						   }
                     }

# Size of raw sensor readouts in bytes
sensor_sizes = {
                  # Engine Controller rev 4.0
                  controller_names[2]: {
						   "pt0": 4,
						   "pt1": 4,
						   "pt2": 4,
						   "pt3": 4,
						   "pt4": 4,
						   "pt5": 4,
						   "pt6": 4,
						   "pt7": 4,
						   "tc ": 4,
						   "lc ": 4            
                           },
				  # Flight Computer rev 1.0
				  controller_names[3]: {
						   "accX" : 2,
                           "accY" : 2,
                           "accZ" : 2,
                           "gryoX": 2,
                           "gryoY": 2,
                           "gryoZ": 2,
                           "magX" : 2,
                           "magY" : 2,
                           "magZ" : 2,
                           "imut" : 2,
                           "pres" : 4,
                           "temp" : 4 
						   }
               }

# Sensor raw readout conversion functions
sensor_conv_funcs = {
                  # Engine Controller rev 4.0
                  controller_names[2]: {
						   "pt0": sensor_conv.adc_readout_to_voltage,
						   "pt1": sensor_conv.adc_readout_to_voltage,
						   "pt2": sensor_conv.adc_readout_to_voltage,
						   "pt3": sensor_conv.adc_readout_to_voltage,
						   "pt4": sensor_conv.adc_readout_to_voltage,
						   "pt5": sensor_conv.adc_readout_to_voltage,
						   "pt6": sensor_conv.adc_readout_to_voltage,
						   "pt7": sensor_conv.adc_readout_to_voltage,
						   "tc ": sensor_conv.adc_readout_to_voltage,
						   "lc ": sensor_conv.adc_readout_to_voltage            
                           },
				  # Flight Computer rev 1.0
				  controller_names[3]: {
						   "accX" : sensor_conv.imu_accel,
                           "accY" : sensor_conv.imu_accel,
                           "accZ" : sensor_conv.imu_accel,
                           "gryoX": sensor_conv.imu_gryo,
                           "gryoY": sensor_conv.imu_gryo,
                           "gryoZ": sensor_conv.imu_gryo,
                           "magX" : None,
                           "magY" : None,
                           "magZ" : None,
                           "imut" : None,
                           "pres" : None,
                           "temp" : sensor_conv.baro_temp 
						   }
	                }


####################################################################################
# Shared Procedures                                                                #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		get_bit                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		extracts a specific bit from an integer                                    #
#                                                                                  #
####################################################################################
def get_bit( num, bit_index ):
	if ( num & ( 1 << bit_index ) ):
		return 1
	else:	
		return 0
# get_bit #


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		byte_array_to_int                                                          #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Returns an integer corresponding the hex number passed into the function   #
#       as a byte array. Assumes most significant bytes are first                  #
#                                                                                  #
####################################################################################
def byte_array_to_int( byte_array ):
	int_val   = 0 # Intermediate computation value
	result    = 0 # Final result integer
	num_bytes = len( byte_array )
	for i, byte in enumerate( byte_array ):
		int_val = int.from_bytes( byte, 'big')
		int_val = int_val << 8*( (num_bytes-1) - i )
		result += int_val
	return result
# byte_array_to_int #


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		get_raw_sensor_readouts                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts an array of bytes into a dictionary containing the raw sensor     #
#       readouts in integer format                                                 #
#                                                                                  #
####################################################################################
def get_raw_sensor_readouts( controller, sensor_bytes ):

	# Sensor readout sizes
	sensor_size_dict = sensor_sizes[controller]

	# Starting index of bytes corresponding to individual 
	# sensor readout in sensor_bytes array
	index = 0

	# Result
	readouts = {}
	
	# Convert each sensor readout 
	for sensor in sensor_size_dict:
		size             = sensor_size_dict[sensor]
		readout_bytes    = sensor_bytes[index:index+size]
		int_val          = byte_array_to_int( readout_bytes )
		readouts[sensor] = int_val
		index           += size 

	return readouts
# get_raw_sensor_readouts #


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		conv_raw_sensor_readouts                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts raw sensor readouts in integer format into the appropriate format #
#                                                                                  #
####################################################################################
def conv_raw_sensor_readouts( controller, raw_readouts ):

	# Conversion functions
	conv_funcs = sensor_conv_funcs[controller]

	# Result
	readouts = {}

	# Convert each readout
	for sensor in conv_funcs:
		if ( conv_funcs[sensor] != None ):
			readouts[sensor] = conv_funcs[sensor]( raw_readouts[sensor] )
		else:
			readouts[sensor] = raw_readouts[sensor]
	
	return readouts
# conv_raw_sensor_readouts #


####################################################################################
# Commands                                                                         #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		sensor                                                                     #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Displays sensor data and/or info                                           #
#                                                                                  #
####################################################################################
def sensor( Args, serialObj ):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

	# Subcommand and Options Dictionary
    sensor_inputs = {
					'dump' : {
                             },
                    'poll' : {
                             '-n' : 'Specify a sensor number',
                             '-h' : 'Display sensor usage info'
                             },
                    'list' : {
                             },
                    'help' : {
                             }
                    }

    # Maximum number of args
    max_args = 7

	# Command type -- subcommand function
    command_type = 'subcommand'

	# Command opcode 
    opcode = b'\x03'

    # Subcommand codes
    subcommand_codes = {
                       'dump' : b'\x01',
                       'poll' : b'\x02'
                       }

    # Lists of sensor data
    sensor_bytes_list = []
    sensor_int_list   = []

    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs(
                           Args,
                           max_args,
                           sensor_inputs,
                           command_type
                           )

	# Return if user input fails parse checks
    if ( not parse_check ):
        return serialObj

	# Set subcommand, options, and input data
    user_subcommand = Args[0]
    if ( len(Args) != 1 ):
        
        # Extract option
        user_option = Args[1]

		# Extract inputs
        user_sensor_nums = Args[2:]

	# Verify connection to board with sensors
    if ( not (serialObj.controller in controller_sensors.keys()) ):
        print( "Error: The sensor command requires a valid " +
               "serial connection to a controller with "     +
               "sensors. Run the \"connect\" command to "    +
               "establish a valid connection" )
        return serialObj

    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

	# Verify sensor nums supplied are valid
    if ( user_subcommand == "poll" ):
        if ( user_option == "-n" ):

			# Throw error if no sensors were supplied
            if ( len(user_sensor_nums) == 0 ):
                print( "Error: no sensor numbers supplied" )

            # Loop over input sensors and validity of each
            for sensor_num in user_sensor_nums:
                if ( not (sensor_num in 
                          controller_sensors[serialObj.controller].keys())
                   ):
                    print("Error: \"" + sensor_num + "\" is "  +
                          "is not a valid sensor for "         +
                          serialObj.controller + ". Run "      +
                          "the \"sensor list\" subcommand to " +
                          "see a list of all available "       +
                          "sensors and their corresponding "   +
                          "codes." )
                    return serialObj

    ################################################################################
    # Subcommand: sensor help                                                      #
    ################################################################################
    if   ( user_subcommand == "help" ):
        commands.display_help_info( "sensor" )
        return serialObj

    ################################################################################
    # Subcommand: sensor dump                                                      #
    ################################################################################
    elif ( user_subcommand == "dump" ):

        # Send command opcode 
        serialObj.sendByte( opcode )

		# Send sensor dump subcommand code
        serialObj.sendByte( subcommand_codes[user_subcommand] )

		# Determine how many bytes are to be recieved
        sensor_dump_size_bytes = serialObj.readByte()
        sensor_dump_size_bytes = int.from_bytes( 
                                     sensor_dump_size_bytes, 
                                     "big" )

        # Recieve data from controller
        for byteNum in range( sensor_dump_size_bytes ):
            sensor_bytes_list.append( serialObj.readByte() )

		# Get readouts from byte array
        raw_sensor_readouts = get_raw_sensor_readouts( 
				                        serialObj.controller,
                                        sensor_bytes_list 
                                                     )
		# Convert raw readouts
        sensor_readouts     = conv_raw_sensor_readouts(
                                        serialObj.controller,
                                        raw_sensor_readouts
                                                      )

		# Display Sensor readouts
        for sensor in sensor_readouts:
            print( sensor + ": " + str( sensor_readouts[sensor] ) )
			

        return serialObj

    ################################################################################
    # Subcommand: sensor poll                                                      #
    ################################################################################
    elif ( user_subcommand == "poll" ):
        print( "Error: sensor poll has not yet been added " +
               "to the sdec terminal by SDR developers. "   + 
               "Try again later or contact SDR for assistance" )
        return serialObj

    ################################################################################
    # Subcommand: sensor list                                                      #
    ################################################################################
    elif ( user_subcommand == "list" ):
        # Identify current serial connection
        print("Sensor numbers for " + serialObj.controller +
               " :" )

        # Loop over all sensors in list and print
        for sensor_num in controller_sensors[serialObj.controller].keys():
            print( "\t" + sensor_num + " : " +
                    controller_sensors[serialObj.controller][sensor_num] 
                 ) 
        return serialObj

    ################################################################################
    # Unknown subcommand                                                           #
    ################################################################################
    else:
        print( "Error: Unknown subcommand passed to sensor " +
               "function. " )
        commands.error_msg()
        return serialObj
# sensor #


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		flash                                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		read and write data to a controller's extenral flash                       #
#                                                                                  #
####################################################################################
def flash(Args, serialObj):

	################################################################################
	# Local Variables                                                              #
	################################################################################

	# Subcommand and Options Dictionary
	flash_inputs= { 
    'enable'  : {
			    },
    'disable' : {
			    },
    'status'  : {
			    },
	'write'   : {
			'-b' : 'Specify a byte to write to flash memory'  ,
			'-s' : 'Specify a string to write to flash memory',
			'-a' : 'Specify a memory address to write to'     ,
			'-f' : 'Specify a file to use for input data'     ,
			'-h' : 'Display help info'
			    },
	'read'    : {
			'-a' : 'Specify a memory address to read from',
			'-n' : 'Specify a number of bytes to read from flash memory',
			'-f' : 'Specify a file to use for output data',
			'-h' : 'Display help info'
			    }, 
	'erase'   : {
			    },
	'help'    : {
			    },
	'extract' : {
			    },
                  }
    
	# Maximum number of arguments
	max_args = 5

	# Command type -- subcommand function
	command_type = 'subcommand'

	# Command opcode
	opcode = b'\x22' 

    # Subcommand Data format
	# SUBOP2 | SUBOP1 | SUBOP0 | BNUM4 | BNUM3 | BNUM2 | BNUM1 | BNUM0  
	# SUBOP(0-2) Subcommand opcode bits specifies the subcommand to be
	#            executed
	# BNUM(0-4) Number of bytes to read/write (max 31)
	max_num_bytes = 31

	# Subcommand codes
	flash_read_base_code    = b'\x00'  # SUBOP 000 -> 0000 0000
	flash_enable_base_code  = b'\x20'  # SUBOP 001 -> 0010 0000
	flash_disable_base_code = b'\x40'  # SUBOP 010 -> 0100 0000
	flash_write_base_code   = b'\x60'  # SUBOP 011 -> 0110 0000
	flash_erase_base_code   = b'\x80'  # SUBOP 100 -> 1000 0000
	flash_status_base_code  = b'\xa0'  # SUBOP 101 -> 1010 0000
	flash_extract_base_code = b'\xc0'  # SUBOP 110 -> 1100 0000

	# Subcommand codes as integers
	flash_read_base_code_int    = ord( flash_read_base_code    )
	flash_enable_base_code_int  = ord( flash_enable_base_code  )
	flash_disable_base_code_int = ord( flash_disable_base_code )
	flash_write_base_code_int   = ord( flash_write_base_code   )
	flash_erase_base_code_int   = ord( flash_erase_base_code   )
	flash_status_base_code_int  = ord( flash_status_base_code  )
	flash_extract_base_code_int = ord( flash_extract_base_code )

	# flash IO data
	byte            = None
	string          = None
	file            = None
	num_bytes       = None

	# Flash status register contents 
	status_register = None

	# Supported flash boards
	flash_supported_boards = [
                   "Liquid Engine Controller (L0002 Rev 4.0)",
				   "Flight Computer (A0002 Rev 1.0)"
							 ]


	################################################################################
	# Basic Inputs Parsing                                                         #
	################################################################################
	parse_check = commands.parseArgs(
                            Args        ,
                            max_args    ,
                            flash_inputs,
                            command_type 
                            )

	# Return if user input fails parse checks
	if ( not parse_check ):
		return serialObj 

	# Set subcommand, options, and input data
	user_subcommand = Args[0]
	if ( len(Args) != 1 ):

		# Pull options from args
		Args_options = Args[1:]

		# Check that two options with input data were supplied
		if ( Args_options[0] == '-h'):
			user_options = [Args_options[0]]
			options_command = False
		elif ( len(Args_options) < 4):
			print("Error: Not enough options/inputs")
			return serialObj
		else:
			user_options = [Args_options[0], Args_options[2]]
			user_inputs  = {
                           user_options[0] : Args_options[1],
                           user_options[1] : Args_options[3]
                           }
			options_command = True
	else:
		options_command = False

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Check input data for each option
	if (options_command):

		# Check for duplicate options
		if (user_options[0] == user_options[1]):
			print('Error: Duplicate option supplied')
			return serialObj

		# Perform option specific checks
		for user_option in user_options:

			################# -b option #######################
			if (user_option == '-b'):
				# Check byte is formatted correctly
				# Format: 0xXX --> XX is a hex number

				# Check length
				if(len(user_inputs[user_option]) != 4):
					print('Error: Invalid byte format.')
					return serialObj
				
				# Check for 0x prefix
				if(user_inputs[user_option][0:2] != '0x'):
					print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

				# Convert to integer
				try:
					byte_int = int(user_inputs[user_option], 0)
				except ValueError:
					print('Error: Invalid byte.')
					return serialObj

				# Convert to byte
				byte = byte_int.to_bytes(1, 'big')
				

			################# -s option #######################
			elif (user_option == '-s'):
				# Currently no parse checks needed
				pass

			################# -n option #######################
			elif (user_option == '-n'):
				# Verify number of bytes is an integer
				try:
					num_bytes = int(user_inputs[user_option], 0)
				except ValueError:
					print('Error: Invalid number of bytes.')
					return serialObj

				# Verify numbers of bytes is in range
				if ( num_bytes <= 0 or num_bytes > max_num_bytes ): 
					print( "Error: Invalid number of bytes." )
					return serialObj

			################# -a option #######################
			elif (user_option == '-a'):
				# Check address is formatted correctly
				# Format: 0xXXXXXX

				# Check length
				if(len(user_inputs[user_option]) != 8):
					print('Error: Invalid Address format.')
					return serialObj
				
				# Check for 0x prefix
				if(user_inputs[user_option][0:2] != '0x'):
					print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

				# Convert to integer
				try:
					address_int = int(user_inputs[user_option], 0)
				except ValueError:
					print('Error: Invalid Address.')
					return serialObj

				# Convert to bytes
				address_bytes = address_int.to_bytes(
                                                    3, 
                                                    byteorder='big',
                                                    signed=False
                                                    )

			################# -f option #######################
			elif (user_option == '-f'):
				# Verify output file doesn't already exist 
				# Verify input file exists
				pass

		# Verify read and write subcommands have an address supplied	
		if (   user_subcommand == 'write' 
			or user_subcommand == 'read'):
			if ('-a' not in user_options):
				print('Error: The write and read operations ' +
					  'require an address supplied by the '   +
					  '-a option')
				return serialObj

	# Verify Engine Controller Connection
	if (not (serialObj.controller in flash_supported_boards) ):
		print("Error: The flash command requires a valid " + 
			  "serial connection to a controller with \n"    + 
			  "external flash. This includes the following " +
		      "boards: \n" )
		for board in flash_supported_boards:
			print( board )
		print()
		return serialObj

	################################################################################
	# Subcommand: flash help                                                       #
	################################################################################
	if (user_subcommand == "help"):
		commands.display_help_info('flash')
		return serialObj

	################################################################################
	# Subcommand: flash enable                                                     #
	################################################################################
	elif (user_subcommand == "enable"):

		# Send the flash Opcode
		serialObj.sendByte(opcode)

		# Send the subcommand Opcode
		serialObj.sendByte(flash_enable_base_code)

		# Recieve the status byte from the engine controller
		return_code = serialObj.readByte()

		# Parse return code
		if (return_code == b''):
			print("Error: No response code recieved")
		elif (return_code == b'\x00'):
			print("Flash write enable successful")
			serialObj.flash_write_enabled = True
		else:
			print("Error: Unrecognised response code recieved")
		

		return serialObj

	################################################################################
	# Subcommand: flash disable                                                    #
	################################################################################
	elif (user_subcommand == "disable"):

		# Send the flash opcode
		serialObj.sendByte(opcode)

		# Send the subcommand opcode
		serialObj.sendByte(flash_disable_base_code)

		# Recieve the status byte from the engine controller
		return_code = serialObj.readByte()

		# Parse return code
		if (return_code == b''):
			print("Error: No response code recieved")
		elif (return_code == b'\x00'):
			print("Flash write disable successful")
			serialObj.flash_write_enabled = False 
		else:
			print("Error: Unrecognised response code recieved")

		return serialObj

	################################################################################
	# Subcommand: flash status                                                     #
	################################################################################
	elif (user_subcommand == "status"):

		# Send the flash opcode
		serialObj.sendByte(opcode)

		# Send the subcommand opcode
		serialObj.sendByte(flash_status_base_code)

		# Recieve the contents of the flash status register 
		status_register     = serialObj.readByte()
		status_register_int = ord( status_register     )

		# Get the status code of the flash operation
		flash_status_code = serialObj.readByte()

		# Parse return code
		if (status_register == b''):
			print("Error: No response recieved from " +
                  "controller")
		else:
			print("Status register contents: \n") 
			print( "BUSY: ", get_bit( status_register_int, 0 ) )
			print( "WEL : ", get_bit( status_register_int, 1 ) )
			print( "BP0 : ", get_bit( status_register_int, 2 ) )
			print( "BP1 : ", get_bit( status_register_int, 3 ) )
			print( "BP2 : ", get_bit( status_register_int, 4 ) )
			print( "BP3 : ", get_bit( status_register_int, 5 ) )
			print( "AAI : ", get_bit( status_register_int, 6 ) )
			print( "BPL : ", get_bit( status_register_int, 7 ) )
			print( )

		return serialObj

	################################################################################
	# Subcommand: flash write                                                      #
	################################################################################
	elif (user_subcommand == "write"):

		# Check if flash chip has writing operations enabled
		if (not serialObj.flash_write_enabled
            and not (user_options[0] == '-h')):
			print("Error: Flash write has not been enabled."  +
                  "Run flash write enable to enable writing " +
                  "to the flash chip")
			return serialObj

	    ################### -h option #########################
		if (user_options[0] == '-h'):
			commands.display_help_info('flash')
			return serialObj

	    ################### -b option #########################
		elif (byte != None):
			# Send flash opcode
			serialObj.sendByte(opcode)

			# Calculate operation code
			num_bytes_to_send = 1
			operation_code_int = (flash_write_base_code_int + 
                                 num_bytes_to_send)
			operation_code = operation_code_int.to_bytes(
								   1, 
					               byteorder = 'big',
								   signed = False
                                   ) 

			# Send flash operation code
			serialObj.sendByte(operation_code)
			
			# Send base address
			serialObj.sendBytes(address_bytes)

			# Send byte to write to flash
			serialObj.sendByte(byte)

			# Recieve response code from engine controller
			return_code = serialObj.readByte()

			# Parse return code
			if (return_code == b''):
				print("Error: No response code recieved")
			elif ( return_code == b'\x00' ):
				print("Flash write successful")
			else:
				print("Error: Unrecognised response code recieved")

			return serialObj

	    ################### -s option #########################
		elif (string != None):
			print("Error: Option not yet supported")
			return serialObj

	    ################### -f option #########################
		elif (file != None):
			print("Error: Option not yet supported")
			return serialObj
		
	    ################# Unknown option #####################
		else:
			print("Error: Something went wrong. The flash "+ 
                  "write command failed to find input "    +
                  "to write to flash")
			return serialObj


	################################################################################
	# Subcommand: flash read                                                       #
	################################################################################
	elif (user_subcommand == "read"):

	    ################### -h option #########################
		if (user_options[0] == '-h'):
			commands.display_help_info('flash')
			return serialObj

	    ################### -n option #########################
		elif( num_bytes != None ):

			# Send flash opcode
			serialObj.sendByte(opcode)

			# Calculate operation code
			operation_code_int = ( flash_read_base_code_int + 
                                 num_bytes )
			operation_code = operation_code_int.to_bytes(
								   1, 
					               byteorder = 'big',
								   signed = False
                                   ) 

			# Send flash operation code
			serialObj.sendByte(operation_code)
			
			# Send base address
			serialObj.sendBytes(address_bytes)

			# Receive Bytes into a byte array
			rx_bytes = []
			for i in range( num_bytes ):
				rx_bytes.append( serialObj.readByte() )

			# Get flash status code
			flash_read_status = serialObj.readByte() 
			if ( flash_read_status != b'\x00' ):
				print( "Error: Flash Read Unsuccessful" )

			# Display Bytes on the terminal
			print( "Received bytes: \n" )
			for rx_byte in rx_bytes:
				print( rx_byte, ", ", end = "" )
			print()

			return serialObj

	    ################### -f option #########################
		elif( file!= None ):
			print("Error: Option not yet supported")
			return serialObj


	################################################################################
	# Subcommand: flash erase                                                      #
	################################################################################
	elif (user_subcommand == "erase"):
		
		# Send flash opcode 
		serialObj.sendByte( opcode )

		# Send flash erase subcommand code 
		serialObj.sendByte( flash_erase_base_code )

		# Get and Display status of flash erase operation
		flash_erase_status = serialObj.readByte()
		if ( flash_erase_status == b'\x00'):
			print( "Flash erase sucessful" )
		else:
			print( "Error: Flash erase unsuccessful" )

		return serialObj


	################################################################################
	# Subcommand: flash extract                                                    #
	################################################################################
	elif ( user_subcommand == "extract" ):

		# Send flash opcode 
		serialObj.sendByte( opcode )

		# Send flash extract subcommand code 
		serialObj.sendByte( flash_extract_base_code )

		# Recieve Data in 32 byte blocks
		# Flash contains 4096 blocks of data
		rx_byte_blocks = []
		for i in range( 4096 ):
			print( "Reading block " + str(i) + "..."  )
			rx_byte_blocks.append( serialObj.readBytes( 32 ) )

		# Recieve the status byte from the engine controller
		return_code = serialObj.readByte()


		# Convert the data into integer format
		rx_int_blocks = []
		for byte_block in rx_byte_blocks:
			rx_int_block = []
			for rx_byte in byte_block:
				rx_int_block.append( ord(rx_byte) )
			rx_int_blocks.append( rx_int_block )

		# Combine bytes from the integer data
		rx_comb_blocks = []
		for int_block in rx_int_blocks:
			rx_comb_block = []
			time = ( ( int_block[0]       ) + 
                     ( int_block[1] << 8  ) + 
					 ( int_block[2] << 16 ) + 
                     ( int_block[3] << 24 ) )
			imu_a_x = ( ( int_block[4] ) + 
                        ( int_block[5] << 8 ) )
			imu_a_y = ( ( int_block[6] ) + 
                        ( int_block[7] << 8 ) )
			imu_a_z = ( ( int_block[8] ) + 
                        ( int_block[9] << 8 ) )
			imu_g_x = ( ( int_block[10] ) + 
                        ( int_block[11] << 8 ) )
			imu_g_y = ( ( int_block[12] ) + 
                        ( int_block[13] << 8 ) )
			imu_g_z = ( ( int_block[14] ) + 
                        ( int_block[15] << 8 ) )
			imu_m_x = ( ( int_block[16] ) + 
                        ( int_block[17] << 8 ) )
			imu_m_y = ( ( int_block[18] ) + 
                        ( int_block[19] << 8 ) )
			imu_m_z = ( ( int_block[20] ) + 
                        ( int_block[21] << 8 ) )
			imu_temp = ( ( int_block[22] ) + 
                         ( int_block[23] << 8 ) )
			baro_temp = ( ( int_block[24]       ) + 
                          ( int_block[25] << 8  ) + 
                          ( int_block[26] << 16 ) + 
                          ( int_block[27] << 24 )  )
			baro_press = ( ( int_block[28] ) + 
                           ( int_block[29] << 8  ) + 
                           ( int_block[30] << 16 ) + 
                           ( int_block[31] << 24 ) )
			rx_comb_block.append( time )
			rx_comb_block.append( imu_a_x )
			rx_comb_block.append( imu_a_y )
			rx_comb_block.append( imu_a_z )
			rx_comb_block.append( imu_g_x )
			rx_comb_block.append( imu_g_y )
			rx_comb_block.append( imu_g_z )
			rx_comb_block.append( imu_m_x )
			rx_comb_block.append( imu_m_y )
			rx_comb_block.append( imu_m_z )
			rx_comb_block.append( imu_temp )
			rx_comb_block.append( baro_temp )
			rx_comb_block.append( baro_press )
			rx_comb_blocks.append( rx_comb_block )
			

		# Export the data to txt files
		with open( "output/int_data.txt", 'w' ) as file:
			for rx_comb_block in rx_comb_blocks:
				for val in rx_comb_block:
					file.write( str( val ) )
					file.write( '\t')
				file.write( '\n' )	

		# Parse return code
		if (return_code == b''):
			print("Error: No response code recieved")
		elif (return_code == b'\x00'):
			print("Flash extract successful")
		else:
			print("Error: Unrecognised response code recieved")
		return serialObj


	################################################################################
    # Unknown Option                                                               #
	################################################################################
	else:
		print("Error: unknown option passed to connect function")	
		commands.error_msg()
		return serialObj


###################################################################################
# END OF FILE                                                                     # 
###################################################################################