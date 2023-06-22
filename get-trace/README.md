# Sample Hardhat Project

This project demonstrates a basic Hardhat use case. It comes with a sample contract, a test for that contract, and a script that deploys that contract.

Try running some of the following tasks:

```shell
npx hardhat help
npx hardhat test
REPORT_GAS=true npx hardhat test
npx hardhat node
npx hardhat run scripts/deploy.js
```


curl -H 'Content-Type: application/json'   --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["0xa24a9c513fdcfd1fcbd1668ed632b7f0231076879eda5c16be565115920b8d15",{} ] }' http://localhost:8545 -o trace.json