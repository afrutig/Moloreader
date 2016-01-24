improt spidev
import time 

spi = spidev.SpiDev()

spi.open(0,0)

to_send = [0x00]

spi.writebytes(to_send)
