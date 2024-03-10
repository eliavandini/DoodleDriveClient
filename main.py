import asyncio
from dis import Instruction
import struct
from threading import Thread
import time
from numpy import empty
from pygments import highlight
import serial
from serial.tools import list_ports

startbyte = b"\xD8"
endbyte = b"\xE4"


INSTRUCTION_SEND_BUFF = 3
INSTRUCTION_ABORT = 5
INSTRUCTION_PAUSE = 10
INSTRUCTION_RESUME = 11
INSTRUCTION_RESTART = 15
INSTRUCTION_PING = 150
INSTRUCTION_MEMORY_MAP = 130
INSTRUCTION_RESULT = 101
INSTRUCTION_STARTED = 110
INSTRUCTION_PROGESS = 102
INSTRUCTION_FINISHED = 103
INSTRUCTION_ERROR = 200

# try: 
#     ser = serial.Serial(
#         port='/dev/ttyUSB1',
#         # baudrate=9600,
#         # parity=serial.PARITY_ODD,
#         # stopbits=serial.STOPBITS_TWO,
#         # bytesize=serial.SEVENBITS
#     )
# except serial.SerialException as e:
#     ser = serial.Serial(
#         port='/dev/ttyUSB0',
#         # baudrate=9600,
#         # parity=serial.PARITY_ODD,
#         # stopbits=serial.STOPBITS_TWO,
#         # bytesize=serial.SEVENBITS
#     )
    

# def serial_init(port='/dev/ttyUSB0')

# for x in range(100, 0, -1):
#     print("\x1b[2K" + '*' * x, x, end='\r')
#     time.sleep(0.1)
# print()

def find_port():
    ports = list(list_ports.grep('CP2102 USB to UART Bridge Controller'))
    if len(ports) > 1:
        raise OSError("too many devices plugged in")
    elif len(ports) == 0:
        raise OSError("no device plugged in")
    else:
        return ports[0].device
    
    
ser =  serial.Serial(find_port(), baudrate=9600)

memory_size = 20
serial_reading = True


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

def print_bytearr(data:bytearray):
    for byte in data:
        print(byte, end=' ')
    print("")
    
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

def split_int16(value):
    # Mask the low byte (rightmost 8 bits)
    low_byte = value & 0xFF
    
    # Shift to the right to get the high byte
    high_byte = (value >> 8) & 0xFF
    
    return high_byte, low_byte
    

def send_to_stm(proc_id, instruction, data: bytearray = None):
    # if data is not None and len(data) ==0:
    #     data = None
    # while serial_reading:
    #     ser.read_until(startbyte, 1)
    #     ser.read()
    #     d = ser.read(size=3)
    #     value = struct.unpack(">HB", d)
    #     proc_id = value[0]
    #     inst_id = value[1]
    #     if inst_id == INSTRUCTION_PING:
    #         if data is None:
    #             ser.write()
    
    bytearr = startbyte+bytes(split_int16(proc_id)+tuple([instruction])) + endbyte
    # print(bytearr)
    print_bytearr(bytearr)
    if data is not None and len(data) > 0:
        ser.write(startbyte+bytes(split_int16(proc_id)+tuple([instruction])) + data + endbyte)
    else:
        ser.write(bytearr)

def recive_from_stm():
    ser.read_until(startbyte)
    d = ser.read(size=3)
    value = struct.unpack(">HB", d)
    proc_id = value[0]
    instruction = value[1]
    data = ser.read_until(endbyte, size=256)
    return proc_id, instruction, data
        
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
    proc_id, Instruction, data = recive_from_stm()
    print("recived:", proc_id, Instruction, data)
    
    
    print("sent:", end="")
    send_to_stm(proc_id, INSTRUCTION_MEMORY_MAP)
    
    print("recived:", recive_from_stm())
    print("done")
    
    # send_to_stm()
    # bit_array = []
    # for index, bit in enumerate(bit_array):
    #     if bit == 1:
    #         print("#", end="")
    #     else:
    #         print(" ", end="")
    #     if index % 8 == 0:
    #         print()
    # print()  # Move to the next line after each row
    pass
    
def change_log_level():
    #mal schauen ob ich wirklich lust habe das zu implementieren
    pass

def exit():
    serial_reading = False
    print("")
    print("Olls fertig. Schian gruaß no.")

def main():
    try:
        while True:
            inp = input("\x1B[1mcommand \x1B[0m(h for help): ")
            # inp = "d"
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
                    exit()
                    break
                case _:
                    print("Invalid choice. Please enter a valid command")
                    display_help()
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()