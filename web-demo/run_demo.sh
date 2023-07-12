#! /bin/bash

SYMEXEC=src/symexec.py
BOOGIE=boogie


### DEMO: addLiquidity
echo "--------------------(Demo 1)------------------------"
SOLIDITY=../uniswapv2-solc0.8/contract_everything.sol
THEOREM=../uniswapv2-solc0.8/theorem_addLiq.json
TRACE=trace_UniswapAddLiquidity.txt
python3 ${SYMEXEC} ${SOLIDITY} ${THEOREM} ${TRACE}
# ${BOOGIE} TCT_out_addLiq.bpl
echo ""





