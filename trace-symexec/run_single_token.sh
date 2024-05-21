#! /bin/bash

SYMEXEC=src/symexec.py
BOOGIE=boogie

### Some boogie versions require "/proverOpt O:smt.arith.solver=2" in order to run

### DEMO: BNB
echo "--------------------(Demo: BNB)------------------------"
SOLIDITY=../single-token/BNB/BNB.sol
THEOREM=../web-demo/uploads/theorem_BNB.json
TRACE=../web-demo/traces/trace-BNB.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/traces/trace-BNB.bpl
echo ""

### DEMO: stETH
# echo "--------------------(Demo: stETH)------------------------"
# SOLIDITY=../single-token/stETH/stETH.sol
# THEOREM=../web-demo/uploads/theorem_stETH.json
# TRACE=../web-demo/traces/trace-stETH.txt
# python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
# ${BOOGIE} ../web-demo/traces/trace-stETH.bpl
# echo ""

### DEMO: TONCOIN
echo "--------------------(Demo: TONCOIN)------------------------"
SOLIDITY=../single-token/TONCOIN/WrappedTON.sol
THEOREM=../web-demo/uploads/theorem_TONCOIN.json
TRACE=../web-demo/traces/trace-TONCOIN.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/traces/trace-TONCOIN.bpl
echo ""

### DEMO: USDC
echo "--------------------(Demo: USDC)------------------------"
SOLIDITY=../single-token/USDC/USDC.sol
THEOREM=../web-demo/uploads/theorem_USDC.json
TRACE=../web-demo/traces/trace-USDC.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/traces/trace-USDC.bpl
echo ""

### DEMO: USDT
echo "--------------------(Demo: USDT)------------------------"
SOLIDITY=../single-token/USDT/USDT.sol
THEOREM=../web-demo/uploads/theorem_USDT.json
TRACE=../web-demo/traces/trace-USDT.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
${BOOGIE} ../web-demo/traces/trace-USDT.bpl
echo ""


### individual
### /proverOpt O:smt.arith.solver=2
# python3 src/symexec.py ../single-token/Demo.sol ../web-demo/uploads/theorem_integerOverflow.json ../web-demo/traces/trace-integerOverflow.txt
# boogie ../web-demo/traces/trace-integerOverflow.bpl
# python3 src/symexec.py ../single-token/Demo.sol ../web-demo/uploads/theorem_reentrancy.json ../web-demo/traces/trace-reentrancy.txt
# boogie ../web-demo/traces/trace-reentrancy.bpl
# python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/theorem_addLiquidity.json ../web-demo/traces/trace-addLiquidity.txt
# boogie ../web-demo/traces/trace-addLiquidity.bpl
# python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/theorem_removeLiquidity.json ../web-demo/traces/trace-removeLiquidity.txt
# boogie ../web-demo/traces/trace-removeLiquidity.bpl
# python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/theorem_swap.json ../web-demo/traces/trace-swap.txt
# boogie ../web-demo/traces/trace-swap.bpl

