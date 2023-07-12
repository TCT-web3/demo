########################################################
#   Main driver for symbolic execution of EVM trace    # 
########################################################
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
EVM core trace analysis
'''
class EVM:
    from memory import recognize_32B_mask, mem_item_len, handle_MLOAD, handle_MSTORE, handle_AND, handle_OR

    def __init__(self, stacks, storage, storage_map, memories, output_file, final_path, final_vars, curr_contract, curr_function, call_stack, abi_info, var_prefix): 
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
        self._var_prefix    = var_prefix

    '''perfprm symbolic execution'''
    def sym_exec(self, code_trace):
            for i in range(len(code_trace)):
                if(code_trace[i][1]=="JUMPI"):
                    self.run_instruction(code_trace[i], (code_trace[i][0]+1 != code_trace[i+1][0]))
                else:
                    self.run_instruction(code_trace[i], None)


    '''run each EVM instruction with PC, operator, and operand'''        
    def run_instruction(self, instr, branch_taken):
        PC      = instr[0]
        opcode  = instr[1]
        operand = instr[2]

        print(instr)
        # print(self._call_stack)

        if opcode=="JUMPDEST" or opcode=="CALL" or opcode=="STOP":
            pass # no-op
        elif instr[0]==(">"):
            # print(instr)
            dest_contract, dest_function = get_dest_contract_and_function(instr)
            
            ### calling a new contract, set up calle stack
            callee_stack    = []
            calldata_pos    = self._stacks[-1][-4].value
            calldata_len    = self._stacks[-1][-5].value
            func_selector   = self._memories[-1][calldata_pos].children[1].value

            if(isinstance(func_selector, int)):
                func_selector//=0x100**28
            else:
                func_selector = (self.find_key(self._memories[-1][calldata_pos].children[1].children[1]))

            callee_stack.append(SVT(func_selector))
            callee_stack.append(SVT("AConstantBySolc"))
            calldata_len -=4
            calldata_pos +=4

            for i in range(calldata_len//0x20):
                callee_stack.append(self._memories[-1][calldata_pos])
                calldata_pos += 0x20

            for elmt in callee_stack:
                if (isinstance(self.find_key(elmt), str) and '.' in str(elmt)):
                    elmt = self.find_key(elmt)
                    var_name = elmt[elmt.find('.')+1: ]
                    self.add_new_vars(var_name)    
                
            ### switch to a new contract and pops out the operands for a successful CALL operation
            for i in range(7):
                self._stacks[-1].pop()
            self._stacks[-1].append(SVT(1)) # CALL successed
            dest_address = get_var_prefix(instr)
            self._var_prefix = dest_address
            self._call_stack.append((dest_contract, dest_function, dest_address))
            self._curr_contract = dest_contract
            self._curr_function = dest_function
            self._var_prefix = get_var_prefix(instr)
            self._stacks.append(callee_stack)
            self._memories.append({0x40: SVT(0x80),0x10000000000: SVT(0)}) # temp
            print(">>CALL,  switched to contract: ", self._call_stack[-1][0])
        elif opcode=="STATICCALL":
            # TODO: finish
            # for i in range(7):
            #     self._stacks[-1].pop()
            # self._call_stack.append((self._curr_function, "somefunction", 0x20))
            # self._call_stack.pop()
        elif instr[0]==("<"):
            # print(instr)
            print(self._call_stack)
            self._call_stack.pop()
            self._curr_contract = self._call_stack[-1][0]
            self._curr_function = self._call_stack[-1][1]     
            self._var_prefix = self._call_stack[-1][2]     
            self._stacks.pop()
            self._memories.pop()
            print(">>LEAVE, switched to contract: ", self._call_stack[-1][0])
        elif opcode=="GAS":
            self._stacks[-1].append(SVT("GAS"))  
        elif opcode=="RETURNDATASIZE":
            for elmt in self._abi_info[self._curr_contract]:
                if ("name" in elmt.keys() and elmt["name"] == self._curr_function):
                    return_count = len(elmt["outputs"])
                    if(return_count == 0):
                        self._stacks[-1].append(SVT(0))
                    else:
                        raise Exception("return data SIZE to be implemented. ")    
        elif opcode=="EXTCODESIZE":
            node=SVT("ACCOUNT_CODESIZE")
            node.children.append(self._stacks[-1].pop()) 
            self._stacks[-1].append(node)                
        elif opcode=="JUMP":
            self._stacks[-1].pop()
        elif opcode=="JUMPI":
            self.boogie_gen_jumpi(self._stacks[-1][-2], branch_taken)
            self._stacks[-1].pop()
            self._stacks[-1].pop()
        elif opcode=="MSTORE":
            self.handle_MSTORE()            
        elif opcode=="MLOAD":
            node = self.handle_MLOAD()
            self._stacks[-1].append(node)  
        elif opcode=="SSTORE":
            self.boogie_gen_sstore(self._stacks[-1].pop(), self._stacks[-1].pop())
        elif opcode=="SLOAD":
            to_load = self._stacks[-1].pop()
            if to_load.value == "MapElement": 
                node = SVT("SLOAD")
                node.children.append(to_load)
                self._stacks[-1].append(node)
            else:
                stored_value = self._var_prefix+'.'+self._storage_map[self._curr_contract][str(to_load.value)]
                self._stacks[-1].append(SVT(stored_value))
        elif opcode=="PC":
            self._stacks[-1].append(SVT(PC))
        elif opcode.startswith("PUSH"):
            self._stacks[-1].append(SVT(operand))
        elif opcode.startswith("POP"):
            self._stacks[-1].pop()
        elif opcode.startswith("CALLER"):
            self._stacks[-1].append(SVT("msg.sender")) # symbolic
        elif opcode.startswith("ORIGIN"):
            self._stacks[-1].append(SVT("tx.origin")) # symbolic
        elif opcode.startswith("DUP"):
            position=int(re.search('[0-9]+', opcode)[0])
            self._stacks[-1].append(self._stacks[-1][len(self._stacks[-1])-position]) 
        elif opcode.startswith("SWAP"):
            position=int(re.search('[0-9]+', opcode)[0])
            dest = self._stacks[-1][len(self._stacks[-1])-position-1] 
            self._stacks[-1][len(self._stacks[-1])-position] = self._stacks[-1].pop()
            self._stacks[-1].append(dest)
        elif opcode=="ISZERO" or opcode=="NOT":
            if type(self._stacks[-1][-1].value) == int:
                val = self._stacks[-1].pop().value
                node = SVT(~(2**256|val) & (2**256-1))
                self._stacks[-1].append(node)
            else:
                node = SVT(opcode)
                node.children.append(self._stacks[-1].pop())
                self._stacks[-1].append(node)
        elif opcode=="AND":
            node = self.handle_AND()
            self._stacks[-1].append(node)
        elif opcode=="OR":
            node = self.handle_OR()
            self._stacks[-1].append(node)
        elif opcode=="ADD" or opcode=="LT" or opcode=="GT" or opcode=="EQ" or opcode=="SUB" or opcode=="DIV" or opcode=="EXP" or opcode=="SHL":            
            if isinstance(self._stacks[-1][-1].value, int) and isinstance(self._stacks[-1][-2].value, int):
                if opcode == "ADD":
                    node = SVT((self._stacks[-1].pop().value + self._stacks[-1].pop().value)%2**256) 
                elif opcode == "SUB":
                    node = SVT((self._stacks[-1].pop().value - self._stacks[-1].pop().value)%2**256)
                elif opcode == "DIV":
                    node = SVT((self._stacks[-1].pop().value // self._stacks[-1].pop().value)%2**256)
                elif opcode == "EXP":
                    node = SVT((self._stacks[-1].pop().value ** self._stacks[-1].pop().value)%2**256)
                elif opcode == "SHL":
                    node = SVT((self._stacks[-1].pop().value << self._stacks[-1].pop().value)%2**256) 
                elif opcode == "LT" or opcode == "GT" or opcode == "EQ":
                    node = SVT(opcode)
                    node.children.append(self._stacks[-1].pop())
                    node.children.append(self._stacks[-1].pop())
            else:
                if opcode == "DIV":
                    node = self._stacks[-1].pop() # actual address
                    self._stacks[-1].pop() # dummy 0x1
                else:
                    node = SVT(opcode)
                    node.children.append(self._stacks[-1].pop())
                    node.children.append(self._stacks[-1].pop())
            self._stacks[-1].append(node)
        elif opcode=="SHA3":
            if self._stacks[-1][-2].value == 64:
                start_offset = self._stacks[-1].pop().value
                if not isinstance(start_offset, int):
                    raise Exception("start offset not constant")
                node = SVT("MapElement")
                node.children.append(self._memories[-1][start_offset+32])
                node.children.append(self._memories[-1][start_offset])
                self._stacks[-1].pop() # pop 64
                self._stacks[-1].append(node)
        else:
            print('[!]',str(instr), 'not supported yet')  
            # sys.exit()

    '''recursively traverse an SVT node'''
    def postorder_traversal(self, node):
        to_return = ""
        if not node.children:
            return node.value

        if node.value == "ISZERO":
            to_return += self.postorder_traversal(node.children[0]) # + "==0;\n"
            if to_return.isnumeric():
                if to_return == "0":
                    to_return = "true"
                else:
                    to_return = "false"
            elif to_return == "false":
                to_return = "true"
            elif to_return == "true":
                to_return = "false"
            else:
                val1=self._tmp_var_count
                self._tmp_var_count+=1
                to_return = "tmp" + str(self._tmp_var_count)
                if (self._final_vars["tmp"+str(val1)] == 'bool'):
                    to_boogie = "\ttmp" + str(self._tmp_var_count) + ":=!tmp" + str(val1) + ";\n"
                elif (self._final_vars["tmp"+str(val1)] == 'uint256'):
                    to_boogie = "\ttmp" + str(self._tmp_var_count) + ":=tmp" + str(val1) + "==0;\n"
            
                self._final_vars[to_return] = 'bool'
                self._final_path.append(to_boogie)
        elif node.value == "SLOAD":
            if node.children[0].value=="MapElement":
                map_id  = self.find_mapID(node.children[0])
                map_key = self.find_key(node.children[0].children[1])
            else:
                map_id = node.children[0].value
            self._tmp_var_count+=1
            to_return = "tmp" + str(self._tmp_var_count)
            var_name  = self._storage_map[self._curr_contract][str(map_id)]
            self.add_new_vars(var_name)
            to_boogie = "\ttmp"+str(self._tmp_var_count)+":="+ self._var_prefix+'.'+var_name

            if node.children[0].value=="MapElement":
                to_boogie +="["+str(map_key)+"]"
            to_boogie +=";\n"
            self._final_vars[to_return] = 'uint256'
            self._final_path.append(to_boogie) 
        elif node.value == "LT" or node.value == "GT" or node.value == "EQ":
            val1 = self.postorder_traversal(node.children[0])
            val2 = self.postorder_traversal(node.children[1])
            if isinstance(val1, int) and isinstance(val2, int):
                to_return = ""
                if node.value == "LT":
                    if val1 < val2:
                        to_return = "true"
                    else:
                        to_return = "false"
                elif node.value == "GT":
                    if val1 > val2:
                        to_return = "true"
                    else:
                        to_return = "false"
                elif node.value == "EQ":
                    if val1 == val2:
                        to_return = "true"
                    else:
                        to_return = "false"
            else:
                self._tmp_var_count+=1
                to_return = "tmp" + str(self._tmp_var_count)
                if node.value == "LT":
                    to_boogie = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"<"+str(val2)+");\n"
                elif node.value == "GT":
                    to_boogie = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+">"+str(val2)+");\n"
                elif node.value == "EQ":
                    to_boogie = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"=="+str(val2)+");\n"
                self._final_vars[to_return] = 'bool'
                self._final_path.append(to_boogie) 
        elif node.value == "ADD" or node.value == "SUB" or node.value == "AND":
            val1=self.postorder_traversal(node.children[0])
            val2=self.postorder_traversal(node.children[1])
            if isinstance(val1, int) and isinstance(val2, int):
                if node.value == "ADD":
                    to_return = val1 + val2
                elif node.value == "SUB":
                    to_return = val1 - val2
                elif node.value == "AND":
                    to_return = val1 & val2
            else:
                self._tmp_var_count+=1
                to_return =  "tmp" + str(self._tmp_var_count)
                if node.value == "ADD":
                    to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmadd("+str(val1)+","+str(val2)+");\n"
                elif node.value == "SUB":
                    to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmsub("+str(val1)+","+str(val2)+");\n"
                elif node.value == "AND":
                    to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmand("+str(val1)+","+str(val2)+");\n"
                self._final_vars[to_return] = 'uint256'
                self._final_path.append(to_boogie)
        elif node.value == "Partial32B":
            to_return = str(self.postorder_traversal(node.children[1]))
        else:
            return str(node)
        return to_return
    
    '''generate boogie code when SSTORE happens'''
    def boogie_gen_sstore(self, node0, node1):
        if node0.value=="MapElement":
            map_key = self.find_key(node0.children[1])
            var_name = self._storage_map[self._curr_contract][str(self.find_mapID(node0))]+"["+str(map_key)+"]"
            path="\t"+self._var_prefix+'.'+var_name+":=" + str(self.postorder_traversal(node1))+";\n\n"
        else:
            var_name = self._storage_map[self._curr_contract][str(node0.value)]
            self.add_new_vars(var_name)
            path="\t"+self._var_prefix+'.'+var_name+":=" + str(self.postorder_traversal(node1))+";\n\n"
        self._final_path.append(path)

    def is_called_param(self, map_key):
        if (re.search("c\_(.*).\_", map_key)):
            print(map_key, "TRUE")
            return True
        print(map_key, "FALSE")    
        return False

    '''generate boogie code when JUMPI happens'''         
    def boogie_gen_jumpi(self, node, isNotZero):
        # self._final_path.append(str(node)+'\n')
        var = self.postorder_traversal(node)
        if var == "true":
            if isNotZero:
                return
            else:
                path = "\tassume(false);\n\n" 
        elif var == "false":
            if isNotZero:
                path = "\tassume(false);\n\n"
            else:
                return
        elif(isinstance(var, int)):
            if (isNotZero and var==0) or (not isNotZero and var!=0):
                raise Exception("JUMPI condition exception")
            else:
                return
        elif(self._final_vars[var]=='bool'):
            if (isNotZero):
                path = "\tassume("+ var +");\n\n"
            else:
                path = "\tassume(!"+ var +");\n\n" 
        elif(self._final_vars[var]=='uint256'):
            if (isNotZero):
                path = "\tassume("+ var +"!=0);\n\n"
            else:    
                path = "\tassume("+ var +"==0);\n\n"
        else:
            raise Exception("JUMPI stack[-1] is_not_zero error")
        self._final_path.append(path)

    '''wrote aux vars to Boogie'''
    def write_vars(self):
        for var in self._final_vars.keys():
            self._output_file.write("\tvar " + var + ":  " + self._final_vars[var] + ";\n")
        self._output_file.write("\n")

    '''write all generated code to Boogie'''
    def write_paths(self):
        for path in self._final_path:
            self._output_file.write(path)

    def is_hex(self, s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

    def add_new_vars(self, var_name):
        self._final_vars[self._var_prefix+'.'+var_name] = MACROS.VAR_TYPES[self._curr_contract][var_name]


    '''helper to find the key of a node'''
    def find_key(self, node):
        if not node.children:
            if isinstance(node.value, str) or (self.is_hex(str(node.value))): 
                # and not (node.value == 0xffffffffffffffffffffffffffffffffffffffff):
                return node.value # or self.postorder_traversal(node)
        # if isintance(node, dict):
        #     return node
        for c in node.children:
            if not isinstance(c, tuple):
                return_val = self.find_key(c)
                if return_val:
                    return return_val

    '''helper to find the map ID'''
    def find_mapID(self, node):
        if node.value == "MapElement":
            return node.children[0]
        for c in node.children:
            self.find_mapID(c)

    ''' helper to inspect the data structures'''
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
        elif what == "currstack":
            # for stack_name in self._stacks:
            print("-----Stack: "+self._curr_contract+"-----")
            c=0
            for elem in self._stacks[-1][::-1]:
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
        elif what == "currmemory":
            print("-----Memory: "+self._curr_contract+"-----")
            temp = self._memories[-1]
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

'''
main symexec 
'''
def main():
    ''' read user arguments: [solidity, theorem, trace] '''
    ARGS = sys.argv
    MACROS.SOLIDITY_FNAME  = ARGS[1]
    MACROS.THEOREM_FNAME   = ARGS[2]
    MACROS.TRACE_FNAME     = ARGS[3]
    MACROS.BOOGIE          = MACROS.TRACE_FNAME[:-4]+".bpl"

    ''' initial generation of solc files and essential trace '''
    gen_solc()
    CONTRACT_NAME,FUNCTION_NAME = get_contract_and_function_names()
    MACROS.CONTRACT_NAME    = CONTRACT_NAME
    MACROS.FUNCTION_NAME    = FUNCTION_NAME
    VAR_PREFIX              = get_init_var_prefix() 
    check_entrypoint()
    gen_trace_essential()
    ABI_INFO    = get_ABI_info()
    STOR_INFO   = get_STORAGE_info()
    

    ''' parameters setup ''' 
    STACKS      = gen_init_STACK(VAR_PREFIX, ABI_INFO)
    STORAGE     = gen_init_STORAGE()
    MEMORIES    = gen_init_MEMORY()
    BOOGIE_OUT  = open(MACROS.BOOGIE, "w")
    PATHS       = []
    CALL_STACK  = gen_init_CALL_STACK(VAR_PREFIX)
    
    HYPOTHESIS  = get_hypothesis()
    INVARIANTS  = get_invariant()
    VARS        = get_init_vars(STOR_INFO,VAR_PREFIX)
    TRACE       = gen_path()
    MAP         = get_MAPS(STOR_INFO)
    MACROS.VAR_TYPES = get_types(STOR_INFO)
   

    ''' run EVM trace instructions '''
    evm = EVM(STACKS, STORAGE, MAP, MEMORIES, BOOGIE_OUT, PATHS, VARS, CONTRACT_NAME, FUNCTION_NAME, CALL_STACK, ABI_INFO, VAR_PREFIX)
    print('inputs: ', MACROS.SOLIDITY_FNAME, MACROS.THEOREM_FNAME, MACROS.TRACE_FNAME)
    print('\n(executing instructions...)')
    evm.sym_exec(TRACE)

    ''' write Boogie output '''
    BOOGIE_OUT.write(MACROS.PREAMBLE)
    BOOGIE_OUT.write(write_params(ABI_INFO,VAR_PREFIX))
    evm.write_vars() # aux vars for Boogie Proofs 
    BOOGIE_OUT.write(write_hypothesis(HYPOTHESIS,VAR_PREFIX))
    BOOGIE_OUT.write(write_invariants(INVARIANTS,VAR_PREFIX))
    evm.write_paths() # codegen for Boogie proofs
    BOOGIE_OUT.write(write_epilogue(INVARIANTS,VAR_PREFIX))
 
if __name__ == '__main__':
    main()