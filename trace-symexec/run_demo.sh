#! /bin/bash

SYMEXEC=src/symexec.py
BOOGIE=boogie


### DEMO 1
# python3 ${SYMEXEC} MultiVulnToken1.sol theorem1.json sampleAutoGenTrace1.txt
# ${BOOGIE} TCT_out_theorem1.bpl


### DEMO 2
# python3 ${SYMEXEC} MultiVulnToken2.sol theorem2.json sampleAutoGenTrace2.txt




### DEMO3
python3 ${SYMEXEC} MultiVulnToken3.sol theorem3.json sampleAutoGenTrace3.txt
${BOOGIE} TCT_out_theorem3.bpl









# curl -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0x6a7d6f21e7f90121449c6f41723b163a970752afca0cf6963d7b2509c49cf051",{} ] }' http://localhost:9545 | json_pp > trace_no_reentrancy.json