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
    def __init__(self, stack, storage=None):  
        self._stack = stack  
        self._storage = storage  
        
    def sym_exec(self, code_trace):
        for instr in code_trace:
            self.run_instruction(instr)

    def inspect(self,what):
        if what == "stack":
            print("-----Stack-----")
            for elem in self._stack[::-1]:
                print(elem)

    def run_instruction(self, instr):
        opcode=instr[0]
        if opcode == "JUMPDEST":
            pass
        elif opcode.startswith("PUSH"):
            self._stack.append(SVT(instr[1]))
        elif opcode.startswith("DUP"):
            position=int(opcode[len("DUP")])
            self._stack.append(self._stack[len(self._stack)-position])
        elif opcode=="ADD" or opcode=="AND":
            node = SVT(opcode)
            node.children.append(self._stack[len(self._stack)-1])
            self._stack.pop()
            node.children.append(self._stack[len(self._stack)-1])
            self._stack.pop()
            self._stack.append(node)
            

        
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
    
def set_code_trace():
    return [
    ("JUMPDEST",None),
    ("PUSH1", 0x00),
    ("DUP3",None),
    ("DUP3",None),
    ("ADD",None),
    ("PUSH1", 0x02),
    ("PUSH1", 0x00),
    ("DUP8",None),
    ("PUSH1", 0xffffffffffffffffffffffffffffffffffffffff),
    ("AND",None),
    ]

      
def main():
    evm = EVM(set_stack())
    evm.inspect("stack")
    code_trace = set_code_trace()
    evm.sym_exec(code_trace)
    evm.inspect("stack")
    
    
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