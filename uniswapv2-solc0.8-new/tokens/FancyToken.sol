// SPDX-License-Identifier: MIT
import '../interfaces/IERC20.sol';
pragma solidity >=0.8.0;

/// @custom:tct invariant: forall x:address :: 0 <= this.balanceOf[x] && this.balanceOf[x] <= this.totalSupply
/// @custom:tct invariant: sum(this.balanceOf) == this.totalSupply
contract FancyToken is IERC20 {
    uint public override totalSupply;
    mapping(address => uint) public override balanceOf;
    mapping(address => mapping(address => uint)) public override allowance;
    string public override name = "Fancy Token";
    string public override symbol = "FNCY";
    uint8 public override decimals = 18;
    constructor () {
        totalSupply = 10**8;
        balanceOf[msg.sender] = totalSupply;
    }
    function transfer(address recipient, uint amount) external override returns (bool) {
        unchecked {
            balanceOf[msg.sender] -= amount;
            balanceOf[recipient] += amount;
            //emit Transfer(msg.sender, recipient, amount);
            return true;
        }
    }

    function approve(address spender, uint amount) external override returns (bool) {
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
    ) external override returns (bool) {
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

