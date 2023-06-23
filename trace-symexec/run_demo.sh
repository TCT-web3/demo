#! /bin/bash

# python3 symexec.py MultiVulnToken1.sol theorem1.json trace1.txt

# python3 symexec.py MultiVulnToken2.sol theorem2.json trace2.txt

curl -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0x4e44d023f6bc1388bb8fdcdb6908a1777bbf586bd8f94e2f6911ae87a1537ddd",{} ] }' http://localhost:7545 | json_pp > trace_no_reentrancy.jso