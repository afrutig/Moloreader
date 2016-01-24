from periphery import SPI
from periphery import I2C
import preferences as pref


'''
Setting up the communication to the periphery devices e.g. digital potentiometer, ADC, and Squiggle motor.
'''
def setupPerifery():

	# SPI for the digital potentiometer (digPot)
	digPot = SPI("/dev/spidev0.0", 0, 50000000,"msb",8,0)

	# SPI vor the ADC (adc)
	adc = SPI("/dev/spidev0.1", 0, 50000000,"msb",8,0)

	# I2C for the Squiggle motor (squiggle)
	squiggle = I2C("/dev/i2c-0")

	return 

'''
Serial Data transfer to  the digital potentiometer.
'''
def w2digPot(one,two):

	data_out= [0x18,0x03]
	data_in = digPot.transfer(data_out)

	if pref.printSerialData == True:
		print("DigPot ------------------")
		print("outline  [0x%02x, 0x%02x]" % tuple(data_out))
		print("inline   [0x%02x, 0x%02x]" % tuple(data_in))

	return
'''
Serial Data transfer to ADC and readout the voltage of the photo diode.
'''
def readVolt():

	data_out= [0x18,0x03]
	data_in = digPot.transfer(data_out)

	if pref.printSerialData == True:
		print("Voltage -----------------")
		print( '{0} V'.format(volt))
		

	return volt

'''
Serial Data transfer to  the digital potentiometer.
'''
def w2squiggle(one,two):

	#Address of the Squiggle motor
	address =

	#

	data_out= [0x18,0x03]
	data_in = digPot.transfer(data_out)

	if pref.printSerialData == True:
		print("Squggle -----------------")
		print("outline  [0x%02x, 0x%02x]" % tuple(data_out))
		print("inline   [0x%02x, 0x%02x]" % tuple(data_in))

	return



