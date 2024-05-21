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

var BNB.decimals:  [address] uint8;
var BNB.totalSupply:  [address] uint256;
var BNB.owner:  [address] address;
var BNB.balanceOf:  [address] [address] uint256;
var BNB.freezeOf:  [address] [address] uint256;
var BNB.allowance:  [address] [address] [address] uint256;
var Demo.user1:  [address] address;
var _to:  address;
var _value:  uint256;

procedure straightline_code ()
modifies BNB.decimals, BNB.totalSupply, BNB.owner, BNB.balanceOf, BNB.freezeOf, BNB.allowance, Demo.user1, _to, _value;
{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
	var tmp1:  bool;
	var tmp2:  bool;
	var tmp3:  uint256;
	var tmp4:  bool;
	var tmp5:  bool;
	var tmp6:  uint256;
	var tmp7:  uint256;
	var tmp8:  uint256;
	var tmp9:  bool;
	var tmp10:  bool;
	var tmp11:  bool;
	var tmp12:  bool;
	var tmp13:  uint256;
	var tmp14:  bool;
	var tmp15:  bool;
	var tmp16:  uint256;
	var tmp17:  bool;
	var tmp18:  bool;
	var tmp19:  uint256;
	var tmp20:  uint256;
	var tmp21:  bool;
	var tmp22:  bool;
	var tmp23:  bool;
	var tmp24:  bool;
	var tmp25:  bool;
	var tmp26:  bool;
	var tmp27:  bool;

	// declare-vars


	// def-vars
	var totalSupply:  uint256;
	totalSupply:= BNB.totalSupply[entry_contract];

	// hypothesis 
	assume(totalSupply < TwoE256 && tx_origin != _to);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= BNB.balanceOf[entry_contract][x] && BNB.balanceOf[entry_contract][x] <= BNB.totalSupply[entry_contract]);
	assume(sum( BNB.balanceOf[entry_contract] ) == BNB.totalSupply[entry_contract]);

	tmp1:=(_to!=0);
	assume(tmp1);

	tmp2:= (_value>0.0);
	assume(tmp2);

	tmp3:=BNB.balanceOf[entry_contract][tx_origin];
	tmp4:= (tmp3<_value);
	tmp5:=!tmp4;
	assume(tmp5);

	tmp6:=BNB.balanceOf[entry_contract][_to];
	tmp7:=BNB.balanceOf[entry_contract][_to];
	tmp8:=evmadd(tmp7,_value);
	tmp9:= (tmp7>tmp8);
	tmp10:=!tmp9;
	assume(tmp10);

	tmp11:= (tmp8<tmp6);
	tmp12:=!tmp11;
	assume(tmp12);

	tmp13:=BNB.balanceOf[entry_contract][tx_origin];
	tmp14:= (_value>tmp13);
	tmp15:=!tmp14;
	assume(tmp15);

	tmp16:=evmsub(tmp13,_value);
	tmp17:= (tmp16>tmp13);
	tmp18:=!tmp17;
	assume(tmp18);

	BNB.balanceOf[entry_contract][tx_origin]:=tmp16;

	tmp19:=BNB.balanceOf[entry_contract][_to];
	tmp20:=evmadd(tmp19,_value);
	tmp21:= (tmp19>tmp20);
	tmp22:=!tmp21;
	assume(tmp22);

	tmp23:= (tmp20<tmp19);
	tmp24:=!tmp23;
	tmp25:=!tmp24;
	assume(!tmp25);

	tmp26:= (tmp20<_value);
	tmp27:=!tmp26;
	assume(tmp27);

	BNB.balanceOf[entry_contract][_to]:=tmp20;


	// (post) insert invariant of entry contract
	assert(forall x:address :: Zero <= BNB.balanceOf[entry_contract][x] && BNB.balanceOf[entry_contract][x] <= BNB.totalSupply[entry_contract]);
	assert(sum( BNB.balanceOf[entry_contract] ) == BNB.totalSupply[entry_contract]);
}