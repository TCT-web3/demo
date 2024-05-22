type uint256 = int;
const Zero : uint256;
axiom Zero == 0; 
const TwoE8 : uint256;
axiom TwoE8 == 32768; 

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
var FiatTokenV1.decimals:  [address] uint8;
var FiatTokenV1.masterMinter:  [address] address;
var FiatTokenV1.initialized:  [address] bool;
var FiatTokenV1.balanceAndBlacklistStates:  [address] [address] uint256;
var FiatTokenV1.allowed:  [address] [address] [address] uint256;
var FiatTokenV1.totalSupply_:  [address] uint256;
var FiatTokenV1.minters:  [address] [address] bool;
var FiatTokenV1.minterAllowed:  [address] [address] uint256;
var to:  address;
var value:  uint256;

procedure straightline_code ()
modifies Demo.user1, FiatTokenV1.decimals, FiatTokenV1.masterMinter, FiatTokenV1.initialized, FiatTokenV1.balanceAndBlacklistStates, FiatTokenV1.allowed, FiatTokenV1.totalSupply_, FiatTokenV1.minters, FiatTokenV1.minterAllowed, to, value;
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
	var tmp10:  bool;
	var tmp11:  bool;
	var tmp12:  uint256;
	var tmp13:  uint256;
	var tmp14:  bool;
	var tmp15:  bool;
	var tmp16:  bool;
	var tmp17:  bool;

	// declare-vars


	// def-vars
	var this.totalSupply:  uint256;
	this.totalSupply:= FiatTokenV1.totalSupply_[entry_contract];

	// hypothesis 
	assume(Zero == Zero);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= FiatTokenV1.balanceAndBlacklistStates[entry_contract][x] && FiatTokenV1.balanceAndBlacklistStates[entry_contract][x] <= this.totalSupply);
	assume( sum( FiatTokenV1.balanceAndBlacklistStates[entry_contract] ) == this.totalSupply);

	tmp1:=evmsub(tx_origin,0);
	assume(tmp1!=Zero);

	tmp2:=(to!=0);
	assume(tmp2);

	tmp3:=FiatTokenV1.balanceAndBlacklistStates[entry_contract][tx_origin];
	tmp4:= (value>tmp3);
	tmp5:=!tmp4;
	assume(tmp5);

	tmp6:=FiatTokenV1.balanceAndBlacklistStates[entry_contract][tx_origin];
	tmp7:= (value>tmp6);
	tmp8:=!tmp7;
	assume(tmp8);

	tmp9:=evmsub(tmp6,value);
	tmp10:= (tmp9>tmp6);
	tmp11:=!tmp10;
	assume(tmp11);

	FiatTokenV1.balanceAndBlacklistStates[entry_contract][tx_origin]:=tmp9;

	tmp12:=FiatTokenV1.balanceAndBlacklistStates[entry_contract][to];
	tmp13:=evmadd(tmp12,value);
	tmp14:= (tmp12>tmp13);
	tmp15:=!tmp14;
	assume(tmp15);

	tmp16:= (tmp13<tmp12);
	tmp17:=!tmp16;
	assume(tmp17);

	FiatTokenV1.balanceAndBlacklistStates[entry_contract][to]:=tmp13;

	assert(forall x:address :: Zero <= FiatTokenV1.balanceAndBlacklistStates[entry_contract][x] && FiatTokenV1.balanceAndBlacklistStates[entry_contract][x] <= this.totalSupply);
	assert( sum( FiatTokenV1.balanceAndBlacklistStates[entry_contract] ) == this.totalSupply);
}