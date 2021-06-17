#!/usr/bin/env python3

import sys
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

        if type(delay) is not int:
            raise TypeError("delay must be int")
        else:
            self.delay = delay

    def __str__(self):
        return str([self.write_address, self.pattern, self.instr, self.delay])

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
    def __init__(self):
        self.instr_array = []

    def append_instr(self, instr):
        self.instr_array.append(instr)

    def print_instr_array(self):
        for instr in self.instr_array:
            print(instr)

    def write_serial(self, port):
        """
        Sends contents of instr_array over serial as PBJ-readable machine code
        """
        pass

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

        pbj_arduino_file = open(file_name, 'w')
        arduino_line = ""

        for instr in self.instr_array:
            arduino_line = instr.to_arduino()
            pbj_arduino_file.write(arduino_line + '\n')

    
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
        split_line[3] = int(split_line[3])

        temp_instr = PBJ_instruction(split_line[0], split_line[1], split_line[2], split_line[3])

        self.append_instr(temp_instr)

    def read_file(self, file_name):

        if file_name.split('.')[1] != "pbj":
            raise ValueError("File should be a .pbj")

        pbj_file = open(file_name, 'r')

        for line in pbj_file:
            self.read_line(line)

    
def main():
    inter = PBJ_interpreter()

    inter.read_file("test.pbj")

    inter.print_instr_array()

    inter.write_Arduino("pbj_test.txt")

if __name__ == "__main__":
    main()