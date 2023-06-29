/// DEMO FOR REENTRANCY 
// const Demo = artifacts.require("Demo")
// module.exports = function(deployer) {
//   deployer.deploy(Demo)
// };

/// Int Overflow
const MVT = artifacts.require("MultiVulnToken")
module.exports = function(deployer) {
  deployer.deploy(MVT, 30000)
}

/// NO REENTRANCY
// const MultiVulnToken = artifacts.require("MultiVulnToken");
// const reentrancy_attack = artifacts.require("reentrancy_attack");
// module.exports = async function(deployer) {
//   // let accounts = await web3.eth.getAccounts()
//   //console.log(MultiVulnToken.address)
//   deployer.deploy(MultiVulnToken, 30000)
//   let MVT = await MultiVulnToken.deployed()
//   MVT
//   console.log(MultiVulnToken.address)
//   console.log(MVT.address)
//   //console.log(MVT.transactionHash)
//   //console.log(MVT)
//   deployer.deploy(reentrancy_attack, MultiVulnToken.address, accounts[1]);
  
//   let REA = await reentrancy_attack.deployed();
//   let REA_result = await REA.attack();
//   console.log(REA_result);
// }

  // deployer.deploy(MultiVulnToken, 30000);
  // const MVT = await MultiVulnToken.deployed();
  // let MVT_result = await MVT.transferProxy(accounts[0], accounts[1 /* or any number 0-9*/], 10, 1);


/// NRA
// const MultiVulnToken = artifacts.require("./MultiVulnToken")
// const no_reentrancy_attack = artifacts.require("no_reentrancy_attack")

// module.exports = async function(deployer) {
//   const accounts = await web3.eth.getAccounts();

//   deployer.deploy(MultiVulnToken, 30000);
//   const MVT = await MultiVulnToken.deployed();
//   console.log(MVT.address);
//   console.log(MultiVulnToken.address);
//   console.log(MVT["address"])
//   console.log(typeof(MultiVulnToken.address))
//   console.log(parseInt(MVT.address, 16))
//   deployer.deploy(no_reentrancy_attack, parseInt(MVT.address, 16), accounts[1]);
//   const NRA = await no_reentrancy_attack.deployed();
//   const NRA_result = await NRA.call_clear();
//   console.log(NRA_result);

// };


/// REA
// const MultiVulnToken = artifacts.require("./MultiVulnToken")
// const reentrancy_attack = artifacts.require("reentrancy_attack")

// module.exports = async function(deployer) {
//   const accounts = await web3.eth.getAccounts();

//   deployer.deploy(MultiVulnToken, 30000);
//   const MVT = await MultiVulnToken.deployed();
//   deployer.deploy(reentrancy_attack, MVT.address, accounts[1]);
//   const REA = await reentrancy_attack.deployed();
//   const REA_result = await REA.attack();
//   console.log(REA_result);
// };