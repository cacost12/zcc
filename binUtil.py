####################################################################################
#                                                                                  #
# binUtil.py -- module with general binary helper functions                        #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 8/6/2023                                                                   #
# Zenith Avionics                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
import struct


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_bit                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         extracts a specific bit from an integer                                  #
#                                                                                  #
####################################################################################
def get_bit( num, bit_index ):
    if ( num & ( 1 << bit_index ) ):
        return 1
    else:    
        return 0
## get_bit ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         byte_array_to_int                                                        #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Returns an integer corresponding the hex number passed into the function #
#       as a byte array. Assumes least significant bytes are first                 #
#                                                                                  #
####################################################################################
def byte_array_to_int( byte_array ):
    int_val   = 0 # Intermediate computation value
    result    = 0 # Final result integer
    num_bytes = len( byte_array )
    for i, byte in enumerate( byte_array ):
        int_val = int.from_bytes( byte, 'big')
        int_val = int_val << 8*i
        result += int_val
    return result
## byte_array_to_int ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         byte_array_to_float                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Returns an floating point number corresponding the hex number passed     #
#         into the function as a byte array. Assumes least significant bytes are   #
#         first                                                                    #
#                                                                                  #
####################################################################################
def byte_array_to_float( byte_array ):
    # Check to NaN
    if ( byte_array == [b'\xFF', b'\xFF', b'\xFF', b'\xFF'] ):
        byte_array = [b'\x00', b'\x00', b'\x00', b'\x00']
    byte_array_joined = b''.join( byte_array )
    return struct.unpack( 'f', byte_array_joined )[0]
## byte_array_to_float ##


###################################################################################
# END OF FILE                                                                     #
###################################################################################