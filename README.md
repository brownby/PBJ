# PBJ

PBJ is a programmable pulse generator designed by Jim MacArthur at the Harvard Univeristy Electronic Instrumentation Design Lab. At the core of PBJ is an FPGA programmed 
as a specialized processor running at 100MHz. This FPGA can be re-programmed via an intermediary microcontroller (a SAMD21) programmed in Arduino. This repository contains
two useful Python scripts for PBJ users:

1. PBJ_interpreter.py - A script to interpret PBJ assembly files and either export them to copy-and-paste ready Arduino code, or program a PBJ directly over USB
2. PBJ_GUI.py - A GUI to more visually create PBJ programs and upload them to a PBJ (COMING SOON, I will be keeping the `gui` branch updated with progress)

Both of these tools should be used with Python 3 :) 

## `.pbj` files

The interpreter accepts `.pbj` files, which are PBJ assembly files. A line of PBJ assembly looks like:

```
<address> <pattern> <command> <delay>
```
Where the `pattern` is either in hexadecimal OR comma separated list of outputs to be HIGH, and there is any amount of white space between the above parameters, e.g:

```
0 0x3 continue 99
```
or, equivalently:
```
0 out1,out2 continue 99
```
(You can mix and match lines that use hex and lines that are a list of outputs in the same `.pbj` file. If you want no outputs to be HIGH, put "0" or "0x0" in for the `pattern`).

The `address` should be a number between 0 and 1023. The `pattern` should be a 24-bit number (i.e. at most 0xffffff) [**NOTE:** some PBJs only have 8-bit outputs, not 24]

The possible commands are:

```
continue
start_loop
end_loop
call_sub
ret_sub
jump_if
wait_for
```

Some of the above commands require arguments, such as conditions or addresses to jump to. If this is the case, these argument(s) should be appended to the `command` with
commas between them ***but no spaces***. For example, the `start_loop` command requires a `loop_counter` argument that instructs PBJ how many times to repeat the loop:

<pre>
1 0x0 <b>start_loop,9</b> 10
</pre>

For more details on what these commands do and what arguments they take, check the "PBJ Commands" section at the end of this README.

**Important notes on delays:** the `delay` introduces an integer number of "wait states", each of which is one clock cycle (or 10 ns), before going to the next instruction. 
Because of the pipelining of the processor, **any non-`continue` command *and the command before it* should have at least two wait states**. 
In practice, make sure that `delay` is always at least 2. If you require 0 wait states, this is allowable for `continue` commands, but with a small quirk. 
Instead of just being one number, the delay parameter should be two numbers separated by a comma. The first number will be 0, indicating a 0 wait state, and 
the next number should be the **delay for the next instruction**. For example:
```
0 0x3 continue 0,10
1 0x4 continue 10
```

**Some other important things to be aware of while writing `.pbj` code:** 
1. Jumping out of loops is forbidden and will result in an error state.
2. Jumping out of subroutines, while technically allowed, is inadvisable. If you need to leave a subroutine, we suggest you use the `ret_sub` command.
3. Loops and subroutines **combined** can be nested up to 16 deep.

## Using the interpreter

PBJ_interpreter.py can be used as a Python module in another script or can be called from the command line. The usage for the latter is:

```
python PBJ_interpreter.py -i <input_file> -o <output_file> -p <serial_port>
```

`input_file` = The `.pbj` file to be interpreted

`output_file` = The file name to write the resulting Arduino code to. This code should then be copied and pasted into the `setup()` function of an Arduino sketch.

`serial_port` = The serial port on which the PBJ appears. Will be different depending on OS. 

You can simultaneously write to a file and write to the serial port if you wish, or you can only do one by omitting the `-p` or `-o` flag. 

To use the interpreter within another Python script, first make sure `PBJ_interpreter.py` is in the same directory as your script, then import it:

```python
from PBJ_interpreter import PBJ_interpreter
```

Create a `PBJ_interpreter` object, then use the `read_file` method to read a `.pbj` file. To write to an Arduino file, use the `write_Arduino` method, and to write over
serial use the `write_serial` method. 

```python
# Create a PBJ_interpreter object
pbj = PBJ_interpreter() 

# Read example.pbj
pbj.read_file("example.pbj") 

# Write Arduino code to example_arduino.txt
pbj.write_Arduino("example_arduino.txt")

# Update PBJ directly over serial, on serial port COM4
pbj.write_serial("COM4")
```
## Using the GUI

Coming soon :)

## PBJ Commands

### `continue`

**What it does:** Go to the next instruction

**Arguments:** 

none

### `start_loop`

 **What it does:** Demarcates the beginnning of a loop
 
 **Arguments:** 
 
 `loop_counter` = the number of times to repeat the loop (minus 1, e.g. to repeat a loop 10 times set `loop_counter` to 9).
 
 ### `end_loop`
 
 **What it does:** Demarcates the end of a loop
 
 **Arguments:** 
 
 none
 
 ### `call_sub`
 
 **What it does:** Calls a subroutine (i.e. moves you to a location in memory where a subroutine is stored). Every subroutine should have a `ret_sub` at the end of it,
 which will return you to wherever in memory the subroutine was called from. 
 
 **Arugments:**
 
 `subroutine_address` = the address in memory of the subroutine to be called
 
 ### `ret_sub`
 
 **What it does:** Returns from a subroutine. Every subroutine should have a `ret_sub` command at the end.
 
 **Arguments:**
 
 none
 
 ### `jump_if`
 
 **What it does:** Jumps to another instruction, depending on a condition.
 
 **Arguments:**
 
 `condition` = the condition that will cause a jump (see below for possible conditions)
 
 `jump_address` = address of the instruction to jump to
 
 ***NOTE:*** the arguments for `jump_if` should always be in the order `jump_if,<condition>,<jump_address>`.
 
 ### `wait_for`
 
 **What it does:** Waits to continue to the next instruction until a condition is met
 
 **Arguments:**
 
 `condition` = the condition to be met before continuing to the next instruction (see below for possible conditions)
 
 ### Possible conditions for `jump_if` and `wait_for`
 
 These are relatively self-explanatory. `In1-4` indicates the 4 digital inputs to the PBJ, `WE` indicates the write enable pin of the FPGA, and `MOSI` the MOSI SPI pin of
 the FPGA. The latter is simple to toggle from the SAMD21 and is always connected to the FPGA, so it can be useful for testing programs that you write.
 
 ```
 now
 never
 in1_low
 in1_high
 in2_low
 in2_high
 in3_low
 in3_high
 in4_low
 in4_high
 we_low
 we_high
 mosi_low
 mosi_high
 ```
 
