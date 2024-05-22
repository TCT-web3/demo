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
var StETH.shares:  [address] [address] uint256;
var StETH.allowances:  [address] [address] [address] uint256;
var _recipient:  address;
var _amount:  uint256;

procedure straightline_code ()
modifies Demo.user1, StETH.shares, StETH.allowances, _recipient, _amount;
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
	var tmp9:  bool;
	var tmp10:  bool;
	var tmp11:  bool;
	var tmp12:  uint256;
	var tmp13:  uint256;
	var tmp14:  bool;
	var tmp15:  bool;
	var tmp16:  bool;
	var tmp17:  bool;
	var tmp18:  uint256;
	var tmp19:  bool;
	var tmp20:  bool;
	var tmp21:  uint256;
	var tmp22:  uint256;
	var tmp23:  bool;
	var tmp24:  bool;
	var tmp25:  bool;
	var tmp26:  bool;

	// declare-vars


	// def-vars

	// hypothesis 
	assume(Zero == Zero);

	// insert invariant of entry contract
	assume(forall x:address :: Zero <= StETH.shares[entry_contract][x] && StETH.shares[entry_contract][x] <= 9765625.0);
	assume(sum( StETH.shares[entry_contract] ) == 9765625.0);

	tmp1:=evmsub(_amount,0.0);
	assume(tmp1!=Zero);

	tmp2:=_amount==Zero;
	tmp3:=evmmul(_amount,1000000000000000000.0);
	tmp4:=evmdiv(tmp3,_amount);
	tmp5:= (1000000000000000000.0==tmp4);
	tmp6:=tmp2||tmp5;
	assume(tmp6);

	assume(_amount!=Zero);

	tmp7:=evmdiv(tmp3,_amount);
	tmp8:= (tmp7==1000000000000000000.0);
	assume(tmp8);

	tmp9:=tx_origin==0;
	assume(!tmp9);

	tmp10:=(_recipient!=0);
	assume(tmp10);

	tmp11:=(_recipient!=entry_contract);
	assume(tmp11);

	tmp12:=StETH.shares[entry_contract][tx_origin];
	tmp13:=evmdiv(tmp3,9765625.0);
	tmp14:= (tmp13>tmp12);
	tmp15:=!tmp14;
	assume(tmp15);

	tmp16:= (tmp13>tmp12);
	tmp17:=!tmp16;
	assume(tmp17);

	tmp18:=evmsub(tmp12,tmp13);
	tmp19:= (tmp18>tmp12);
	tmp20:=!tmp19;
	assume(tmp20);

	StETH.shares[entry_contract][tx_origin]:=tmp18;

	tmp21:=StETH.shares[entry_contract][_recipient];
	tmp22:=evmadd(tmp21,tmp13);
	tmp23:= (tmp21>tmp22);
	tmp24:=!tmp23;
	assume(tmp24);

	tmp25:= (tmp22<tmp21);
	tmp26:=!tmp25;
	assume(tmp26);

	StETH.shares[entry_contract][_recipient]:=tmp22;


	// (post) insert invariant of entry contract
	assert(forall x:address :: Zero <= StETH.shares[entry_contract][x] && StETH.shares[entry_contract][x] <= 9765625.0);
	assert(sum( StETH.shares[entry_contract] ) == 9765625.0);
}