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

var BasicToken._totalSupply:  [address] uint256;
var BasicToken.owner:  [address] address;
var BasicToken.balances:  [address] [address] uint256;
var BasicToken.basisPointsRate:  [address] uint256;
var BasicToken.maximumFee:  [address] uint256;
var Demo.user1:  [address] address;
var ERC20._totalSupply:  [address] uint256;
var ERC20Basic._totalSupply:  [address] uint256;
var StandardToken._totalSupply:  [address] uint256;
var StandardToken.owner:  [address] address;
var StandardToken.balances:  [address] [address] uint256;
var StandardToken.basisPointsRate:  [address] uint256;
var StandardToken.maximumFee:  [address] uint256;
var StandardToken.allowed:  [address] [address] [address] uint256;
var TetherToken._totalSupply:  [address] uint256;
var TetherToken.owner:  [address] address;
var TetherToken.balances:  [address] [address] uint256;
var TetherToken.basisPointsRate:  [address] uint256;
var TetherToken.maximumFee:  [address] uint256;
var TetherToken.allowed:  [address] [address] [address] uint256;
var TetherToken.decimals:  [address] uint256;
var _to:  address;
var _value:  uint256;

procedure straightline_code ()
modifies BasicToken._totalSupply, BasicToken.owner, BasicToken.balances, BasicToken.basisPointsRate, BasicToken.maximumFee, Demo.user1, ERC20._totalSupply, ERC20Basic._totalSupply, StandardToken._totalSupply, StandardToken.owner, StandardToken.balances, StandardToken.basisPointsRate, StandardToken.maximumFee, StandardToken.allowed, TetherToken._totalSupply, TetherToken.owner, TetherToken.balances, TetherToken.basisPointsRate, TetherToken.maximumFee, TetherToken.allowed, TetherToken.decimals, _to, _value;
{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
	var tmp1:  uint256;
	var tmp2:  bool;
	var tmp3:  uint256;
	var tmp4:  uint256;
	var tmp5:  bool;
	var tmp6:  bool;
	var tmp7:  uint256;
	var tmp8:  bool;
	var tmp9:  uint256;
	var tmp10:  bool;
	var tmp11:  bool;
	var tmp12:  bool;
	var tmp13:  bool;
	var tmp14:  uint256;
	var tmp15:  bool;
	var tmp16:  bool;
	var tmp17:  uint256;
	var tmp18:  bool;
	var tmp19:  bool;
	var tmp20:  uint256;
	var tmp21:  bool;
	var tmp22:  bool;
	var tmp23:  uint256;
	var tmp24:  uint256;
	var tmp25:  bool;
	var tmp26:  bool;
	var tmp27:  bool;
	var tmp28:  bool;
	var tmp29:  bool;
	var tmp30:  bool;

	// declare-vars


	// def-vars
	var this._totalSupply:  uint256;
	this._totalSupply:= TetherToken._totalSupply[entry_contract];

	// hypothesis 
	assume(1.0 == 1.0);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= TetherToken.balances[entry_contract][x] && TetherToken.balances[entry_contract][x] <= TetherToken._totalSupply[entry_contract]);
	assume(sum( TetherToken.balances[entry_contract] ) == TetherToken._totalSupply[entry_contract]);

	tmp1:=evmsub(_value,0.0);
	assume(tmp1!=Zero);

	tmp2:=_value==Zero;
	tmp3:=evmmul(_value,TetherToken.basisPointsRate[entry_contract]);
	tmp4:=evmdiv(tmp3,_value);
	tmp5:= (TetherToken.basisPointsRate[entry_contract]==tmp4);
	tmp6:=tmp2||tmp5;
	assume(tmp6);

	assume(_value!=Zero);

	tmp7:=evmdiv(tmp3,_value);
	tmp8:= (tmp7==TetherToken.basisPointsRate[entry_contract]);
	assume(tmp8);

	tmp9:=evmdiv(tmp3,10000.0);
	tmp10:= (tmp9>TetherToken.maximumFee[entry_contract]);
	tmp11:=!tmp10;
	assume(tmp11);

	tmp12:= (tmp9>_value);
	tmp13:=!tmp12;
	assume(tmp13);

	tmp14:=evmsub(_value,tmp9);
	tmp15:= (tmp14>_value);
	tmp16:=!tmp15;
	assume(tmp16);

	tmp17:=TetherToken.balances[entry_contract][tx_origin];
	tmp18:= (_value>tmp17);
	tmp19:=!tmp18;
	assume(tmp19);

	tmp20:=evmsub(tmp17,_value);
	tmp21:= (tmp20>tmp17);
	tmp22:=!tmp21;
	assume(tmp22);

	TetherToken.balances[entry_contract][tx_origin]:=tmp20;

	tmp23:=TetherToken.balances[entry_contract][_to];
	tmp24:=evmadd(tmp23,tmp14);
	tmp25:= (tmp23>tmp24);
	tmp26:=!tmp25;
	assume(tmp26);

	tmp27:= (tmp24<tmp23);
	tmp28:=!tmp27;
	assume(tmp28);

	TetherToken.balances[entry_contract][_to]:=tmp24;

	tmp29:= (tmp9>0.0);
	tmp30:=!tmp29;
	assume(tmp30);


	// (post) insert invariant of entry contract
	assert(forall x:address :: Zero <= TetherToken.balances[entry_contract][x] && TetherToken.balances[entry_contract][x] <= TetherToken._totalSupply[entry_contract]);
	assert(sum( TetherToken.balances[entry_contract] ) == TetherToken._totalSupply[entry_contract]);
}