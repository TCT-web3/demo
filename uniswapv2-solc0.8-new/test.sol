// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity >=0.8.4;

//solhint-disable not-rely-on-time
//solhint-disable var-name-mixedcase
//solhint-disable reason-string

// import "./interfaces/IUniswapV2Factory.sol";
// import "./libraries/TransferHelper.sol";

// import "./interfaces/IUniswapV2Router.sol";
// import "./libraries/UniswapV2Library.sol";
// import "./interfaces/IERC20.sol";
// import "./interfaces/IWETH.sol";


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
    
    // function get_pair_hash() public pure returns (bytes32)
    // {
    //     bytes32 r=keccak256(type(UniswapV2Pair).creationCode);
    //     return r;
    // }
    
    
}