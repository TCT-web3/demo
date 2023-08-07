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

    for contract in storage_info["contracts"]:
        elements = storage_info["contracts"][contract]["storage-layout"]["storage"]
        for elmt in elements:
            label =  elmt["label"]
            t_type = elmt["type"]
            
            if (label in locals):
                pass
            else:
                if ("t_string" in t_type):
                    pass
                elif ("t_contract" in t_type):
                    pass # TODO: contract address as a type
                elif ("t_array" in t_type):
                    var_type = get_boogie_type(t_type)
                    vars[var_prefix+'.'+label] = '[int] ' + var_type[var_type.find("(")+1:var_type.find(")")]
                elif ("t_mapping" in t_type):
                    var_type = get_boogie_type(t_type)
                    vars[var_prefix+'.'+label] = '[address] ' + var_type
                else:
                    vars[var_prefix+'.'+label] = '[address] ' + t_type.lstrip("t_")

    for elmt in abi_info['contracts'][MACROS.CONTRACT_NAME]['abi']:
        if ("name" in elmt.keys() and elmt["name"] == MACROS.FUNCTION_NAME):
            for input in elmt["inputs"]:
                if ('[]' in input["type"]):
                    vars[input["name"]] = "[int] " + (input["type"]).replace("[]", "")
                else:
                    vars[input["name"]] = input["type"]
                

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
    if not t_type.startswith("t_mapping"):
        return t_type.replace("t_","")

    ret_str = t_type[len("t_mapping("):]
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
    #     if MACROS.CONTRACT_NAME == contractName:
    #         nodes = AST_INFO["sources"][sourceName]["AST"]["nodes"]

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
    
    # for node in nodes:
    #     if node["nodeType"] == "ContractDefinition":
    #         natSpec_build(node)
    
    for sources in AST_INFO["sources"]:
        nodes = AST_INFO["sources"][sources]["AST"]["nodes"]
        for node in nodes:
            if node["nodeType"] == "ContractDefinition":
                natSpec_build(node)
    
    invariants = {}
    for name, natSpec in natSpec_dict.items():
        invariants[name] = []
        inv_list = natSpec.split("\n")
        for inv in inv_list:
            inv = inv.strip()
            inv = inv.replace("@custom:tct ", "")
            if inv.startswith("invariant: "):
                invariants[name].append(inv.replace("invariant: ", ""))
    return invariants

'''
get postconditions from devdoc file
'''
def get_postcondition():
    devdoc_file = open(MACROS.DEVDOC, )
    devdoc = json.load(devdoc_file)
    postconditions = {}
    for contract in devdoc["contracts"]:
        contract_name = contract[contract.find(":")+1:]
        postconditions[contract_name] = {}
        methods = devdoc["contracts"][contract]["devdoc"].get("methods", [])
        for method in methods:
            method_name = method[:method.find("(")]
            postconditions[contract_name][method_name] = {}
            for natspec in methods[method]:
                natspec_name = natspec.replace("custom:", "") # TODO: "this" name resolution use name_substitution need var prefix
                d = ";"
                spec = [e+d for e in methods[method][natspec].split(d) if e]
                postconditions[contract_name][method_name][natspec_name] = spec

    return postconditions
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

def get_defvars():
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    THEOREM = json.load(THEOREM_file)
    vars = THEOREM["def-vars"]
    return vars

def write_defvars(var_prefix):
    rt = "\n\t// def-vars\n"
    THEOREM_file = open(MACROS.THEOREM_FNAME, )
    THEOREM = json.load(THEOREM_file)
    vars = THEOREM["def-vars"]
    for var in vars: 
        # if (len(vars[var][0])!=0):
        #     rt = "\tvar " + var + ":  " + vars[var][0] + ";\n" + rt

        rt = rt + "\t" + var + ":= " + vars[var][1].replace("this.", var_prefix) + ";\n"
    return(rt) 

        
'''
write hypothesis to Boogie
'''
def write_hypothesis(hypothesis, var_prefix):
    # hypothesis = hypothesis.replace("this", var_prefix)
    rt = "\n\t// hypothesis \n"
    for hypo in hypothesis:
        rt += "\tassume(" + name_substitution(var_prefix, hypo) + ");\n" 
        # rt += "\tassume(" + hypo + ");\n" 
    
    rt += "\n"
    return(rt)

