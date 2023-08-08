curl -H "Content-Type: application/json" --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0x2ddc8a732313702bea8e0d49aa4fbf332c159116dfefc7319563ef193a384585",{} ] }' http://localhost:7545 | json_pp > trace_swap.json

# FINALIZED COPY
# add liq: 0x02c8cf592c81ee52a8327df1fd35e0c4e1f05634b9fc588f58720722fec99148
# remove liq: 0x455d0f523122d529a54e53209c6cf368cf22e2e19a561456994ebc7fb46c1608
# swap: 0x2ddc8a732313702bea8e0d49aa4fbf332c159116dfefc7319563ef193a384585

# int overflow: 0xf8a80a310c0956a65145d07208773c4c37cd60206938aa195b573ab2e98b95dc
# no reentrancy: 0x8468bb462b833fa2e49a987c292a19fef51a65684f3fd18172e2b435e269c28d
# reentrancy: 0xc3e814be9abc2a1ced9d049910834981f6fa5791820024f641b24a785adf5224

# require: 0x91b95147362619901e51ab17983e5ea6ddfb4a9f387c0bbce1e6ad559a2d7d06

geth --http --http.corsdomain https://remix.ethereum.org 

geth --http --http.corsdomain="https://remix.ethereum.org" --http.api web3,eth,debug,personal,net --vmdebug --goerli --vmdebug --allow-insecure-unlock --unlock "0x1470e4d2bb2625867ff2b2cbed1f9905e621ffb6" console

geth --http --http.corsdomain="https://remix.ethereum.org" --http.api web3,eth,debug,personal,net --vmdebug --goerli --vmdebug --allow-insecure-unlock --unlock "0x340343e2b9a536f556ca9bffb283846c57d93edb" console

