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


class EVM:

    def __init__(self, stacks, storage, storage_map, memories, output_file, final_path, final_vars, curr_contract, curr_function, call_stack, abi_info, stor_info): 
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
        self._stor_info = stor_info


    def write_preamble(self):
        self._output_file.write("""type address = int;
type uint256 = int;
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

procedure straightline_code ()
{  
    var msg.sender: address ;  
""")
                 
                                
    def write_storages(self, storage_info):
        # self._output_file.write("===========\n")
        for elmt in storage_info[self._curr_contract]["storage"]:
            label = (elmt["label"])
            t_type = elmt["type"]
            if ("string" in t_type):
                pass
            elif "t_mapping" in t_type:
                t_type = t_type.replace("t_", "")
                t_type = t_type.replace("mapping", "")[1:-1]
                t_type = t_type.split(',')
                self._output_file.write("\tvar " + label + ':['+t_type[0]+'] ' + t_type[1] + ';\n')
            else:
                self._output_file.write("\tvar " + label + ":\t" + t_type[2:] + ";\n")
        # self._output_file.write("===========\n")    
        # self._output_file.write(storage_info[self._curr_contract]["storage"][1]["label"])
        # for elmt in storage_info[self._curr_contract]:
        #     self._output_file.write(elmt)
            # for item in elmt["storage"]:
                # self._output_file["label"]
            #         for input in elmt["inputs"]:
            #             self._output_file.write("\tvar " + input["name"] + ":\t" + input["type"]+'\n')


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
        self._output_file.write('}')


    def write_vars(self):

        # self._output_file.write("=============\n")

        for elmt in self._abi_info[self._curr_contract]:
            if ("name" in elmt.keys() and elmt["name"] == self._curr_function):
                for input in elmt["inputs"]:
                    # if ("string" not in input["type"]):
                    self._output_file.write("\tvar " + input["name"] + ":\t" + input["type"]+';\n')
                    # self._output_file.write(input["name"]+"\n")
                    # self._output_file.write(input["type"]+"\n")
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
        print(node0)
        if node0.value=="MapElement":
            map_key = self.find_key(node0.children[1])
            path="\t"+self._storage_map[str(self.find_mapID(node0))]+"["+str(map_key)+"]:=" + str(self.postorder_traversal(node1))+";\n\n"
        else:
            path="\t"+self._storage_map[str(node0.value)]+":=" + str(self.postorder_traversal(node1))+";\n\n"
        self._final_path.append(path)
        # print("\n[code gen SSTORE]")
        # print(node0)
        # print(node1)
        # print(path)
        
            
                      
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


        # if (node.value == 1):
        #     path = "\tassume(true);\n\n"
        # else:
        # # print(">>>>>", node)
        #     path = "\tassume("+str(self.postorder_traversal(node))+");\n\n"
        
        self._final_path.append(path)
        # print("\n[code gen JUMPI]") 
        # print(node)
        # print(path)


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
        # return_string += "("
        # for child in node.children:
        #     return_string += self.postorder_traversal(child)
        #     return_string += ","
        # return_string += ")"
        # return_string += str(node.value)
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
            if node.children[0].value=="MapElement":
                map_id = self.find_mapID(node.children[0])
                map_key = self.find_key(node.children[0].children[1])
            else:
                map_id = node.children[0].value
            
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            # print_string = "\ttmp"+str(self._tmp_var_count)+":=mapID"+str(map_id)+"["+str(map_key)+"];\n"
            # print(str(map_id))
            print_string = "\ttmp"+str(self._tmp_var_count)+":="+self._storage_map[str(map_id)]
            if node.children[0].value=="MapElement":
                print_string +="["+str(map_key)+"]"
            print_string +=";\n"
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
        else:
            return str(node)
        return return_string
    
    def sym_exec(self, code_trace):
        for i in range(len(code_trace)):
            if(code_trace[i][1]=="JUMPI"):
                self.run_instruction(code_trace[i], (code_trace[i][0]+1 != code_trace[i+1][0]))
            #elif code_trace[i][1]=="EXP":
            #    return
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
    '''
    def set_callStack(self, offset, data):
        stack = [
            SVT("FourByteSelector"),
            SVT("SomethingIDontKnow"),
            offset
        ]
        return stack
    '''
    '''    
    def count_lower_ffs(self, a):
        c = 0
        while a > 0:
            if a % 0x100 != 0xff:
                return -1
            c += 1
            a //= 0x100
        return c
        
    def count_upper_ffs(self, a):
        a = (1<<256) - 1 - a
        return self.count_lower_ffs(a)
    '''

    def recognize_32B_mask(self,a):
        separation_position = None
        if a % 0x100 == 0xff:   # potentially a (?,31) mask
            for i in range(32):
                scanned_byte = a % 0x100
                if scanned_byte != 0x00 and scanned_byte != 0xff:
                    return -1,-1
                if scanned_byte == 0x00 and separation_position==None:
                    separation_position = 32-i   # the position of the left-most 0xff
                if scanned_byte == 0xff and separation_position!=None:
                    return -1,-1
                a//=0x100
            if separation_position == None:
                return 0,31
            else:
                return separation_position,31
        elif a % 0x100 == 0x00:  # potentially a (0,?) mask
            for i in range(32):
                scanned_byte = a % 0x100
                if scanned_byte != 0x00 and scanned_byte != 0xff:
                    return -1,-1
                if scanned_byte == 0xff and separation_position==None:
                    separation_position = 32-i   # the position of the left-most 0x00
                if scanned_byte == 0x00 and separation_position!=None:
                    return -1,-1
                a//=0x100
            if separation_position == None:
                return -1,-1
            else:
                return 0,separation_position-1
        else:
            return -1,-1  #a is not a 32-byte mask
    '''    
    def count_lower_00s(self, a):
        if a == 0:
            return -1
        c = 0
        while a % 0x100 == 0x00:
            c += 1
            a //= 0x100
        return c, a

    '''    
    def mem_item_len(self, mem_item):
        if mem_item.value != "Partial32B":
            return 32
        segment = mem_item.children[0]
        return segment[1]-segment[0]+1
        
    def handle_MLOAD(self):
        offset = self._stacks[self._curr_contract].pop().value
        if not isinstance(offset, int):
                 raise Exception("Memory offset is not a concrete value. CodeGen is needed here!")
            
        prev_k=None
        in_copy_mode = False
        node = SVT("concat")
        bytes_to_copy = 32
        for k,v in self._memories[self._curr_contract].items():
            if k == offset:
                if bytes_to_copy == 32 and self.mem_item_len(self._memories[self._curr_contract][offset]) == 32:
                    return self._memories[self._curr_contract][offset]
                unfilled_position = offset
                in_copy_mode = True
                
            if k > offset and not in_copy_mode:   
            # We have found the place to insert the mem item of offset. It is between prev_k and k
                #print("found k="+hex(k)+"   prev_k"+hex(prev_k))
                prev_len = self.mem_item_len(prev_v)
                #print("prev_len="+hex(prev_len))
                if (offset - prev_k < prev_len):
                #In this case, offset falls into the previous item.
                    ignored_len = offset - prev_k
                    len_to_copy = prev_len - ignored_len
                    node1=SVT("Partial32B")
                    if prev_v!= "Partial32B":
                        node1_segment = (ignored_len,31)
                        node1_value = prev_v
                    else:
                        original_segment = prev_v.children[0]
                        node1_segment = (original_segment[0]+ignored_len, original_segment[1])
                        node1_value = prev_v.children[1]
                    node1.children.append(node1_segment)
                    node1.children.append(node1_value)
                    node.children.append(node1)
                    bytes_to_copy -= len_to_copy
                    unfilled_position = prev_k + prev_len
                else:
                    unfilled_position = offset
                in_copy_mode = True
                
            if in_copy_mode:
                #We handle the bytes between unfilled_position and k                
                len_uninitialized_bytes = k-unfilled_position
                #print("k="+hex(k))
                #print("unfilled_position="+hex(unfilled_position))
                #print("len_uninitialized_bytes="+hex(len_uninitialized_bytes))
                #print("bytes_to_copy="+hex(bytes_to_copy))
                if len_uninitialized_bytes >= 32 and bytes_to_copy==32:                   
                    return SVT(0)
                if len_uninitialized_bytes > 0:
                    
                    node1=SVT("Partial32B")
                    num_zero_bytes = min(len_uninitialized_bytes,bytes_to_copy)
                    #print("num_zero_bytes="+hex(num_zero_bytes))
                    node1.children.append((0,num_zero_bytes-1))
                    node1.children.append(SVT(0))
                    node.children.append(node1)
                    #print(node)
                    bytes_to_copy-=num_zero_bytes
                    unfilled_position+=num_zero_bytes
                    if bytes_to_copy==0:
                        return node
                        
                curr_len = self.mem_item_len(v)
                if bytes_to_copy >= curr_len:
                    # copy the current mem item in entirety 
                    node.children.append(v)
                    bytes_to_copy-=curr_len
                    unfilled_position+=curr_len
                    if bytes_to_copy==0:
                        return node
                else:
                    node1=SVT("Partial32B")
                    if v!= "Partial32B":
                        node1_segment = (0,bytes_to_copy-1)
                        node1_value = v
                    else:
                        original_segment = v.children[0]
                        node1_segment = (original_segment[0], original_segment[1]+bytes_to_copy)
                        node1_value = v.children[1]
                    node1.children.append(node1_segment)
                    node1.children.append(node1_value)
                    #print(node1)
                    node.children.append(node1)
                    bytes_to_copy = 0
                    return node
            prev_k = k
            prev_v = v
        
        # Because memory has dummy item 0x10000:SVT(0), the function should return before the loop ends.
        raise Exception ("In handle_mload. It should always return before the loop ends")
        
    def handle_MSTORE(self):
        offset = self._stacks[self._curr_contract].pop().value
        content_to_store = self._stacks[self._curr_contract].pop()
        content_to_store_len = 32
        if not isinstance(offset, int):
            raise Exception("An MSTORE offset is not int.")
        
        last_partial_overwritten_node=None
        for k,v in self._memories[self._curr_contract].items():
            curr_len=self.mem_item_len(v)
            if k < offset and k+curr_len>offset:
            # This means offset falls in the current mem item
                node1=SVT("Partial32B")
                if v.value == "Partial32B":
                    node1_segment = (v.children[0][0], v.children[0][1]-(k+curr_len-offset))  # retract the current mem item's right end
                    node1_value = v.children[1]
                else:
                    node1_segment = (0,31-(k+curr_len-offset)) # retract the current mem item's right end
                    node1_value = v
                node1.children.append(node1_segment)
                node1.children.append(node1_value)
                self._memories[self._curr_contract][k] = node1
            if k < offset+content_to_store_len and k+curr_len>offset+content_to_store_len:
            # This means the end of content_to_store falls in the current mem item
                node1=SVT("Partial32B")
                if v.value == "Partial32B":
                    node1_segment = (v.children[0][0]+(offset+content_to_store_len-k), v.children[0][1])  # retract the current mem item's left end
                    node1_value = v.children[1]
                else:
                    node1_segment = (offset+content_to_store_len-k,31) # retract the current mem item's left end
                    node1_value = v
                node1.children.append(node1_segment)
                node1.children.append(node1_value)
                last_partial_overwritten_node = node1
                
        if  last_partial_overwritten_node!=None:
            self._memories[self._curr_contract][offset+content_to_store_len] = last_partial_overwritten_node
                
        for k,v in self._memories[self._curr_contract].items():        
            if k > offset and k+curr_len<offset+content_to_store_len:
            # This mem item is completely overwrittn by the MSTORE
                del self._memories[self._curr_contract][k]
        
        if isinstance(content_to_store.value,int) or content_to_store.value != "concat":
            self._memories[self._curr_contract][offset] = content_to_store
        else:
            pos = offset
            for item in content_to_store.children:
                self._memories[self._curr_contract][pos] = item
                pos+=self.mem_item_len(item)

        self._memories[self._curr_contract] = dict(sorted(self._memories[self._curr_contract].items()))  # use sorted dictionary to mimic memory allocation 
        
        memory_with_consolidated_items = {}
        active_k = None
        active_v = None
        for k,v in self._memories[self._curr_contract].items():
            if active_k == None:
                active_k = k
                active_v = v
            elif isinstance(active_v.value,int) or isinstance(v.value,int) \
              or active_v.value!="Partial32B" or v.value!="Partial32B" \
              or active_v.children[1]!=v.children[1] \
              or active_v.children[0][1]+1!=v.children[0][0]:
                #print("active item="+hex(active_item[0])+":"+str(active_item[1]))
                if not isinstance(active_v.value,int) and active_v.value=="Partial32B" \
                   and active_v.children[0][0]==0 and active_v.children[0][1]==31:
                    memory_with_consolidated_items[active_k]=active_v.children[1]
                else:
                    memory_with_consolidated_items[active_k]=active_v
                active_k = k
                active_v = v
            else:
                #active_item[1].children[0]=(active_item[1].children[0][0],item[1].children[0][1])
                new_v=SVT("Partial32B")
                new_v.children.append((active_v.children[0][0],v.children[0][1]))
                new_v.children.append(active_v.children[1])
                active_v = new_v
                
        if not isinstance(active_v.value,int) and active_v.value=="Partial32B" \
           and active_v.children[0][0]==0 and active_v.children[0][1]==31:
            memory_with_consolidated_items[active_k]=active_v.children[1]
        else:
            memory_with_consolidated_items[active_k]=active_v

        self._memories[self._curr_contract] = memory_with_consolidated_items
        
        
    def handle_AND(self):
        a = self._stacks[self._curr_contract].pop()
        b = self._stacks[self._curr_contract].pop()
        segment = None
        if isinstance(a.value, int):
            first,last = self.recognize_32B_mask(a.value)
            if first!=-1:
                segment = (first,last)
                num = b
        elif isinstance(b.value, int):
            first,last = self.recognize_32B_mask(b.value)
            if first!=-1:
                segment = (first,last)
                num = a
        if segment != None:
            if num.value == "Partial32B" and num.children[0][0] == first and num.children[0][1] == last:
            # This means the new Partial32B would be superfuous
                return num
                          
            if num.value == "concat":
                new_concat_node = SVT("concat")
                if last ==31:
                # It is the lower-mask situation
                    left_zero_node= SVT("Partial32B")
                    left_zero_node.children.append((0,first-1))
                    left_zero_node.children.append(SVT(0x0))
                    new_concat_node.children.append(left_zero_node)
                    pos = 0
                    for child in num.children:
                        print(child)
                        if pos>=first:
                            new_concat_node.children.append(child)
                        elif pos+child.children[0][1]-child.children[0][0]+1 > first:
                            newPartial32BNode = SVT("Partial32B")
                            newPartial32BNode.children.append(child.children[0][0]+first-pos,child.children[0][1])
                            newPartial32BNode.children.append(child.children[1])
                            new_concat_node.children.append(newPartial32BNode)
                        pos+= child.children[0][1]-child.children[0][0]+1
                    return new_concat_node
            node = SVT("Partial32B")
            node.children.append((segment))
            node.children.append(num)
        else:
            if isinstance(a.value, int) and isinstance(b.value, int):
                node = SVT((a.value & b.value)%2**256)
            else:
                node = SVT("AND")
                node.children.append(a)
                node.children.append(b)
        return node
        
    def handle_OR(self):
        a = self._stacks[self._curr_contract].pop()
        b = self._stacks[self._curr_contract].pop()
        if a.value == "Partial32B" and b.value == "Partial32B":
            if b.children[0][0]==0:
                tmp=a
                a=b
                b=tmp
            if a.children[0][0]==0 and b.children[0][1] == 31 and a.children[0][1]+1 == b.children[0][0]:
                node = SVT("concat")
                node.children.append(a)
                node.children.append(b)
                return node
                
                
        if a.value == "concat" and b.value == "Partial32B":
            tmp=a
            a=b
            b=tmp
        if a.value == "Partial32B" and b.value == "concat":
            pos = 0
            node = SVT("concat")
            for child in b.children:
                l = pos
                r = pos + child.children[0][1]-child.children[0][0]
                if isinstance(child.children[1].value,int) and child.children[1].value == 0x0 and a.children[0][0]==l and a.children[0][1]==r:
                    newnode = SVT("Partial32B")
                    newnode.children.append(child.children[0])
                    newnode.children.append(a.children[1])
                    node.children.append(newnode)
                else:
                    node.children.append(child)
                pos+= child.children[0][1]-child.children[0][0]+1
            return node
            
            
        if isinstance(a.value, int) and isinstance(b.value, int):
            node = SVT((a.value & b.value)%2**256)
        else:
            node = SVT("OR")
            node.children.append(a)
            node.children.append(b)
        
    def run_instruction(self, instr, branch_taken):
        shuo_count=0
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
        
        
        # if isinstance(PC,int) and int(PC)==174:
        #     print("=======before======")
        #     self.inspect("memory")
        #     self.inspect("stack")
        
        # if opcode=="MSTORE":
        #     print("=======before======")
        #     self.inspect("memory")
        #     self.inspect("stack")
            
        # if opcode=="EXP":
        #     print("=======before======")
        #     self.inspect("memory")
        #     self.inspect("stack")
            
        print(instr)
        

        if instr[0]==(">"):
            # self.inspect("memory")
            # self.inspect("stack")
            info = re.search("\((.*)\)", instr)[0]
            info = info.split("::")
            dest_contract = (info[0][1:])
            dest_function = (info[1][:-1])


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

             # pops out the operands for a successful CALL operation
            for i in range(7):
                self._stacks[self._curr_contract].pop()
            self._stacks[self._curr_contract].append(SVT(1))

            self._call_stack.append((dest_contract, dest_function))
            self._curr_contract = dest_contract
            self._curr_function = dest_function
            # self.inspect("stack")
            print(">>> switched to contract: ", self._call_stack[-1][0])
            print("after switch:", self._call_stack)
            self.inspect("memory")
            self.inspect("stack")
        elif instr[0]==("<"):
            print("before leave:", self._call_stack)
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
            # print(self.inspect("stack"))
            print(instr)
            print(self._stacks[self._curr_contract][-2])

            # if branch taken we assume stack [-1] is not 0 
            # if not taken we should assume [-2] == 0
            # thiss part is kinda 
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
            # print(instr)
            self.boogie_gen_sstore(self._stacks[self._curr_contract].pop(), self._stacks[self._curr_contract].pop())
            # sys.exit()
        elif opcode=="SLOAD":
            # self.inspect("storage") 
            # self.inspect("stack")
            node = SVT("SLOAD")
            node.children.append(self._stacks[self._curr_contract].pop())
            self._stacks[self._curr_contract].append(node)
            #self.inspect("stack")
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
                # self.inspect("stack")
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
            # self.inspect("stack")
        elif opcode=="ADD" or opcode=="LT" or opcode=="GT" or opcode=="EQ" or opcode=="SUB" or opcode=="DIV" or opcode=="EXP" or opcode=="SHL":
            # self.inspect("stack")
            if isinstance(self._stacks[self._curr_contract][-1].value, int) and isinstance(self._stacks[self._curr_contract][-2].value, int):
                if opcode == "ADD":
                    node = SVT((self._stacks[self._curr_contract].pop().value + self._stacks[self._curr_contract].pop().value)%2**256) 
                elif opcode == "SUB":
                    node = SVT((self._stacks[self._curr_contract].pop().value - self._stacks[self._curr_contract].pop().value)%2**256)
                elif opcode == "DIV":
                    node = SVT((self._stacks[self._curr_contract].pop().value // self._stacks[self._curr_contract].pop().value)%2**256)
                elif opcode == "EXP":
                    node = SVT((self._stacks[self._curr_contract].pop().value ** self._stacks[self._curr_contract].pop().value)%2**256)
                elif opcode == "SHL":
                    node = SVT((self._stacks[self._curr_contract].pop().value << self._stacks[self._curr_contract].pop().value)%2**256)
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

                node.children.append(self._memories[self._curr_contract][start_offset+32])
                node.children.append(self._memories[self._curr_contract][start_offset])

                self._stacks[self._curr_contract].pop() # pop 64
                self._stacks[self._curr_contract].append(node)
            # self.inspect("stack")
        else:
            print('[!]',str(instr), 'not supported yet')  
            #sys.exit()
            return
        # self.inspect("stack")
        # if opcode=="MSTORE":
        #     print("=======after======")
        #     self.inspect("memory")
        #     self.inspect("stack")
        
        # if isinstance(PC,int) and int(PC)==860  :
        #     print("=======after======")
        #     self.inspect("memory")
        #     self.inspect("stack")
        #     #raise Exception ("debug stop")
        
        
        
# Note that "FourByteSelector" is at the BOTTOM of the stack     
def set_stack(abi, solidity_fname, contract_name, function_name):
    stack = [
        SVT("FourByteSelector"),      # It would be good to fill in the actual value into this placeholder
        SVT("AConstantBySolc"), 
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
    file.close()
    for n in file_names:
        os.remove(n)
    
    return stack

def set_storage():
    return {
        0: '0x00'
    } 

def set_memory():
    return {
        # We need to understand why this 0x40 is needed. Perhaps need to read more thoroughly the yellow paper, 
        # or ask other people
        0x40: SVT(0x80),
        # Dummy mem item
        0x10000000000: SVT(0)
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
    file.close()
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

def get_FUNCTIONINFO3(storage, solidity_fname):
    STORAGE_file = open(storage, "r")
    tmp = '{'
    lines = STORAGE_file.readlines()
    for line in lines:
        # print("l" + line)
        if len(line.strip()) == 0:
            # print("},")
            line = ",\n"    
        elif '===' in line:
            c_name = line.replace("======= ", "").replace(" =======", "").replace(solidity_fname+":", "").replace("\n", "")
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
    BOOGIE          = TRACE_FNAME[:TRACE_FNAME.find(".")] + ".bpl"

    

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
    STOR_INFO = get_FUNCTIONINFO3(STORAGE, SOLIDITY_FNAME)


    PATHS = []
    VARS  = []
    MAP = get_MAP(STORAGE, SOLIDITY_FNAME, CONTRACT_NAME)    # ToDo: we need the maps for all contracts.
    evm = EVM(STACKS, set_storage(), MAP, MEMORIES, open(BOOGIE, "w"), PATHS, VARS, CONTRACT_NAME, FUNCTION_NAME, [init_CALL], ABI_INFO, STOR_INFO)
    print('\n(pre-execution)')
    
    '''
    first,last = evm.recognize_32B_mask(0xff)
    print (first,last)
    first,last = evm.recognize_32B_mask(0xff * (256**30))
    print (first,last)
    return
    '''
    
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
    evm.write_storages(STOR_INFO)
    evm.write_vars()
    evm.write_hypothesis(THEOREM["hypothesis"])
    evm.write_invariants(INVARIANTS)
    evm.write_paths()
    evm.write_epilogue(INVARIANTS)
 
if __name__ == '__main__':
    main()