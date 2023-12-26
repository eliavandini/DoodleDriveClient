import time
import serial

# ser = serial.Serial(
#     port='/dev/ttyUSB1',
#     # baudrate=9600,
#     # parity=serial.PARITY_ODD,
#     # stopbits=serial.STOPBITS_TWO,
#     # bytesize=serial.SEVENBITS
# )

for x in range(100, 0, -1):
    print("\x1b[2K" + '*' * x, x, end='\r')
    time.sleep(0.1)
print()


# while True:
#     if ser.isOpen():
#         pass