'''
write invariant to Boogie
'''
def write_invariants(invariants, var_prefix):
    # get from ast
    rt = ""
    trace_invariants = invariants.get(MACROS.CONTRACT_NAME, [])
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
    # trace_invariants = invariants[MACROS.CONTRACT_NAME]
    # for inv in trace_invariants:
    #     rt = rt + ("\tassert(" + inv + ");\n")
    #     rt = rt.replace("this", var_prefix )
    trace_invariants = invariants.get(MACROS.CONTRACT_NAME, [])
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
                MACROS.ALL_VARS[input["name"]] = input["type"]
                if ('[]' in input["type"]):
                    # if it's a simple array
                    rt = rt + "\tvar " +input["name"] + ":\t" + "[int] " + (input["type"]).replace("[]", "")+';\n'
                else:
                    rt = rt + "\tvar " +input["name"] + ":\t" + input["type"]+';\n'
    return rt + '\n'


def name_substitution(c_prefix, expression):
    parts = expression.split(" ")
    new_parts = []
    for elmt in parts:
        if elmt in MACROS.ALL_VARS.keys():
            new_parts.append(elmt)
            # print("existing variable: " + elmt)
        elif ('=' in elmt or '>' in elmt or '<' in elmt or isfloat(elmt) or elmt.isdigit()):
            new_parts.append(elmt)
        else:
            # print('find name: ', elmt)
            new_elmt = (find_realname(elmt, c_prefix, MACROS.DEF_VARS))
            new_parts.append(new_elmt)
    # print(new_parts)
    actual_val = ''.join(new_parts)
    return actual_val
    # print("realhypo: ", realhypo)
        
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def find_realname(var, c_prefix, defvars):
    if var in MACROS.ALL_VARS.keys() or var in MACROS.DEF_VARS:
        return var
    elif(in_allvars(var)):
        return get_fullname(var)
    elif var in defvars.keys():
        # print(var)
        return find_realname(defvars[var][1], c_prefix, defvars)
    elif var=="this":
        return c_prefix
    elif "this." in var:
        var = var.replace("this", c_prefix)
        # return c_prefix
        return var
    elif var.startswith('['):
        # TODO: make it general
        return "[" + find_realname(var[1:-1], c_prefix, defvars) + "]" 
    elif '.' in var:
        if(var in MACROS.ALL_VARS.keys()):
            return var
        to_sub = var[:var.find(".")]
        rest = var[var.find(".")+1:]
        # if (MACROS.VAR_TYPES[get_varname(to_sub)] == "address"):
                # insert address before decoding rest
        if('[' in rest):
            map_name = rest[:rest.find('[')]
            map_key = rest[rest.find('['):]
            print("map name: "+map_name)
            print("map key:  "+map_key)
            return find_realname(map_name, c_prefix, defvars)+'['+find_realname(to_sub, c_prefix, defvars)+']'+find_realname(map_key, c_prefix, defvars)

        print('to_sub ', to_sub)
        print('rest: ', rest)
        if('[' in rest):
            return find_realname(rest, c_prefix, defvars)+'['+find_realname(to_sub, c_prefix, defvars)+']'
        else:
            return get_fullname(rest)+'['+find_realname(to_sub, c_prefix, defvars)+']'
        
    elif '[' in var:
        name = var[:var.find("[")]
        # print(name)
        if name in MACROS.ALL_VARS.keys():
            name_type = MACROS.ALL_VARS[name]
        else:
            name_type = MACROS.ALL_VARS[get_fullname(name)]
        
        if("[int]" in name_type or name_type=="[address]"):
            # print("simplae array: ", var)
            return var
        else:
            # print(var)
            # print(name_type)
            mapkeys=re.search("\[.*\]", var)[0]
            mapkeys=mapkeys.split(']')[:-1]
            # print(mapkeys)
            # rt = find_realname(name,c_prefix,defvars)
            rt = get_fullname(name)
            for key in mapkeys:
                rt += '[' + find_realname(key[1:], c_prefix, defvars)+ ']'
            return rt
    else:
        return var


def in_allvars(name):
    for var in MACROS.ALL_VARS:
        if('.'+name in var):
            return True

def get_fullname(name):
    for var in MACROS.ALL_VARS:
        if('.'+name in var):
            return var





def get_var_mapping(var):
    mapping = []
    word = ""
    openBr = 0
    for ltr in var:
        if ltr == "[":
            if openBr == 1:
                word += ltr
            openBr += 1
        elif ltr == "]":
            openBr -= 1
            if openBr >= 1:
                word += ltr
            elif openBr == 0:
                mapping.append(word)
                word = ""
        elif openBr >= 1:
            word += ltr
    
    return(mapping)
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
