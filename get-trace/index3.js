const axios = require('axios');
// Requiring fs module in which
// writeFile function is defined.
const fs = require('fs')
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

async function traceRevertedTransaction() {
	try {
		const response = await axios.post('http://localhost:8545', {
			jsonrpc: '2.0',
			method: 'debug_traceCall',
			params: [
				{
					from: "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
					to: "0x5FbDB2315678afecb367f032d93F642f64180aa3", //contract addr
					data: functionSignature,
				},
				"latest",
				{ tracer: "callTracer"},
			],
			id: 1,
		});

		console.log('Transaction EVM trace:', response.data.result);
		// Write data in 'Output.txt'
		const jsonData = JSON.stringify(response.data.result);
		fs.writeFile('EVM_trace_1.json', jsonData, (err) => {
			// In case of a error throw err.
			if (err) throw err;
		})
	} catch (error) {
		console.error('Error:', error);
	}
}

traceRevertedTransaction();


