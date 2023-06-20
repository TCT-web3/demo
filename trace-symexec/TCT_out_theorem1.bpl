type address = int;
type uint256 = int;
var totalSupply: uint256;
const TwoE16 : uint256;
axiom TwoE16 == 65536; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768;
const TwoE256 : int; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b-TwoE256);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b<0 ==> evmsub(a,b) == a-b+TwoE256);

function evmand(a, b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmand(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmand(a,b) == a+b-TwoE256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: 0<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));    

var balances: [address] uint256;

procedure straightline_code ()
modifies balances;
{  
    var msg.sender: address ;
    var _from: address ;
    var _to: address;
    var _value: uint256;
    var _fee: uint256;
       
	var tmp1: uint256;
	var tmp2: uint256;
	var tmp3: bool;
	var tmp4: bool;
	var tmp6: uint256;
	var tmp5: uint256;
	var tmp7: uint256;
	var tmp8: bool;
	var tmp9: bool;
	var tmp11: uint256;
	var tmp10: uint256;
	var tmp12: uint256;
	var tmp13: bool;
	var tmp14: bool;
	var tmp16: uint256;
	var tmp15: uint256;
	var tmp18: uint256;
	var tmp17: uint256;
	var tmp20: uint256;
	var tmp21: uint256;
	var tmp19: uint256;

	assume(0<=_value && _value<TwoE255 && 0<=_fee && _fee<TwoE255 && totalSupply<TwoE255);
	assume(forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply);
	assume( sum(balances) == totalSupply );

	tmp1:=balances[_from];
	tmp2:=evmadd(_fee,_value);
	tmp3:=tmp1<tmp2;
	tmp4:=!tmp3;
	assume(tmp4);

	tmp6:=balances[_to];
	tmp5:=evmadd(tmp6,_value);
	tmp7:=balances[_to];
	tmp8:=tmp5<tmp7;
	tmp9:=!tmp8;
	assume(tmp9);

	tmp11:=balances[msg.sender];
	tmp10:=evmadd(tmp11,_fee);
	tmp12:=balances[msg.sender];
	tmp13:=tmp10<tmp12;
	tmp14:=!tmp13;
	assume(tmp14);

	tmp16:=balances[_to];
	tmp15:=evmadd(tmp16,_value);
	balances[_to]:=tmp15;

	tmp18:=balances[msg.sender];
	tmp17:=evmadd(tmp18,_fee);
	balances[msg.sender]:=tmp17;

	tmp20:=balances[_from];
	tmp21:=evmadd(_value,_fee);
	tmp19:=evmsub(tmp20,tmp21);
	balances[_from]:=tmp19;

	assert(forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply);
	assert( sum(balances) == totalSupply );
}