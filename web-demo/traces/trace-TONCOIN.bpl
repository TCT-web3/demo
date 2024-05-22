type uint256 = real;
const Zero : uint256;
axiom Zero == 0.0; 
const TwoE8 : uint256;
axiom TwoE8 == 32768.0; 

function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmdiv(evmmul(a,b),a)==b ==> evmmul(a,b) == a*b);

type address = int;
type bytes32 = int;
type uint8 = int;
const TwoE16 : uint256;
axiom TwoE16 == TwoE8 * TwoE8; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 * TwoE8;
const TwoE256 : uint256; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=Zero ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=Zero ==> evmadd(a,b) == a+b-TwoE256);
axiom (forall a,b: uint256 :: evmadd(a,b)>=a ==> evmadd(a,b) == a+b);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a>=b ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a<b ==> evmsub(a,b) == a-b+TwoE256);
axiom (forall a,b: uint256 :: evmsub(a,b)<=a ==> evmsub(a,b) == a-b);

function evmmod(a,b:uint256) returns (uint256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: Zero<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));

function nondet() returns (uint256);

var Demo.user1:  [address] address;
var ERC20._balances:  [address] [address] uint256;
var ERC20._allowances:  [address] [address] [address] uint256;
var ERC20._totalSupply:  [address] uint256;
var WrappedTON._balances:  [address] [address] uint256;
var WrappedTON._allowances:  [address] [address] [address] uint256;
var WrappedTON._totalSupply:  [address] uint256;
var recipient:  address;
var amount:  uint256;

procedure straightline_code ()
modifies Demo.user1, ERC20._balances, ERC20._allowances, ERC20._totalSupply, WrappedTON._balances, WrappedTON._allowances, WrappedTON._totalSupply, recipient, amount;
{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
	var tmp1:  uint256;
	var tmp2:  bool;
	var tmp3:  uint256;
	var tmp4:  bool;
	var tmp5:  bool;
	var tmp6:  uint256;
	var tmp7:  bool;
	var tmp8:  bool;
	var tmp9:  uint256;
	var tmp10:  uint256;
	var tmp11:  bool;
	var tmp12:  bool;

	// declare-vars


	// def-vars

	// hypothesis 
	assume(1.0 == 1.0);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= WrappedTON._balances[entry_contract][x] && WrappedTON._balances[entry_contract][x] <= WrappedTON._totalSupply[entry_contract]);
	assume(sum( WrappedTON._balances[entry_contract] ) == WrappedTON._totalSupply[entry_contract]);

	tmp1:=evmsub(tx_origin,0.0);
	assume(tmp1!=Zero);

	tmp2:=(recipient!=0);
	assume(tmp2);

	tmp3:=WrappedTON._balances[entry_contract][tx_origin];
	tmp4:= (tmp3<amount);
	tmp5:=!tmp4;
	assume(tmp5);

	tmp6:=evmsub(tmp3,amount);
	tmp7:= (tmp6>tmp3);
	tmp8:=!tmp7;
	assume(tmp8);

	WrappedTON._balances[entry_contract][tx_origin]:=tmp6;

	tmp9:=WrappedTON._balances[entry_contract][recipient];
	tmp10:=evmadd(tmp9,amount);
	tmp11:= (tmp9>tmp10);
	tmp12:=!tmp11;
	assume(tmp12);

	WrappedTON._balances[entry_contract][recipient]:=tmp10;


	// (post) insert invariant of entry contract
	assert(forall x:address :: Zero <= WrappedTON._balances[entry_contract][x] && WrappedTON._balances[entry_contract][x] <= WrappedTON._totalSupply[entry_contract]);
	assert(sum( WrappedTON._balances[entry_contract] ) == WrappedTON._totalSupply[entry_contract]);
}