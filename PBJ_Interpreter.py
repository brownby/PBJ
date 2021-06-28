#!/usr/bin/env python3

import sys, getopt
import serial
from datetime import datetime

class PBJ_instruction:
    allowable_instructions = ["continue", "start_loop", "end_loop", "call_sub", "ret_sub", "jump_if", "wait_for"]

    def __init__(self, write_address, pattern, instr, delay):
        if type(write_address) is not int:
            raise TypeError("write_address must be int")
        elif write_address > 1023:
            raise ValueError("write_address must be between 0 and 1023")
        else:
            self.write_address = write_address

        hex_pattern = int(pattern, base=16)
        if hex_pattern > ((1 << 24) - 1) or hex_pattern < 0:
            raise ValueError("pattern must be at most 24-bit")
        else:
            self.pattern = pattern

        # NEED TO FIGURE OUT HOW TO HANDLE JUMP_IF AND WAIT_FOR
        # if instr not in self.allowable_instructions:
        #     raise ValueError("not a valid instruction")
        # else:
        self.instr = instr

        delay = delay.split(',')

        if len(delay) == 1:
            if int(delay[0]) < 2:
                if instr != "continue":
                    raise Exception("Can only have zero wait states with \"continue\" instruction")
                else:
                    raise Exception("To implement zero wait states, you must add a comma after the 0 then the delay for the next instruciton\nFor example:\n4   0x0     continue            0,30")
            self.delay = int(delay[0])
            self.zero_delay_flag = False
        else:
            if instr != "continue":
                raise Exception("Can only have zero wait states with \"continue\" instruction")
            self.zero_delay_flag = True
            self.delay = int(delay[1])

    def __str__(self):
        return str([self.write_address, self.pattern, self.instr, self.delay, self.zero_delay_flag])

    def to_arduino(self):
        arduino_line = "WriteSequencer("
        arduino_line += str(self.write_address) + ", "
        
        hex_pattern = int(self.pattern, base=16)
        out_str = ""
        # Loop through 24 bits of pattern, add "OUTx |" to the out_str
        for i in range(0, 24):
            if(hex_pattern & (1 << i) != 0):
                out_str += "OUT" + str(i+1) + " | "
        
        # If out_str is still empty, set pattern to zero
        if out_str == "":
            out_str = "0"
        # Otherwise, remove last " |"
        else:
            out_str = out_str[:len(out_str)-3]

        arduino_line += out_str + ", "

        # For checking JUMPIF and WAITFOR conditions
        instr_str = ""
        instr_str_array = self.instr.split(',')
        if (instr_str_array[0] == "jump_if"):
            instr_str += "JUMPIF | "
            instr_str += instr_str_array[1].upper() + " | " # Condition, all uppercase
            instr_str += '(' + instr_str_array[2] + "<<4)" # Location to jump to 
        elif (instr_str_array[0] == "wait_for"):
            instr_str += "WAITFOR | "
            instr_str += instr_str_array[1].replace('_','').upper() # Condition to wait for
        elif (instr_str_array[0] == "start_loop"):
            instr_str += "STARTLOOP | "
            instr_str += '(' + instr_str_array[1] + "<<4)" # Loop counter
        else:
            # Otherwise just use the instruction in all uppercase (removing underscores)
            instr_str += instr_str_array[0].replace('_','').upper() 

        arduino_line += instr_str + ", "

        arduino_line += str(self.delay) + ");"

        return arduino_line
        



