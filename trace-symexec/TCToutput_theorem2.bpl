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
       
	var tmp2: uint256;
	var tmp3: uint256;
	var tmp1: uint256;
	var tmp5: uint256;
	var tmp6: uint256;
	var tmp4: uint256;
	var tmp7: bool;
	var tmp8: bool;
	var tmp9: bool;

	assume(totalSupply<TwoE256 && msg.sender!=_to );
	assume(forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply);
	assume( sum(balances) == totalSupply );

	tmp2:=evmand(fff,msg.sender);
	tmp3:=evmand(fff,_to);
	tmp1:=evmsub(tmp2,tmp3);
	assume(tmp1);

	tmp5:=balances[_to];
	tmp6:=balances[msg.sender];
	tmp4:=evmadd(tmp5,tmp6);
	balances[_to]:=tmp4;

	tmp7:=!tmp6;
	assume(tmp7);

	tmp8:=!tmp7;
	assume(tmp8);

	tmp9:=!tmp8;
	assume(tmp9);

	assume(EQ(RETURNDATASIZE,0));

	assume(GAS);

	balances[msg.sender]:=0;

	assert(forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply);
	assert( sum(balances) == totalSupply );
}