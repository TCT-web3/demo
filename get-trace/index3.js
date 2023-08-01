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

async function traceRevertedTransaction() {
	try {
		const response = await axios.post('http://localhost:8545', {
			jsonrpc: '2.0',
			method: 'debug_traceCall',
			params: [
				{
					from: "0xe4E341401D7904c4C78db2De8bd7d923150DF980",
					to: "0x1c16dADF903f6B25f79c8c8038341053371Fc15b", //contract addr
					data: functionSignature,
				},
				"latest",
			],
			id: 1,
		});

		console.log('Transaction EVM trace:', response.data.result);
	} catch (error) {
		console.error('Error:', error);
	}
}

traceRevertedTransaction();


