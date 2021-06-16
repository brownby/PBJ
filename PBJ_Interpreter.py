#!/usr/bin/env python3

import sys
import serial

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

        if instr not in self.allowable_instructions:
            raise ValueError("not a valid instruction")
        else:
            self.instr = instr

        if type(delay) is not int:
            raise TypeError("delay must be int")
        else:
            self.delay = delay

    def __str__(self):
        return str([self.write_address, self.pattern, self.instr, self.delay])

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

    def write_Arduino(self, file_name):
        """
        Writes contents of instr_array to a .txt file that can be copied and pasted into an Arduino setup() function to write to a PBJ
        """
        pass
    
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

    print("first print, should be empty")
    inter.print_instr_array()

    inter.read_line("0 0x3 continue 99")

    print("\nsecond print, should have one instruction")
    inter.print_instr_array()

    inter.read_line("1 0x5 continue 30")

    print("\nthird print, should have two instructions")
    inter.print_instr_array()

if __name__ == "__main__":
    main()