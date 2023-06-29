##########################################################
#   Helper functions for preparing EVM trace analysis    # 
##########################################################
import json
import os
import re
from macros import *
from symexec import SVT

'''
Generate the auxiliary files using solc: storage layout, function debug runtime, ABI, and AST
'''
def gen_solc():
    os.system('solc --storage-layout --pretty-json ' + MACROS.SOLIDITY_FNAME + ' > '+ MACROS.STORAGE)
    os.system('solc --combined-json function-debug-runtime --pretty-json ' + MACROS.SOLIDITY_FNAME + ' > ' + MACROS.RUNTIME)
    os.system('solc --abi --pretty-json ' + MACROS.SOLIDITY_FNAME + ' > ' + MACROS.ABI)
    os.system('solc --pretty-json --combined-json ast ' + MACROS.SOLIDITY_FNAME + ' > ' + MACROS.AST)

'''
generate the inital stack dictionary {<contract_name> : <contract_stack>}
    Note that "FourByteSelector" is at the BOTTOM of the stack     
'''
def gen_init_STACK():
    STACKS = {}
    stack = [
        SVT("FourByteSelector"),      # It would be good to fill in the actual value into this placeholder
        SVT("AConstantBySolc"), 
    ]
    file = open(MACROS.ABI, 'r')
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
            line = line.replace(MACROS.SOLIDITY_FNAME+":", '')
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
    file = open(MACROS.CONTRACT_NAME+".json", 'r')
    json_object = json.load(file)
    for o in json_object:
        if "name" in o and o["name"] == MACROS.FUNCTION_NAME:
            for i in o["inputs"]:
                stack.append(SVT(i["name"]))
    file.close()
    for n in file_names:
        os.remove(n)
    
    STACKS[MACROS.CONTRACT_NAME] = stack
    return STACKS

'''
generate initial memory dictionary {<contract_name> : <contract_memory>}
'''
def gen_init_MEMORY():
    MEMORIES = {}
    init_MEM = {
        # We need to understand why this 0x40 is needed. Perhaps need to read more thoroughly the yellow paper, 
        # or ask other people
        0x40: SVT(0x80),
        # Dummy mem item
        0x10000000000: SVT(0)
    }
    MEMORIES[MACROS.CONTRACT_NAME] = init_MEM
    return MEMORIES


'''
generate initial storage dictionary
'''
def gen_init_STORAGE():
    return {
        0: '0x00'
    } 

'''
generate initial callstack array
'''
def gen_init_CALL_STACK():
    CALL_STACK = []
    init_CALL = (MACROS.CONTRACT_NAME, MACROS.FUNCTION_NAME)
    CALL_STACK.append(init_CALL)
    return CALL_STACK

'''
generate the concrete path with (PC, oprator, oprand) format from TRACE_ESSENTIAL 
'''
def gen_path():
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



