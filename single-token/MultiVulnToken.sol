// SPDX-License-Identifier: MIT

import './StandardToken.sol';
pragma solidity >=0.8.4;

contract MultiVulnToken is StandardToken {
    constructor(uint256 initialSupply) {
        totalSupply = initialSupply;
        balances[msg.sender] = totalSupply;
    }

    function transferProxy(
        address _from,
        address _to,
        uint256 _value,
        uint256 _fee
    ) public returns (bool) {
        unchecked {
            require(balances[_from] >= _fee + _value);
            require(balances[_to] + _value >= balances[_to]);
            require(balances[msg.sender] + _fee >= balances[msg.sender]);

            balances[_to] += _value;
            balances[msg.sender] += _fee;
            balances[_from] -= _value + _fee;
            return true;
        }
    }

    //This function moves all tokens of msg.sender to the account of "_to"
    function clear(address _to) public {
        unchecked {
            uint256 bal = balances[msg.sender];
            balances[_to] += bal;
            bool success;
            (success, ) = msg.sender.call(
                abi.encodeWithSignature("receiveNotification(uint256)", bal)
            );
            require(success);
            balances[msg.sender] = 0;
        }
    }
}