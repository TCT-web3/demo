#on MacOS
curl -H "Content-Type: application/json" --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0x490b2180bef816017083d239e4fe66ed1131465fbb37d7e6b6944a4640e6c5af",{} ] }' http://localhost:7545 | json_pp > trace_swap.json

#on Windows
#curl -H "Content-Type: application/json" --data "{\"jsonrpc\":\"2.0\", \"id\": 1, \"method\": \"debug_traceTransaction\", \"params\": [\"0x97daf6bed892f5f1fc175301a7ba25638bc37c4faea1314ddf76f94a6dab5a73\",{} ] }" http://localhost:7545 -o client_trace.json

# FINALIZED COPY
# add liq: 0xd642b0084167b9f0d4423a608b30ca619a60c04641535ef3e9a2a6d955633f00
# remove liq: 0xeb7f3e1554e8ead45a25eb54d0a9cf221222e04fe5237c8304a07d2c2c50741b
# swap: 0x490b2180bef816017083d239e4fe66ed1131465fbb37d7e6b6944a4640e6c5af

# int overflow: 0xf8a80a310c0956a65145d07208773c4c37cd60206938aa195b573ab2e98b95dc
# no reentrancy: 0x8468bb462b833fa2e49a987c292a19fef51a65684f3fd18172e2b435e269c28d
# reentrancy: 0xc3e814be9abc2a1ced9d049910834981f6fa5791820024f641b24a785adf5224

# require: 0x91b95147362619901e51ab17983e5ea6ddfb4a9f387c0bbce1e6ad559a2d7d06

geth --http --http.corsdomain https://remix.ethereum.org 

geth --http --http.corsdomain="https://remix.ethereum.org" --http.api web3,eth,debug,personal,net --vmdebug --goerli --vmdebug --allow-insecure-unlock --unlock "0x1470e4d2bb2625867ff2b2cbed1f9905e621ffb6" console

geth --http --http.corsdomain="https://remix.ethereum.org" --http.api web3,eth,debug,personal,net --vmdebug --goerli --vmdebug --allow-insecure-unlock --unlock "0x340343e2b9a536f556ca9bffb283846c57d93edb" console

