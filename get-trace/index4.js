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
    privateKey: '0xa2c28995f93af6f9ca02bb1082dfa55fab1d0c7945e7c09b7594d82b83a06f79',
    address: '0x0e6322d1B8b3d57D6f96fA3f529892fE77c3daE8',
};

const contractAddress = '0x93B1eC1655303B81F5D00b888854eD3674966B14'; // Change addressTo


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