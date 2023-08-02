###############################
#  Other utility functions    # 
###############################
import re
import os
import json
from macros     import *

'''
get initial variables
'''
def get_init_vars(storage_info, abi_info, var_prefix):
    vars = {}
    locals = []

    elements = storage_info["contracts"][MACROS.CONTRACT_NAME]["storage-layout"]["storage"]

    for elmt in elements:
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
                vars[var_prefix+'.'+label] = '['+t_type[0]+'] ' + t_type[1] 
            else:
                vars[var_prefix+'.'+label] = t_type[2:]
    
    # for elmt in abi_info['contracts'][MACROS.CONTRACT_NAME]['abi']:
    #     if ("name" in elmt.keys() and elmt["name"] == MACROS.FUNCTION_NAME):
    #         for input in elmt["inputs"]:
    #             vars[input["name"]] = input["type"]
    return vars

'''
get the prefix for the inital variables
'''
def get_init_var_prefix():
    TRACE_file = open(MACROS.TRACE_FNAME, "r") 
    lines = [line.rstrip() for line in TRACE_file]   
    for i in range(0, len(lines)-1):
        if lines[i].startswith(">>"):
            prefix = get_var_prefix(lines[i])
            break
    return prefix

'''
get the current contract address
'''
def get_curr_address(instr):
    L = instr.find(" ")
    R = instr.find("::")
    return instr[L:R]

'''
get the variable prefix
'''
def get_var_prefix(instr):
    L = instr.find(" ") 
    c_name = re.search("\(.*::", instr)[0][1:-2]
    c_name += '_c' + instr[L+3:L+8] + '_'
    # print(c_name)
    # print(test)
    return c_name

'''
get the storage map
''' 
def get_MAPS(storage_info):
    MAPS = {}
    for contract in storage_info["contracts"]:
        MapIDs = {}
        for elmt in storage_info["contracts"][contract]["storage-layout"]["storage"]:
            slot =  elmt["slot"]
            label = elmt["label"]          
            MapIDs[slot] = label
        contract_name = contract[contract.find(':')+1:]
        # contract_name = contract_name[':':]
        # print(contract) 
        MAPS[contract_name] = MapIDs
    return MAPS

'''
write local variables from storage file to Boogie
'''
def get_types(storage_info):
    locals = []
    TYPES = {}    
    rt = ""
    # for contract in storage_info.keys():
    for contract in storage_info["contracts"]:
        types = {}
        for elmt in storage_info["contracts"][contract]["storage-layout"]["storage"]:
            label =  elmt["label"]
            t_type = elmt["type"]
            if (label in locals):
                pass
            else:
                if ("string" in t_type):
                    pass
                elif ("contract" in t_type):
                    pass # TODO: contract address as a type
                    var_type = "address"
                    rt = rt + ("\tvar " + contract+'.'+label + ': ' + var_type + ';\n')
                    types[label] = var_type
                elif "t_mapping" in t_type:
                    var_type = get_boogie_type(t_type)
                    # t_type = t_type.replace("t_", "")
                    # t_type = t_type.replace("mapping", "")[1:-1]
                    # t_type = t_type.split(',')
                    rt = rt + ("\tvar " + contract+'.'+label + ': ' + var_type + ';\n')
                    types[label] = var_type
                else:
                    rt = rt + ("\tvar " + contract+'.'+label + ":\t" + t_type[2:] + ";\n") 
                    types[label] = t_type[2:] 
                locals.append(contract+'.'+label)
                # print(contract, label, t_type)
        # contract_name = contract[contract.find(':'):]
        # contract_name = str(contract)
        # contract_name = contract_name[':':]        
        # print(contract)
        # print(types)
        TYPES[contract] = types

    return TYPES

'''
convert t_mapping to Boogie type
'''
def get_boogie_type(t_type):
    #print(t_type)
    if not t_type.startswith("t_mapping"):
        return t_type.replace("t_","")

    #"t_mapping(t_address,t_mapping(t_address,t_address))"
    ret_str = t_type[len("t_mapping("):]
    #print(f"ret_str={ret_str}")
    comma_pos = ret_str.find(",")
    first = ret_str[0:comma_pos]
    first = "["+first.replace("t_","")+"]"
    ret_str = ret_str[comma_pos+1:len(ret_str)-1]
    return first + " " + get_boogie_type(ret_str)

