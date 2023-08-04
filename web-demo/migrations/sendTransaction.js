const Web3 = require('web3');

// Create a web3 instance
const providerUrl = 'http://127.0.0.1:9545'; // Replace with your provider URL
const web3 = new Web3(providerUrl);

// Set the contract address and ABI
const contractAddress = 'CONTRACT_ADDRESS'; // Replace with your contract address
const contractABI = [
  // Define your contract ABI here
  // ...
];

// Create an instance of the contract
const contract = new web3.eth.Contract(contractABI, contractAddress);

// Function: attack1_int_overflow
async function attack1IntOverflow() {
  try {
    const tx = await contract.methods.attack1_int_overflow().send({ from: 'SENDER_ADDRESS' });
    console.log('Transaction hash:', tx.transactionHash);
  } catch (error) {
    console.error('Error calling attack1_int_overflow:', error);
  }
}

// Function: no_reentrancy
async function noReentrancy() {
  try {
    const tx = await contract.methods.no_reentrancy().send({ from: 'SENDER_ADDRESS' });
    console.log('Transaction hash:', tx.transactionHash);
  } catch (error) {
    console.error('Error calling no_reentrancy:', error);
  }
}

// Function: attack2_reentrancy
async function attack2Reentrancy() {
  try {
    const tx = await contract.methods.attack2_reentrancy().send({ from: 'SENDER_ADDRESS' });
    console.log('Transaction hash:', tx.transactionHash);
  } catch (error) {
    console.error('Error calling attack2_reentrancy:', error);
  }
}

// Call the functions and retrieve transaction hashes
attack1IntOverflow();
noReentrancy();
attack2Reentrancy();
