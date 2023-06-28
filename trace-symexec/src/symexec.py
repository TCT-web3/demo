import re
import os
import json
import binascii
import subprocess
import sys

from prepare    import *
from macros     import *
from utils      import *
'''
Symbolic value tree 
'''
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
            if isinstance(self.children[i], tuple):
                s = str(self.children[i])
            elif isinstance(self.children[i].value, int):
                s = hex(self.children[i].value)
            else:
                s = str(self.children[i])
            if i<len(self.children)-1:
                ret+=s+","
            else:
                ret+=s
        ret+=")"
        return ret

'''
EVM core
'''
class EVM:
    from memory import recognize_32B_mask, mem_item_len, handle_MLOAD, handle_MSTORE, handle_AND, handle_OR


    def __init__(self, stacks, storage, storage_map, memories, output_file, final_path, final_vars, curr_contract, curr_function, call_stack, abi_info): 
        self._stacks        = stacks  
        self._storage       = storage
        self._memories      = memories
        self._output_file   = output_file
        self._tmp_var_count = 0
        self._final_path    = final_path
        self._final_vars    = final_vars
        self._storage_map   = storage_map
        self._curr_contract = curr_contract
        self._curr_function = curr_function
        self._call_stack    = call_stack
        self._abi_info      = abi_info

    def write_vars(self):
        for elmt in self._abi_info[self._curr_contract]:
            if ("name" in elmt.keys() and elmt["name"] == self._curr_function):
                for input in elmt["inputs"]:
                    self._output_file.write("\tvar " + input["name"] + ":\t" + input["type"]+';\n')
        self._output_file.write("\n")

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
                      
    def boogie_gen_jumpi(self, node, isNotZero):
        if (type(node.value) == int):
            if (isNotZero):
                path =  "\tassume("+str(self.postorder_traversal(node))+"!=0);\n\n"
            else:    
                path =  "\tassume("+str(self.postorder_traversal(node))+"==0);\n\n"
        elif (isNotZero):
            path =  "\tassume("+str(self.postorder_traversal(node))+");\n\n"
        elif (not isNotZero):
            path = "\tassume(!"+str(self.postorder_traversal(node))+");\n\n" 
        else: 
            raise Exception("wrong JUMPI value.")
        self._final_path.append(path)

    def find_key(self, node):
        if not node.children:
            if isinstance(node.value, str): # and not (node.value == 0xffffffffffffffffffffffffffffffffffffffff):
                return node.value # or self.postorder_traversal(node)
        for c in node.children:
            if not isinstance(c, tuple):
                return_val = self.find_key(c)
                if return_val:
                    return return_val

    def postorder_traversal(self, node):
        # children then parent
        return_string = ""
        if not node.children:
            return str(node.value)

        if node.value == "ISZERO":
            print(">>>", node.children[0])
            return_string += self.postorder_traversal(node.children[0]) # + "==0;\n"
            val1=self._tmp_var_count
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "\ttmp" + str(self._tmp_var_count) + ":=!tmp" + str(val1) + ";\n"
            self._final_vars.append("\tvar " + return_string + ": bool;")
            self._final_path.append(print_string)
        elif node.value == "SLOAD":
            map_id = self.find_mapID(node.children[0])
            map_key = self.find_key(node.children[0].children[1])
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
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
            print_string = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"=="+str(val2)+");\n"
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
        elif node.value == "Partial32B":
            return_string = str(self.postorder_traversal(node.children[1]))
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
                    print(hex(key), ": ", s)
        elif what == "storage":
            print("-----Storage-----")
            for key in self._storage:
                print('(', key, ',', self._storage[key], ')')

   
    def run_instruction(self, instr, branch_taken):
        shuo_count=0
        PC=instr[0]
        opcode=instr[1]
        operand=instr[2]

        if instr[0]==(">"):

            info = re.search("\((.*)\)", instr)[0]
            info = info.split("::")
            dest_contract = (info[0][1:])
            dest_function = (info[1][:-1])

            ### calling a new contract
            if (dest_contract not in self._stacks.keys()):
                #offset = self._memories[self._curr_contract][self._stacks[self._curr_contract][-4].value]
                #length = self._stacks[self._curr_contract][-5]
                callee_stack = []
                calldata_pos = self._stacks[self._curr_contract][-4].value
                calldata_len = self._stacks[self._curr_contract][-5].value
                
                func_selector = self._memories[self._curr_contract][calldata_pos].children[1].value
                func_selector//=0x100**28
                print("func_selector="+hex(func_selector))
                callee_stack.append(SVT(func_selector))
                callee_stack.append(SVT("AConstantBySolc"))
                calldata_len -=4
                calldata_pos +=4

                for i in range(calldata_len//0x20):
                    callee_stack.append(self._memories[self._curr_contract][calldata_pos])
                    calldata_pos += 0x20
                    
                self._stacks[dest_contract] = callee_stack  
                self._memories[dest_contract] = set_memory()

            # switch to a new contract
            # pops out the operands for a successful CALL operation
            for i in range(7):
                self._stacks[self._curr_contract].pop()
            self._stacks[self._curr_contract].append(SVT(1))
            self._call_stack.append((dest_contract, dest_function))
            self._curr_contract = dest_contract
            self._curr_function = dest_function
            print(">>> switched to contract: ", self._call_stack[-1][0])
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
                self.boogie_gen_jumpi(self._stacks[self._curr_contract][-2], True) 
            else:
                self.boogie_gen_jumpi(self._stacks[self._curr_contract][-2], False)
            self._stacks[self._curr_contract].pop()
            self._stacks[self._curr_contract].pop()
        elif opcode=="MSTORE":
            self.handle_MSTORE()            
        elif opcode=="MLOAD":
            node = self.handle_MLOAD()
            self._stacks[self._curr_contract].append(node)  
        elif opcode=="SSTORE":
            self.boogie_gen_sstore(self._stacks[self._curr_contract].pop(), self._stacks[self._curr_contract].pop())
        elif opcode=="SLOAD":
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
                print(hex(node.value))
            else:
                node = SVT(opcode)
                node.children.append(self._stacks[self._curr_contract].pop())
                self._stacks[self._curr_contract].append(node)
        elif opcode=="AND":
            node = self.handle_AND()
            self._stacks[self._curr_contract].append(node)
        elif opcode=="OR":
            node = self.handle_OR()
            self._stacks[self._curr_contract].append(node)
            self.inspect("stack")
        elif opcode=="ADD" or opcode=="LT" or opcode=="GT" or opcode=="EQ" or opcode=="SUB":            
            if isinstance(self._stacks[self._curr_contract][-1].value, int) and isinstance(self._stacks[self._curr_contract][-2].value, int):
                if opcode == "ADD":
                    node = SVT((self._stacks[self._curr_contract].pop().value + self._stacks[self._curr_contract].pop().value)%2**256) 
                elif opcode == "SUB":
                    node = SVT((self._stacks[self._curr_contract].pop().value - self._stacks[self._curr_contract].pop().value)%2**256) 
                elif opcode == "LT" or opcode == "GT" or opcode == "EQ":
                    node = SVT(opcode)
                    node.children.append(self._stacks[self._curr_contract].pop())
                    node.children.append(self._stacks[self._curr_contract].pop())
            else:
                node = SVT(opcode)
                node.children.append(self._stacks[self._curr_contract].pop())
                node.children.append(self._stacks[self._curr_contract].pop())
            self._stacks[self._curr_contract].append(node)
        elif opcode=="SHA3":
            if self._stacks[self._curr_contract][-2].value == 64:
                start_offset = self._stacks[self._curr_contract].pop().value
                if not isinstance(start_offset, int):
                    raise Exception("start offset not constant")
                node = SVT("MapElement")
                node.children.append(self._memories[self._curr_contract][start_offset+32])
                node.children.append(self._memories[self._curr_contract][start_offset])
                self._stacks[self._curr_contract].pop() # pop 64
                self._stacks[self._curr_contract].append(node)
        else:
            print('[!]',str(instr), 'not supported yet')  
            sys.exit()
        # self.inspect("stack")
        # if opcode=="MSTORE":
            # print("=======after======")
            # self.inspect("memory")
            # self.inspect("stack")
        
        # if isinstance(PC,int) and int(PC)==860  :
            # print("=======after======")
            # self.inspect("memory")
            # self.inspect("stack")
            #raise Exception ("debug stop")
        
'''
main
'''
def main():
    ### read arguments
    ARGS = sys.argv # output: ['symexec.py', solidity, theorem, trace]
    MACROS.SOLIDITY_FNAME  = ARGS[1]
    MACROS.THEOREM_FNAME   = ARGS[2]
    MACROS.TRACE_FNAME     = ARGS[3]
    MACROS.BOOGIE          = "TCT_out_"+MACROS.THEOREM_FNAME[:-5]+".bpl"

    ### initial generation of solc files and essential trace
    gen_solc()
    CONTRACT_NAME,FUNCTION_NAME = get_contract_and_function_names()
    MACROS.CONTRACT_NAME    = CONTRACT_NAME
    MACROS.FUNCTION_NAME    = FUNCTION_NAME
    check_entrypoint(MACROS.TRACE_FNAME)
    gen_trace_essential()

    ### setup 
    STACKS      = gen_init_STACK()
    STORAGE     = set_init_storage()
    MAP         = get_MAP()
    MEMORIES    = gen_init_MEMORY()
    BOOGIE_OUT  = open(MACROS.BOOGIE, "w")
    PATHS       = []
    VARS        = []
    CALL_STACK  = gen_init_CALL_STACK()
    ABI_INFO    = get_ABI_info()
    STOR_INFO   = get_STORAGE_info()
    HYPOTHESIS  = get_hypothesis()
    INVARIANTS  = map_invariant(MACROS.AST, MACROS.SOLIDITY_FNAME)
    
    ### run EVM trace instructions
    evm = EVM(STACKS, STORAGE, MAP, MEMORIES, BOOGIE_OUT, PATHS, VARS, CONTRACT_NAME, FUNCTION_NAME, CALL_STACK, ABI_INFO)
    print('\n(pre-execution)')
    evm.inspect("stack")
    print('\n(executing instructions...)')
    code_trace = build_path()
    evm.sym_exec(code_trace)
    print('\n(end)')
    print('\n(post-execution)')
    evm.inspect("stack")

    ### write Boogie output
    BOOGIE_OUT.write(MACROS.PREAMBLE)
    BOOGIE_OUT.write(write_storages(STOR_INFO))
    evm.write_vars() # aux vars for Boogie Proofs 
    BOOGIE_OUT.write(write_hypothesis(HYPOTHESIS))
    BOOGIE_OUT.write(write_invariants(INVARIANTS))
    evm.write_paths() # codegen for Boogie proofs
    BOOGIE_OUT.write(write_epilogue(INVARIANTS))
 
if __name__ == '__main__':
    main()