###############################
#  Other utility functions    # 
###############################
import re
import os
import json
from macros import *

# TODO: we need the maps for all contracts.
def get_MAP(storage, solidity_name, contract_name):
    file = open(storage, 'r')
    new_file = None
    file.readline()
    file_names = []
    for line in file:
        if line.startswith("======"):
            # get name of contract
            if new_file:
                new_file.close()
            line = line.rstrip("\n")
            line = line.strip("======")
            line = line.replace(solidity_name+":", '')
            line = line.strip()
            new_name = line+".json"
            new_file = open(new_name, 'w')
            file_names.append(new_name)
        elif line.startswith("Contract Storage Layout:"):
            continue
        elif line != " ":
            new_file.write(line)
            
    new_file.close()
    file.close()
    # get the map
    file = open(contract_name+".json", 'r')
    json_object = json.load(file)["storage"]
    mapIDs = {}
    
    for o in json_object:
        mapIDs[o["slot"]] = o["label"]
    file.close()
    for n in file_names:
        os.remove(n)
    return mapIDs

# a function to get a list of JSON from a text file  
def get_MAP():
    file = open(MACROS.STORAGE, 'r')
    new_file = None
    file.readline()
    file_names = []
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
        elif line.startswith("Contract Storage Layout:"):
            continue
        elif line != " ":
            new_file.write(line)
            
    new_file.close()
    file.close()
    # get the map
    file = open(MACROS.CONTRACT_NAME+".json", 'r')
    json_object = json.load(file)["storage"]
    mapIDs = {}
    
    for o in json_object:
        mapIDs[o["slot"]] = o["label"]
    file.close()
    for n in file_names:
        os.remove(n)
    return mapIDs



def find_essential_start():
    RUNTIME_file = open(MACROS.RUNTIME, )
    RUNTIME_BYTE = json.load(RUNTIME_file)
    essential_start=0
    function_list = (RUNTIME_BYTE["contracts"][MACROS.SOLIDITY_FNAME+":"+MACROS.CONTRACT_NAME]["function-debug-runtime"])
    for func in function_list:
        if (MACROS.FUNCTION_NAME in func):
            essential_start = (function_list[func]["entryPoint"])
            break 
    if (essential_start==0):
        raise Exception("error, cannot find function entrypoint")
    return essential_start

def gen_trace_essential():
    # TODO: use regex to accomodate digits with fix width or not
    TRACE_file = open(MACROS.TRACE_FNAME, "r")
    TRACE_essential = open(MACROS.ESSENTIAL, "w")
    essential_start = find_essential_start()
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
                essential_start = find_essential_start()
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
                # raise Exception("input trace should include at least one pre instruction of the essential part")
                if essential_end == 9999:
                    essential_end = PRE_start+1
                TRACE_essential.write(lines[i]+"\n")
                start = True
            else:
                PRE_start = int(lines[i][0:4])

def get_FUNCTIONINFO(runtime, solidity_fname):
    RUNTIME_file = open(runtime, )
    RUNTIME_BYTE = json.load(RUNTIME_file)
    contracts_info = {}
    for contract in RUNTIME_BYTE["contracts"].keys():
        c_name = contract.replace(solidity_fname+":", "")
        contracts_info[c_name] = {}
        for function in RUNTIME_BYTE["contracts"][contract]["function-debug-runtime"].keys():
            if '@' in function:
                function_info = {}
                f_name = function[1:function.rfind('_')]
                function_info = RUNTIME_BYTE["contracts"][contract]["function-debug-runtime"][function]
                contracts_info[c_name][f_name] = (function_info)
    # print(contracts_info)
    return contracts_info

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
    # print(tmp)
    # INFO = ""
    return INFO   

# invariant dictionary
def map_invariant(ast_fname, sol_fname):
    ast_file = open(ast_fname, 'r')
    json_file = json.load(ast_file)
    nodes = json_file["sources"][sol_fname]["AST"]["nodes"]
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

def check_entrypoint(trace):
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(THEOREM_file)
    # check theorem against trace
    trace = open(trace, 'r')
    line = ""
    while not line.startswith(">>enter"):
        line = trace.readline()
    trace_i1, trace_i2 = line.find("(")+1, line.find(")")
    m1 = line[trace_i1:trace_i2+1]

    m2 = theorem["entry-for-test"]

    if m1 != m2:
        raise Exception("entry point wrong")
    
def get_contract_and_function_names():
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    THEOREM = json.load(THEOREM_file)
    CONTRACT_NAME = (re.search("(.*)::", THEOREM['entry-for-test']))[0][:-2]    
    FUNCTION_NAME = (re.search("::(.*)\(", THEOREM['entry-for-test']))[0][2:-1]
    return CONTRACT_NAME, FUNCTION_NAME

def get_dest_contraction_and_function(instr):
    info = re.search("\((.*)\)", instr)[0]
    info = info.split("::")
    dest_contract = (info[0][1:])
    dest_function = (info[1][:-1])
    return dest_contract, dest_function

def get_hypothesis():
    theorem_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(theorem_file)
    return theorem["hypothesis"]


def write_storages(storage_info):
    rt = ""
    for elmt in storage_info[MACROS.CONTRACT_NAME]["storage"]:
        label = (elmt["label"])
        t_type = elmt["type"]
        if ("string" in t_type):
            pass
        elif "t_mapping" in t_type:
            t_type = t_type.replace("t_", "")
            t_type = t_type.replace("mapping", "")[1:-1]
            t_type = t_type.split(',')
            # self._output_file.write("\tvar " + label + ':['+t_type[0]+'] ' + t_type[1] + ';\n')
            rt = rt + ("\tvar " + label + ':['+t_type[0]+'] ' + t_type[1] + ';\n')
        else:
            # self._output_file.write("\tvar " + label + ":\t" + t_type[2:] + ";\n")
            rt = rt + ("\tvar " + label + ":\t" + t_type[2:] + ";\n")
    return rt

def write_hypothesis(hypothesis):
        return("\tassume(" + hypothesis + ");\n")

def write_invariants(invariants):
    # get from ast
    rt = ""
    MVT_invariants = invariants[MACROS.CONTRACT_NAME]
    for inv in MVT_invariants:
        rt = rt + ("\tassume(" + inv + ");\n")
        # self._output_file.write("\tassume(" + inv + ");\n")
    rt = rt + ("\n")
    return rt 

def write_epilogue(invariants):
    rt = ""
    MVT_invariants = invariants["MultiVulnToken"]
    for inv in MVT_invariants:
        rt = rt + ("\tassert(" + inv + ");\n")
        # self._output_file.write("\tassert(" + inv + ");\n")
    # self._output_file.write('}')
    rt = rt + ('}')
    return rt

