# Logic Simulator 

## Summary

This logic simulator allows combinatorial and clocked logic circuits to be simulated before hardware implementation.

### Launching the Simulator

To launch the simulator, run the following command in the command line:

```
<path>logsim.py <definition_filepath>
```

This will read a text file definition initializing the logic elements, connections, generators, and monitor points. The user can then execute the network in the GUI, choosing different methods of visualization, running, or language.

Alternatively, the program can also be run in a command line interface using the `-c` flag: 
```
<path>logsim.py -c <definition_filepath>
```

### Available Devices for Simulation

- **CLOCK**
  - Outputs: 1
  - Inputs: 0
  - Function: Output changes state every `n` simulation cycles, where `n` is specified in the definition file.

- **SWITCH**
  - Outputs: 1
  - Inputs: 0
  - Function: Output is either 1 or 0. Initial value is specified in the definition file but can be changed by a user command during the simulation.

- **AND / NAND / OR / NOR**
  - Outputs: 1
  - Inputs: 1–16
  - Input Names: I1, I2, I3, etc.
  - Function: Logic gates with the usual boolean functions.

- **DTYPE**
  - Outputs: 2
  - Inputs: 4
  - Input Names: DATA, CLK, SET, CLEAR
  - Output Names: Q, QBAR
  - Function: QBAR is always the inverse of Q. Logic 1 on the SET input forces Q high, logic 1 on the CLEAR input forces Q low. Otherwise, input to DATA is transferred to Q on the rising edge of the CLK input.

- **XOR**
  - Outputs: 1
  - Inputs: 2
  - Input Names: I1, I2
  - Function: Output is high when I1 is high or I2 is high, but not both.

- **RC**
  - Outputs: 1
  - Inputs: 0
  - Function: On power-up, output starts high but falls low after `n` simulation cycles, where `n` is specified in the definition file.

## Definition File Syntax

Definition files must be specified according to the following EBNF syntax:

```ebnf
spec_file = definition, connection, monitor, end;

definition = "DEFINE", [def_list], ";";

def_list = name, "AS", (device | gate), ["WITH", set_param], 
           {",", name, "AS", (device | gate), ["WITH", set_param]};

set_param = param, "=", value;

param = "inputs" | "initial" | "cycle_rep" | "rc_cycles";

value = digit, [{digit}];

connection = "CONNECT", [con_list], ";";

con_list = input_con, "=", output_con, {",", input_con, "=", output_con};

name = letter, {letter | digit};

input_con = name, ".", input_notation;

output_con = name, [".", output_notation];

input_notation = "I", digit, {digit} | "DATA" | "CLK" | "CLEAR" | "SET";

output_notation = "Q" | "QBAR";

monitor = "MONITOR", [output_con, {",", output_con}], ";";

end = "END", ";";

letter = "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" |
         "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" |
         "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" |
         "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z";

digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";

device = "CLOCK" | "SWITCH" | "DTYPE" | "RC";

gate = "NAND" | "AND" | "OR" | "NOR" | "XOR";
```
