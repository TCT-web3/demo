curl -H "Content-Type: application/json" --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0x91b95147362619901e51ab17983e5ea6ddfb4a9f387c0bbce1e6ad559a2d7d06",{} ] }' http://localhost:7545 | json_pp > trace_swap_temp.json

# FINALIZED COPY
# add liq: 0xeebfb0e897f662692eed364ceacb4f2b2826b7e7c1dc2c7d1018f00a74224f61
# remove liq: 0x566ddffb4fcadb38f8a441d4fed3d50a6354ca5f32589b87a455e633edadd94d
# swap: 0x21d51464a4ee7bcd1a73b1b8961db8a739dd256307f8098bc1ba01d3bffcb90d

# int overflow: 0xf8a80a310c0956a65145d07208773c4c37cd60206938aa195b573ab2e98b95dc
# no reentrancy: 0x8468bb462b833fa2e49a987c292a19fef51a65684f3fd18172e2b435e269c28d
# reentrancy: 0xc3e814be9abc2a1ced9d049910834981f6fa5791820024f641b24a785adf5224

# require: 0x91b95147362619901e51ab17983e5ea6ddfb4a9f387c0bbce1e6ad559a2d7d06

geth --http --http.corsdomain https://remix.ethereum.org 

geth --http --http.corsdomain="https://remix.ethereum.org" --http.api web3,eth,debug,personal,net --vmdebug --goerli --vmdebug --allow-insecure-unlock --unlock "0x1470e4d2bb2625867ff2b2cbed1f9905e621ffb6" console

geth --http --http.corsdomain="https://remix.ethereum.org" --http.api web3,eth,debug,personal,net --vmdebug --goerli --vmdebug --allow-insecure-unlock --unlock "0x340343e2b9a536f556ca9bffb283846c57d93edb" console

