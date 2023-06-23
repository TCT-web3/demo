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
            if isinstance(self.children[i].value, int):
                s = hex(self.children[i].value)
            else:
                s = str(self.children[i])
            if i<len(self.children)-1:
                ret+=s+","
            else:
                ret+=s
        ret+=")"
        return ret


class EVM:

    def __init__(self, stacks, storage, storage_map, memories, output_file, final_path, final_vars, curr_contract, curr_function, call_stack, abi_info): 
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
        self._abi_info = abi_info

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
        path="\t"+self._storage_map[str(self.find_mapID(node0))]+"["+str(map_id)+"]:=" + str(self.postorder_traversal(node1))+";\n\n"
        self._final_path.append(path)
        # print("\n[code gen SSTORE]")
        # print(node0)
        # print(node1)
        # print(path)
                      
    def boogie_gen_jumpi(self, node):
        path = "\tassume("+str(self.postorder_traversal(node))+");\n\n"
        self._final_path.append(path)
        # print("\n[code gen JUMPI]") 
        # print(node)
        # print(path)


    def find_key(self, node):
        if not node.children:
            if isinstance(node.value, str): # and not (node.value == 0xffffffffffffffffffffffffffffffffffffffff):
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
            print_string = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"<"+str(val2)+");\n"
            self._final_vars.append("\tvar " + return_string + ": bool;")
            self._final_path.append(print_string)
        elif node.value == "GT":
            val1 = self.postorder_traversal(node.children[0])
            val2 = self.postorder_traversal(node.children[1])
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+">"+str(val2)+");\n"
            self._final_vars.append("\tvar " + return_string + ": bool;")
            self._final_path.append(print_string)  
        elif node.value == "EQ":
            val1 = self.postorder_traversal(node.children[0])
            val2 = self.postorder_traversal(node.children[1])
            self._tmp_var_count+=1
            return_string = "tmp" + str(self._tmp_var_count)
            print_string = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"="+str(val2)+");\n"
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
                self.run_instruction(code_trace[i], (code_trace[i][0]+1 != code_trace[i+1][0]))
            else:
                self.run_instruction(code_trace[i], None)
        
    def inspect(self, what):
        if what == "stack":
            for stack_name in self._stacks:
                print("-----Stack: "+stack_name+"-----")
                c=0
                for elem in self._stacks[stack_name][::-1]:
                    if isinstance(elem.value, int):
                        s = hex(elem.value)
                    else:
                        s = elem
                    print('stack['+str(c)+'] ', s)
                    c=c+1
        elif what == "memory":
            for memory_name in self._memories.keys():
                print("-----Memory: "+memory_name+"-----")
                temp = self._memories[memory_name]
                for key in temp.keys(): 
                    if isinstance(temp[key].value, int):
                        s = hex(temp[key].value)
                    else:
                        s = temp[key]
                    print(key, ": ", s)
        elif what == "storage":
            print("-----Storage-----")
            for key in self._storage:
                print('(', key, ',', self._storage[key], ')')

    def set_callStack(self, offset, data):
        stack = [
            SVT("FourByteSelector"),
            SVT("SomethingIDontKnow"),
            offset
        ]
        return stack
    def count_lower_ffs(self, a):
        c = 0
        while a > 0:
            if a % 0x100 != 0xff:
                return -1
            c += 1
            a //= 0x100
        return c
    def count_lower_00s(self, a):
        if a == 0:
            return -1
        c = 0
        while a % 0x100 == 0x00:
            c += 1
            a //= 0x100
        return c, a
    def run_instruction(self, instr, branch_taken):
        # print(instr)
        # self.inspect("stack")
        # self.inspect("memory")
        
        PC=instr[0]
        opcode=instr[1]
        operand=instr[2]

        
        # if int(PC) == 757 or int(PC) == 786:
        #     print("=======before======")
        #     self.inspect("memory")
        #     self.inspect("stack")
        # if int(PC) >= 787 and int(PC) <= 825:
        #     print("=======before======")
        #     self.inspect("memory")
        #     self.inspect("stack")
        # if int(PC) >= 825 and int(PC) <= 830:
        #     print("=======before======")
        #     self.inspect("memory")
        #     self.inspect("stack")

        if instr[0]==(">"):
            # self.inspect("memory")
            # self.inspect("stack")
            info = re.search("\((.*)\)", instr)[0]
            info = info.split("::")
            dest_contract = (info[0][1:])
            dest_function = (info[1][:-1])


            if (dest_contract not in self._stacks.keys()):
                offset = self._memories[self._curr_contract][hex(self._stacks[self._curr_contract][-4].value)]
                length = self._stacks[self._curr_contract][-5]
                self._stacks[dest_contract] = self.set_callStack(offset, length)  
                self._memories[dest_contract] = {}

             # pops out the operands for a successful CALL operation
            for i in range(7):
                self._stacks[self._curr_contract].pop()
            self._stacks[self._curr_contract].append(SVT(1))

            self._call_stack.append((dest_contract, dest_function))
            self._curr_contract = dest_contract
            self._curr_function = dest_function
            # self.inspect("stack")
            print(">>> switched to contract: ", self._call_stack[-1][0])
            # self.inspect("memory")
            # self.inspect("stack")
        elif instr[0]==("<"):
            self._call_stack.pop()
            self._curr_contract = self._call_stack[-1][0]
            self._curr_function = self._call_stack[-1][1]
            
            print(">>> switched to contract: ", self._call_stack[-1][0])
        elif opcode=="JUMPDEST":
            pass
        elif opcode=="GAS":
            self._stacks[self._curr_contract].append(SVT("GAS"))  # what is the GAS amount? 
        elif opcode=="RETURNDATASIZE":
            for elmt in self._abi_info[self._curr_contract]:
                if ("name" in elmt.keys() and elmt["name"] == self._curr_function):
                    return_count = len(elmt["outputs"])
                    if(return_count == 0):
                        self._stacks[self._curr_contract].append(SVT(0))
                    else:
                        raise Exception("return data SIZE to be implemented. ")    
        elif opcode=="CALL":
            pass
        elif opcode=="STOP":
            pass     
        elif opcode=="JUMP":
            self._stacks[self._curr_contract].pop()
        elif opcode=="JUMPI":
            if(branch_taken):
                self.boogie_gen_jumpi(self._stacks[self._curr_contract][-2])

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
                if not mem_offset.value in self._memories[self._curr_contract].keys() and value.value == "OR":
                    rl = value.children[0]
                    rr = value.children[1]
                    if rl.value == "AND":
                        rlr = rl.children[1]
                        ffs = self.count_lower_ffs(rlr.value)
                    print(type(rr.value))
                    print(isinstance(rr.value, int))
                    if rr.value == "AND":
                        rrr = rr.children[1]
                        OOs, a = self.count_lower_00s(rrr.value)
                    elif isinstance(rr.value, int):
                        OOs, a = self.count_lower_00s(rr.value)
                    if ffs != OOs:
                        raise Exception("MSTORE exception")
                    print(hex(a))
                    self._memories[self._curr_contract][hex(mem_offset.value)] = SVT(a) 

                else:
                    self._memories[self._curr_contract][hex(mem_offset.value)] = value   
            self._memories[self._curr_contract] = dict(sorted(self._memories[self._curr_contract].items()))  # use sorted dictionary to mimic memory allocation  
            
        elif opcode=="MLOAD":
            mem_offset = self._stacks[self._curr_contract].pop()
            if not isinstance(mem_offset.value, int):
                if mem_offset not in self._memories[self._curr_contract].keys():
                    value = 0 # empty memory space
                else:    
                    value = self._memories[self._curr_contract][str(mem_offset)] # get symbolic memory location 
            else:
                if hex(mem_offset.value) not in self._memories[self._curr_contract].keys():
                    value = SVT("unknown") # empty memory space
                else:   
                    value = self._memories[self._curr_contract][hex(mem_offset.value)] # get exact memory location
            self._stacks[self._curr_contract].append(value)  
        elif opcode=="SSTORE":
            # print(instr)
            self.boogie_gen_sstore(self._stacks[self._curr_contract].pop(), self._stacks[self._curr_contract].pop())
            # sys.exit()
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
            if type(self._stacks[self._curr_contract][-1].value) == int:
                val = self._stacks[self._curr_contract].pop().value
                print(hex(val))
                node = SVT(~(2**256|val) & (2**256-1))
                self._stacks[self._curr_contract].append(node)
                # print(hex(node.value & f))
                self.inspect("stack")
                print(hex(node.value))
            else:
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
                elif opcode == "LT" or opcode == "GT" or opcode == "EQ":
                    node = SVT(opcode)
                    node.children.append(self._stacks[self._curr_contract].pop())
                    node.children.append(self._stacks[self._curr_contract].pop())
                # elif opcode == "LT":
                #     node = SVT((self._stacks[self._curr_contract].pop().value < self._stacks[self._curr_contract].pop().value)) #True or False 
                # elif opcode == "GT":
                #     node = SVT((self._stacks[self._curr_contract].pop().value > self._stacks[self._curr_contract].pop().value)) #True or False
                # elif opcode == "EQ":
                #     node = SVT((self._stacks[self._curr_contract].pop().value == self._stacks[self._curr_contract].pop().value)) #True or False          
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
        
        # self.inspect("stack")


        
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
        hex(64): SVT(128) # initial setting of the memory!!! 
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
    RUNTIME_file = open(runtime, )
    RUNTIME_BYTE = json.load(RUNTIME_file)
    essential_start=0
    function_list = (RUNTIME_BYTE["contracts"][solidity_fname+":"+contract_name]["function-debug-runtime"])
    for func in function_list:
        if (function_name in func):
            essential_start = (function_list[func]["entryPoint"])
            break 
    if (essential_start==0):
        raise Exception("error, cannot find function entrypoint")
    return essential_start

