type address;
type uint256 = real;
var ERC20.totalSupply: [address] uint256;
var ERC20.balanceOf: [address] [address] uint256;

function add(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: add(a,b) == a+b);
function sub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: sub(a,b) == a-b);
function mul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: mul(a,b) == a*b);
function preciseDiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: preciseDiv(a,b) == a / b);

procedure straightline_code ()
  modifies ERC20.balanceOf, ERC20.totalSupply;
{  
	var msg.sender: address ;
	var tokenA: address;
	var tokenB: address;
	var amountBDesired: uint256;
	var pair:address;
	var pair.reserve0: uint256;
	var pair.reserve1: uint256;
		
	//local vars
	var reserveA, reserveB, amountAOptimal, amountA, amountB : uint256;
	var _reserve0, _reserve1, balance0, balance1, amount0, amount1, _totalSupply, liquidity: uint256;
	
	//--------------------------The conjunction of these conditions is the "phi(v,s)" part in theorem tau: -------------
	assume tokenA != tokenB;
	assume msg.sender != pair;    //I didn't think of this condition until Boogie returned negative result.
	assume ERC20.balanceOf[tokenA][pair] !=0.0;
	assume ERC20.balanceOf[tokenB][pair] !=0.0;
	assume ERC20.totalSupply[pair]!=0.0;
	
	//assume invariants
	assume (pair.reserve0 == ERC20.balanceOf[tokenA][pair]);
	assume (pair.reserve1 == ERC20.balanceOf[tokenB][pair]);
	
	//--------------------------EVM code logic starts here: -------------
	reserveA := pair.reserve0;
	reserveB := pair.reserve1;
	amountAOptimal := preciseDiv(mul(amountBDesired , reserveA) , reserveB);
	amountA := amountAOptimal;
	amountB := amountBDesired;

	ERC20.balanceOf[tokenA][msg.sender] := sub(ERC20.balanceOf[tokenA][msg.sender] , amountA);
	ERC20.balanceOf[tokenA][pair] := add(ERC20.balanceOf[tokenA][pair] , amountA);
	ERC20.balanceOf[tokenB][msg.sender] := sub(ERC20.balanceOf[tokenB][msg.sender] , amountB);
	ERC20.balanceOf[tokenB][pair] := add(ERC20.balanceOf[tokenB][pair] , amountB);
	
	_reserve0 := pair.reserve0;         
	_reserve1 := pair.reserve1; 
	balance0 := ERC20.balanceOf[tokenA][pair];
	balance1 := ERC20.balanceOf[tokenB][pair];
	amount0 := sub(balance0 , _reserve0);
	amount1 := sub(balance1 , _reserve1);

	_totalSupply := ERC20.totalSupply[pair];
	liquidity := preciseDiv(mul(_totalSupply , amount0) , _reserve0);

	ERC20.totalSupply[pair] := add(ERC20.totalSupply[pair] , liquidity);
	ERC20.balanceOf[pair][msg.sender] := add(ERC20.balanceOf[pair][msg.sender] , liquidity);
	pair.reserve0 := balance0;
	pair.reserve1 := balance1;

	//We want to prove the invariant:
	//assert( preciseDiv(ERC20.balanceOf[tokenA][pair] , old_reserveA) == preciseDiv(ERC20.balanceOf[tokenB][pair] , old_reserveB));
	assert( preciseDiv(ERC20.balanceOf[tokenA][pair] , old(ERC20.balanceOf[tokenA][pair])) == preciseDiv(ERC20.balanceOf[tokenB][pair] , old(ERC20.balanceOf[tokenB][pair])));
	assert( preciseDiv(ERC20.balanceOf[tokenB][pair] , old(ERC20.balanceOf[tokenB][pair])) == preciseDiv(ERC20.totalSupply[pair] , old(ERC20.totalSupply[pair])));
	
	//Finally, dont forget to prove the invariant
	assert (pair.reserve0 == ERC20.balanceOf[tokenA][pair]);
	assert (pair.reserve1 == ERC20.balanceOf[tokenB][pair]);
}    