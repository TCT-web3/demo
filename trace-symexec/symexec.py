import re
import os
import json
import binascii
import subprocess
import sys
import pprint
#SVT -- Symbolic value tree
class SVT:
    def __init__(self, _value):
        self.value = _value
        self.children = []
        
    def __str__(self):        
        ret = str(self.value)
        if len(self.children)==0:
            return ret
        ret+="("
        for i in range(len(self.children)):
            if i<len(self.children)-1:
                ret+=str(self.children[i])+","
            else:
                ret+=str(self.children[i])
        ret+=")"
        return ret


class EVM:

    def __init__(self, stacks, storage, storage_map, memories, output_file, final_path, final_vars, curr_contract, curr_function, call_stack): 
        # TODO: extend EVM with dictionaries of stack/memory for different contracts. 
        #       - each should have it's own stack/memory
        #       - var_count and final vars should be shared
        # self._stacks[0] = stack 
        self._stacks = stacks  
        self._storage = storage
        # self._memory = memory
        self._memories = memories
        self._output_file = output_file
        self._tmp_var_count = 0
        self._final_path = final_path
        self._final_vars = final_vars
        self._storage_map = storage_map
        self._curr_contract = curr_contract
        self._curr_function = curr_function

        self._call_stack = call_stack
    
    def write_preamble(self):
        self._output_file.write("""type address = int;
type uint256 = int;
var totalSupply: uint256;
const TwoE16 : uint256;
axiom TwoE16 == 65536; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768;
const TwoE256 : int; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b-TwoE256);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b<0 ==> evmsub(a,b) == a-b+TwoE256);

function evmand(a, b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmand(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmand(a,b) == a+b-TwoE256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: 0<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));    

var balances: [address] uint256;

procedure straightline_code ()
modifies balances;
{  
    var msg.sender: address ;
    var _from: address ;
    var _to: address;
    var _value: uint256;
    var _fee: uint256;
       
""")
    def write_hypothesis(self, hypothesis):
        self._output_file.write("\tassume(" + hypothesis + ");\n")

    def write_invariants(self, invariants):
        # get from ast
        MVT_invariants = invariants["MultiVulnToken"]
        for inv in MVT_invariants:
            self._output_file.write("\tassume(" + inv + ");\n")
        self._output_file.write("\n")

    def write_epilogue(self, invariants):
        MVT_invariants = invariants["MultiVulnToken"]
        for inv in MVT_invariants:
            self._output_file.write("\tassert(" + inv + ");\n")
        self._output_file.write("}")

    def write_vars(self):
        for var in self._final_vars:
            self._output_file.write(var+"\n")
        self._output_file.write("\n")

    def write_paths(self):
        for path in self._final_path:
            self._output_file.write(path)

    def find_mapID(self, node):
        if node.value == "MapElement":
            return node.children[0]
        for c in node.children:
            self.find_mapID(c)

    def boogie_gen_sstore(self, node0, node1):
        map_id = self.find_key(node0.children[1])
        rt="\t"+self._storage_map[str(self.find_mapID(node0))]+"["+str(map_id)+"]:=" + str(self.postorder_traversal(node1))+";\n\n"
        self._final_path.append(rt)
                      
    def boogie_gen(self, node):
        self._final_path.append("\tassume("+str(self.postorder_traversal(node))+");\n\n")

    def find_key(self, node):
        if not node.children:
            if isinstance(node.value, str) and not (node.value == 'fff'):
                return node.value # or self.postorder_traversal(node)
        for c in node.children:
            return_val = self.find_key(c)
            if return_val:
                return return_val

    def postorder_traversal(self, node):
        # children then parent
        return_string = ""
        if not node.children:
            return str(node.value)
        # return_string += "("
        # for child in node.children:
        #     return_string += self.postorder_traversal(child)
        #     return_string += ","
        # return_string += ")"
        # return_string += str(node.value)
        if node.value == "ISZERO":
            return_string += self.postorder_traversal(node.children[0]) # + "==0;\n"
            val1=self._tmp_var_count
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            # print_string = "tmp" + str(self._tmp_var_count) + ":=tmp" + str(val1) + "==0;\n"
            print_string = "\ttmp" + str(self._tmp_var_count) + ":=!tmp" + str(val1) + ";\n"
            self._final_vars.append("\tvar " + return_string + ": bool;")
            self._final_path.append(print_string)
        elif node.value == "SLOAD":
            print(node.children[0])
            map_id = self.find_mapID(node.children[0])
            map_key = self.find_key(node.children[0].children[1])
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            # print_string = "\ttmp"+str(self._tmp_var_count)+":=mapID"+str(map_id)+"["+str(map_key)+"];\n"
            # print(str(map_id))
            print_string = "\ttmp"+str(self._tmp_var_count)+":="+self._storage_map[str(map_id)]+"["+str(map_key)+"];\n"
            self._final_vars.append("\tvar " + return_string + ": uint256;")
            self._final_path.append(print_string)  
        elif node.value == "LT":
            val1 = self.postorder_traversal(node.children[0])
            val2 = self.postorder_traversal(node.children[1])
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "\ttmp"+str(self._tmp_var_count)+":="+str(val1)+"<"+str(val2)+";\n"
            self._final_vars.append("\tvar " + return_string + ": bool;")
            self._final_path.append(print_string)
        elif node.value == "GT":
            val1 = self.postorder_traversal(node.children[0])
            val2 = self.postorder_traversal(node.children[1])
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "\ttmp"+str(self._tmp_var_count)+":="+str(val1)+">"+str(val2)+";\n"
            self._final_vars.append("\tvar " + return_string + ": bool;")
            self._final_path.append(print_string)  
        elif node.value == "ADD":
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string ="\ttmp"+str(self._tmp_var_count)+":=evmadd("+str(self.postorder_traversal(node.children[0]))+","+str(self.postorder_traversal(node.children[1]))+");\n"
            self._final_vars.append("\tvar " + return_string + ": uint256;")
            self._final_path.append(print_string)
        elif node.value == "SUB":
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string ="\ttmp"+str(self._tmp_var_count)+":=evmsub("+str(self.postorder_traversal(node.children[0]))+","+str(self.postorder_traversal(node.children[1]))+");\n"
            self._final_vars.append("\tvar " + return_string + ": uint256;")
            self._final_path.append(print_string) 
        elif node.value == "AND":    
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string ="\ttmp"+str(self._tmp_var_count)+":=evmand("+str(self.postorder_traversal(node.children[0]))+","+str(self.postorder_traversal(node.children[1]))+");\n"
            self._final_vars.append("\tvar " + return_string + ": uint256;")
            self._final_path.append(print_string)
        else:
            return str(node)
        return return_string
    
    def sym_exec(self, code_trace):
        for i in range(len(code_trace)):
            if(code_trace[i][1]=="JUMPI"):
                self.run_instruction(code_trace[i], code_trace[i][0]+1 != code_trace[i+1][0])
            else:
                self.run_instruction(code_trace[i], None)
        
    def inspect(self, what):
        if what == "stack":
            print("-----Stack-----")
            for stack_name in self._stacks:
                c=0
                print(stack_name)
                for elem in self._stacks[stack_name][::-1]:
                    print('stack['+str(c)+'] ', elem)
                    c=c+1
        elif what == "memory":
            print("-----Memory-----")
            for memory_name in self._memories:
                for key in memory_name.keys(): 
                    print(key, ": ", memory_name[key])
        elif what == "storage":
            print("-----Storage-----")
            for key in self._storage:
                print('(', key, ',', self._storage[key], ')')
                
    def run_instruction(self, instr, branch_taken):
        # self.inspect("stack")
        # self.inspect("memory")
        print(instr)
        PC=instr[0]
        opcode=instr[1]
        operand=instr[2]

        if instr[0]==(">"):
            # print(instr)
            info = re.search("\((.*)\)", instr)[0]
            info = info.split("::")
            self._curr_contract = (info[0][1:])
            self._curr_function = (info[1][:-1])
            print("switch to ", info)
            self._call_stack.append((self._curr_contract, self._curr_function))
            # sys.exit()
        elif instr[0]==("<"):
            self._call_stack.pop() #TODO: finish !

        elif opcode=="JUMPDEST":
            pass
        elif opcode=="GAS":
            self._stacks[self._curr_contract].append(SVT("GAS"))  # what is the GAS amount? 
        elif opcode=="RETURNDATASIZE":
            self._stacks[self._curr_contract].append(SVT("RETURNDATASIZE"))
        elif opcode=="CALL":
            pass # we can skip now since >>enter
        elif opcode=="STOP":
            pass     
        elif opcode=="JUMP":
            self._stacks[self._curr_contract].pop()
        elif opcode=="JUMPI":
            self.boogie_gen(self._stacks[self._curr_contract][-2])
            self._stacks[self._curr_contract].pop()
            self._stacks[self._curr_contract].pop()
        elif opcode=="MSTORE":
            mem_offset = (self._stacks[self._curr_contract].pop())
            # if not isinstance(mem_offset, int):
            #     raise Exception("We assume mem offset to be constant.")
            # elif mem_offset % 32 != 0:
            #     raise Exception("We assume mem offset to be a multiple of 32.")
            # mem_offset //= 32 #   use actually offset
            value = self._stacks[self._curr_contract].pop()
            if not isinstance(mem_offset.value, int):
                self._memories[self._curr_contract][str(mem_offset)] = value
            else:
                self._memories[self._curr_contract][hex(mem_offset.value)] = value    
            self._memories[self._curr_contract] = dict(sorted(self._memories[self._curr_contract].items()))  # use sorted dictionary to mimic memory allocation  
        elif opcode=="MLOAD":
            mem_offset = self._stacks[self._curr_contract].pop()
            if not isinstance(mem_offset.value, int):
                if mem_offset not in self._memories[self._curr_contract].keys():
                    value = 0 # empty memory space
                else:    
                    value = self._memories[self._curr_contract][str(mem_offset)] # get symbolic memory location (?)
            else:
                if hex(mem_offset.value) not in self._memories[self._curr_contract].keys():
                    value = SVT(0) # empty memory space
                else:    
                    value = self._memories[self._curr_contract][hex(mem_offset.value)] # get exact memory location
            self._stacks[self._curr_contract].append(value)  
        elif opcode=="SSTORE":
            self.boogie_gen_sstore(self._stacks[self._curr_contract].pop(), self._stacks[self._curr_contract].pop())
        elif opcode=="SLOAD":
            # self.inspect("storage")
            node = SVT("SLOAD")
            node.children.append(self._stacks[self._curr_contract].pop())
            self._stacks[self._curr_contract].append(node)
        elif opcode=="PC":
            self._stacks[self._curr_contract].append(SVT(PC))
        elif opcode.startswith("PUSH"):
            self._stacks[self._curr_contract].append(SVT(operand))
        elif opcode.startswith("POP"):
            self._stacks[self._curr_contract].pop()
        elif opcode.startswith("CALLER"):
            self._stacks[self._curr_contract].append(SVT("msg.sender")) # symbolic
        elif opcode.startswith("ORIGIN"):
            self._stacks[self._curr_contract].append(SVT("tx.origin")) # symbolic
        elif opcode.startswith("DUP"):
            position=int(re.search('[0-9]+', opcode)[0])
            self._stacks[self._curr_contract].append(self._stacks[self._curr_contract][len(self._stacks[self._curr_contract])-position]) 
        elif opcode.startswith("SWAP"):
            position=int(re.search('[0-9]+', opcode)[0])
            dest = self._stacks[self._curr_contract][len(self._stacks[self._curr_contract])-position-1] 
            self._stacks[self._curr_contract][len(self._stacks[self._curr_contract])-position] = self._stacks[self._curr_contract].pop()
            self._stacks[self._curr_contract].append(dest)
        elif opcode=="ISZERO" or opcode=="NOT":
            node = SVT(opcode)
            node.children.append(self._stacks[self._curr_contract].pop())
            self._stacks[self._curr_contract].append(node)
        elif opcode=="ADD" or opcode=="AND" or opcode=="OR" or opcode=="LT" or opcode=="GT" or opcode=="EQ" or opcode=="SUB":
            # self.inspect("stack")
            if isinstance(self._stacks[self._curr_contract][-1].value, int) and isinstance(self._stacks[self._curr_contract][-2].value, int):
                if opcode == "ADD":
                    node = SVT((self._stacks[self._curr_contract].pop().value + self._stacks[self._curr_contract].pop().value)%2**256)
                elif opcode == "AND":
                    node = SVT((self._stacks[self._curr_contract].pop().value & self._stacks[self._curr_contract].pop().value)%2**256) 
                elif opcode == "OR":
                    node = SVT((self._stacks[self._curr_contract].pop().value | self._stacks[self._curr_contract].pop().value)%2**256)    
                elif opcode == "SUB":
                    node = SVT((self._stacks[self._curr_contract].pop().value - self._stacks[self._curr_contract].pop().value)%2**256) 
                elif opcode == "LT":
                    node = SVT((self._stacks[self._curr_contract].pop().value < self._stacks[self._curr_contract].pop().value)) #True or False 
                elif opcode == "GT":
                    node = SVT((self._stacks[self._curr_contract].pop().value > self._stacks[self._curr_contract].pop().value)) #True or False
                elif opcode == "EQ":
                    node = SVT((self._stacks[self._curr_contract].pop().value == self._stacks[self._curr_contract].pop().value)) #True or False          
            else:
                node = SVT(opcode)
                node.children.append(self._stacks[self._curr_contract].pop())
                node.children.append(self._stacks[self._curr_contract].pop())
            self._stacks[self._curr_contract].append(node)
        elif opcode=="SHA3":
            # self.inspect("stack")
            # self.inspect("memory")
            if self._stacks[self._curr_contract][-2].value == 64:
                start_offset = self._stacks[self._curr_contract].pop().value
                if not isinstance(start_offset, int):
                    raise Exception("start offset not constant")
                node = SVT("MapElement")
                # node.children.append(self._memory[start_offset//32+1]) # map name: balances
                # node.children.append(self._memory[start_offset//32]) # key in balances

                node.children.append(self._memories[self._curr_contract][hex(start_offset+32)])
                node.children.append(self._memories[self._curr_contract][hex(start_offset)])

                self._stacks[self._curr_contract].pop() # pop 64
                self._stacks[self._curr_contract].append(node)
            # self.inspect("stack")
        else:
            print('[!]',str(instr), 'not supported yet')  
            sys.exit()


        
