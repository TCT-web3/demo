# Convert trace file
After getting the json trace file, parse into txt with python program.
```shell
python3 convert_trace.py <trace json>
```
The resulting output file will be ```output.txt``` which can then be inputted into the symexec.py file under ```<trace file>```.
# symexec.py file
## Running the Python file
```shell
python3 symexec.py <solidity file> <theorem file> <trace file>
```
