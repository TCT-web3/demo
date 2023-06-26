#! /bin/bash

# python3 symexec.py MultiVulnToken1.sol theorem1.json trace1.txt

# python3 symexec.py MultiVulnToken2.sol theorem2.json trace2.txt

curl -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0x6a7d6f21e7f90121449c6f41723b163a970752afca0cf6963d7b2509c49cf051",{} ] }' http://localhost:9545 | json_pp > trace_no_reentrancy.json