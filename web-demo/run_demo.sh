#! /bin/bash

SYMEXEC=src/symexec.py
BOOGIE=boogie


### DEMO: addLiquidity
# echo "--------------------(Demo 1)------------------------"
# SOLIDITY=../uniswapv2-solc0.8-new/test.sol
# # THEOREM=../uniswapv2-solc0.8/theorem_addLiq.json
# # TRACE=trace_UniswapAddLiquidity2.txt
# python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
# ${BOOGIE} /proverOpt O:smt.arith.solver=2 TCT_out_addLiq.bpl
# echo ""


# python3 web-demo/src/symexec.py uniswapv2-solc0.8-new/test.sol web-demo/uploads/theorem_addLiquidity.json web-demo/trace_addLiquidity.txt
# python3 web-demo/src/symexec.py uniswapv2-solc0.8-new/test.sol web-demo/uploads/theorem_removeLiquidity.json web-demo/trace_removeLiquidity.txt


# ${BOOGIE} /proverOpt O:smt.arith.solver=2 addLiqTest.bpl
# ${BOOGIE} /proverOpt O:smt.arith.solver=2 removeLiqTest.bpl

python3 src/symexec.py ../uniswapv2-solc0.8-new/test.sol uploads/theorem_swap.json trace_swap.txt
${BOOGIE} /proverOpt O:smt.arith.solver=2 swapTest.bpl



