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

var Demo.attacker1Address:  [address] address;
var Demo.attacker2Address2:  [address] address;
var Demo.benignUserAddress2:  [address] address;
var MultiVulnToken.owner:  [address] address;
var MultiVulnToken.totalSupply:  [address] uint256;
var MultiVulnToken.balances:  [address] [address] uint256;
var StandardToken.owner:  [address] address;
var StandardToken.totalSupply:  [address] uint256;
var StandardToken.balances:  [address] [address] uint256;
var Token.owner:  [address] address;
var Token.totalSupply:  [address] uint256;
var no_reentrancy_attack._to:  [address] address;
var reentrancy_attack._to:  [address] address;
var reentrancy_attack.count:  [address] uint256;
var _from:  address;
var _to:  address;
var _value:  uint256;
var _fee:  uint256;

procedure straightline_code ()
modifies Demo.attacker1Address, Demo.attacker2Address2, Demo.benignUserAddress2, MultiVulnToken.owner, MultiVulnToken.totalSupply, MultiVulnToken.balances, StandardToken.owner, StandardToken.totalSupply, StandardToken.balances, Token.owner, Token.totalSupply, no_reentrancy_attack._to, reentrancy_attack._to, reentrancy_attack.count, _from, _to, _value, _fee;
{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
	var tmp1:  uint256;
	var tmp2:  uint256;
	var tmp3:  bool;
	var tmp4:  bool;
	var tmp5:  uint256;
	var tmp6:  uint256;
	var tmp7:  uint256;
	var tmp8:  bool;
	var tmp9:  bool;
	var tmp10:  uint256;
	var tmp11:  uint256;
	var tmp12:  uint256;
	var tmp13:  bool;
	var tmp14:  bool;
	var tmp15:  uint256;
	var tmp16:  uint256;
	var tmp17:  uint256;
	var tmp18:  uint256;
	var tmp19:  uint256;
	var tmp20:  uint256;
	var tmp21:  uint256;

	// declare-vars


	// def-vars
	var totalSupply:  uint256;
	totalSupply:= MultiVulnToken.totalSupply[entry_contract];

	// user given hypothesis 
	assume(totalSupply<TwoE255);

	// addresses aliasing
	assume(_from!=_to);
	// input parameter concrete values
	assume(Zero<=_value);
	assume(_value<TwoE255);
	assume(Zero<=_fee);
	assume(_fee<TwoE254);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= MultiVulnToken.balances[entry_contract][x] && MultiVulnToken.balances[entry_contract][x] <= MultiVulnToken.totalSupply[entry_contract]);
	assume(sum( MultiVulnToken.balances[entry_contract] ) == MultiVulnToken.totalSupply[entry_contract]);

	tmp1:=MultiVulnToken.balances[entry_contract][_from];
	tmp2:=evmadd(_fee,_value);
	tmp3:= (tmp1<tmp2);
	tmp4:=!tmp3;
	assume(tmp4);

	tmp5:=MultiVulnToken.balances[entry_contract][_to];
	tmp6:=MultiVulnToken.balances[entry_contract][_to];
	tmp7:=evmadd(tmp6,_value);
	tmp8:= (tmp7<tmp5);
	tmp9:=!tmp8;
	assume(tmp9);

	tmp10:=MultiVulnToken.balances[entry_contract][tx_origin];
	tmp11:=MultiVulnToken.balances[entry_contract][tx_origin];
	tmp12:=evmadd(tmp11,_fee);
	tmp13:= (tmp12<tmp10);
	tmp14:=!tmp13;
	assume(tmp14);

	tmp15:=MultiVulnToken.balances[entry_contract][_to];
	tmp16:=evmadd(tmp15,_value);
	MultiVulnToken.balances[entry_contract][_to]:=tmp16;

	tmp17:=MultiVulnToken.balances[entry_contract][tx_origin];
	tmp18:=evmadd(tmp17,_fee);
	MultiVulnToken.balances[entry_contract][tx_origin]:=tmp18;

	tmp19:=MultiVulnToken.balances[entry_contract][_from];
	tmp20:=evmadd(_value,_fee);
	tmp21:=evmsub(tmp19,tmp20);
	MultiVulnToken.balances[entry_contract][_from]:=tmp21;


	// (post) insert invariant of entry contract
	assert(forall x:address :: Zero <= MultiVulnToken.balances[entry_contract][x] && MultiVulnToken.balances[entry_contract][x] <= MultiVulnToken.totalSupply[entry_contract]);
	assert(sum( MultiVulnToken.balances[entry_contract] ) == MultiVulnToken.totalSupply[entry_contract]);
}