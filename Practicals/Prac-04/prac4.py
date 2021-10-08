import busio
import digitalio
import board
import threading
import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

increment = 1

    # create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

    # create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

    # create the mcp object
mcp = MCP.MCP3008(spi, cs)
    # create an analog input channel on pin 1
chanLDR = AnalogIn(mcp, MCP.P2)
chanTemp = AnalogIn(mcp, MCP.P1)

#def print_values():
#    thread = threading.Timer(increment, print_values)
#    thread.daemon = True
#    thread.start()
#    print(str(datetime.datetime.now()+ 's      ' + str(chanTemp.value) + '      ' + str(chanTemp.value) + 'C' + str(chanLDR.value))

print('Raw ADC Value: ', chanLDR.value)
print('ADC Voltage: ' + str(chanLDR.voltage) + 'V')
print('Raw ADC Value: ', chanTemp.value)
print('ADC Voltage: ' + str(chanTemp.voltage) + 'V')
print('Runtime')
