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
4. Build and compile by typing ```build <contract file>```. You should then see the builds for all the contracts in the folder ```builds/contracs```. 
5. In the ```migrations``` folder, change the JS file to run our contracts and not the MetaCoin and ConvertLib examples. This example deploys the MultiVulnToken contract:
```js
const MVT = artifacts.require("MultiVulnToken");

module.exports = function(deployer) {
    deployer.deploy(MVT, 30000);
};
```
5. Inside Ganache, create a new workspace. In Server, set the port number and network ID to match the Truffle development mode's port number and network ID to match the migration network ID. In most cases, the port number should be set to 9545 and network ID to 5777.
6. In Accounts & Keys, set the mnemonic to match with the mnemonic from Truffle development mode. I think it is consistent for everyone:
```hub normal easy valid clinic jeans soon distance service wagon ketchup update```
7. Return to terminal and deploy your contract by typing either ```deploy``` or ```migrate```. Check that the contract has been created in Ganache. 
8. Run these lines of JS to run a transaction. In this example, we will run ```transferProxy``` from the MultiVulnToken contract:
```js
let MVT = await MultiVulnToken.deployed()
MVT
let accounts = await web3.eth.getAccounts()
let result = await MVT.transferProxy(accounts[0], accounts[1 /* or any number 1-9*/], 10, 1)
result
```
9. Go back to Ganache and you should now see the transaction. The tx hash in your terminal should match with the tx hash in Ganache.
# Get trace 
# Convert trace file
After getting the json trace file, parse into txt with python program.
```shell
python3 convert_trace.py <trace json>
```
The resulting output file is currently ```output.txt```.
# Symexec
```shell
python3 symexec.py <solidity file> <theorem file> <trace file>
```
