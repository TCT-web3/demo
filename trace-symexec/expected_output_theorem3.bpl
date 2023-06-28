type address = int;
type uint256 = int;
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

procedure straightline_code ()
{  
    var msg.sender: address ;  
	var owner:	address;
	var totalSupply:	uint256;
	var balances:[address] uint256;
	
	var tmp2: uint256;
	var tmp3: uint256;
	var tmp1: uint256;
	var tmp4: bool;
	var tmp5: bool;
	var tmp6: bool;
	var tmp7: bool;
	var tmp8: bool;
	var tmp9: bool;
	var tmp10: uint256;
	var tmp11: bool;
	var tmp12: bool;
	var tmp14: uint256;
	var tmp13: uint256;
	var tmp15: bool;
	var tmp16: bool;
	var tmp18: uint256;
	var tmp19: uint256;
	var tmp17: uint256;
	var tmp20: bool;
	var tmp21: bool;
	var tmp22: bool;
	var tmp23: bool;
	var tmp24: bool;
	var tmp25: bool;
	var tmp26: uint256;
	var tmp27: bool;
	var tmp28: bool;
	var tmp29: bool;

	var _to: address;
	var count: uint256;
	
	// assume(totalSupply<TwoE256 && msg.sender!=_to );
	assume(totalSupply<TwoE256 && msg.sender!=_to && balances[msg.sender]==0);
	
	
	assume(forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply);
	assume( sum(balances) == totalSupply);

	tmp2:=balances[_to];
	tmp3:=balances[msg.sender];
	tmp1:=evmadd(tmp2,tmp3);
	balances[_to]:=tmp1;

	
//>>>>>>>>>>>>>>>>>>>>>>> reentrancy_attack
	tmp10:=count;    // SLOAD(0x2)
	tmp11:= (tmp10<1);
	tmp12:=!tmp11;
	assume(!tmp12);

	tmp14:=count;
	tmp13:=evmadd(1,tmp14);
	count:=tmp13;

	
//>>>>>>>>>>>>>>>>>>>>>>> MultiVulnToken
	tmp18:=balances[_to];     //None is _to
	tmp19:=balances[msg.sender];
	tmp17:=evmadd(tmp18,tmp19);
	balances[_to]:=tmp17;    //None is _to

	

	tmp26:=count;
	tmp27:= (tmp26<1);
	tmp28:=!tmp27;
	assume(tmp28);

	balances[msg.sender]:=0;

	assert(forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply);
	assert( sum(balances) == totalSupply);
}