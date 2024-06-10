import string
import struct
import threading
import time
import serial
from serial.tools import list_ports
from halo import Halo
import fancybar
from fancybar import ProgressBar

# from fancybar.progressbar import ProgressBar

startbyte = b"\xD8"
endbyte = b"\xE4"
startbyte_dec = 218
endbyte_dec = 228

NO_OP = 0
STATUS_WORKING = 1
STATUS_PAUSED = 2
STATUS_STANDBY = 3



INSTRUCTION_SEND_BUFF = 3
INSTRUCTION_FREE_MEM = 4
INSTRUCTION_ABORT = 5
INSTRUCTION_PAUSE = 10
INSTRUCTION_WALK = 90
INSTRUCTION_EDGE = 91
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
    ports = list(list_ports.grep('USB to UART Bridge Controller'))
    if len(ports) > 1:
        exit("ERROR: too many devices plugged in")
    elif len(ports) == 0:
        exit("ERROR: no device plugged in")
    else:
        return ports[0].device

memory_size = (10 *15) // 8
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
    s | save      save a string to memory
    f | free      free some memory
    r | read      read from memory 
    m | map       display memory map
    
    \x1B[1mRuntime Operations\x1B[0m
    z | result    display what has been read
    c | status    monitor process
    p | pause     pause process
    o | resume    resume process
    t | restart   restart process
    a | abort     abort process
    
    \x1B[1mAdvanced\x1B[0m
    w | walk      walk motor to position
    e | edge      reallign with limiters
    
    \x1B[1mMisc\x1B[0m
    h | help      display the HELP screen
    l | log       change the log verbose level
    q | quit      quit
          """)

def print_bytearr(data:bytearray):
    out = ""
    for byte in data:
        out += f"{int(str(byte), 10):02X} "
    return out
    
def is_ascii(s):
    return all(c in string.printable for c in s)
                                                                                                 
def exception_handler(func): 
    def wrapper(*arg, **kwargs):
        try:
            func(*arg, **kwargs)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
    return wrapper

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
    
    
    bytearr = startbyte+bytes(split_int16(proc_id)+tuple([instruction, len(data) & 0xFF])) + endbyte
    if len(data) > 0:
        bytearr += data + endbyte
    # print(bytearr)
    # print_bytearr(bytearr)
    if (instruction != INSTRUCTION_STATUS):
        print("instruction: ", print_bytearr(bytearr))
    # print("\n\n\n\"")
    ser =  serial.Serial(find_port(), baudrate=9600)
    print_bytearr(bytearr)
    ser.write(bytearr)

def recive_from_stm(silent=False):
    ser =  serial.Serial(find_port(), baudrate=9600)
    ser.flush()
    ser.reset_output_buffer()
    ser.reset_input_buffer()  # not resetting input buffers leads to pyserial rereading the same comunication over and over for some reason (buffer resetting should be done automatically wtf?!?!?)
    if not silent:
        spinner = Halo(text='synching with board', spinner='dots12')
        spinner.start()
    ser.read_until(startbyte)
    if not silent:
        spinner.stop()
    
    # ser.reset_output_buffer()
    # ser.reset_input_buffer()
    d = ser.read(size=5)
    value = struct.unpack(">HBBB", d)
    proc_id = value[0]
    instruction = value[1]
    data_size = value[2]
    
    
    if value[3] != 228:
        raise Exception(f"failed to assert endbyte at end of transmission. proc_id:{proc_id}, instruction:{instruction}, data size:{data_size}, end_byte: {value[3]}")

    
    
    
    data = b'' 
    if data_size:
        data = ser.read_until(size=data_size)
        if ser.read() != endbyte:
            raise Exception(f"failed to assert endbyte at end of transmission. proc_id:{proc_id}, instruction:{instruction}, data size:{data_size}, data:{data}")
        if instruction == INSTRUCTION_ERROR:
            raise Exception(f"stm sent the following error message: " + data.decode("ascii"))
            print(f"stm sent the following error message: " + data.decode("ascii"))
    if instruction == INSTRUCTION_ERROR:
        raise Exception(f"stm sent the following error message: " + data.decode("ascii"))
        print(f"stm sent the following error message: " + data.decode("ascii"))
    return proc_id, instruction, data

def wait_for_ping(ok=False, silent=False):
    if ok:
        expected_id = INSTRUCTION_OK
    else:
        expected_id = INSTRUCTION_PING 
    proc_id, Instruction, data = recive_from_stm(silent=silent)
    if Instruction != expected_id:
        raise Exception(f"expected {'ok' if ok else 'ping'} , got {proc_id, Instruction, data} instead")
    return proc_id, Instruction, data
    
@exception_handler
def save_to_memory(pos=None, input_str=None):
    if pos is None or input_str is None:
        a, b = parse_memory_range(input("\x1B[1menter section to write to \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
        input_str = input(f"enter an ascii string (max {abs(b-a)} bytes): ")
    else:
        a, b = parse_memory_range(pos)
    if not is_ascii(input_str):
        print("ERROR: Failed to Decode to ASCII")
        return
    print(print_bytearr(bytearray(input_str, "ascii")))
    if len(input_str) > abs(b-a):
        print(f"ERROR: Input is too long (max is {abs(b-a)})")
        return

    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_SEND_BUFF, bytearray([a, a+len(input_str)])+input_str.encode("ascii"))
    wait_for_ping(ok=True)
    
@exception_handler
def free_memory(pos=None):
    if pos is None:
        a, b = parse_memory_range(input("\x1B[1menter section to write to \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    else:
        a, b = parse_memory_range(pos)   
    
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_FREE_MEM, bytearray([a, b]))
    wait_for_ping(ok=True)

@exception_handler
def read_memory(pos=None):
    if pos is None:
        a, b = parse_memory_range(input("\x1B[1menter section to write to \x1B[0m(\x1B[2mstart index\x1B[0m:\x1B[2mstop index\x1B[0m):\n"))
    else:
        a, b = parse_memory_range(pos)  
    
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_READ, bytearray([a, b]))
    wait_for_ping(ok=True)

@exception_handler
def result():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_RESULT)
    proc_id, Instruction, data = recive_from_stm()
    if Instruction == INSTRUCTION_RESULT:
        try:
            print(f"stm read buffer: {data.decode('ascii'), print_bytearr(data)}")
        except UnicodeDecodeError:
            print(f"stm read buffer: {print_bytearr(data)}")
    else:
        raise Exception(f"expected INSTRUCTION_READ got proc_id:{proc_id}, instruction:{Instruction}, data:{data}")

@exception_handler
def display_memory():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_MEMORY_MAP)
    proc_id, Instruction, data = recive_from_stm()
    print(recive_from_stm())
    for index, i in enumerate(data):
        if index % 8 == 0:
            print(f"\n\x1B[1m{index:04X}: \x1B[0m", end="")
        if i:
            print("#", end="")
        else:
            print("_", end="")
    
    
    # print("recived:", proc_id, Instruction, data)

@exception_handler
def status_op():
    # args = {"length":250, "bartype":"gradient", "spinner":"dots12", "start_color":(0, 255, 255), "end_color":(0, 255, 0), "spinner_fg_color":(0, 255, 255), "spinner_speed":0.1}
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_STATUS)
    proc_id, Instruction, data = recive_from_stm()
    value = struct.unpack(">BHH", data)
    last_state = value[0]
    last_max_prog = value[2]
    
    run_thread = True
    bar = ProgressBar(last_max_prog, length=250, bartype="gradient", spinner="dots12", start_color=(0, 255, 255), end_color=(0, 255, 0), spinner_fg_color=(0, 255, 255), spinner_speed=0.1, item_name="STATUS")
    bar.items_done_at_start = value[1]
    bar.start()
    def func():
        while run_thread:
            bar.items_done -= 1
            if bar.items_done < 0:
                bar.items_done = 0
            bar.update()
            time.sleep(0.01)
    thread = threading.Thread(target=func)
    thread.start()
    try:
        while True:
            _, _, _ = wait_for_ping(silent=True)
            send_to_stm(proc_id, INSTRUCTION_STATUS)
            proc_id, Instruction, data = recive_from_stm(silent=True)
            value = struct.unpack(">BHH", data)
            state = value[0]
            max_prog = value[2]
            prog = value[1]
            # print(proc_id, Instruction, data, state, max_prog, prog)
            # if state == STATUS_WORKING and state != last_state:
                # bar = fancybar.ProgressBar(max_prog, **args)
            
            # if state != STATUS_WORKING and last_state == STATUS_WORKING:
            #     bar.stop()
                    
            # if state == STATUS_PAUSED and last_state != STATUS_PAUSED:
            #     print("paused")
            # if state == STATUS_STANDBY and last_state != STATUS_STANDBY:
            #     print("standby")
            
            if state == STATUS_PAUSED:
                bar.item_name = "PAUSED"
            if state == STATUS_STANDBY:
                bar.item_name = "STANDBY"
            if state == STATUS_WORKING:
                bar.item_name = "WORKING"
                bar.items = max_prog
                bar.items_done = prog
                
            
            last_state = state
            last_max_prog = max_prog
    except KeyboardInterrupt as e:
        pass
    run_thread = False
    thread.join()
        
        
@exception_handler
def pause_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_PAUSE)
    wait_for_ping(ok=True)

@exception_handler
def resume_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_RESUME)
    wait_for_ping(ok=True)
    
@exception_handler
def restart_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_RESTART)
    wait_for_ping(ok=True)

@exception_handler
def abort_op():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_ABORT)
    wait_for_ping(ok=True)

@exception_handler
def walk(id=None, goal=None):
    if id is None and goal is None:
        p = [int(input("enter motor id: ")), int(input("enter goal post: "))]
    else:
        p = [int(id), int(goal)]
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_WALK, bytearray(p))
    wait_for_ping(ok=True)

@exception_handler
def edge():
    proc_id, Instruction, data = wait_for_ping()
    send_to_stm(proc_id, INSTRUCTION_EDGE)
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

@exception_handler
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
            inp = input("\n\n\x1B[1mcommand \x1B[0m(h for help): ").lower()
            # inp = "d"
            print()
            match inp.split():
                case ["h"] | ["help"]:
                    display_help()
                case ["s", pos, string] | ["save", pos, string]:
                    save_to_memory(pos, string)
                case ["s"] | ["save"]:
                    save_to_memory()
                case ["f", pos] | ["free", pos]:
                    free_memory(pos)
                case ["f"] | ["free"]:
                    free_memory()
                case ["r", pos] | ["read", pos]:
                    read_memory(pos)
                case ["r"] | ["read"]:
                    read_memory()
                case ["z"] | ["result"]:
                    result()
                case ["m"] | ["map"]:
                    display_memory()
                case ["c"] | ["status"]:
                    status_op()
                case ["p"] | ["pause"]:
                    pause_op()
                case ["o"] | ["resume"]:
                    resume_op()
                case ["t"] | ["restart"]:
                    restart_op()
                case ["a"] | ["abort"]:
                    abort_op()
                case ["l"] | ["log"]:
                    change_log_level()
                case ["q"] | ["quit"]:
                    exit()
                    break
                case ["w", id, goal] | ["walk", id, goal]:
                    walk(id, goal)
                case ["w"] | ["walk"]:
                    walk()
                case ["e"] | ["edge"]:
                    edge()
                case _:
                    print("Invalid choice. Please enter a valid command")
                    display_help()
    except KeyboardInterrupt:
        exit()

if __name__ == "__main__":
    main()