def write_trace_essential(complete_trace, essential_trace, essential_start, solidity_fname):
    # TODO: use regex to accomodate digits with fix width or not
    TRACE_file = open(complete_trace, "r")
    TRACE_essential = open(essential_trace, "w")
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
                essential_start = find_essential_start("temp_solc_runtime.json", solidity_fname, contract_name, function_name)
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


def get_FUNCTIONINFO2(abi, solidity_fname):
    ABI_file = open(abi, "r")
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
            c_name = line.replace("======= ", "").replace(" =======", "").replace(solidity_fname+":", "").replace("\n", "")
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
    SOLIDITY_FNAME  = ARGS[1]
    THEOREM_FNAME   = ARGS[2]
    TRACE_FNAME     = ARGS[3]
    STORAGE         = "temp_solc_storage.json"
    ABI             = "temp_solc_abi.json"
    AST             = "temp_solc_ast.json"
    ESSENTIAL       = "temp_essential.txt"
    RUNTIME         = "temp_solc_runtime.json"
    BOOGIE          = "TCT_out_"+THEOREM_FNAME[:-5]+".bpl"

   

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
    # RUNTIME_BYTE_file = open(RUNTIME, )
    essential_start = find_essential_start(RUNTIME, SOLIDITY_FNAME, CONTRACT_NAME, FUNCTION_NAME)
    write_trace_essential(TRACE_FNAME, ESSENTIAL, essential_start, SOLIDITY_FNAME)


    # EVM construction
    STACKS = {}
    init_STACK = set_stack(ABI, SOLIDITY_FNAME, CONTRACT_NAME, FUNCTION_NAME)
    STACKS[CONTRACT_NAME] = init_STACK
    
    MEMORIES = {}
    init_MEM = set_memory()
    MEMORIES[CONTRACT_NAME] = init_MEM

    CALL_STACK = []
    init_CALL = (CONTRACT_NAME, FUNCTION_NAME)
    CALL_STACK.append(init_CALL)


    # Function_info = get_FUNCTIONINFO(RUNTIME, SOLIDITY_FNAME)

    ABI_INFO = get_FUNCTIONINFO2(ABI, SOLIDITY_FNAME)


    PATHS = []
    VARS  = []
    MAP = get_MAP(STORAGE, SOLIDITY_FNAME, CONTRACT_NAME)
    evm = EVM(STACKS, set_storage(), MAP, MEMORIES, open(BOOGIE, "w"), PATHS, VARS, CONTRACT_NAME, FUNCTION_NAME, [init_CALL], ABI_INFO)
    print('\n(pre-execution)')
    evm.inspect("stack")
    print('\n(executing instructions...)')
    code_trace = read_path(ESSENTIAL)
    evm.sym_exec(code_trace)
    print('\n(end)')
    print('\n(post-execution)')
    evm.inspect("stack")
    # evm.inspect("memory")
    # evm.inspect("storage")

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