### 
# PBJ interpreter class, which will accept .pbj "assembly" files and convert them to 
# an Arduino file OR send them directly over serial to a PBJ
###
class PBJ_interpreter:
    opcodes = {
        "continue" : 0,
        "start_loop" : 2,
        "end_loop" : 3,
        "call_sub" : 4,
        "ret_sub" : 5,
        "jump_if" : 6, 
        "wait_for" : 8
    }

    conditions = {
        "now" : 0,
        "never" : 0x00010000,
        "in1_low" : 0x00020000,
        "in1_high" : 0x00030000,
        "in2_low" : 0x00040000,
        "in2_high": 0x00050000,
        "in3_low" : 0x00060000,
        "in3_high" : 0x00070000,
        "in4_low" : 0x00080000,
        "in4_high" : 0x00090000,
        "we_low" : 0x000A0000,
        "we_high" : 0x000B0000,
        "mosi_low" : 0x000C0000,
        "mosi_high" : 0x000D0000
    }

    def __init__(self):
        self.instr_array = []
        self.last_instruction_address = 0

    def append_instr(self, instr):
        self.instr_array.append(instr)

    def print_instr_array(self):
        for instr in self.instr_array:
            print(instr)

    def error_check(self):
        subroutines = [] # array of arrays with stop and start address of subroutines
        temp_subr_array = [0,0,0] # index 1 is start address of subroutine, index 2 is end address, and index 3 is return address for ret_sub
        subr_start_flag = False
        subr_ctr = 0

        pc = 0
        cur_instr = []
        # First put together an array of subroutine start and end addresses
        while pc <= self.last_instruction_address:
            for instr in self.instr_array:
                if instr.write_address == pc:
                    cur_instr = instr.instr.split(',')
                    break
            if cur_instr[0] == "call_sub":
                # jump to the subroutine
                subr_start_flag = True
                subr_start_address = int(cur_instr[1])
                temp_subr_array[0] = subr_start_address
                temp_subr_array[2] = instr.write_address
                pc = subr_start_address 
                # print("Subroutine called, going to address", pc)
            elif cur_instr[0] == "ret_sub" and subr_start_flag == True:
                subr_start_flag = False
                subr_end_address = pc
                temp_subr_array[1] = subr_end_address
                subroutines.append(temp_subr_array)
                # Come back from subroutine
                pc = subroutines[subr_ctr][0] + 1
                subr_ctr += 1
                # print("Returning from subroutine")
            else:
                pc += 1
        
        # print(subroutines)

        # Now go through program and check for jumping out of loops and subroutines
        loop_flag = False # set to true if we're in a loop
        subr_flag = False # set to true if we're in a subroutine
        loop_ctr = 0
        pc = 0
        cur_instr = []

        while pc <= self.last_instruction_address:
            for instr in self.instr_array:
                if instr.write_address == pc:
                    cur_instr = instr.instr.split(',')
                    break

            if cur_instr[0] == "start_loop": # Start of a loop, increment loop ctr
                loop_flag = True
                loop_ctr += 1
            elif cur_instr[0] == "end_loop": # End of a loop
                loop_ctr -= 1
                if loop_ctr == 0: # only set back to false if we're outside of all loops
                    loop_flag = False
            elif cur_instr[0] == "jump_if":
                if loop_flag == True:
                    raise Exception("Cannot jump out of loops")
                elif subr_flag == True:
                    print(Warning("Inadvisable to jump out of subroutines. Consider ret_sub if you want to leave the subroutine instead."))
            elif instr.write_address in [subroutine[0] for subroutine in subroutines]: # Check if write address is the start of a subroutine  
                subr_flag = True
            elif instr.write_address in [subroutine[1] for subroutine in subroutines]: # Check if write address is the end of a subroutine (could also check in instruction is ret_sub)
                subr_flag = False
            
            if loop_ctr > 16:
                raise Exception("Loops and subroutines (total) can only be nested 16 deep")
            pc += 1

        # Now make a pass at checking for nesting subroutines
        # TODO:
        #   This will infinitely loop if the subroutine is stored in an address below the call_sub, because it will get down then jump back up
        #   The method below "fixes" this with a sort of clumsy break if the write_address isn't in the .pbj file, but that's not ideal
        # pc = 0
        # cur_instr = []
        # loop_ctr = 0
        # while pc <= self.last_instruction_address:
            
        #     if pc in [i.write_address for i in self.instr_array]:
        #         for instr in self.instr_array:
        #             if instr.write_address == pc:
        #                 cur_instr = instr.instr.split(',')
        #                 break
        #     else:
        #         print("Reached a point in memory with no instructions stored")
        #         break
            
            
        #     if cur_instr[0] == "start_loop":
        #         loop_ctr += 1
        #         pc += 1
        #     elif cur_instr[0] == "end_loop":
        #         loop_ctr -= 1
        #         pc += 1
        #     elif cur_instr[0] == "call_sub":
        #         loop_ctr += 1
        #         pc = int(cur_instr[1]) # jump to subroutine
        #     elif cur_instr[0] == "ret_sub":
        #         loop_ctr -= 1
        #         # Find return address for this subroutine in subroutines list, then jump to following instr
        #         for subroutine in subroutines:
        #             if instr.write_address == subroutine[1]:
        #                 pc = subroutine[2] + 1
        #                 break
        #     else:
        #         pc += 1
        #     print(pc)
        #     if loop_ctr > 16:
        #         raise Exception("Total loops + subroutines can only be nested to 16")


    def write_serial(self, port):
        """
        Sends contents of instr_array over serial as PBJ-readable machine code
        Format for commands over serial:
            PBJ<address>,<pattern>,<command>,<delay>;

            where address, pattern, command, and delay are all decimal numbers
        """
        self.error_check()

        ser = serial.Serial(port)

        ser.open()

        for instr in self.instr_array:
            command_arr = instr.instr.split(',')
            command_int = 0
            if command_arr[0] == "start_loop":
                command_int |= int(command_arr[1]) << 19
            elif command_arr[0] == "call_sub":
                command_int |= int(command_arr[1]) << 13
            elif command_arr[0] == "jump_if" or command_arr[0] == "wait_for":
                command_int |= self.conditions[command_arr[1]]
                if command_arr[0] == "jump_if":
                    command_int |= int(command_arr[2]) << 13
            command_int |= self.opcodes[command_arr[0]]
            command = str(command_int)

            delay = instr.delay
            if instr.zero_delay_flag == True:
                delay |= 0x80000000

            ser.write("PBJ" + str(instr.write_address) + ',' + str(int(instr.pattern, base=16)) + ',' + command + ',' + str(delay) + ";\n")

        ser.close()

    def write_Arduino(self, file_name="default"):
        """
        Writes contents of instr_array to a .txt file that can be copied and pasted into an Arduino setup() function to write to a PBJ
        If no file name is given, writes to pbj_arduino_[date]_[time].txt
        """
        if file_name == "":
            raise ValueError("Empty file name")
        elif type(file_name) is not str:
            raise TypeError("File name is not string")
        elif file_name == "default":
            now = datetime.now()
            dt_string = now.strftime("%m%d%y_%H%M%S")
            file_name = "pbj_arduino_" + dt_string

        self.error_check()

        pbj_arduino_file = open(file_name, 'w')
        arduino_line = ""

        pbj_arduino_file.write("// Copy and paste the following code into your setup() function\n")

        for instr in self.instr_array:
            arduino_line = instr.to_arduino()
            pbj_arduino_file.write(arduino_line + '\n')

        pbj_arduino_file.close()

    
    def read_line(self, line):
        """
        Reads single line of a .pbj file and converts it to an instruction, then adds to the interpreter's instr_array
        """

        # Error checking, may add more later
        if type(line) is not str:
            raise TypeError("Line should be a string")
        elif line == "":
            raise ValueError("Empty string")

        # Parse line into array of strings
        split_line = line.split() # default splits by space, which is fine

        # Convert write_address and delay to ints
        split_line[0] = int(split_line[0])
        if split_line[0] > self.last_instruction_address:
            self.last_instruction_address = int(split_line[0])
        # split_line[3] = int(split_line[3])

        temp_instr = PBJ_instruction(split_line[0], split_line[1], split_line[2], split_line[3])

        self.append_instr(temp_instr)

    def read_file(self, file_name):

        if file_name.split('.')[1] != "pbj":
            raise ValueError("File should be a .pbj")

        pbj_file = open(file_name, 'r')

        for line in pbj_file:
            self.read_line(line)

    
def main(argv):
    input_file = ""
    output_file = ""
    serial_port = ""
    arduino_flag = False
    serial_flag = False
    
    try:
        opts, args = getopt.getopt(argv, "hi:o:p:", ["help", "input_file=", "output_file=", "serial_port="])
    except getopt.GetoptError:
        print("usage:\nPBJ_interpreter.py -i <input_file> -o <output_file>\nor\nPBJ_interpreter.py -i <input_file> -p <serial_port>")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == "-h":
            print("usage:\nPBJ_interpreter.py -i <input_file> -o <output_file>\nor\nPBJ_interpreter.py -i <input_file> -p <serial_port>")
        elif opt in ("-i", "--input_file"):
            input_file = arg
        elif opt in ("-o", "--output_file"):
            output_file = arg
            arduino_flag = True
        elif opt in ("-p", "--serial_port"):
            serial_port = arg
            serial_flag = True

    if input_file == "":
        print("Input file is empty!")
        sys.exit(2)

    inter = PBJ_interpreter()
    inter.read_file(input_file)

    if arduino_flag == True:
            inter.write_Arduino(output_file)

    if serial_flag == True:
        inter.write_serial(serial_port)


if __name__ == "__main__":
    main(sys.argv[1:])