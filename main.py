import time
import serial

# ser = serial.Serial(
#     port='/dev/ttyUSB1',
#     # baudrate=9600,
#     # parity=serial.PARITY_ODD,
#     # stopbits=serial.STOPBITS_TWO,
#     # bytesize=serial.SEVENBITS
# )

# def serial_init(port='/dev/ttyUSB1')

# for x in range(100, 0, -1):
#     print("\x1b[2K" + '*' * x, x, end='\r')
#     time.sleep(0.1)
# print()

def display_help():
    print("""
\x1B[1mHelp:
    Operations\x1B[0m
    s   save a string to memory
    a   append a string to memory
    f   free some memory
    r   read from memory 
    
    \x1B[1mMisc\x1B[0m
    h   display the HELP screen
    l   change the log verbose level
    q   quit
          """)

while True:
    match input("command (h for help)"):
        case "h":
            display_help()
        case "q":
            print("Olls fertig. Schian griaß no.")
            break
        case _:
            print("Invalid choice. Please enter a valid command")
            display_help()

    