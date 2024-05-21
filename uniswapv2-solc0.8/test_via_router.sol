// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity >=0.8.4;

/* How to use this file in Remix
+ Deploy Test
+ Click getAddress, which gives three address:
    0: address: 0x7F7fF6b7695c3cC810f63aC8D5D71aE4929BdB87
    1: address: 0x02180dD815cA64898F6126f3911515B06D17acaD
    2: address: 0x0A9C6D9d0AF27FC9F3F96196c3F8c89C79Df287D
+ Prepare the following argument string in notepad, using the last two addresses. Note that "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4" is the automatic account in remix
    10,1,[0x02180dD815cA64898F6126f3911515B06D17acaD,0x0A9C6D9d0AF27FC9F3F96196c3F8c89C79Df287D],0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
+ Use 0x7F7fF6b7695c3cC810f63aC8D5D71aE4929BdB87 in the "At Address" box to load the UniswapV2Router contract
+ In the swapExactTokensForTokens box, enter the argument string.
*/

import "./libraries/UniswapV2Library.sol";
import "./UniswapV2Factory.sol";
import "./UniswapV2Router.sol";
import "./tokens/FancyToken.sol";

contract Test {
    address _feeToSetter;
    UniswapV2Factory _factory;
    UniswapV2Router _router;
    FancyToken _tokenA;
    FancyToken _tokenB;
    constructor ()
    {
        _feeToSetter = address(this);
        _factory = new UniswapV2Factory(_feeToSetter);
        _factory.setFeeTo(_feeToSetter);
        _tokenA = new FancyToken();
        _tokenB = new FancyToken();
        _factory.createPair(address(_tokenA),address(_tokenB));
        _router = new UniswapV2Router(address(_factory));

        _router.addLiquidity(
            address(_tokenA),
            address(_tokenB),
            2000,
            1000,
            2000,
            1000,
            address(this)
        );

        _router.addLiquidity(
            address(_tokenA),
            address(_tokenB),
            2000,
            1000,
            2000,
            1000,
            address(msg.sender)
        );

        _tokenA.transfer(msg.sender,100000);
        _tokenB.transfer(msg.sender,100000);
    }
    
    function approve() public {
        address pair = UniswapV2Library.pairFor(address(_factory), address(_tokenA), address(_tokenB));
        IERC20(pair).approve(address(_router),40000);
        IERC20(pair).approve(address(msg.sender),40000);
    }

    function call_removeLiquidity() public {
        _router.removeLiquidity(
            address(_tokenA),
            address(_tokenB),
            20,
            1,
            1,
            address(this)
        );
    }

    function getLiquidity() public view returns (uint256) {
        address pair = UniswapV2Library.pairFor(address(_factory), address(_tokenA), address(_tokenB));
        return IERC20(pair).balanceOf(address(this));
    }

    function getRouterAllowance() public view returns (uint256) {
        address pair = UniswapV2Library.pairFor(address(_factory), address(_tokenA), address(_tokenB));
        return IERC20(pair).allowance(address(this),address(_router));
    }

    function getAddresses() public view returns (address,address,address,address) {
        address pair = UniswapV2Library.pairFor(address(_factory), address(_tokenA), address(_tokenB));
        return (address(_router),address(_tokenA),address(_tokenB), address(pair));
    }

    function getBalances() public view returns (uint256,uint256,uint256,uint256) {
        address pair_addr = UniswapV2Library.pairFor(address(_factory), address(_tokenA), address(_tokenB));
        UniswapV2Pair pair = UniswapV2Pair(pair_addr);
        return (pair.reserve0(),pair.reserve1(),_tokenA.balanceOf(pair_addr), _tokenB.balanceOf(pair_addr));
    }

    function call_addLiquidity() public
    {
        _router.addLiquidity(
            address(_tokenA),
            address(_tokenB),
            2000,
            1000,
            2000,
            1000,
            address(this)
        );
    }

    function call_swapExactTokensForTokens() public
    {
        address[] memory path = new address[](2);
        path[0] = address(_tokenA);
        path[1] = address(_tokenB);
        _router.swapExactTokensForTokens(
            10,
            1,
            path,
            msg.sender
        );
    }
}