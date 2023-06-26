# How to get the trace from Truffle
1. Install either [Truffle](https://trufflesuite.com/docs/truffle/how-to/install/) or the [Truffle VS Code Extension](https://trufflesuite.com/docs/vscode-ext/quickstart/). Be sure to unbox [MetaCoin](https://trufflesuite.com/docs/truffle/how-to/create-a-project/) as well.
2. Run the following command to check that truffle installed correctly:
```shell
truffle --version
```
3. Enter truffle development mode with the following command:
```shell
truffle develop
```
4. Build and compile by typing ```build <contract file>```. You should then see the builds for all the contracts in the folder ```builds/contracts```. 
5. In the ```migrations``` folder, change the JS file to run our contracts and not the MetaCoin and ConvertLib examples. This example deploys the MultiVulnToken contract:
```js
const MVT = artifacts.require("MultiVulnToken");

module.exports = function(deployer) {
    deployer.deploy(MVT, 30000);
};
```
6. Inside Ganache, create a new workspace. In Server, set the port number and network ID to match the Truffle development mode's port number and network ID to match the migration network ID. In most cases, the port number should be set to 9545 and network ID to 5777.
7. In Accounts & Keys, set the mnemonic to match with the mnemonic from Truffle development mode. I think it is consistent for everyone:
```
hub normal easy valid clinic jeans soon distance service wagon ketchup update
```
8. Return to terminal and deploy your contract by typing either ```deploy``` or ```migrate```. Check that the contract has been created in Ganache. 
9. Run these lines of JS to run a transaction. In this example, we will run ```transferProxy``` from the MultiVulnToken contract:
```js
let MVT = await MultiVulnToken.deployed()
MVT
let accounts = await web3.eth.getAccounts()
let result = await MVT.transferProxy(accounts[0], accounts[1 /* or any number 0-9*/], 10, 1)
result
```
10. Go back to Ganache and you should now see the transaction. The tx hash in your terminal should match with the tx hash in Ganache.
# Get trace
Follow Nanqing's guide on the demo README or run the script in ```run_demo.sh```.
# Convert trace file
After getting the json trace file, parse into txt with python program.
```shell
python3 convert_trace.py <trace json>
```
The resulting output file is currently ```output.txt```. As of now, our ```symexec.py``` file still requires the entry point which our file is not producing because we have directly called the ```transferProxy``` function. In the ```output.txt``` file, after the "Begin" line, create a new line and paste this line:
```
>>enter <tx hash>::0xcf053d9d (MultiVulnToken::transferProxy(address,address,uint256,uint256))
```
# Symexec
```shell
python3 symexec.py <solidity file> <theorem file> <trace file>
```
