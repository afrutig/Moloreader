from periphery import SPI
import time

spi = SPI("/dev/spidev0.0", 0, 50000000,"msb",8,0)

while True:
	#for y in range (0x04,0x08):
		for x in range(0x00,0x100):

			#if y==0x07 & x==0x9b:
			#	break

			init= [0x18,0x03]
			data_in = spi.transfer(init)

			data_out = [0x04, x]
			data_in = spi.transfer(data_out)
		
			time.sleep(0.5)

			print("shifted out [0x%02x, 0x%02x]" % tuple(data_out))
	
