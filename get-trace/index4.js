const axios = require('axios');
const {Web3} = require('web3');
var web3 = new Web3('http://localhost:8545');

// This is an example, replace it with your own contract's ABI
const contractABI = [
	{
		"inputs": [],
		"name": "attack1_int_overflow",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "attack2_reentrancy",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "no_reentrancy",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "attacker2Address1",
		"outputs": [
			{
				"internalType": "contract reentrancy_attack",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "benignUserAddress1",
		"outputs": [
			{
				"internalType": "contract no_reentrancy_attack",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "multiVulnToken",
		"outputs": [
			{
				"internalType": "contract MultiVulnToken",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

// Finding the function signature
const functionSignature = web3.eth.abi.encodeFunctionSignature(contractABI.find(x => x.name === 'attack1_int_overflow'));
console.log(functionSignature)

// 2. Create account variables
const accountFrom = {
    privateKey: '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80',
    address: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266',
};

const contractAddress = '0x5FbDB2315678afecb367f032d93F642f64180aa3'; // Change addressTo


async function send() {
    try {
        console.log(`Attempting to send transaction from ${accountFrom.address} to ${contractAddress}`);
        const nonce = await web3.eth.getTransactionCount(accountFrom.address, "latest");

        const rawTx = {
            from: accountFrom.address,
            to: contractAddress,
            nonce: web3.utils.toHex(nonce),
            gasPrice: web3.utils.toHex(web3.utils.toWei('10', 'gwei')), 
            gasLimit: web3.utils.toHex(300000), 
            data: functionSignature,
        };

        const signedTx = await web3.eth.accounts.signTransaction(rawTx, accountFrom.privateKey);

        const response = await axios.post('http://localhost:8545', {
            jsonrpc: '2.0',
            method: 'eth_sendRawTransaction',
            params: [signedTx.rawTransaction],
            id: 1,
        });

        console.log("The hash of your transaction is: ", response.data.result,
            "\nCheck Transactions tab in your Ethereum client to view your transaction!");
    } catch (error) {
        console.log("Something went wrong while submitting your transaction:", error);
    }
};

send();