const { Web3 } = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider('http://localhost:8545'));

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

web3.eth.getAccounts().then(console.log);

// Finding the function signature
const functionSignature = web3.eth.abi.encodeFunctionSignature(contractABI.find(x => x.name === 'attack1_int_overflow'));

// 2. Create account variables
const accountFrom = {
    privateKey: '0xf60b17f41fbe2439ade252df277118da48d7e9f83d56',
    address: '0xf60b17f41fbe2439ade252df277118da48d7e9f8',
};

const addressTo = '0xf60b17f41fbe2439ade252df277118da48d7e08f'; // Change addressTo

console.log("sender addr:", accountFrom.address, " to addr: ", addressTo)

// 3. Create send function
async function send() {
    console.log(`Attempting to send transaction from ${accountFrom.address} to ${addressTo}`);
    // 4. Sign tx with PK
    const signedTx = await web3.eth.accounts.signTransaction(
        {
            from: accountFrom.address,
            to: addressTo,
            value: web3.utils.toWei('1', 'ether'),
            nonce: await web3.eth.getTransactionCount(accountFrom.address, "latest"),
            gas: 300000,
            maxFeePerGas: 250000000000,
            maxPriorityFeePerGas: 250000000000,
            gasLimit: 300000,
            data: functionSignature,
        },
        accountFrom.privateKey
    );
    // 5. Send tx and wait for receipt
    web3.eth.sendSignedTransaction(signedTx.rawTransaction, function (error, hash) {
        if (!error) {
            console.log("The hash of your transaction is: ", hash,
                "\n Check Transactions tab in Ganache to view your transaction!");
        } else {
            console.log("Something went wrong while submitting your transaction:", error);
        }
    });
};


// 6. Call send function
send();