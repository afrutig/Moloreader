import peripheryFunctions as pF 
import time
import numpy as np
import preferences as pref


'''
Catches the sent data to the digital potentiometer and stores the corresponding voltage.
'''
def coupleIn():
	container = np.array
	pF.setupPeripery()

	if pref.fullCouplingRange == True:
		x = (0x04,0x08)
		a = (0x00,0xFF)
	else:
		x = (0x04,0x08)
		a = (0x00,0xFF)

	for i in range(x[0],x[1]):

		for j in range(a[0],a[1]):

			pF.w2digPot(i,j)

			time.sleep(0.2)

			volt = pF.readVoltage()

			newrow = np.array([i,j,volt])

			container = np.vstack([container,newrow])

	maxVLocation = np.argmax(container[:,2])

	maxVInput = container[maxVLocation,:]

	pF.w2digPot(container[maxVLocation,0], container[maxVLocation,1])

if __name__ = '__main__'

	coupleIn()


