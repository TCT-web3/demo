#! /bin/bash

SYMEXEC=src/symexec.py
BOOGIE=boogie


### DEMO 1: simple token
echo "--------------------(Demo 1)------------------------"
python3 ${SYMEXEC} MultiVulnToken1.sol theorem1.json sampleAutoGenTrace1.txt
${BOOGIE} TCT_out_theorem1.bpl
echo ""


### DEMO 2: simple cross-contract call
echo "--------------------(Demo 2)------------------------"
python3 ${SYMEXEC} MultiVulnToken2.sol theorem2.json sampleAutoGenTrace2.txt
${BOOGIE} TCT_out_theorem2.bpl
echo ""

### DEMO3: multiple cross contract call
echo "--------------------(Demo 3)------------------------"
python3 ${SYMEXEC} MultiVulnToken3.sol theorem3.json sampleAutoGenTrace3.txt
${BOOGIE} TCT_out_theorem3.bpl
echo ""




