import re
import binascii
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
    def __init__(self, stack, storage, memory, output_file):  
        self._stack = stack  
        self._storage = storage
        self._memory = memory
        self._output_file = output_file
        self._tmp_var_count = 0
    
    def write_preamble(self):
        self._output_file.write("""type address;
type uint256 = int;>
var totalSupply: uint256;
const TwoE16 : uint256;
axiom TwoE16 == 65536; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768;
const TwoE256 : int; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;


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
    var tmp1: uint256;
    var tmp2: uint256;
    var tmp3: uint256;

    assume (0<=_value && _value<TwoE255+1 && 0<=_fee && _fee<TwoE255);           
    assume (totalSupply<TwoE255);    
    
    assume (sum(balances) == totalSupply);
    assume (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);            
""")
    
    def write_epilogue(self):
        self._output_file.write("""	
    assert (sum(balances) == totalSupply);         
    assert (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);
}   
""")
    def find_mapID(self, node):
        if node.value == "MapElement":
            print("map_id: ", node.children[0])
            return node.children[0]
        for c in node.children:
            self.find_mapID(c)

    def boogie_gen_sstore(self, node0, node1):
        self.inspect("stack")
        print("gen sstore")
        rt="mapID"+str(self.find_mapID(node0))+"["+node1.value+"]:=" + str(self.postorder_traversal(node0))
        print(rt)
        # self,_output_file.write("mapID"+self.find_mapID(node0)+"["+node1._value"]:=" + self.postorder_traversal(node0))
        print("gen sstore")

                                
    def boogie_gen(self, node):
        self.inspect("stack")
        self._output_file.write("assume("+str(self.postorder_traversal(node))+");\n")
    

    def find_key(self, node):
        if not node.children:
            if isinstance(node.value, str):
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
            # return_string += "tmp"+str(self._tmp_var_count)+":="
            return_string += self.postorder_traversal(node.children[0]) # + "==0;\n"
            val1=self._tmp_var_count
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "tmp" + str(self._tmp_var_count) + ":=tmp" + str(val1) + "==0;\n"
            self._output_file.write(print_string)
        elif node.value == "SLOAD":
            self._tmp_var_count+=1
            # map_id = node.children[0].children[0]
            map_id = self.find_mapID(node.children[0])
            # map_key = node.children[0].children[1].children[1].children[1]
            map_key = self.find_key(node.children[0].children[1])
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "tmp"+str(self._tmp_var_count)+":=mapID"+str(map_id)+"["+str(map_key)+"];\n"
            self._output_file.write(print_string)   
        elif node.value == "LT":
            val1 = self.postorder_traversal(node.children[0])
            val2 = self.postorder_traversal(node.children[1])
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string = "tmp"+str(self._tmp_var_count)+":="+str(val1)+"<"+str(val2)+";\n"
            self._output_file.write(print_string)
        elif node.value == "ADD":
            self._tmp_var_count+=1
            return_string =  "tmp" + str(self._tmp_var_count)
            print_string ="tmp"+str(self._tmp_var_count)+":=evmadd("+str(self.postorder_traversal(node.children[0]))+","+str(self.postorder_traversal(node.children[1]))+");\n"
            self._output_file.write(print_string)

        else:
            return str(node)
        return return_string
    def sym_exec(self, code_trace):
        self.write_preamble()
        for i in range(len(code_trace)):
            if(code_trace[i][1]=="JUMPI"):
                self.run_instruction(code_trace[i], code_trace[i][0]+1 != code_trace[i+1][0])
            else:
                self.run_instruction(code_trace[i], None)
        self.write_epilogue()
        self._output_file.close()
        
    def inspect(self, what):
        if what == "stack":
            print("-----Stack-----")
            c=0
            for elem in self._stack[::-1]:
                print('stack['+str(c)+'] ', elem)
                c=c+1
        elif what == "memory":
            print("-----Memory-----")
            c=0
            for i in range(4):
                print('mem['+str(i)+'] ', self._memory[i])
                c=c+1
        elif what == "storage":
            print("-----Storage-----")
            for key in self._storage:
                print('(', key, ',', self._storage[key], ')')
                

    def run_instruction(self, instr, branch_taken):
        print(instr)
        PC=instr[0]
        opcode=instr[1]
        operand=instr[2]
        
        if opcode=="JUMPDEST" or opcode=="JUMP":
            pass
        elif opcode=="JUMPI":
            self.boogie_gen(self._stack[-2])
            # node = SVT("ISNOTZERO")
            # node.children.append(self._stack[len(self._stack)-2])
            # self._stack.pop()
            # self._stack.append(node)
        elif opcode=="MSTORE":
            mem_offset = self._stack.pop().value
            if not isinstance(mem_offset, int):
                raise Exception("We assume mem offset to be constant.")
            elif mem_offset % 32 != 0:
                raise Exception("We assume mem offset to be a multiple of 32.")
            mem_offset //= 32
            value = self._stack.pop()
            self._memory[mem_offset] = value
            self.inspect("memory")
        elif opcode=="MLOAD":
            self._stack.append(self._memory[len(self._stack)-1]) 
            # self.inspect("stack")
            self.inspect("memory")
        elif opcode=="SSTORE":
            # node = SVT("SSTORE")
            # node.children.append(self._stack[-1])
            # node.children.append(self._stack[-2])
            self.boogie_gen_sstore(self._stack.pop(), self._stack.pop())
        elif opcode=="SLOAD":
            self.inspect("storage")
            node = SVT("SLOAD")
            node.children.append(self._stack.pop())
            self._stack.append(node)
        elif opcode=="PC":
            self._stack.append(SVT(PC))
        elif opcode.startswith("PUSH"):
            self._stack.append(SVT(operand))
        elif opcode.startswith("POP"):
            self._stack.pop()
        elif opcode.startswith("CALLER"):
            self._stack.append(SVT("msg.sender")) 
        elif opcode.startswith("ORIGIN"):
            self._stack.append(SVT("tx.origin"))
        elif opcode.startswith("DUP"):
            # position=int(opcode[len("DUP")]) ## include cases such as `DUP16`
            position=int(re.search('[0-9]+', opcode)[0])
            self._stack.append(self._stack[len(self._stack)-position]) 
        elif opcode.startswith("SWAP"):
            position=int(re.search('[0-9]+', opcode)[0])
            dest = self._stack[len(self._stack)-position-1] 
            self._stack[len(self._stack)-position] = self._stack.pop()
            self._stack.append(dest)
            # self._stack.append(self._stack[len(self._stack)-position]) 
        elif opcode=="ISZERO":
            node = SVT(opcode)
            node.children.append(self._stack.pop())
            self._stack.append(node)
        elif opcode=="ADD" or opcode=="AND" or opcode=="LT" or opcode=="GT" or opcode=="SUB":
            if isinstance(self._stack[-1].value, int) and isinstance(self._stack[-2].value, int):
                if opcode == "ADD":
                    node = SVT((self._stack.pop().value + self._stack.pop().value)%2**256)
                elif opcode == "AND":
                    node = SVT((self._stack.pop().value & self._stack.pop().value)%2**256) 
                elif opcode == "SUB":
                    node = SVT((self._stack.pop().value - self._stack.pop().value)%2**256)       
            else:
                node = SVT(opcode)
                node.children.append(self._stack.pop())
                node.children.append(self._stack.pop())
            self._stack.append(node)
            self.inspect("stack")
        elif opcode=="SHA3":
            if self._stack[-2].value == 64:
                start_offset = self._stack.pop().value
                if not isinstance(start_offset, int):
                    raise Exception("start offset not constant")
                node = SVT("MapElement")
                node.children.append(self._memory[start_offset//32+1]) # map name: balances
                node.children.append(self._memory[start_offset//32]) # key in balances
                self._stack.pop()
                self._stack.append(node)
            self.inspect("stack")
        else:
            print('[!]',str(instr), 'not supported yet')  

        
# Note that "FourByteSelector" is at the BOTTOM of the stack     
def set_stack():
    return [
    SVT("FourByteSelector"), 
    SVT("SomethingIDontKnow"), 
    SVT("_from"), 
    SVT("_to"), 
    SVT("_value"), 
    SVT("_fee")
    ]    

def set_storage():
    return {
        0: '0x5c9eb5d6a6c2c1b3efc52255c0b356f116f6f66d'
    } 


def set_code_trace():
    return [
    (1174, "JUMPDEST",None),
    (1175, "PUSH1", 0x00),
    (1177, "DUP3",None),
    (1178, "DUP3",None),
    (1179, "ADD",None),
    (1180, "PUSH1", 0x02),
    (1182, "PUSH1", 0x00),
    (1184, "DUP8",None),
    (1185, "PUSH20", 0xffffffffffffffffffffffffffffffffffffffff),
    (1206, "AND",None),
    ]


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
            # print(trace_node)  
    inputfile.close()
    return trace

      
def main():
    evm = EVM(set_stack(), set_storage(), [0] * 1000, open("output.bpl", "w"))
    evm.inspect("stack")
    print('-----Instructions-----')
    # code_trace = set_code_trace()
    # code_trace = read_path("trace.txt")
    code_trace = read_path("test.txt")
    evm.sym_exec(code_trace)
    evm.inspect("stack")
    evm.inspect("memory")
    evm.inspect("storage")

 
if __name__ == '__main__':
    main()
    
    
'''

This trace contains the essential part of the transferProxy call to the contract https://github.com/TCT-web3/demo/blob/main/trace-symexec/MultiVulnToken.sol. 
At the starting point of the trace, all arguments are on the top of the stack

stack
[
	"0x8000000000000000000000000000000000000000000000000000000000000000",
	"0x8000000000000000000000000000000000000000000000000000000000000001",
	"0x00000000000000000000000092349ef835ba7ea6590c3947db6a11eee1a90cfd",
	"0x0000000000000000000000000fc5025c764ce34df352757e82f7b5c4df39a836",
	"0x0000000000000000000000000000000000000000000000000000000000000127",
	"0x00000000000000000000000000000000000000000000000000000000cf053d9d"
]
======================================Begin==========================================


1174 JUMPDEST -
1175 PUSH1 00 - LINE 35
1177 DUP3 - LINE 37
1178 DUP3 - LINE 37
1179 ADD - LINE 37        This is where integer overflow happens.
1180 PUSH1 02 - LINE 37
1182 PUSH1 00 - LINE 37
1184 DUP8 - LINE 37
1185 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 37
1206 AND - LINE 37
1207 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 37
1228 AND - LINE 37
1229 DUP2 - LINE 37
1230 MSTORE - LINE 37
1231 PUSH1 20 - LINE 37
1233 ADD - LINE 37
1234 SWAP1 - LINE 37
1235 DUP2 - LINE 37
1236 MSTORE - LINE 37
1237 PUSH1 20 - LINE 37
1239 ADD - LINE 37
1240 PUSH1 00 - LINE 37
1242 SHA3 - LINE 37
1243 SLOAD - LINE 37
1244 LT - LINE 37
1245 ISZERO - LINE 37
1246 PUSH2 04e6 - LINE 37
1249 JUMPI - LINE 37

1254 JUMPDEST -
1255 PUSH1 02 - LINE 38
1257 PUSH1 00 - LINE 38
1259 DUP6 - LINE 38
1260 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 38
1281 AND - LINE 38
1282 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 38
1303 AND - LINE 38
1304 DUP2 - LINE 38
1305 MSTORE - LINE 38
1306 PUSH1 20 - LINE 38
1308 ADD - LINE 38
1309 SWAP1 - LINE 38
1310 DUP2 - LINE 38
1311 MSTORE - LINE 38
1312 PUSH1 20 - LINE 38
1314 ADD - LINE 38
1315 PUSH1 00 - LINE 38
1317 SHA3 - LINE 38
1318 SLOAD - LINE 38
1319 DUP4 - LINE 38
1320 PUSH1 02 - LINE 38
1322 PUSH1 00 - LINE 38
1324 DUP8 - LINE 38
1325 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 38
1346 AND - LINE 38
1347 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 38
1368 AND - LINE 38
1369 DUP2 - LINE 38
1370 MSTORE - LINE 38
1371 PUSH1 20 - LINE 38
1373 ADD - LINE 38
1374 SWAP1 - LINE 38
1375 DUP2 - LINE 38
1376 MSTORE - LINE 38
1377 PUSH1 20 - LINE 38
1379 ADD - LINE 38
1380 PUSH1 00 - LINE 38
1382 SHA3 - LINE 38
1383 SLOAD - LINE 38
1384 ADD - LINE 38
1385 LT - LINE 38
1386 ISZERO - LINE 38
1387 PUSH2 0573 - LINE 38
1390 JUMPI - LINE 38

1395 JUMPDEST -
1396 PUSH1 02 - LINE 39
1398 PUSH1 00 - LINE 39
1400 CALLER - LINE 39
1401 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 39
1422 AND - LINE 39
1423 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 39
1444 AND - LINE 39
1445 DUP2 - LINE 39
1446 MSTORE - LINE 39
1447 PUSH1 20 - LINE 39
1449 ADD - LINE 39
1450 SWAP1 - LINE 39
1451 DUP2 - LINE 39
1452 MSTORE - LINE 39
1453 PUSH1 20 - LINE 39
1455 ADD - LINE 39
1456 PUSH1 00 - LINE 39
1458 SHA3 - LINE 39
1459 SLOAD - LINE 39
1460 DUP3 - LINE 39
1461 PUSH1 02 - LINE 39
1463 PUSH1 00 - LINE 39
1465 CALLER - LINE 39
1466 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 39
1487 AND - LINE 39
1488 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 39
1509 AND - LINE 39
1510 DUP2 - LINE 39
1511 MSTORE - LINE 39
1512 PUSH1 20 - LINE 39
1514 ADD - LINE 39
1515 SWAP1 - LINE 39
1516 DUP2 - LINE 39
1517 MSTORE - LINE 39
1518 PUSH1 20 - LINE 39
1520 ADD - LINE 39
1521 PUSH1 00 - LINE 39
1523 SHA3 - LINE 39
1524 SLOAD - LINE 39
1525 ADD - LINE 39
1526 LT - LINE 39
1527 ISZERO - LINE 39
1528 PUSH2 0600 - LINE 39
1531 JUMPI - LINE 39

1536 JUMPDEST - LINE 39
1537 DUP3 - LINE 41
1537 DUP3 - LINE 41
1538 PUSH1 02 - LINE 41
1540 PUSH1 00 - LINE 41
1542 DUP7 - LINE 41
1543 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 41
1564 AND - LINE 41
1565 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 41
1586 AND - LINE 41
1587 DUP2 - LINE 41
1588 MSTORE - LINE 41
1589 PUSH1 20 - LINE 41
1591 ADD - LINE 41
1592 SWAP1 - LINE 41
1593 DUP2 - LINE 41
1594 MSTORE - LINE 41
1595 PUSH1 20 - LINE 41
1597 ADD - LINE 41
1598 PUSH1 00 - LINE 41
1600 SHA3 - LINE 41
1601 PUSH1 00 - LINE 41
1603 DUP3 - LINE 41
1604 DUP3 - LINE 41
1605 SLOAD - LINE 41
1606 ADD - LINE 41
1607 SWAP3 - LINE 41
1608 POP - LINE 41
1609 POP - LINE 41
1610 DUP2 - LINE 41
1611 SWAP1 - LINE 41
1612 SSTORE - LINE 41
1613 POP - LINE 41
1614 DUP2 - LINE 42
1615 PUSH1 02 - LINE 42
1617 PUSH1 00 - LINE 42
1619 CALLER - LINE 42
1620 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 42
1641 AND - LINE 42
1642 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 42
1663 AND - LINE 42
1664 DUP2 - LINE 42
1665 MSTORE - LINE 42
1666 PUSH1 20 - LINE 42
1668 ADD - LINE 42
1669 SWAP1 - LINE 42
1670 DUP2 - LINE 42
1671 MSTORE - LINE 42
1672 PUSH1 20 - LINE 42
1674 ADD - LINE 42
1675 PUSH1 00 - LINE 42
1677 SHA3 - LINE 42
1678 PUSH1 00 - LINE 42
1680 DUP3 - LINE 42
1681 DUP3 - LINE 42
1682 SLOAD - LINE 42
1683 ADD - LINE 42
1684 SWAP3 - LINE 42
1685 POP - LINE 42
1686 POP - LINE 42
1687 DUP2 - LINE 42
1688 SWAP1 - LINE 42
1689 SSTORE - LINE 42
1690 POP - LINE 42
1691 DUP2 - LINE 43
1692 DUP4 - LINE 43
1693 ADD - LINE 43
1694 PUSH1 02 - LINE 43
1696 PUSH1 00 - LINE 43
1698 DUP8 - LINE 43
1699 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 43
1720 AND - LINE 43
1721 PUSH20 ffffffffffffffffffffffffffffffffffffffff - LINE 43
1742 AND - LINE 43
1743 DUP2 - LINE 43
1744 MSTORE - LINE 43
1745 PUSH1 20 - LINE 43
1747 ADD - LINE 43
1748 SWAP1 - LINE 43
1749 DUP2 - LINE 43
1750 MSTORE - LINE 43
1751 PUSH1 20 - LINE 43
1753 ADD - LINE 43
1754 PUSH1 00 - LINE 43
1756 SHA3 - LINE 43
1757 PUSH1 00 - LINE 43
1759 DUP3 - LINE 43
1760 DUP3 - LINE 43
1761 SLOAD - LINE 43
1762 SUB - LINE 43
1763 SWAP3 - LINE 43
1764 POP - LINE 43
1765 POP - LINE 43
1766 DUP2 - LINE 43
1767 SWAP1 - LINE 43
1768 SSTORE - LINE 43
1769 POP - LINE 43
1770 PUSH1 01 - LINE 44
1772 SWAP1 - LINE 44
1773 POP - LINE 44
1774 SWAP5 - LINE 44
1775 SWAP4 - LINE 44
1776 POP - LINE 44
1777 POP - LINE 44
1778 POP - LINE 44
1779 POP - LINE 44
1780 JUMP - LINE 44   the essentail computation basically ends here. The rest is the return.

0295 JUMPDEST - LINE 34
0296 PUSH1 40 - LINE 34
0298 MLOAD - LINE 34
0299 PUSH2 0134 - LINE 34
0302 SWAP2 - LINE 34
0303 SWAP1 - LINE 34
0304 PUSH2 0943 - LINE 34
0307 JUMP - LINE 34

2371 JUMPDEST - LINE 34
2372 PUSH1 00 - LINE 34
2374 PUSH1 20 - LINE 34
2376 DUP3 - LINE 34
2377 ADD - LINE 34
2378 SWAP1 - LINE 34
2379 POP - LINE 34
2380 PUSH2 0958 - LINE 34
2383 PUSH1 00 - LINE 34
2385 DUP4 - LINE 34
2386 ADD - LINE 34
2387 DUP5 - LINE 34
2388 PUSH2 0934 - LINE 34
2391 JUMP - LINE 34

2356 JUMPDEST - LINE 34
2357 PUSH2 093d - LINE 34
2360 DUP2 - LINE 34
2361 PUSH2 0928 - LINE 34
2364 JUMP - LINE 34

2344 JUMPDEST - LINE 34
2345 PUSH1 00 - LINE 34
2347 DUP2 - LINE 34
2348 ISZERO - LINE 34
2349 ISZERO - LINE 34
2350 SWAP1 - LINE 34
2351 POP - LINE 34
2352 SWAP2 - LINE 34
2353 SWAP1 - LINE 34
2354 POP - LINE 34
2355 JUMP - LINE 34

2365 JUMPDEST - LINE 34
2366 DUP3 - LINE 34
2367 MSTORE - LINE 34
2368 POP - LINE 34
2369 POP - LINE 34
2370 JUMP - LINE 34

2392 JUMPDEST - LINE 34
2393 SWAP3 - LINE 34
2394 SWAP2 - LINE 34
2395 POP - LINE 34
2396 POP - LINE 34
2397 JUMP - LINE 34

0308 JUMPDEST - LINE 34
0309 PUSH1 40 - LINE 34
0311 MLOAD - LINE 34
0312 DUP1 - LINE 34
0313 SWAP2 - LINE 34
0314 SUB - LINE 34
0315 SWAP1 - LINE 34
0316 RETURN - LINE 34

======================================End==========================================

The ultimate goal is the generate the following boogie code:

tmp1 := add(_fee , _value);   
assume (balances[_from] >= tmp1);
tmp2 := add(balances[_to] , _value);  
assume(tmp2 >= balances[_to]);
tmp3 := add(balances[msg.sender] , _fee);
assume(tmp3 >= balances[msg.sender]);
balances[_to] := add(balances[_to] , _value);
balances[msg.sender] := add(balances[msg.sender] , _fee);
balances[_from] := sub(balances[_from] , tmp1);

Here are the aliases we know at the starting point of the trace (represented as "old"):
_fee is a.k.a. old(stack[0])
_value is a.k.a. old(stack[1])
_to is a.k.a. (old(stack[2]) 0xffffffffffffffffffffffffffffffffffffffff)
_from is a.k.a. (old(stack[3]) & 0xffffffffffffffffffffffffffffffffffffffff)
msg.sender is a.k.a. (CALLER & 0xffffffffffffffffffffffffffffffffffffffff)
balances[_from] is a.k.a.  SHA3(_from ConcatWith 0x0000000000000000000000000000000000000000000000000000000000000002)  //SHA3 computed over the 64-byte memory
balances[_to] is a.k.a.  SHA3(_to ConcatWith 0x0000000000000000000000000000000000000000000000000000000000000002)
//0x0000000000000000000000000000000000000000000000000000000000000002 is because the token contract has "offset 0: owner", "offset 1: totalSupply", "offset 2: balances" and "offet 3:name"


Let's do a small exercise:
Before instruction 1179, the symbolic stack is:
[
	old(stack[0]),
	old(stack[1]),
	"0x0000000000000000000000000000000000000000000000000000000000000000",
	old(stack[1]),
	old(stack[2]),
	old(stack[3]),
	old(stack[4]),
	old(stack[5]),
]
After instruction 1179, the symbolic stack should be:
[
	add(old(stack[0]),old(stack[1]))
	"0x0000000000000000000000000000000000000000000000000000000000000000",
	old(stack[1]),
	old(stack[2]),
	old(stack[3]),
	old(stack[4]),
	old(stack[5]),
]
'''