###############################
#  Other utility functions    # 
###############################
import re
import os
import json
from macros     import *

'''
get a list of JSON from a text file  
'''
# TODO: we need the maps for all contracts.
# def get_MAP():
#     file = open(MACROS.STORAGE, 'r')
#     new_file = None
#     file.readline()
#     file_names = []
#     for line in file:
#         if line.startswith("======"):
#             # get name of contract
#             if new_file:
#                 new_file.close()
#             line = line.rstrip("\n")
#             line = line.strip("======")
#             line = line.replace(MACROS.SOLIDITY_FNAME+":", '')
#             line = line.strip()
#             new_name = line+".json"
#             new_file = open(new_name, 'w')
#             file_names.append(new_name)
#         elif line.startswith("Contract Storage Layout:"):
#             continue
#         elif line != " ":
#             new_file.write(line)
#     new_file.close()
#     file.close()
#     # get the map
#     file = open(MACROS.CONTRACT_NAME+".json", 'r')
#     json_object = json.load(file)["storage"]
#     mapIDs = {}
    
#     for o in json_object:
#         mapIDs[o["slot"]] = o["label"]
#     file.close()
#     for n in file_names:
#         os.remove(n)
#     print(mapIDs)
#     return mapIDs


# TODO: Tzu-Han finish this part 
def get_MAPS(storage_info):
    MAPS = {}
    for contract in storage_info.keys():
        MapIDs = {}
        for elmt in storage_info[contract]["storage"]:
            slot =  elmt["slot"]
            label = elmt["label"]          
            MapIDs[slot] = label  
        MAPS[contract] = MapIDs
        print(contract)
        print(MapIDs)
    return MAPS

'''
find where the essential part starts in a contract call
'''
def find_essential_start(contract_name, function_name):
    RUNTIME_file = open(MACROS.RUNTIME, )
    RUNTIME_BYTE = json.load(RUNTIME_file)
    essential_start=0
    function_list = (RUNTIME_BYTE["contracts"][MACROS.SOLIDITY_FNAME+":"+contract_name]["function-debug-runtime"])
    for func in function_list:
        if (function_name in func):
            essential_start = (function_list[func]["entryPoint"])
            break 
    if (essential_start==0):
        raise Exception("error, cannot find function entrypoint")
    return essential_start

'''
output the essential part of a trace to file TRACE_ESSENTIAL
'''
def gen_trace_essential():
    # TODO: use regex to accomodate digits with fix width or not
    TRACE_file = open(MACROS.TRACE_FNAME, "r")
    TRACE_essential = open(MACROS.ESSENTIAL, "w")
    essential_start = find_essential_start(MACROS.CONTRACT_NAME, MACROS.FUNCTION_NAME)
    lines = [line.rstrip() for line in TRACE_file]
    essential_end = 9999
    start = False
    PRE_start = 0
    for i in range(0, len(lines)-1):
        if lines[i].startswith(">>"):
            matches = re.search(r"\(([^:]+)::([^()]+)\(.*?\)\)", lines[i])
            contract_name = matches.group(1)
            function_name = matches.group(2)
            # print("Class name:", contract_name)
            # print("Function signature:", function_name)
            if not lines[i-1].startswith("==="):
                TRACE_essential.write(lines[i] + '\n')
                essential_start = find_essential_start(contract_name, function_name)
                start = False
        elif lines[i].startswith("<<leave"):
            TRACE_essential.write(lines[i] + '\n')
        elif not lines[i][0:1].isnumeric():
            continue
        else:
            if lines[i][0:1].isnumeric() and int(lines[i][0:4]) == essential_end:
                break
            if start and lines[i][0:1].isnumeric():
                TRACE_essential.write(lines[i]+'\n')
            if (int(lines[i][0:4]) == int(essential_start)):
                if essential_end == 9999:
                    essential_end = PRE_start+1
                TRACE_essential.write(lines[i]+"\n")
                start = True
            else:
                PRE_start = int(lines[i][0:4])

'''
get ABI information as a JSON
'''
def get_ABI_info():
    ABI_file = open(MACROS.ABI, "r")
    tmp = ""
    lines = ABI_file.readlines()
    for line in lines:
        # print("l" + line)
        if line[0] == '{':
            continue
        elif len(line.strip()) == 0:
            # print("},")
            line = ",\n"
        elif '===' in line:
            c_name = line.replace("======= ", "").replace(" =======", "").replace(MACROS.SOLIDITY_FNAME+":", "").replace("\n", "")
            line = "\"" + c_name + "\"" +":\n"
            # print(c_name)
        elif 'JSON ABI' in line:
            continue    
        tmp = tmp + line
        # print(line)
    tmp = tmp + '}'
    tmp = '{' + tmp[1:] #patch
    # print(tmp)
    INFO = json.loads(tmp)
    return INFO

