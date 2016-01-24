import peripheryFunction as pF
import numpy as np
import matplotlib.pyplot as plt

setupPeriphery()

dataplot = np.zeros(100)

for i in range(0,99)
	readVoltage()

	dataplot[i] = volt

	print('the {0}th measurement is done...')

	time.sleep(0.1)

np.savetxt('voltagePlotData.txt', dataplot, delimiter=' ')








