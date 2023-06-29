####################################
#  Operations realted to memory    # 
####################################
from symexec import SVT

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