'''
find where the essential part starts in a contract call
'''
def find_essential_start(contract_name, function_name):
    # print(MACROS.SOLIDITY_FNAME)
    RUNTIME_file = open(MACROS.RUNTIME, )
    RUNTIME_BYTE = json.load(RUNTIME_file)
    essential_start=0
    # function_list = (RUNTIME_BYTE["contracts"][MACROS.SOLIDITY_FNAME+":"+contract_name]["function-debug-runtime"])
    for contract in RUNTIME_BYTE["contracts"]:
        if ":"+contract_name in contract:
            function_list = RUNTIME_BYTE["contracts"][contract]["function-debug-runtime"]
    for func in function_list:
        match = re.search(r'@(.+?)_', func)
        func_name = match.group(1)
        if (function_name==func_name):
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
    depth = 0
    PRE_start = 0
    for i in range(0, len(lines)-1):
        if lines[i].startswith(">>"):
            # matches = re.search(r"\(([^:]+)::([^()]+)\(.*?\)\)", lines[i])
            depth += 1
            matches = re.search(r"\(([^:]+)::([^()]+)\(.*?\)\)", lines[i])
            # print(line[1])
            # print(matches.group(1))
            contract_name = matches.group(1)
            function_name = matches.group(2)
            if not lines[i-1].startswith("==="):
                TRACE_essential.write(lines[i] + '\n')
                essential_start = find_essential_start(contract_name, function_name)
                start = False
            else:
                matches = re.search(r"(0x[a-fA-F0-9]+)::(0x[a-fA-F0-9]+)", lines[i])
                entry_address   = matches.group(1)
                entry_func_hash = matches.group(2)
        elif lines[i].startswith("<<"):
            depth -= 1
            TRACE_essential.write(lines[i] + '\n')
        elif not lines[i][0:1].isnumeric():
            continue
        else:
            PC = int(lines[i].split(" ")[0])
            if PC == essential_end and depth == 1:
                break
            if start:
                TRACE_essential.write(lines[i]+'\n')
            if PC == essential_start:
                if essential_end == 9999:
                    essential_end = PRE_start+1
                TRACE_essential.write(lines[i]+"\n")
                start = True
            else:
                PRE_start = PC
    return int(entry_address, 16), int(entry_func_hash, 16)
'''
get ABI information as a JSON
'''
def get_ABI_info():
    ABI_file = open(MACROS.ABI, "r")
    INFO = json.load(ABI_file)

    rt = {}
    info = {}
    for contract_name in INFO["contracts"].keys():
        new_name = contract_name[contract_name.find(':')+1:] #trim name
        info[new_name] = INFO["contracts"][contract_name]
    rt["contracts"] = info
    # print(rt["contracts"].keys())

    # tmp = ""
    # lines = ABI_file.readlines()
    # for line in lines:
    #     # print("l" + line)
    #     if line[0] == '{':
    #         continue
    #     elif len(line.strip()) == 0:
    #         line = ",\n"
    #     elif '===' in line:
    #         c_name = line.replace("======= ", "").replace(" =======", "").replace(MACROS.SOLIDITY_FNAME+":", "").replace("\n", "")
    #         line = "\"" + c_name + "\"" +":\n"
    #     elif 'JSON ABI' in line:
    #         continue    
    #     tmp = tmp + line
    # tmp = tmp + '}'
    # tmp = '{' + tmp[1:] #patch
    # INFO = json.loads(tmp)
    return rt

'''
get storage information as a python
'''
def get_STORAGE_info():
    STORAGE_file = open(MACROS.STORAGE, "r")
    INFO = json.load(STORAGE_file)
    rt = {}
    info = {}
    for contract_name in INFO["contracts"].keys():
        new_name = contract_name[contract_name.find(':')+1:] #trim name
        info[new_name] = INFO["contracts"][contract_name]
    rt["contracts"] = info
    # print(rt["contracts"].keys())
        # print(contract_name)
    # STORAGE_file = open(MACROS.STORAGE, "r")
    # tmp = '{'
    # lines = STORAGE_file.readlines()
    # for line in lines:
    #     # print("l" + line)
    #     if len(line.strip()) == 0:
    #         # print("},")
    #         line = ",\n"    
    #     elif '===' in line:
    #         c_name = line.replace("======= ", "").replace(" =======", "").replace(MACROS.SOLIDITY_FNAME+":", "").replace("\n", "")
    #         line = "\"" + c_name + "\"" +":\n"
    #         # print(c_name)
    #     elif 'Contract Storage' in line:
    #         continue    
    #     tmp = tmp + line
    # tmp = tmp + '}'
    # tmp = '{' + tmp[2:] #patch
    # INFO = json.loads(tmp)
    return rt  


'''
get proof invariant from AST file
'''
def get_invariant():    
    ast_file = open(MACROS.AST, 'r')
    AST_INFO = json.load(ast_file)
    astNode_dict = {}
    natSpec_dict = {}
    
    for contract in AST_INFO["contracts"]:
        matches = re.findall(r"(.*?):(.*$)", contract)[0]
        sourceName = matches[0]
        contractName = matches[1]
        astNode_dict[contractName] = sourceName
        if MACROS.CONTRACT_NAME == contractName:
            nodes = AST_INFO["sources"][sourceName]["AST"]["nodes"]

    def natSpec_build(node):
        contractName = node["name"]
        if contractName in natSpec_dict and natSpec_dict[contractName] is not None:
            return
        if "documentation" in node and "text" in node["documentation"]:
            my_natSpec = node["documentation"]["text"] + "\n"
        else:
            my_natSpec = ""
        if "baseContracts" in node:
            for parent in node["baseContracts"]:
                parentName = parent["baseName"]["name"]
                parentNode = AST_INFO["sources"][astNode_dict[parentName]]["AST"]["nodes"]
                for node in parentNode:
                    if node["nodeType"] == "ContractDefinition":
                        natSpec_build(node)
                
                if parentName in natSpec_dict and natSpec_dict[parentName] is not None:
                    my_natSpec += natSpec_dict[parentName]
                else:
                    my_natSpec += ""
        
                if my_natSpec:
                    natSpec_dict[contractName] = my_natSpec
    
    for node in nodes:
        if node["nodeType"] == "ContractDefinition":
            natSpec_build(node)
    
    
    invariants = {}
    for name, natSpec in natSpec_dict.items():
        print(name)
        print(natSpec)
        invariants[name] = []
        inv_list = natSpec.split("\n")
        for inv in inv_list:
            inv = inv.strip()
            inv = inv.replace("@custom:tct invariant: ", "")
            if inv:
                invariants[name].append(inv)
    
    return invariants

