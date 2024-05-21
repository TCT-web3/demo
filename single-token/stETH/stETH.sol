// StETH @ 0x17144556fd3424edc8fc8a4c940b2d04936d17eb

// SPDX-FileCopyrightText: 2023 Lido <info@lido.fi>
// SPDX-License-Identifier: GPL-3.0


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

interface IERC20 {
    
    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);

    function totalSupply() external view returns (uint256);

    function balanceOf(address account) external view returns (uint256);

    function transfer(address to, uint256 value) external returns (bool);

    function allowance(address owner, address spender) external view returns (uint256);

    function approve(address spender, uint256 value) external returns (bool);

    function transferFrom(address from, address to, uint256 value) external returns (bool);
}


/// @custom:tct invariant: forall x:address :: Zero <= this.balances[x] && this.balances[x] <= this.totalSupply
/// @custom:tct invariant: sum( this.balances ) == this.totalSupply
contract StETH is IERC20 {
    using SafeMath for uint256;

    address constant internal INITIAL_TOKEN_HOLDER = address(0xdead);
    uint256 constant internal INFINITE_ALLOWANCE = ~uint256(0);

    
    mapping (address => uint256) private shares;

    
    mapping (address => mapping (address => uint256)) private allowances;

    
    bytes32 internal constant TOTAL_SHARES_POSITION =
        0xe3b4b636e601189b5f4c6742edf2538ac12bb61ed03e6da26949d69838fa447e;

    
    event TransferShares(
        address indexed from,
        address indexed to,
        uint256 sharesValue
    );
    
    
    event SharesBurnt(
        address indexed account,
        uint256 preRebaseTokenAmount,
        uint256 postRebaseTokenAmount,
        uint256 sharesAmount
    );

    
    function name() external pure returns (string memory) {
        return "Liquid staked Ether 2.0";
    }

    
    function symbol() external pure returns (string memory) {
        return "stETH";
    }

    
    function decimals() external pure returns (uint8) {
        return 18;
    }

    
    function totalSupply() external view returns (uint256) {
        return _getTotalPooledEther();
    }

    constructor() {
        shares[msg.sender] = 10**18;
    }

    
    function getTotalPooledEther() external view returns (uint256) {
        return _getTotalPooledEther();
    }

    
    function balanceOf(address _account) external view returns (uint256) {
        return getPooledEthByShares(_sharesOf(_account));
    }

    
    function transfer(address _recipient, uint256 _amount) external returns (bool) {
        _transfer(msg.sender, _recipient, _amount);
        return true;
    }

    function allowance(address _owner, address _spender) external view returns (uint256) {
        return allowances[_owner][_spender];
    }

    
    function approve(address _spender, uint256 _amount) external returns (bool) {
        _approve(msg.sender, _spender, _amount);
        return true;
    }

    function transferFrom(address _sender, address _recipient, uint256 _amount) external returns (bool) {
        _spendAllowance(_sender, msg.sender, _amount);
        _transfer(_sender, _recipient, _amount);
        return true;
    }

    
    function increaseAllowance(address _spender, uint256 _addedValue) external returns (bool) {
        _approve(msg.sender, _spender, allowances[msg.sender][_spender].add(_addedValue));
        return true;
    }

    
    function decreaseAllowance(address _spender, uint256 _subtractedValue) external returns (bool) {
        uint256 currentAllowance = allowances[msg.sender][_spender];
        require(currentAllowance >= _subtractedValue, "ALLOWANCE_BELOW_ZERO");
        _approve(msg.sender, _spender, currentAllowance.sub(_subtractedValue));
        return true;
    }

    
    function getTotalShares() external view returns (uint256) {
        return _getTotalShares();
    }

    
    function sharesOf(address _account) external view returns (uint256) {
        return _sharesOf(_account);
    }

    
    function getSharesByPooledEth(uint256 _ethAmount) public view returns (uint256) {
        return _ethAmount
            .mul(_getTotalShares())
            .div(_getTotalPooledEther());
    }

    
    function getPooledEthByShares(uint256 _sharesAmount) public view returns (uint256) {
        return _sharesAmount
            .mul(_getTotalPooledEther())
            .div(_getTotalShares());
    }

    
    function transferShares(address _recipient, uint256 _sharesAmount) external returns (uint256) {
        _transferShares(msg.sender, _recipient, _sharesAmount);
        uint256 tokensAmount = getPooledEthByShares(_sharesAmount);
        _emitTransferEvents(msg.sender, _recipient, tokensAmount, _sharesAmount);
        return tokensAmount;
    }

    
    function transferSharesFrom(
        address _sender, address _recipient, uint256 _sharesAmount
    ) external returns (uint256) {
        uint256 tokensAmount = getPooledEthByShares(_sharesAmount);
        _spendAllowance(_sender, msg.sender, tokensAmount);
        _transferShares(_sender, _recipient, _sharesAmount);
        _emitTransferEvents(_sender, _recipient, tokensAmount, _sharesAmount);
        return tokensAmount;
    }

    
    function _getTotalPooledEther() internal view returns (uint256) {
        return 5**10; //placeholder
    }

    
    function _transfer(address _sender, address _recipient, uint256 _amount) internal {
        uint256 _sharesToTransfer = getSharesByPooledEth(_amount);
        _transferShares(_sender, _recipient, _sharesToTransfer);
        _emitTransferEvents(_sender, _recipient, _amount, _sharesToTransfer);
    }

    
    function _approve(address _owner, address _spender, uint256 _amount) internal {
        require(_owner != address(0), "APPROVE_FROM_ZERO_ADDR");
        require(_spender != address(0), "APPROVE_TO_ZERO_ADDR");

        allowances[_owner][_spender] = _amount;
        emit Approval(_owner, _spender, _amount);
    }

    
    function _spendAllowance(address _owner, address _spender, uint256 _amount) internal {
        uint256 currentAllowance = allowances[_owner][_spender];
        if (currentAllowance != INFINITE_ALLOWANCE) {
            require(currentAllowance >= _amount, "ALLOWANCE_EXCEEDED");
            _approve(_owner, _spender, currentAllowance - _amount);
        }
    }

    
    function _getTotalShares() internal view returns (uint256) {
        return 10**18; //Placeholder:   TOTAL_SHARES_POSITION.getStorageUint256();
    }

    
    function _sharesOf(address _account) internal view returns (uint256) {
        return shares[_account];
    }

    
    function _transferShares(address _sender, address _recipient, uint256 _sharesAmount) internal {
        require(_sender != address(0), "TRANSFER_FROM_ZERO_ADDR");
        require(_recipient != address(0), "TRANSFER_TO_ZERO_ADDR");
        require(_recipient != address(this), "TRANSFER_TO_STETH_CONTRACT");

        uint256 currentSenderShares = shares[_sender];
        require(_sharesAmount <= currentSenderShares, "BALANCE_EXCEEDED");

        shares[_sender] = currentSenderShares.sub(_sharesAmount);
        shares[_recipient] = shares[_recipient].add(_sharesAmount);
    }

    
    function _mintShares(address _recipient, uint256 _sharesAmount) internal returns (uint256 newTotalShares) {
        require(_recipient != address(0), "MINT_TO_ZERO_ADDR");

        newTotalShares = _getTotalShares().add(_sharesAmount);
        //placeholder TOTAL_SHARES_POSITION.setStorageUint256(newTotalShares);

        shares[_recipient] = shares[_recipient].add(_sharesAmount);

        // Notice: we're not emitting a Transfer event from the zero address here since shares mint
        // works by taking the amount of tokens corresponding to the minted shares from all other
        // token holders, proportionally to their share. The total supply of the token doesn't change
        // as the result. This is equivalent to performing a send from each other token holder's
        // address to `address`, but we cannot reflect this as it would require sending an unbounded
        // number of events.
    }

    
    function _burnShares(address _account, uint256 _sharesAmount) internal returns (uint256 newTotalShares) {
        require(_account != address(0), "BURN_FROM_ZERO_ADDR");

        uint256 accountShares = shares[_account];
        require(_sharesAmount <= accountShares, "BALANCE_EXCEEDED");

        uint256 preRebaseTokenAmount = getPooledEthByShares(_sharesAmount);

        newTotalShares = _getTotalShares().sub(_sharesAmount);
        //placeholder TOTAL_SHARES_POSITION.setStorageUint256(newTotalShares);

        shares[_account] = accountShares.sub(_sharesAmount);

        uint256 postRebaseTokenAmount = getPooledEthByShares(_sharesAmount);

        emit SharesBurnt(_account, preRebaseTokenAmount, postRebaseTokenAmount, _sharesAmount);

        // Notice: we're not emitting a Transfer event to the zero address here since shares burn
        // works by redistributing the amount of tokens corresponding to the burned shares between
        // all other token holders. The total supply of the token doesn't change as the result.
        // This is equivalent to performing a send from `address` to each other token holder address,
        // but we cannot reflect this as it would require sending an unbounded number of events.

        // We're emitting `SharesBurnt` event to provide an explicit rebase log record nonetheless.
    }

    
    function _emitTransferEvents(address _from, address _to, uint _tokenAmount, uint256 _sharesAmount) internal {
        emit Transfer(_from, _to, _tokenAmount);
        emit TransferShares(_from, _to, _sharesAmount);
    }

    
    function _emitTransferAfterMintingShares(address _to, uint256 _sharesAmount) internal {
        _emitTransferEvents(address(0), _to, getPooledEthByShares(_sharesAmount), _sharesAmount);
    }

    
    function _mintInitialShares(uint256 _sharesAmount) internal {
        _mintShares(INITIAL_TOKEN_HOLDER, _sharesAmount);
        _emitTransferAfterMintingShares(INITIAL_TOKEN_HOLDER, _sharesAmount);
    }
}

contract Demo {
    StETH token;
    address user1 =
        address(0x92349Ef835BA7Ea6590C3947Db6A11EeE1a90cFd); //just an arbitrary address
    constructor() {
        token = new StETH();
    }
    function DoTransfer() public{
        token.transfer(user1, 5);
    }
	function CheckUser1Balance() public view returns (uint256) {
        return token.balanceOf(user1);
    }
    function CheckOwnerBalance() public view returns (uint256) {
        return token.balanceOf(address(this));
    }
}