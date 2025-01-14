from matplotlib import pyplot as plt
import numpy as np

with open( "output/sensor_data.txt", "r" ) as file:
	lines = file.readlines()

lines_int = []
for line in lines:
	line_int_str = line.split( "\t" ) 
	line_int = []	
	for val in line_int_str:
		if ( val != '\n' ):
			line_int.append( float(val) )
	lines_int.append( line_int )

sensor_data = np.array( lines_int )
plt.plot( sensor_data[0:1000,0], sensor_data[0:1000,sensor_indices["pres"]] )
plt.show()