'''
get proof hypothesis from the the theorem file
'''
def get_hypothesis():
    theorem_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(theorem_file)
    return theorem["hypothesis"]

'''
get numerical type from the theorem file, either int or real
'''
def get_numerical_type():
    theorem_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(theorem_file)
    return theorem["numerical-type"]

'''
check if given trace has correct starting entry point
'''
def check_entrypoint():
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    theorem = json.load(THEOREM_file)
    # check theorem against trace
    trace = open(MACROS.TRACE_FNAME, 'r')
    line = ""
    while not line.startswith(">>"):
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
    dest_function = dest_function[:dest_function.find('(')]
    return dest_contract, dest_function


def write_defvars(var_prefix):
    rt = ""
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    THEOREM = json.load(THEOREM_file)
    vars = THEOREM["def-vars"]
    for var in vars: 
        if (len(vars[var][0])!=0):
            rt += "\tvar " + var + ":  " + vars[var][0] + ";\n"

        rt += "\t" + var + ":= " + vars[var][1].replace("this.", var_prefix) + ";\n"
    return(rt) 

# def try_substitution():
#     rt = ""
#     THEOREM_file = open(MACROS.THEOREM_FNAME, )
#     THEOREM = json.load(THEOREM_file)
#     vars = THEOREM["def-vars"]
#     for var in vars:
#         if (len(vars[var][0])==0):

            
'''
write hypothesis to Boogie
'''
def write_hypothesis(hypothesis, var_prefix):
    # hypothesis = hypothesis.replace("this", var_prefix)
    rt = ""
    for hypo in hypothesis:
        hypo = hypo.replace("this.", var_prefix)
        rt += "\tassume(" + hypo + ");\n"
    return(rt)

'''
write invariant to Boogie
'''
def write_invariants(invariants, var_prefix):
    # get from ast
    rt = ""
    trace_invariants = invariants[MACROS.CONTRACT_NAME]
    for inv in trace_invariants:
        rt = rt + ("\tassume(" + inv + ");\n")
        rt = rt.replace("this", var_prefix )
    rt = rt + ("\n")
    return rt 

'''
write epilogue to Boogie
'''
def write_epilogue(invariants,var_prefix):
    rt = ""
    trace_invariants = invariants[MACROS.CONTRACT_NAME]
    for inv in trace_invariants:
        rt = rt + ("\tassert(" + inv + ");\n")
        rt = rt.replace("this", var_prefix )
    rt = rt + ('}')
    return rt

'''
write the function parameters
'''
def write_params(abi_info, var_prefix):
    rt = ""
    for elmt in abi_info['contracts'][MACROS.CONTRACT_NAME]['abi']:
        if ("name" in elmt.keys() and elmt["name"] == MACROS.FUNCTION_NAME):
            for input in elmt["inputs"]:
                if ('[]' in input["type"]):
                    # if it's a simple array
                    rt = rt + "\tvar " +input["name"] + ":\t" + "[int] " + (input["type"]).replace("[]", "")+';\n'
                else:
                    rt = rt + "\tvar " +input["name"] + ":\t" + input["type"]+';\n'
    return rt + '\n'


# '''
# write local variables from storage file to Boogie
# '''
# def write_locals(storage_info):
#     locals = []
#     rt = ""
#     for contract in storage_info.keys():
#         for elmt in storage_info[contract]["storage"]:
#             label =  elmt["label"]
#             t_type = elmt["type"]
            
#             if (label in locals):
#                 pass
#             else:
#                 if ("string" in t_type):
#                     pass
#                 elif ("contract" in t_type):
#                     pass # TODO: contract address as a type
#                 elif "t_mapping" in t_type:
#                     t_type = t_type.replace("t_", "")
#                     t_type = t_type.replace("mapping", "")[1:-1]
#                     t_type = t_type.split(',')
#                     rt = rt + ("\tvar " + contract+'.'+label + ':['+t_type[0]+'] ' + t_type[1] + ';\n')
#                 else:
#                     rt = rt + ("\tvar " + contract+'.'+label + ":\t" + t_type[2:] + ";\n")  
#                 locals.append(contract+'.'+label)
#     return rt + '\n'
