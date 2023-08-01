// SPDX-License-Identifier: MIT

pragma solidity >=0.8.4;

abstract contract Token {
    address public owner;
    uint256 public totalSupply;

    function balanceOf(
        address _owner
    ) public view virtual returns (uint256 balance);
}