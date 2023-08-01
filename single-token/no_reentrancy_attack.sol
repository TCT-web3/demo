// SPDX-License-Identifier: MIT

/* Vulnerability examples:

   reentrancy:
   https://blog.chain.link/reentrancy-attacks-and-the-dao-hack/

   integer overflow:
   https://peckshield.medium.com/integer-overflow-i-e-proxyoverflow-bug-found-in-multiple-erc20-smart-contracts-14fecfba2759
*/

import './MultiVulnToken.sol';
pragma solidity >=0.8.0;

contract no_reentrancy_attack {
    MultiVulnToken public multiVulnToken;
    address _to;
    constructor(address _multiVulnTokenAddress, address __to) {
        multiVulnToken = MultiVulnToken(_multiVulnTokenAddress);
        _to = __to;
    }
    function receiveNotification(uint256) public {
        //nothing special
    }
    function call_clear() public {
        multiVulnToken.clear(_to);
    }
}