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
var _to:  address;
var reentrancy_attack.multiVulnToken:  [address] address;

procedure straightline_code ()
modifies Demo.attacker1Address, Demo.attacker2Address2, Demo.benignUserAddress2, MultiVulnToken.owner, MultiVulnToken.totalSupply, MultiVulnToken.balances, StandardToken.owner, StandardToken.totalSupply, StandardToken.balances, Token.owner, Token.totalSupply, no_reentrancy_attack._to, reentrancy_attack._to, reentrancy_attack.count, _to, reentrancy_attack.multiVulnToken;
{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
	var tmp1:  uint256;
	var tmp2:  uint256;
	var tmp3:  uint256;
	var tmp4:  bool;
	var tmp5:  bool;
	var tmp6:  uint256;
	var tmp7:  uint256;
	var tmp8:  bool;
	var tmp9:  bool;
	var tmp10:  uint256;
	var tmp11:  uint256;
	var tmp12:  uint256;
	var tmp13:  bool;
	var tmp14:  bool;

	// declare-vars


	// def-vars
	var totalSupply:  uint256;
	totalSupply:= MultiVulnToken.totalSupply[entry_contract];

	// hypothesis 
	assume(totalSupply < TwoE256 && tx_origin != _to);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= MultiVulnToken.balances[entry_contract][x] && MultiVulnToken.balances[entry_contract][x] <= MultiVulnToken.totalSupply[entry_contract]);
	assume(sum( MultiVulnToken.balances[entry_contract] ) == MultiVulnToken.totalSupply[entry_contract]);

	tmp1:=MultiVulnToken.balances[entry_contract][tx_origin];
	tmp2:=MultiVulnToken.balances[entry_contract][_to];
	tmp3:=evmadd(tmp2,tmp1);
	MultiVulnToken.balances[entry_contract][_to]:=tmp3;

	tmp4:= (reentrancy_attack.count[tx_origin]<1);
	tmp5:=!tmp4;
	assume(!tmp5);

	tmp6:=evmadd(1,reentrancy_attack.count[tx_origin]);
	reentrancy_attack.count[tx_origin]:=tmp6;

	tmp7:=nondet(); //EXTCODESIZE
	tmp8:=tmp7==Zero;
	tmp9:=!tmp8;
	assume(tmp9);

	// insert invariant of MultiVulnToken
	assume(forall x:address :: Zero <= MultiVulnToken.balances[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]][x] && MultiVulnToken.balances[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]][x] <= MultiVulnToken.totalSupply[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]]);
	assume(sum( MultiVulnToken.balances[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]] ) == MultiVulnToken.totalSupply[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]]);

	tmp10:=MultiVulnToken.balances[reentrancy_attack.multiVulnToken[tx_origin]][tx_origin];
	tmp11:=MultiVulnToken.balances[reentrancy_attack.multiVulnToken[tx_origin]][reentrancy_attack._to[tx_origin]];
	tmp12:=evmadd(tmp11,tmp10);
	MultiVulnToken.balances[reentrancy_attack.multiVulnToken[tx_origin]][reentrancy_attack._to[tx_origin]]:=tmp12;

	tmp13:= (reentrancy_attack.count[tx_origin]<1);
	tmp14:=!tmp13;
	assume(tmp14);

	MultiVulnToken.balances[reentrancy_attack.multiVulnToken[tx_origin]][tx_origin]:=0;

	assume(forall x:address :: Zero <= MultiVulnToken.balances[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]][x] && MultiVulnToken.balances[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]][x] <= MultiVulnToken.totalSupply[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]]);
	assume(sum( MultiVulnToken.balances[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]] ) == MultiVulnToken.totalSupply[MultiVulnToken.multiVulnToken[reentrancy_attack][tx_origin]]);
	MultiVulnToken.balances[entry_contract][tx_origin]:=0;


	// (post) insert invariant of entry contract
	assert(forall x:address :: Zero <= MultiVulnToken.balances[entry_contract][x] && MultiVulnToken.balances[entry_contract][x] <= MultiVulnToken.totalSupply[entry_contract]);
	assert(sum( MultiVulnToken.balances[entry_contract] ) == MultiVulnToken.totalSupply[entry_contract]);
}