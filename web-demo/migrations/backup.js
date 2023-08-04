const {Web3} = require('web3');
const fs = require('fs')

// Connect to a Web3 provider
const web3 = new Web3(new Web3.providers.HttpProvider('http://127.0.0.1:7545'));

// Define the contract ABI and bytecode
const contractABI = JSON.parse(fs.readFileSync('migrations/Submitter_ABI.json', 'utf8'));
const contractBytecode = fs.readFileSync('migrations/Submitter_Bytecode.txt', 'utf8');

// Deploy the contract
async function deployContract() {
  const contract = new web3.eth.Contract(contractABI);

  try {
    const deployTransaction = contract.deploy({
      data: contractBytecode,
    });

    const deployReceipt = await deployTransaction.send({
      from: '0x2a82881FC3200692623FCB14D15729c4A5a5C0c0',
      gas: 67219750, // Adjust the gas limit as needed
    });

    console.log('Contract deployed successfully');
    console.log('Transaction hash:', deployReceipt.transactionHash);
    console.log('Contract address:', deployReceipt.contractAddress);
  } catch (error) {
    console.error('Contract deployment failed:', error);
  }
}

deployContract();
