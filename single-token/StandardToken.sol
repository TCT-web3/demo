// SPDX-License-Identifier: MIT

import './Token.sol';
pragma solidity >=0.8.4;

/// @custom:tct invariant: forall x:address :: 0 <= this.balances[x] && this.balances[x] <= this.totalSupply
/// @custom:tct invariant: sum(this.balances) == this.totalSupply
abstract contract StandardToken is Token {
    function balanceOf(
        address _owner
    ) public view override returns (uint256 balance) {
        return balances[_owner];
    }

    mapping(address => uint256) balances;
}