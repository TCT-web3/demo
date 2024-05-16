// USDT (Tether Token) @ 0xdac17f958d2ee523a2206206994597c13d831ec7
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.4;

library SafeMath {
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) {
            return 0;
        }
        uint256 c = a * b;
        assert(c / a == b);
        return c;
    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // assert(b > 0); // Solidity automatically throws when dividing by 0
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold
        return c;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        assert(b <= a);
        return a - b;
    }

    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        assert(c >= a);
        return c;
    }
}

abstract contract ERC20Basic {
    uint public _totalSupply;
    function totalSupply() public view virtual returns (uint);
    function balanceOf(address who) public view virtual returns (uint);
    function transfer(address to, uint value) virtual public;
    event Transfer(address indexed from, address indexed to, uint value);
}

abstract contract ERC20 is ERC20Basic {
    function allowance(address owner, address spender) public view returns (uint) {}
    function transferFrom(address from, address to, uint value) public {}
    function approve(address spender, uint value) public {}
    event Approval(address indexed owner, address indexed spender, uint value);
}


abstract contract BasicToken is ERC20Basic {
    using SafeMath for uint;
    address public owner;
    mapping(address => uint) public balances;

    // additional variables for use if transaction fees ever became necessary
    uint public basisPointsRate = 0;
    uint public maximumFee = 0;

    function totalSupply() public view override returns (uint) {
        return _totalSupply;
    }
    function balanceOf(address who) public view override returns (uint) {
        return balances[who];
    }

    function transfer(address _to, uint _value) virtual override public {
        uint fee = (_value.mul(basisPointsRate)).div(10000);
        if (fee > maximumFee) {
            fee = maximumFee;
        }
        uint sendAmount = _value.sub(fee);
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(sendAmount);
        if (fee > 0) {
            balances[owner] = balances[owner].add(fee);
            emit Transfer(msg.sender, owner, fee);
        }
        emit Transfer(msg.sender, _to, sendAmount);
    }
}	
	
abstract contract StandardToken is BasicToken, ERC20 {
	mapping (address => mapping (address => uint)) public allowed;
}	

contract TetherToken is StandardToken {
    string public name;
    string public symbol;
    uint public decimals;	
    function transfer(address _to, uint _value) override(BasicToken,ERC20Basic) public {
        return super.transfer(_to, _value);
    }

    constructor() {
        name = "Tether Token";
        symbol = "USDT";
        decimals = 18;
        _totalSupply = 10**decimals;
        balances[msg.sender] = _totalSupply;
        basisPointsRate = 30;
        maximumFee = 40;
    }
}

contract Demo {
    TetherToken token;
    address user1 =
        address(0x92349Ef835BA7Ea6590C3947Db6A11EeE1a90cFd); //just an arbitrary address
    constructor() {
        token = new TetherToken();
    }
    function DoTransfer() public{
        token.transfer(user1, 5);
    }
	function CheckUser1Balance() public view returns (uint256) {
        return token.balanceOf(user1);
    }
}