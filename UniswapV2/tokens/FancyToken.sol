// SPDX-License-Identifier: MIT
import '../interfaces/IERC20.sol';
pragma solidity >=0.8.0;

contract ERC20 is IERC20 {
    uint public totalSupply;
    mapping(address => uint) public balanceOf;
    mapping(address => mapping(address => uint)) public allowance;
    string public name = "Fancy Token";
    string public symbol = "FNCY";
    uint8 public decimals = 18;

    function transfer(address recipient, uint amount) external returns (bool) {
        unchecked {
            balanceOf[msg.sender] -= amount;
            balanceOf[recipient] += amount;
            //emit Transfer(msg.sender, recipient, amount);
            return true;
        }
    }

    function approve(address spender, uint amount) external returns (bool) {
        unchecked {
            allowance[msg.sender][spender] = amount;
            //emit Approval(msg.sender, spender, amount);
            return true;
        }
    }

    function transferFrom(
        address sender,
        address recipient,
        uint amount
    ) external returns (bool) {
        unchecked {
            allowance[sender][msg.sender] -= amount;
            balanceOf[sender] -= amount;
            balanceOf[recipient] += amount;
            //emit Transfer(sender, recipient, amount);
            return true;
        }
    }

    function mint(uint amount) external {
        unchecked {
            balanceOf[msg.sender] += amount;
            totalSupply += amount;
            //emit Transfer(address(0), msg.sender, amount);
        }
    }

    function burn(uint amount) external {
        unchecked {
            balanceOf[msg.sender] -= amount;
            totalSupply -= amount;
            //emit Transfer(msg.sender, address(0), amount);
        }
    }
}

