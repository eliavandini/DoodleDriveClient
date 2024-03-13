import struct
from tkinter import EXCEPTION
import serial
from serial.tools import list_ports
from halo import Halo
import fancybar

startbyte = b"\xD8"
endbyte = b"\xE4"


INSTRUCTION_SEND_BUFF = 3
INSTRUCTION_FREE_MEM = 4
INSTRUCTION_ABORT = 5
INSTRUCTION_PAUSE = 10
INSTRUCTION_RESUME = 11
INSTRUCTION_RESTART = 15
INSTRUCTION_READ = 50
INSTRUCTION_PING = 150
INSTRUCTION_MEMORY_MAP = 130
INSTRUCTION_RESULT = 101
INSTRUCTION_OK = 110
INSTRUCTION_STATUS = 102
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
        exit("ERROR: too many devices plugged in")
    elif len(ports) == 0:
        exit("ERROR: no device plugged in")
    else:
        return ports[0].device

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
    m   display memory map
    
    \x1B[1mRuntime Operations\x1B[0m
    p   pause
    o   resume
    t   restart process
    a   abort
    
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
    

def send_to_stm(proc_id, instruction, data: bytearray = bytearray([])):
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
    
    
    
    bytearr = startbyte+bytes(split_int16(proc_id)+tuple([instruction, len(data) & 0xFF])) + data + endbyte
    # print(bytearr)
    # print_bytearr(bytearr)
    ser =  serial.Serial(find_port(), baudrate=9600)
    ser.write(bytearr)

def recive_from_stm():
    ser =  serial.Serial(find_port(), baudrate=9600)
    ser.flush()
    ser.reset_input_buffer()  # not resetting input buffers leads to pyserial rereading the same comunication over and over for some reason (buffer resetting should be done automatically wtf?!?!?)
    spinner = Halo(text='synching with board', spinner='dots12')
    spinner.start()
    ser.read_until(startbyte)
    spinner.stop()
    
    d = ser.read(size=3)
    value = struct.unpack(">HBB", d)
    proc_id = value[0]
    instruction = value[1]
    data_size = value[2]
    if data_size:
        data = ser.read_until(size=data_size)
    else:
        data = bytearray([])
    if ser.read() != endbyte:
        raise Exception(f"failed to assert endbyte at end of transmission. proc_id:{proc_id}, instruction:{instruction}, data size:{data_size}, data:{data}")
    if instruction == INSTRUCTION_ERROR:
        raise Exception(f"stm sent the following error message: " + data.decode("ascii"))
    return proc_id, instruction, data

def wait_for_ping(ok=False):
    if ok:
        expected_id = INSTRUCTION_PING
    else:
        expected_id = INSTRUCTION_OK
    proc_id, Instruction, data = recive_from_stm()
    if Instruction != expected_id:
        raise Exception(f"expected ping , got {proc_id, Instruction, data} instead")
    return proc_id, Instruction, data
    
        
def save_to_memory():
    a, b = parse_memory_range(input("\x1B[1menter section to write to \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    input_str = input(f"enter an ascii string (max {abs(b-a)} bytes)")
    try:
        input_str: bytearray = input_str.decode('ascii')
    except UnicodeDecodeError:
        print("ERROR: Failed to Decode to ASCII")
        return
    if len(input_str) > abs(b-a):
        print(f"ERROR: Input is too long (max is {abs(b-a)})")

    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_SEND_BUFF, bytearray([a, a+len(input_str)])+input_str)
    wait_for_ping(ok=True)
    
    
def free_memory():
    a, b = parse_memory_range(input("\x1B[1menter section to free \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    
    
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_FREE_MEM, bytearray([a, b]))
    wait_for_ping(ok=True)
    
def read_memory():
    a, b = parse_memory_range(input("\x1B[1menter section to read \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    
    
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_FREE_MEM, bytearray([a, b]))
    wait_for_ping(ok=True)
    
def display_memory():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_MEMORY_MAP)
    print(recive_from_stm())
    
    
    # print("recived:", proc_id, Instruction, data)
    
def status_op():
    bar = fancybar.GradientBarType()
    while True:
        proc_id, Instruction, data = wait_for_ping()
        send_to_stm(proc_id, INSTRUCTION_STATUS)
        print(recive_from_stm())
        

def pause_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_MEMORY_MAP)
    print(recive_from_stm())
    
def resume_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_RESUME)
    wait_for_ping(ok=True)

def restart_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_RESTART)
    wait_for_ping(ok=True)

def abort_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_ABORT)
    wait_for_ping(ok=True)
    
    
    # print("sent:", end="")
    # send_to_stm(proc_id, INSTRUCTION_MEMORY_MAP)
    # proc_id, Instruction, data = recive_from_stm()
    # print("recived:", proc_id, Instruction, data)
    
    # print("recived:", recive_from_stm())
    # print("done")
    
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
    # pass
    
def change_log_level():
    # mal schauen ob ich wirklich lust habe das zu implementieren oder überhaupt brauche.
    # villeicht implementiere ich es trotzdem nur zur vorstellung programmiere einen dummy log mit fake logs
    pass

def exit(exit_msg = "Olls fertig. Schian gruaß no."):
    print("")
    print(exit_msg)

def main():
    try:
        while True:
            inp = input("\x1B[1mcommand \x1B[0m(h for help): ").lower()
            # inp = "d"
            print()
            match inp:
                case "h" | "help":
                    display_help()
                case "s" | "save":
                    save_to_memory()
                case "f" | "free":
                    free_memory()
                case "r" | "read":
                    read_memory()
                case "m" | "map":
                    display_memory()
                case "c" | "status":
                    status_op()
                case "p" | "pause":
                    pause_op()
                case "o" | "resume":
                    resume_op()
                case "t" | "restart":
                    restart_op()
                case "a" | "abort":
                    abort_op()
                case "l" | "log":
                    change_log_level()
                case "q" | "quit":
                    exit()
                    break
                case _:
                    print("Invalid choice. Please enter a valid command")
                    display_help()
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()