#! /bin/bash

SYMEXEC=src/symexec.py
BOOGIE=boogie

### Some boogie versions require "/proverOpt O:smt.arith.solver=2" in order to run

### DEMO: integer overflow
echo "--------------------(Demo: Integer Overflow)------------------------"
SOLIDITY=../single-token/Demo.sol
THEOREM=../web-demo/uploads/theorem_integerOverflow.json
TRACE=../web-demo/trace_integerOverflow.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/trace_integerOverflow.bpl
echo ""

### DEMO: no reentrancy
echo "--------------------(Demo: No Reentrancy)------------------------"
SOLIDITY=../single-token/Demo.sol
THEOREM=../web-demo/uploads/theorem_noReentrancy.json
TRACE=../web-demo/trace_noReentrancy.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/trace_noReentrancy.bpl
echo ""

### DEMO: reentrancy
echo "--------------------(Demo: Reentrancy)------------------------"
SOLIDITY=../single-token/Demo.sol
THEOREM=../web-demo/uploads/theorem_Reentrancy.json
TRACE=../web-demo/trace_Reentrancy.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/trace_Reentrancy.bpl
echo ""

### DEMO: add liquidity
echo "--------------------(Demo: Add Liquidity)------------------------"
SOLIDITY=../uniswapv2-solc0.8/test.sol
THEOREM=../web-demo/uploads/theorem_addLiquidity.json
TRACE=../web-demo/trace_addLiquidity.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
# ${BOOGIE} ../web-demo/trace_addLiquidity.bpl
echo ""

### DEMO: remove liquidity
echo "--------------------(Demo: Remove Liquidity)------------------------"
SOLIDITY=../uniswapv2-solc0.8/test.sol
THEOREM=../web-demo/uploads/theorem_removeLiquidity.json
TRACE=../web-demo/trace_removeLiquidity.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
# ${BOOGIE} ../web-demo/trace_removeLiquidity.bpl
echo ""

### DEMO: swap
echo "--------------------(Demo: Swap)------------------------"
SOLIDITY=../uniswapv2-solc0.8/test.sol
THEOREM=../web-demo/uploads/theorem_swap.json
TRACE=../web-demo/trace_swap.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/trace_swap.bpl
echo ""

### individual
### /proverOpt O:smt.arith.solver=2
# python3 src/symexec.py ../single-token/Demo.sol ../web-demo/uploads/theorem_integerOverflow.json ../web-demo/trace_integerOverflow.txt
# boogie ../web-demo/trace_integerOverflow.bpl
# python3 src/symexec.py ../single-token/Demo.sol ../web-demo/uploads/theorem_reentrancy.json ../web-demo/trace_reentrancy.txt
# boogie ../web-demo/trace_reentrancy.bpl
# python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/theorem_addLiquidity.json ../web-demo/trace_addLiquidity.txt
# boogie ../web-demo/trace_addLiquidity.bpl
# python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/theorem_removeLiquidity.json ../web-demo/trace_removeLiquidity.txt
# boogie ../web-demo/trace_removeLiquidity.bpl
# python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/theorem_swap.json ../web-demo/trace_swap.txt
# boogie ../web-demo/trace_swap.bpl

