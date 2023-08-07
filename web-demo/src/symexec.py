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
    from memory import recognize_32B_mask, mem_item_len, content_item_len, handle_MLOAD, handle_MSTORE, handle_AND, handle_OR, memory_write
    def __init__(self, stacks, storage, storage_map, memories, output_file, final_path, final_vars, curr_contract, curr_function, call_stack, abi_info, var_prefix, non_static_calls): 
        self._stacks            = stacks  
        self._storage           = storage
        self._memories          = memories
        self._output_file       = output_file
        self._tmp_var_count     = 0
        self._final_path        = final_path
        self._final_vars        = final_vars
        self._storage_map       = storage_map
        self._curr_contract     = curr_contract
        self._curr_function     = curr_function
        self._call_stack        = call_stack
        self._abi_info          = abi_info
        self._var_prefix        = var_prefix
        self._return_data_size  = 0
        self._non_static_calls  = non_static_calls
        self._postcondition     = get_postcondition()

    '''perform symbolic execution'''
    def sym_exec(self, code_trace):
        for i in range(len(code_trace)):
            # try:
                if(code_trace[i][1]=="JUMPI"):
                    self.run_instruction(code_trace[i], (code_trace[i][0]+1 != code_trace[i+1][0]))
                else:
                    self.run_instruction(code_trace[i], None)
            # except:
            #     self.inspect("currstack")
            #     self.inspect("currmemory")
            #     self.write_vars()
            #     self.write_paths()
            #     sys.exit()
            
    def isAddress(self, operand):
        if not isinstance(operand,str):
            return False
        i = operand.find('[');
        name= operand[0:i] if i>=0 else operand

        if name in self._final_vars:
            t=self._final_vars[name]
        else:
            return False
            
        bracket_count = operand.count(']')
        start = -1
        for _ in range(bracket_count):
            start = t.find(']', start + 1)
            if start == -1:
                return False
        return t[start+1:].strip()=="address"

    '''run each EVM instruction with PC, operator, and operand'''        
    def run_instruction(self, instr, branch_taken):
        PC      = instr[0]
        opcode  = instr[1]
        operand = instr[2]

        if opcode=="JUMPDEST" or opcode=="CALL" or opcode=="STATICCALL":
            if (opcode=="CALL"):
                self._non_static_calls.append("non-static")
            elif (opcode=="STATICCALL"):
                self._non_static_calls.append("static")
            pass # no-op
        elif instr[0]==(">"):
            dest_contract, dest_function = get_dest_contract_and_function(instr)
            
            ### get call or staticcall
            static_idx_diff = 0 if instr.startswith(">>call") else 1
            ### calling a new contract, set up calle stack
            callee_stack    = []
            calldata_pos    = self._stacks[-1][-4+static_idx_diff].value
            calldata_len    = self._stacks[-1][-5+static_idx_diff].value
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
                # if calldata_pos in self._memories[-1]:
                callee_stack.append(self._memories[-1][calldata_pos])
                calldata_pos += 0x20

            this_address = self._stacks[-1][-2]
            this_address = self.postorder_traversal(this_address)
            self._sym_this_addresses.append(SVT(this_address))

            ### switch to a new contract and pops out the operands for a successful CALL operation
            for i in range(7-static_idx_diff):
                self._stacks[-1].pop()
            self._stacks[-1].append(SVT(1)) # CALL successed
            dest_address = get_var_prefix(instr)
            self._full_address = get_curr_address(instr)
            #dict.push{self._full_address:self._sym_this_addresses[-1]}

            # self._var_prefix = dest_address
            self._call_stack.append((dest_contract, dest_function, dest_address))
            self._curr_contract = dest_contract
            self._curr_function = dest_function
            MACROS.CONTRACT_NAME = self._curr_contract
            MACROS.FUNCTION_NAME = self._curr_function
            for asgmt in self._postcondition[self._curr_contract].get(self._curr_function, {}).get("assignment", []):
                self._final_path.append("\t" + asgmt.strip() + "\n")
            self._var_prefix = self._curr_contract # get_var_prefix(instr)
            self._stacks.append(callee_stack)
            self._memories.append({0x40: SVT(0x80),0x10000000000: SVT(0)}) # temp

            print(">>CALL,  switched to contract: ", self._call_stack[-1][0])
            

            ### TODO: make "this" as the correct mapping to the vars
            if(len(self._non_static_calls)>0 and self._non_static_calls[-1] == "non-static"):
                self._non_static_calls[-1] = self._var_prefix
                for contract in MACROS.INVARIANTS:
                    if (contract == dest_contract):
                        # if (len(MACROS.INVARIANTS[dest_contract])>0):
                        self._final_path.append("\t// insert invariant of " + dest_contract + '\n')
                        for inv in MACROS.INVARIANTS[dest_contract]:
                            inv = inv.replace("this", self._var_prefix)
                            # print(">>>>>", inv)
                            # expr = name_substitution(self._var_prefix, inv)
                            # print(">>>>>>>", expr)
                            self._final_path.append("\tassume("+inv+");\n")
                        self._final_path.append("\n")

            # sys.exit()
        elif instr[0]==("<"):
            # print(instr)
            pass
        elif opcode=="RETURN" or opcode=="STOP":

            # print("----BEFORE----")
            # self.inspect("currstack")
            # self.inspect("currmemory")
            self._return_data_size =0

            if(len(self._non_static_calls)>0 and self._non_static_calls[-1] == "static"):
                self._non_static_calls.pop()
            else:
                # print(MACROS.INVARIANTS)
                # for contract in MACROS.INVARIANTS:
                #     if (contract == self._curr_contract):
                        # print(MACROS.INVARIANTS[contract])
                # if (len(MACROS.INVARIANTS.get(self._curr_contract, []))>0):
                self._final_path.append("\t// (post) insert invariant of " + self._curr_contract + '\n')
                for inv in MACROS.INVARIANTS.get(self._curr_contract, []):
                    inv = inv.replace("this", self._var_prefix)
                    self._final_path.append("\tassert("+inv+");\n")
                    self._final_path.append("\n")

            postcons = self._postcondition[self._curr_contract].get(self._curr_function, {}).get("postcondition", [])
            if postcons:
                self._final_path.append("\t// (post) insert postcondition of " + self._curr_function + '\n')
                for postcon in postcons:
                    self._final_path.append("\t" + postcon.strip() + "\n")

            if opcode=="RETURN":
                return_data_start = self._stacks[-1][-1].value
                self._return_data_size = self._stacks[-1][-2].value
                pos_src = return_data_start
                pos_dst = self._memories[-2][0x40].value
                count = self._return_data_size
                while count>0:  
                    data = self._memories[-1][pos_src]
                    self.memory_write(pos_dst, data, 32, -2)
                    pos_src+=32
                    pos_dst+=32
                    count-=32
            elif opcode=="STOP":
                self._return_data_size = 0
            # print(self._call_stack)
            
            self._call_stack.pop()
            self._curr_contract = self._call_stack[-1][0]
            self._curr_function = self._call_stack[-1][1]
            MACROS.CONTRACT_NAME = self._curr_contract
            MACROS.FUNCTION_NAME = self._curr_function
            # self._var_prefix = self._call_stack[-1][2]
            self._stacks.pop()
            self._memories.pop()   
            self._sym_this_addresses.pop()     
            self._var_prefix = self._curr_contract
            print(">>LEAVE, switched to contract: ", self._call_stack[-1][0])
            

            
            # print("----AFTER----")
            # self.inspect("currmemory")
        elif opcode=="GAS":
            self._stacks[-1].append(SVT("GAS"))  
        elif opcode=="RETURNDATASIZE":
            # for elmt in self._abi_info["contracts"][self._curr_contract]["abi"]:
                # if ("name" in elmt.keys() and elmt["name"] == self._curr_function):
                #     return_count = len(elmt["outputs"])
                #     if(return_count == 0):
                #         self._stacks[-1].append(SVT(0))
                #     else:
            self._stacks[-1].append(SVT(self._return_data_size))
        elif opcode=="TIMESTAMP":
            self._stacks[-1].append(SVT("BLOCKTIME"))
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
                self.add_new_vars(stored_value)
                self._stacks[-1].append(SVT(stored_value+"["+self.postorder_traversal(self._sym_this_addresses[-1])+"]"))
        elif opcode=="PC":
            self._stacks[-1].append(SVT(PC))
        elif opcode.startswith("LOG"):
            position=int(re.search('[0-9]+', opcode)[0])
            for _ in range(position+2):
                self._stacks[-1].pop()
        elif opcode.startswith("PUSH"):
            self._stacks[-1].append(SVT(operand))
        elif opcode.startswith("POP"):
            self._stacks[-1].pop()
        elif opcode.startswith("CALLER"):
            self._stacks[-1].append(self._sym_this_addresses[-2]) 
        elif opcode.startswith("ORIGIN"):
            self._stacks[-1].append(SVT("tx_origin")) # symbolic
        elif opcode.startswith("DUP"):
            position=int(re.search('[0-9]+', opcode)[0])
            self._stacks[-1].append(self._stacks[-1][len(self._stacks[-1])-position]) 
        elif opcode.startswith("SWAP"):
            position=int(re.search('[0-9]+', opcode)[0])
            dest = self._stacks[-1][len(self._stacks[-1])-position-1] 
            self._stacks[-1][len(self._stacks[-1])-position] = self._stacks[-1].pop()
            self._stacks[-1].append(dest)
        elif opcode=="ISZERO":
            if isinstance(self._stacks[-1][-1].value, int):
                val = self._stacks[-1].pop().value
                # if val == 0:
                self._stacks[-1].append(SVT(1 if val==0 else 0))
                # else:
                #     self._stacks[-1].append(SVT(0))
            else:
                node = SVT(opcode)
                node.children.append(self._stacks[-1].pop())
                self._stacks[-1].append(node)
        elif opcode=="NOT":
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
        elif opcode=="ADD" or opcode=="LT" or opcode=="GT" or opcode=="EQ" or opcode=="SUB" or opcode=="DIV" or opcode=="EXP" or opcode=="SHL" or opcode=="SLT" or opcode=="MUL" or opcode=="SHR" or opcode=="MOD":            
            if isinstance(self._stacks[-1][-1].value, int) and isinstance(self._stacks[-1][-2].value, int):
                if opcode == "ADD":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    node = SVT((val1 + val2)%2**256) 
                elif opcode == "SUB":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    node = SVT((val1 - val2)%2**256)
                elif opcode == "MUL":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    node = SVT((val1 * val2)%2**256)
                elif opcode == "DIV":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    node = SVT((val1 // val2)%2**256)
                elif opcode == "EXP":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    node = SVT((val1 ** val2)%2**256)
                elif opcode == "SHL":
                    shift= self._stacks[-1].pop().value
                    base = self._stacks[-1].pop().value
                    node = SVT((base << shift)%2**256)
                elif opcode == "SHR":
                    shift = self._stacks[-1].pop().value
                    base = self._stacks[-1].pop().value
                    node = SVT(base >> shift) 
                elif opcode == "MOD":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    node = SVT(val1 % val2)
                elif opcode == "LT" or opcode == "SLT":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    result = val1 < val2
                    node = SVT(1) if result else SVT(0)
                elif opcode == "GT":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    result = val1 > val2
                    node = SVT(1) if result else SVT(0)
                elif opcode == "EQ":
                    val1 = self._stacks[-1].pop().value
                    val2 = self._stacks[-1].pop().value
                    result = val1 == val2
                    node = SVT(1) if result else SVT(0)
            else:
                if opcode == "DIV" and self._stacks[-1][-2].value == 1:
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
                mapID = self._memories[-1][start_offset+32]
                if(mapID.value!="MapElement"):
                    var_name = self._var_prefix+'.'+self._storage_map[self._curr_contract][str(mapID.value)]
                    self.add_new_vars(var_name)
                    node.children.append(SVT(var_name))
                else:
                    node.children.append(mapID)
                node.children.append(self._memories[-1][start_offset])
                self._stacks[-1].pop() # pop 64
                self._stacks[-1].append(node)
            else:
                self._stacks[-1].pop()    #ToDo: this is a temporary patch. It makes the stack layout correct. The content is still incorrect.
                self._stacks[-1].pop()
                self._stacks[-1].append(SVT(0xdeadbeef))
        elif opcode=="ADDRESS":
            self._stacks[-1].append(self._sym_this_addresses[-1])
        elif opcode=="CALLDATACOPY": # for swap trace
            destOffset  = self._stacks[-1].pop()
            offset      = self._stacks[-1].pop()
            size        = self._stacks[-1].pop()
        elif opcode=="CALLDATASIZE":
            self._stacks[-1].append(SVT("CALLDATASIZE"))
        else:
            print('[!]',str(instr), 'not supported yet')
            self.inspect("currstack")
            self.inspect("currmemory")
            raise Exception("not handled") 
            # sys.exit()
        # self.inspect("currstack")
        # self.inspect("currmemory")
    
    '''recursively traverse an SVT node'''
    def postorder_traversal(self, node):
        to_return = ""
        if not node.children:
            return node.value

        if node.value == "ISZERO":
            to_return = self.postorder_traversal(node.children[0])
            if isinstance(to_return, int):
                if to_return == 0:
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
                    to_boogie = "\ttmp" + str(self._tmp_var_count) + ":=tmp" + str(val1) + "==Zero;\n"
                node.value = to_return
                node.children = []
                self._final_vars[to_return] = 'bool'
                self._final_path.append(to_boogie)
        elif node.value == "SLOAD":
            sym_this = self.postorder_traversal(self._sym_this_addresses[-1])
            if node.children[0].value=="MapElement":
                if node.children[0].children[0].value=="MapElement": 
                    map_ID = node.children[0].children[0].children[0].value
                    self.postorder_traversal(node.children[0].children[0].children[1])
                    self.postorder_traversal(node.children[0].children[1])
                    map_key1 = self.find_key(node.children[0].children[0].children[1])
                    map_key2 = self.find_key(node.children[0].children[1])
                    key_for_boogie = f"[{sym_this}][{str(map_key1)}][{str(map_key2)}]"
                    var_name = map_ID+key_for_boogie
                else:
                    map_ID  = node.children[0].children[0].value
                    self.postorder_traversal(node.children[0].children[1])
                    map_key = self.find_key(node.children[0].children[1])
                    key_for_boogie = f"[{sym_this}][{str(map_key)}]"
                    var_name = map_ID + key_for_boogie
            # else:
            #     map_ID = node.children[0].value
            self._tmp_var_count+=1
            to_return = "tmp" + str(self._tmp_var_count)
            # var_name  = self._storage_map[self._curr_contract][str(map_id)]
            self.add_new_vars(var_name)
            to_boogie = "\ttmp"+str(self._tmp_var_count)+":="+ var_name

            # if node.children[0].value=="MapElement":
            #     to_boogie += key_for_boogie
            to_boogie +=";\n"
            node.value = to_return
            node.children = []
            self._final_vars[to_return] = self._final_vars[map_ID].split()[-1] # patch
            self._final_path.append(to_boogie) 
        elif node.value == "LT" or node.value == "GT" or node.value == "EQ" or node.value == "SLT": #TODO: SLT implementation
            if node.value == "EQ" and node.children[0] == node.children[1]:
                to_return = "true"
            else:
                val1 = self.postorder_traversal(node.children[0])
                val2 = self.postorder_traversal(node.children[1])
                if (str(val1).isdigit() and MACROS.NUM_TYPE == "real"):
                     val1 = str(val1)+'.0'
                if (str(val2).isdigit() and MACROS.NUM_TYPE == "real"):
                     val2 = str(val2)+'.0'
                if isinstance(val1, int) and isinstance(val2, int):
                    to_return = ""
                    if node.value == "LT" or node.value == "SLT": #TODO: SLT implementation
                        to_return = "true" if val1 < val2 else "false"
                    elif node.value == "GT":
                        to_return = "true" if val1 > val2 else "false"
                    elif node.value == "EQ":
                        to_return = "true" if val1 == val2 else "false"
                # elif node.value == "EQ" and val1 == val2:
                #     to_return = "true"
                else:
                    self._tmp_var_count+=1
                    to_return = "tmp" + str(self._tmp_var_count)
                    if node.value == "LT" or node.value == "SLT": #TODO: SLT implementation
                        to_boogie = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"<"+str(val2)+");\n"
                    elif node.value == "GT":
                        to_boogie = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+">"+str(val2)+");\n"
                    elif node.value == "EQ":
                        to_boogie = "\ttmp"+str(self._tmp_var_count)+":= ("+str(val1)+"=="+str(val2)+");\n"
                    node.value = to_return
                    node.children = []
                    self._final_vars[to_return] = 'bool'
                    self._final_path.append(to_boogie) 
        elif node.value == "ADD" or node.value == "SUB" or node.value == "AND" or node.value == "OR" or node.value == "MUL" or node.value == "DIV" or node.value == "MOD": # DIV, MUL
            val1=self.postorder_traversal(node.children[0])
            val2=self.postorder_traversal(node.children[1])           
            if isinstance(val1, int) and isinstance(val2, int):
                if (str(val1).isdigit() and MACROS.NUM_TYPE == "real"):
                         val1 = str(val1)+'.0'
                if (str(val2).isdigit() and MACROS.NUM_TYPE == "real"):
                         val2 = str(val2)+'.0'
                if node.value == "ADD":
                    to_return = val1 + val2
                elif node.value == "SUB":
                    to_return = val1 - val2
                elif node.value == "AND":
                    to_return = val1 & val2
                elif node.value == "OR":
                    to_return = val1 | val2
                elif node.value == "MUL":
                    to_return = val1 * val2
                elif node.value == "DIV":
                    to_return = val1 / val2
            # elif (isinstance(val2, int) and val2 == 0) and (node.value == "MUL" or node.value == "SUB" or node.value == "ADD"):
            #     if node.value == "MUL":
            #         to_return = 0
            #     elif node.value == "SUB" or node.value == "ADD":
            #         to_return = val1
            else:
                self._tmp_var_count+=1
                to_return =  "tmp" + str(self._tmp_var_count)
                if (val1 in self._final_vars and self._final_vars[val1] == 'bool') or (val2 in self._final_vars and self._final_vars[val2] == 'bool'):
                    if isinstance(val1, int):
                        str_val1="false" if val1==0 else "true"
                    else:
                        str_val1=str(val1)
                    if isinstance(val2, int):
                        str_val2="false" if val2==0 else "true"
                    else:
                        str_val2=str(val2)
                    if node.value == "AND":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":="+str_val1+"&&"+str_val2+";\n"
                    elif node.value == "OR":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":="+str_val1+"||"+str_val2+";\n"
                    self._final_vars[to_return] = 'bool'
                elif  node.value == "SUB" and (self.isAddress(val1) or self.isAddress(val2)):
                    to_boogie ="\ttmp"+str(self._tmp_var_count)+":=("+str(val1)+"!="+str(val2)+");\n"   
                    self._final_vars[to_return] = 'bool'
                else:
                    if (str(val1).isdigit() and MACROS.NUM_TYPE == "real"):
                         val1 = str(val1)+'.0'
                    if (str(val2).isdigit() and MACROS.NUM_TYPE == "real"):
                         val2 = str(val2)+'.0'
                    if node.value == "ADD":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmadd("+str(val1)+","+str(val2)+");\n"
                    elif node.value == "SUB":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmsub("+str(val1)+","+str(val2)+");\n"    
                    elif node.value == "AND":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmand("+str(val1)+","+str(val2)+");\n"
                    elif node.value == "OR":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmor("+str(val1)+","+str(val2)+");\n"
                        print(f"{val1}   {type(val1)}")
                    elif node.value == "MUL":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmmul("+str(val1)+","+str(val2)+");\n"
                    elif node.value == "DIV":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmdiv("+str(val1)+","+str(val2)+");\n"
                    if node.value == "MOD":
                        to_boogie ="\ttmp"+str(self._tmp_var_count)+":=evmmod("+str(val1)+","+str(val2)+");\n"
                    self._final_vars[to_return] = 'uint256'
                node.value = to_return
                node.children = []
                self._final_path.append(to_boogie)
        elif node.value == "Partial32B":
            to_return = self.postorder_traversal(node.children[1])
        elif node.value == "SHL":
            shift = self.postorder_traversal(node.children[0])
            val = self.postorder_traversal(node.children[1])
            to_return = val << shift
            node.value = to_return
            node.children = []
        elif node.value == "ACCOUNT_CODESIZE":
            self._tmp_var_count+=1
            to_return =  "tmp" + str(self._tmp_var_count)
            to_boogie ="\ttmp"+str(self._tmp_var_count)+":=nondet(); //EXTCODESIZE\n"
            self._final_vars[to_return] = 'uint256'
            node.value = to_return
            node.children = []
            self._final_path.append(to_boogie)
        else:
            return str(node)
        return to_return
    
    '''generate boogie code when SSTORE happens'''
    def boogie_gen_sstore(self, node0, node1):
        sym_this = str(self.postorder_traversal(self._sym_this_addresses[-1]))
        if node0.value=="MapElement":
            if node0.children[0].value=="MapElement": 
                map_ID = (node0.children[0].children[0])
                self.postorder_traversal(node0.children[0].children[1])
                self.postorder_traversal(node0.children[1].children[1])
                map_key1 = self.find_key(node0.children[0].children[1])
                map_key2 = self.find_key(node0.children[1].children[1])
                if "." in str(map_ID):
                    var_name = f"{map_ID}[{sym_this}][{map_key1}][{map_key2}]"
                else:
                    var_name = f"{self._storage_map[self._curr_contract][str(map_ID)]}[{sym_this}][{str(map_key1)}][{str(map_key2)}]"
            else:
                map_ID = self.find_mapID(node0)
                self.postorder_traversal(node0.children[1])
                map_key = self.find_key(node0.children[1])
                if "." in str(map_ID):
                    var_name = f"{str(map_ID)}[{sym_this}][{str(map_key)}]"
                else:
                    var_name = f"{self._storage_map[self._curr_contract][str(map_ID)]}[{sym_this}][{str(map_key)}]"
        else:
            var_name = f"{self._var_prefix}.{self._storage_map[self._curr_contract][str(node0.value)]}[{sym_this}]"
        path="\t"+var_name+":=" + str(self.postorder_traversal(node1))
        if isinstance(node1.value,int) and MACROS.NUM_TYPE == "real":
            path+=".0"
        path+=";\n\n"
        self.add_new_vars(var_name)
        self._final_path.append(path)
        

    def is_called_param(self, map_key):
        if (re.search("c\_(.*).\_", map_key)):
            print(map_key, "TRUE")
            return True
        print(map_key, "FALSE")    
        return False

    '''generate boogie code when JUMPI happens'''         
    def boogie_gen_jumpi(self, node, isNotZero):
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
                path = "\tassume("+ var +"!=Zero);\n\n"
            else:    
                path = "\tassume("+ var +"==Zero);\n\n"
        else:
            raise Exception("JUMPI stack[-1] is_not_zero error")
        self._final_path.append(path)
        # self.write_paths()
        # sys.exit()

    '''write aux vars to Boogie'''
    def write_vars(self):
        for var in self._final_vars.keys():
            MACROS.ALL_VARS[var] = self._final_vars[var]
            if var.startswith("tmp"):
                self._output_file.write("\tvar " + var + ":  " + self._final_vars[var] + ";\n")
        self._output_file.write("\n")
    
    '''write global vars to Boogie'''
    def write_global_vars(self):
        modified = []
        for var in self._final_vars.keys():
            MACROS.ALL_VARS[var] = self._final_vars[var]
            if not var.startswith("tmp"):
                modified.append(var)
                self._output_file.write("var " + var + ":  " + self._final_vars[var] + ";\n")
        self._output_file.write("\n")

        self._output_file.write("""procedure straightline_code ()
modifies """)
        for i in range(len(modified)-1):
            self._output_file.write(modified[i] + ", ")
        self._output_file.write(modified[-1] + ";\n")
        self._output_file.write("""{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
""")


    '''write declared vars to Boogie'''
    def write_declared_vars(self):
        declaration = self._postcondition.get(self._curr_contract, []).get(self._curr_function, []).get("declaration", [])
        for decl in declaration:
            decl = decl.replace("this", self._curr_contract)
            self._output_file.write("\t" + decl + "\n")
        self._output_file.write("\n")

    '''write entry assignment to Boogie'''
    def write_entry_assignment(self):
        for asgmt in self._postcondition[self._curr_contract].get(self._curr_function, {}).get("assignment", []):
            asgmt = asgmt.replace("this", self._curr_contract).strip()
            self._output_file.write("\t" + asgmt.strip() + "\n")
        self._output_file.write("\n")
    
    '''write entry postcondition to Boogie'''
    def write_entry_postcondition(self):
        postcons = self._postcondition[self._curr_contract].get(self._curr_function, {}).get("postcondition", [])
        if postcons:
            self._output_file.write("\t// (post) insert postcondition of " + self._curr_function + '\n')
            for postcon in postcons:
                postcon = postcon.strip(";")
                expression = name_substitution(self._curr_contract, postcon)
                self._output_file.write("\tassert(" + expression + ");\n")
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
        mapping = get_var_mapping(var_name)
        var_name = var_name.split('[')[0]
        var_type = ""
        if var_name in self._final_vars:
            return
        else:
            var_type += "[address] "
            for i in range(1, len(mapping)):
                if mapping[i][mapping[i].find("[")+1:mapping[i].find("]")].isnumeric():
                    mapping[i] = mapping[i][:mapping[i].find("[")]
                var_type += "[" + self._final_vars[mapping[i]] + "] "
            # elif ('][' in var_name):
            #     self._final_vars[var_name] = 'address' # patch

            if ('.' in var_name):
                self._final_vars[var_name] = var_type + MACROS.VAR_TYPES[self._curr_contract][var_name[var_name.find('.')+1:]]
            else:
                self._final_vars[self._var_prefix+'.'+var_name] = var_type + MACROS.VAR_TYPES[self._curr_contract][var_name]

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
    VAR_PREFIX              = CONTRACT_NAME # get_init_var_prefix() 
    check_entrypoint()
    entry_contract_address=gen_trace_essential()[0]
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
    MACROS.INVARIANTS  = get_invariant()
    VARS        = get_init_vars(STOR_INFO, ABI_INFO, VAR_PREFIX)
    TRACE       = gen_path()
    MAP         = get_MAPS(STOR_INFO)
    MACROS.VAR_TYPES = get_types(STOR_INFO)
    MACROS.NUM_TYPE  = get_numerical_type()
    MACROS.DEF_VARS  = get_defvars()



    ''' run EVM trace instructions '''
    evm = EVM(STACKS, STORAGE, MAP, MEMORIES, BOOGIE_OUT, PATHS, VARS, CONTRACT_NAME, FUNCTION_NAME, CALL_STACK, ABI_INFO, VAR_PREFIX, [])
    evm._sym_this_addresses  = [SVT("tx_origin"),SVT("entry_contract")]
    print('inputs: ', MACROS.SOLIDITY_FNAME, MACROS.THEOREM_FNAME, MACROS.TRACE_FNAME)
    print('\n(executing instructions...)')
    evm.sym_exec(TRACE)

    ''' write Boogie output '''
    if (MACROS.NUM_TYPE == 'real'):
        BOOGIE_OUT.write(MACROS.PREAMBLE_REAL)
    elif (MACROS.NUM_TYPE == 'int'):
        BOOGIE_OUT.write(MACROS.PREAMBLE_INT)

    evm.write_global_vars()
    # BOOGIE_OUT.write(write_params(ABI_INFO,VAR_PREFIX))
    evm.write_vars() # aux vars for Boogie Proofs
    evm.write_declared_vars() # postcondition vars for Boogie proofs

    BOOGIE_OUT.write(write_defvars(VAR_PREFIX))
    BOOGIE_OUT.write(write_hypothesis(HYPOTHESIS,VAR_PREFIX))

    # BOOGIE_OUT.write(write_invariants(MACROS.INVARIANTS,VAR_PREFIX))

    evm.write_paths() # codegen for Boogie proofs
    evm.write_entry_assignment() # from AST file
    evm.write_entry_postcondition() # from AST file
    BOOGIE_OUT.write(write_epilogue(MACROS.INVARIANTS,VAR_PREFIX))
 
if __name__ == '__main__':
    main()