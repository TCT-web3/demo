import json
import os
import re
from macros import *
from symexec import SVT

'''
Generate the auxiliary files using solc
    - storage layout
    - function debug runtime
    - ABI
    - AST
'''
def gen_solc():
    os.system('solc --storage-layout --pretty-json ' + MACROS.SOLIDITY_FNAME + ' > '+ MACROS.STORAGE)
    os.system('solc --combined-json function-debug-runtime --pretty-json ' + MACROS.SOLIDITY_FNAME + ' > ' + MACROS.RUNTIME)
    os.system('solc --abi --pretty-json ' + MACROS.SOLIDITY_FNAME + ' > ' + MACROS.ABI)
    os.system('solc --pretty-json --combined-json ast ' + MACROS.SOLIDITY_FNAME + ' > ' + MACROS.AST)

'''
Set the inital stack of the initial Callee and add to the stack list of EVM 
Note that "FourByteSelector" is at the BOTTOM of the stack     
'''
def set_stack(abi, solidity_fname, contract_name, function_name):
    stack = [
        SVT("FourByteSelector"),      # It would be good to fill in the actual value into this placeholder
        SVT("AConstantBySolc"), 
    ]

    file = open(abi, 'r')
    file.readline()
    file_names = []
    new_file = None
    for line in file:
        if line.startswith("======"):
            # get name of contract
            if new_file:
                new_file.close()
            line = line.rstrip("\n")
            line = line.strip("======")
            line = line.replace(solidity_fname+":", '')
            line = line.strip()
            new_name = line+".json"
            new_file = open(new_name, 'w')
            file_names.append(new_name)
        elif line.startswith("Contract"):
            continue
        elif line != " ":
            new_file.write(line)
            # print(line)
    new_file.close()
    file.close()

    # get the map
    file = open(contract_name+".json", 'r')
    json_object = json.load(file)
    
    for o in json_object:
        if "name" in o and o["name"] == function_name:
            for i in o["inputs"]:
                stack.append(SVT(i["name"]))
    file.close()
    for n in file_names:
        os.remove(n)
    
    return stack

def set_init_storage():
    return {
        0: '0x00'
    } 

def set_memory():
    return {
        # We need to understand why this 0x40 is needed. Perhaps need to read more thoroughly the yellow paper, 
        # or ask other people
        0x40: SVT(0x80),
        # Dummy mem item
        0x10000000000: SVT(0)
    }

'''
Build the concrete path with (PC, oprator, oprand) format from the essentai trace 
'''
def build_path():
    trace=[]
    inputfile = open(MACROS.ESSENTIAL, 'r')
    while True:
        line = inputfile.readline()
        if not line:
            break
        if(line[0].isdigit()):    
            necessary = re.search("([0-9]+)\s(.*)-", line)
            necessary = necessary[0][:-2]
            instr = necessary.split(" ")
            PC=int(instr[0])
            operator=instr[1]
            if(len(instr)>2):
                operand=int('0x'+ instr[2], 16)
            else:  
                operand = None
            trace_node = (PC, operator, operand) 
            trace.append(trace_node)
        elif(">>" in line or "<<" in line):
            trace.append(line)     
    inputfile.close()
    return trace

def gen_init_STACK():
    STACKS = {}
    init_STACK = set_stack(MACROS.ABI, MACROS.SOLIDITY_FNAME, MACROS.CONTRACT_NAME, MACROS.FUNCTION_NAME)
    STACKS[MACROS.CONTRACT_NAME] = init_STACK
    return STACKS

def gen_init_MEMORY():
    MEMORIES = {}
    init_MEM = set_memory()
    MEMORIES[MACROS.CONTRACT_NAME] = init_MEM
    return MEMORIES

def gen_init_CALL_STACK():
    CALL_STACK = []
    init_CALL = (MACROS.CONTRACT_NAME, MACROS.FUNCTION_NAME)
    CALL_STACK.append(init_CALL)
    return CALL_STACK