# Note that "FourByteSelector" is at the BOTTOM of the stack     
def set_stack(abi, solidity_fname, contract_name, function_name):
    stack = [
        SVT("FourByteSelector"), 
        SVT("SomethingIDontKnow"), 
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

    for n in file_names:
        os.remove(n)
    
    return stack

def set_storage():
    return {
        0: '0x00'
    } 

def set_memory():
    return {
        hex(64): SVT(128) # initial setting of the memory 
    }

def read_path(filename):
    trace=[]
    inputfile = open(filename, 'r')
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
                if 'fff' in str(instr[2]):
                    operand = 'fff'
                else:    
                    operand=int('0x'+ instr[2], 16)
            else:  
                operand = None
            trace_node = (PC, operator, operand) 
            trace.append(trace_node)
        elif(">>" in line or "<<" in line):
            trace.append(line)     
    inputfile.close()
    return trace

# a function to get a list of JSON from a text file  
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
    
    for n in file_names:
        os.remove(n)
    return mapIDs

def find_essential_start(runtime, solidity_fname, contract_name, function_name):
    RUNTIME_BYTE = json.load(runtime)
    essential_start=0
    function_list = (RUNTIME_BYTE["contracts"][solidity_fname+":"+contract_name]["function-debug-runtime"])
    for func in function_list:
        if (function_name in func):
            essential_start = (function_list[func]["entryPoint"])
            break
    print(essential_start)    
    if (essential_start==0):
        raise Exception("error, cannot find function entrypoint")
    return essential_start

def write_trace_essential(complete_trace, essential_trace, essential_start):
    # TODO: use regex to accomodate digits with fix width or not
    TRACE_file = open(complete_trace, "r")
    TRACE_essential = open(essential_trace, "w")
    lines = [line.rstrip() for line in TRACE_file]
    essential_end = 9999
    start = False
    PRE_start = 0
    for i in range(0, len(lines)-1):
        if lines[i].startswith(">>") or lines[i].startswith("<<"):
            # contract_name_start = lines[i].find('(')+1
            # contract_name_end = lines[i].find('::', contract_name_start)
            # contract_name = lines[i][contract_name_start:contract_name_end]
            # TRACE_essential.write(">>enter " + contract_name + '\n')
            TRACE_essential.write(lines[i] + '\n')
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
                essential_end = PRE_start+1
                TRACE_essential.write(lines[i]+"\n")
                start = True
            else:
                PRE_start = int(lines[i][0:4])

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

def check_entry_thingy(trace, theorem):
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
    
def main():
    ARGS = sys.argv # output: ['symexec.py', solidity, theorem, trace]

    STORAGE     ="solc_storage.json"
    ABI         ="solc_abi.json"
    AST         ="solc_ast.json"
    ESSENTIAL   ="trace_essential.txt"
    RUNTIME     ="solc_runtime.json"
    BOOGIE      ="output.bpl"

    SOLIDITY_FNAME  = ARGS[1]
    THEOREM_FNAME   = ARGS[2]
    TRACE_FNAME     = ARGS[3]

    os.system('solc --storage-layout --pretty-json ' + SOLIDITY_FNAME + ' > '+ STORAGE)
    os.system('solc --abi --pretty-json ' + SOLIDITY_FNAME + ' > ' + ABI)
    os.system('solc --combined-json function-debug-runtime --pretty-json ' + SOLIDITY_FNAME + ' > ' + RUNTIME)
    os.system('solc --pretty-json --combined-json ast ' + SOLIDITY_FNAME + ' > ' + AST)

    # get contract and function name
    THEOREM_file = open(THEOREM_FNAME, )
    THEOREM = json.load(THEOREM_file)
    CONTRACT_NAME = (re.search("(.*)::", THEOREM['entry-for-test']))[0][:-2]    
    FUNCTION_NAME = (re.search("::(.*)\(", THEOREM['entry-for-test']))[0][2:-1]

    check_entry_thingy(TRACE_FNAME, THEOREM)


    INVARIANTS = map_invariant(AST, SOLIDITY_FNAME)

    # get essential part of the trace
    RUNTIME_BYTE_file = open(RUNTIME, )
    essential_start = find_essential_start(RUNTIME_BYTE_file, SOLIDITY_FNAME, CONTRACT_NAME, FUNCTION_NAME)
    write_trace_essential(TRACE_FNAME, ESSENTIAL, essential_start)


    # TODO: initialize all the stacks for each functions in each contracts 
    CONTRACT_lst = json.load(open(RUNTIME,))
    for entries in CONTRACT_lst["contracts"]:
        parts = entries.split(":")
        solidity_file=parts[0]
        contract=parts[1]
        print(solidity_file)
        print(contract)



    # EVM construction
    STACKS = {}
    init_STACK = set_stack(ABI, SOLIDITY_FNAME, CONTRACT_NAME, FUNCTION_NAME)


    STACKS[CONTRACT_NAME] = init_STACK
    
    MEMORIES = {}
    init_MEM = set_memory()
    MEMORIES[CONTRACT_NAME] = init_MEM


    STACKS["no_reentrancy_attack"] = [
        "0x000000000000000000000000000000000000000000000000000000000000430e",
	    "0x00000000000000000000000073d5596f97950f1048b251e3e3ee5ab888d76d37",
	    "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x00000000000000000000000000000000000000000000000000000000000000c4",
        "0x0000000000000000000000000000000000000000000000000000000000000024",
        "0x00000000000000000000000000000000000000000000000000000000000000c4",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x00000000000000000000000000000000000000000000000000000000000000e8",
        "0x00000000000000000000000073d5596f97950f1048b251e3e3ee5ab888d76d37",
        "0x0000000000000000000000000000000000000000000000000000000000000000",
        "0x0000000000000000000000000000000000000000000000000000000000000005",
        "0x00000000000000000000000071c7656ec7ab88b098defb751b7401b5f6d8976f",
        "0x00000000000000000000000000000000000000000000000000000000000000bd",
        "0x000000000000000000000000000000000000000000000000000000003d0a4061"
    ]

    MEMORIES["no_reentrancy_attack"] = {
        0x0: "00000000000000000000000071c7656ec7ab88b098defb751b7401b5f6d8976f",
	    0x20: "0000000000000000000000000000000000000000000000000000000000000002",
	    0x40: "00000000000000000000000000000000000000000000000000000000000000c4",
	    0x60: "0000000000000000000000000000000000000000000000000000000000000000",
	    0x80: "0000000000000000000000000000000000000000000000000000000000000024",
	    0xa0: "85892c2400000000000000000000000000000000000000000000000000000000",
	    0xc0: "0000000585892c24000000000000000000000000000000000000000000000000",
	    0xe0: "0000000000000005000000000000000000000000000000000000000000000000",
	    0x100: "0000000000000000000000000000000000000000000000000000000000000000"
    }



    PATHS = []
    VARS  = []
    MAP = get_MAP(STORAGE, SOLIDITY_FNAME, CONTRACT_NAME)
    evm = EVM(STACKS, set_storage(), MAP, MEMORIES, open(BOOGIE, "w"), PATHS, VARS, CONTRACT_NAME, FUNCTION_NAME, [])
    evm.inspect("stack")
    print('(executing instructions...)')
    code_trace = read_path(ESSENTIAL)
    evm.sym_exec(code_trace)
    evm.inspect("stack")
    evm.inspect("memory")
    evm.inspect("storage")

    # sys.exit()
    # write to final Boogie output
    evm.write_preamble()
    evm.write_vars()
    evm.write_hypothesis(THEOREM["hypothesis"])
    evm.write_invariants(INVARIANTS)
    evm.write_paths()
    evm.write_epilogue(INVARIANTS)

 
if __name__ == '__main__':
    main()