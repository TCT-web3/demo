pragma solidity >=0.8.4;

// USDC (FiatTokenV2_2) @ 0x43506849d7c04f9138d1a2050bbf3a0c054402dd

/**
 * SPDX-License-Identifier: Apache-2.0
 *
 * Copyright (c) 2023, Circle Internet Financial, LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

//import { SafeMath } from "@openzeppelin/contracts/math/SafeMath.sol";
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

/// @custom:tct invariant: forall x:address :: Zero <= this.balances[x] && this.balances[x] <= this.totalSupply
/// @custom:tct invariant: sum( this.balances ) == this.totalSupply
contract FiatTokenV1  {
    using SafeMath for uint256;

    string public name;
    string public symbol;
    uint8 public decimals;
    string public currency;
    address public masterMinter;
    bool internal initialized;

    /// @dev A mapping that stores the balance and blacklist states for a given address.
    /// The first bit defines whether the address is blacklisted (1 if blacklisted, 0 otherwise).
    /// The last 255 bits define the balance for the address.
    mapping(address => uint256) internal balanceAndBlacklistStates;
    mapping(address => mapping(address => uint256)) internal allowed;
    uint256 internal totalSupply_ = 0;
    mapping(address => bool) internal minters;
    mapping(address => uint256) internal minterAllowed;

    event Mint(address indexed minter, address indexed to, uint256 amount);
    event Burn(address indexed burner, uint256 amount);
    event MinterConfigured(address indexed minter, uint256 minterAllowedAmount);
    event MinterRemoved(address indexed oldMinter);
    event MasterMinterChanged(address indexed newMasterMinter);


    constructor(
        string memory tokenName,
        string memory tokenSymbol,
        string memory tokenCurrency,
        uint8 tokenDecimals,
        address newMasterMinter,
        address newPauser,
        address newBlacklister,
        address newOwner
    ) {
        require(!initialized, "FiatToken: contract is already initialized");
        require(
            newMasterMinter != address(0),
            "FiatToken: new masterMinter is the zero address"
        );
        require(
            newPauser != address(0),
            "FiatToken: new pauser is the zero address"
        );
        require(
            newBlacklister != address(0),
            "FiatToken: new blacklister is the zero address"
        );
        require(
            newOwner != address(0),
            "FiatToken: new owner is the zero address"
        );

        name = tokenName;
        symbol = tokenSymbol;
        currency = tokenCurrency;
        decimals = tokenDecimals;
        masterMinter = newMasterMinter;
        //pauser = newPauser;
        //blacklister = newBlacklister;
        //setOwner(newOwner);
        totalSupply_ = 10** tokenDecimals;
        balanceAndBlacklistStates[msg.sender] = totalSupply_;
        initialized = true;
    }

    
    modifier onlyMinters() {
        require(minters[msg.sender], "FiatToken: caller is not a minter");
        _;
    }

    
    function mint(address _to, uint256 _amount)
        external
        onlyMinters
        returns (bool)
    {
        require(_to != address(0), "FiatToken: mint to the zero address");
        require(_amount > 0, "FiatToken: mint amount not greater than 0");

        uint256 mintingAllowedAmount = minterAllowed[msg.sender];
        require(
            _amount <= mintingAllowedAmount,
            "FiatToken: mint amount exceeds minterAllowance"
        );

        totalSupply_ = totalSupply_.add(_amount);
        _setBalance(_to, _balanceOf(_to).add(_amount));
        minterAllowed[msg.sender] = mintingAllowedAmount.sub(_amount);
        emit Mint(msg.sender, _to, _amount);
        //emit Transfer(address(0), _to, _amount);
        return true;
    }

    
    modifier onlyMasterMinter() {
        require(
            msg.sender == masterMinter,
            "FiatToken: caller is not the masterMinter"
        );
        _;
    }

    
    function minterAllowance(address minter) external view returns (uint256) {
        return minterAllowed[minter];
    }

    
    function isMinter(address account) external view returns (bool) {
        return minters[account];
    }

    
    function allowance(address owner, address spender)
        external
        view
        returns (uint256)
    {
        return allowed[owner][spender];
    }

    
    function totalSupply() external view returns (uint256) {
        return totalSupply_;
    }

    
    function balanceOf(address account)
        external
        view
        returns (uint256)
    {
        return _balanceOf(account);
    }

    
    function approve(address spender, uint256 value)
        external
        virtual
        returns (bool)
    {
        _approve(msg.sender, spender, value);
        return true;
    }

    
    function _approve(
        address owner,
        address spender,
        uint256 value
    ) internal {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");
        allowed[owner][spender] = value;
        //emit Approval(owner, spender, value);
    }

    
    function transferFrom(
        address from,
        address to,
        uint256 value
    )
        external
        returns (bool)
    {
        require(
            value <= allowed[from][msg.sender],
            "ERC20: transfer amount exceeds allowance"
        );
        _transfer(from, to, value);
        allowed[from][msg.sender] = allowed[from][msg.sender].sub(value);
        return true;
    }

    
    function transfer(address to, uint256 value)
        external
        returns (bool)
    {
        _transfer(msg.sender, to, value);
        return true;
    }

    
    function _transfer(
        address from,
        address to,
        uint256 value
    ) internal {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");
        require(
            value <= _balanceOf(from),
            "ERC20: transfer amount exceeds balance"
        );

        _setBalance(from, _balanceOf(from).sub(value));
        _setBalance(to, _balanceOf(to).add(value));
        //emit Transfer(from, to, value);
    }

    
    function configureMinter(address minter, uint256 minterAllowedAmount)
        external
        onlyMasterMinter
        returns (bool)
    {
        minters[minter] = true;
        minterAllowed[minter] = minterAllowedAmount;
        emit MinterConfigured(minter, minterAllowedAmount);
        return true;
    }

    
    function removeMinter(address minter)
        external
        onlyMasterMinter
        returns (bool)
    {
        minters[minter] = false;
        minterAllowed[minter] = 0;
        emit MinterRemoved(minter);
        return true;
    }

    
    function burn(uint256 _amount)
        external
        onlyMinters
    {
        uint256 balance = _balanceOf(msg.sender);
        require(_amount > 0, "FiatToken: burn amount not greater than 0");
        require(balance >= _amount, "FiatToken: burn amount exceeds balance");

        totalSupply_ = totalSupply_.sub(_amount);
        _setBalance(msg.sender, balance.sub(_amount));
        emit Burn(msg.sender, _amount);
        //emit Transfer(msg.sender, address(0), _amount);
    }

    
    function updateMasterMinter(address _newMasterMinter) external {
        require(
            _newMasterMinter != address(0),
            "FiatToken: new masterMinter is the zero address"
        );
        masterMinter = _newMasterMinter;
        emit MasterMinterChanged(masterMinter);
    }

    
    function _setBalance(address _account, uint256 _balance) internal virtual {
        balanceAndBlacklistStates[_account] = _balance;
    }

    
    function _balanceOf(address _account)
        internal
        virtual
        view
        returns (uint256)
    {
        return balanceAndBlacklistStates[_account];
    }
}


contract Demo {
    FiatTokenV1 token;
    address user1 =
        address(0x92349Ef835BA7Ea6590C3947Db6A11EeE1a90cFd); //just an arbitrary address
    constructor() {
        token = new FiatTokenV1("USDC","USDC","USDC",18,msg.sender,msg.sender,msg.sender,msg.sender);
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