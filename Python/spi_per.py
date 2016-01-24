from periphery import SPI
import time

spi = SPI("/dev/spidev0.0", 0, 50000000,"msb",8,0)

what = 1

#if what==1:
data_out= [0x18,0x03]
data_in = spi.transfer(data_out)

#print("shifted out [0x%02x, 0x%02x]" % tuple(data_out))
#print("shifted out [0x%02x, 0x%02x]" % tuple(data_in))

#time.sleep(1)

	
#else:
data_out = [0x04, 0x00]
data_in = spi.transfer(data_out)

print("shifted out [0x%02x, 0x%02x]" % tuple(data_out))
print("shifted out [0x%02x, 0x%02x]" % tuple(data_in))