'''
get storage information as a python
'''
def get_STORAGE_info():
    STORAGE_file = open(MACROS.STORAGE, "r")
    tmp = '{'
    lines = STORAGE_file.readlines()
    for line in lines:
        # print("l" + line)
        if len(line.strip()) == 0:
            # print("},")
            line = ",\n"    
        elif '===' in line:
            c_name = line.replace("======= ", "").replace(" =======", "").replace(MACROS.SOLIDITY_FNAME+":", "").replace("\n", "")
            line = "\"" + c_name + "\"" +":\n"
            # print(c_name)
        elif 'Contract Storage' in line:
            continue    
        tmp = tmp + line
    tmp = tmp + '}'
    tmp = '{' + tmp[2:] #patch
    INFO = json.loads(tmp)
    return INFO   

'''
get proof invariant from AST file
'''
def get_invariant():
    ast_file = open(MACROS.AST, 'r')
    json_file = json.load(ast_file)
    nodes = json_file["sources"][MACROS.SOLIDITY_FNAME]["AST"]["nodes"]
    # Sources->AST->nodes->[contracts: token, standard token, multivulntoken, reentrancy attack, demo]
    invariants = {}
    for node in nodes:
        if node["nodeType"] == "ContractDefinition":
            if node["name"] not in invariants:
                invariants[node["name"]] = []
            if "documentation" in node:
                if "text" in node["documentation"]:
                    inv_list = node["documentation"]["text"].split("\n")
                    for i in range(len(inv_list)):
                        inv_list[i] = inv_list[i].replace("@custom:tct invariant: ", "")
                    invariants[node["name"]] = inv_list
                    
            if "baseContracts" in node:
                for b in node["baseContracts"]:
                    invariants[node["name"]] += invariants[b["baseName"]["name"]]
    
    return invariants

'''
get proof hypothesis from the the theorem file
'''
def get_hypothesis():
    theorem_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(theorem_file)
    return theorem["hypothesis"]

'''
check if given trace has correct starting entry point
'''
def check_entrypoint():
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(THEOREM_file)
    # check theorem against trace
    trace = open(MACROS.TRACE_FNAME, 'r')
    line = ""
    while not line.startswith(">>enter"):
        line = trace.readline()
    trace_i1, trace_i2 = line.find("(")+1, line.find(")")
    m1 = line[trace_i1:trace_i2+1]
    m2 = theorem["entry-for-test"]
    if m1 != m2:
        raise Exception("entry point wrong")
    
'''
get the beginning contraction and function names 
'''    
def get_contract_and_function_names():
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    THEOREM = json.load(THEOREM_file)
    CONTRACT_NAME = (re.search("(.*)::", THEOREM['entry-for-test']))[0][:-2]    
    FUNCTION_NAME = (re.search("::(.*)\(", THEOREM['entry-for-test']))[0][2:-1]
    return CONTRACT_NAME, FUNCTION_NAME

'''
get the contract and function name when a CALL happens
'''
def get_dest_contract_and_function(instr):
    info = re.search("\((.*)\)", instr)[0]
    info = info.split("::")
    dest_contract = (info[0][1:])
    dest_function = (info[1][:-1])
    return dest_contract, dest_function

def write_params(abi_info):
    rt = ""
    for elmt in abi_info[MACROS.CONTRACT_NAME]:
        if ("name" in elmt.keys() and elmt["name"] == MACROS.FUNCTION_NAME):
            for input in elmt["inputs"]:
                # print('?', input["name"], input["type"])
                rt = rt + "\tvar " + MACROS.CONTRACT_NAME+'.'+input["name"] + ":\t" + input["type"]+';\n'
                # self._output_file.write("\tvar " + self._curr_contract+'.'+input["name"] + ":\t" + input["type"]+';\n')
    return rt + '\n'
            

'''
write local variables from storage file to Boogie
'''
def write_locals(storage_info):
    locals = []
    rt = ""
    for contract in storage_info.keys():
        for elmt in storage_info[contract]["storage"]:
            label =  elmt["label"]
            t_type = elmt["type"]
            
            if (label in locals):
                pass
            else:
                if ("string" in t_type):
                    pass
                elif ("contract" in t_type):
                    pass # TODO: contract address as a type
                elif "t_mapping" in t_type:
                    t_type = t_type.replace("t_", "")
                    t_type = t_type.replace("mapping", "")[1:-1]
                    t_type = t_type.split(',')
                    rt = rt + ("\tvar " + contract+'.'+label + ':['+t_type[0]+'] ' + t_type[1] + ';\n')
                else:
                    rt = rt + ("\tvar " + contract+'.'+label + ":\t" + t_type[2:] + ";\n")  
                locals.append(contract+'.'+label)
    
    return rt + '\n'

'''
write hypothesis to Boogie
'''
def write_hypothesis(hypothesis):
        return("\tassume(" + hypothesis + ");\n")

'''
write invariant to Boogie
'''
def write_invariants(invariants):
    # get from ast
    rt = ""
    MVT_invariants = invariants[MACROS.CONTRACT_NAME]
    for inv in MVT_invariants:
        rt = rt + ("\tassume(" + inv + ");\n")
    rt = rt + ("\n")
    return rt 

'''
write epilogue to Boogie
'''
def write_epilogue(invariants):
    rt = ""
    MVT_invariants = invariants["MultiVulnToken"]
    for inv in MVT_invariants:
        rt = rt + ("\tassert(" + inv + ");\n")
        # self._output_file.write("\tassert(" + inv + ");\n")
    # self._output_file.write('}')
    rt = rt + ('}')
    return rt
