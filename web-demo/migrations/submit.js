const {Web3} = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:7545'));
//  const contractAbi = new web3.eth.Contract("build\\contracts\\Submitter.json");
// This is an example, replace it with your own contract's ABI
const contractABI = [
    //...
    {
      "inputs": [],
      "name": "attack1_int_overflow",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
    //...
];
web3.eth.getAccounts(console.log);
// Finding the function signature
const functionSignature = web3.eth.abi.encodeFunctionSignature(contractABI.find(x => x.name === 'attack1_int_overflow'));

// 2. Create account variables
const accountFrom = {
    privateKey: '8e2f206ac2008d22f3ba710540c9ecd86134d2dfb42f804a7c2e18b60b48d835',
    address: '0x17941B852b291315314DF40d279D4e3F6c35d86A',
  };
const addressTo = '0xcdb21d8Ce2cae359a07F473b2f44382AD6d60B43'; // Change addressTo

// 3. Create send function
const send = async () => {
console.log(`Attempting to send transaction from ${accountFrom.address} to ${addressTo}`);

// 4. Sign tx with PK
const createTransaction = await web3.eth.accounts.signTransaction(
  {
	gas: 21000,
	to: addressTo,
	value: web3.utils.toWei('1', 'ether'),
	data: functionSignature
  },
  accountFrom.privateKey
);

// 5. Send tx and wait for receipt
//const createReceipt = await web3.eth.sendSignedTransaction(createTransaction.rawTransaction);
console.log(`Transaction successful with hash: ${createReceipt.transactionHash}`);
};

// 6. Call send function
send();