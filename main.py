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

memory_size = 20

def get_bit(value, bit_index):
    return (value >> bit_index) & 1

def set_bit(value, bit_index, bit):
    if bit:
        return value | (1 << bit_index)
    else:
        return value & ~(1 << bit_index)




def display_help():
    print("""
\x1B[1mHelp:
    Operations\x1B[0m
    s   save a string to memory
    f   free some memory
    r   read from memory 
    d   display memory map
    
    \x1B[1mMisc\x1B[0m
    h   display the HELP screen
    l   change the log verbose level
    q   quit
          """)
    
def parse_memory_range(inp):
    try:
        try:
            if inp == "q":
                return -1, -1
            if inp.count(",") == 1:
                a, b = inp.split(",")
            elif inp.count(";") == 1:
                a, b = inp.split(";")
            else:
                a, b = inp.split(":")
                
            a, b = int(a), int(b)
        except Exception as e:
            raise Exception("Couldn't parse input") 
        if 0 > a or 0 > b:
            raise Exception("values cannot be lower than 0") 
        if a >= b:
            raise Exception("Invalid memory range")
        if b >= memory_size:
            raise Exception("Out of memory bounds")
        return a, b
        
    except Exception as e:
        return parse_memory_range(input("\x1B[1m" + str(e) + ". Try again \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
        
def save_to_memory():
    a, b = parse_memory_range(input("\x1B[1menter section to write to \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    if a < 0 or b < 0:
        return
    
def free_memory():
    a, b = parse_memory_range(input("\x1B[1menter section to free \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    if a < 0 or b < 0:
        return
    
def read_memory():
    a, b = parse_memory_range(input("\x1B[1menter section to read \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    if a < 0 or b < 0:
        return
    
def display_memory():
    # rectangular display of memory map using # and spaces to represent occupied and free bytes in memory
    pass
    
def change_log_level():
    #mal schauen ob ich wirklich lust habe das zu implementieren
    pass

while True:
    inp = input("\x1B[1mcommand \x1B[0m(h for help): ")
    print()
    match inp:
        case "h":
            display_help()
        case "s":
            save_to_memory()
        case "f":
            free_memory()
        case "r":
            read_memory()
        case "d":
            display_memory()
        case "l":
            change_log_level()
        case "q":
            print("Olls fertig. Schian griaß no.")
            break
        case _:
            print("Invalid choice. Please enter a valid command")
            display_help()

    