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
	var tmp12: uint256;
	var tmp13: uint256;
	var tmp14: bool;
	var tmp15: bool;
	var tmp10: uint256;
	var tmp16: uint256;
	var tmp17: bool;
	var tmp18: bool;
	var tmp20: uint256;
	var tmp22: uint256;
	var tmp21: uint256;
	var tmp23: uint256;
	var tmp24: bool;
	var tmp25: bool;
	var tmp19: uint256;
	var tmp27: uint256;
	var tmp29: uint256;
	var tmp30: uint256;
	var tmp31: uint256;
	var tmp32: bool;
	var tmp33: bool;
	var tmp28: uint256;
	var tmp34: uint256;
	var tmp35: bool;
	var tmp36: bool;
	var tmp26: uint256;

    assume (0<=_value && _value<TwoE255+1 && 0<=_fee && _fee<TwoE255);           
    assume (totalSupply<TwoE255);    

    assume (sum(balances) == totalSupply);
    assume (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);  

	tmp1:=mapID2[_from];
	tmp2:=evmadd(_fee,_value);
	tmp3:=tmp1<tmp2;
	tmp4:=!tmp3;
	assume(tmp4);

	tmp6:=mapID2[_value];
	tmp5:=evmadd(tmp6,_fee);
	tmp7:=mapID2[_value];
	tmp8:=tmp5<tmp7;
	tmp9:=!tmp8;
	assume(tmp9);

	tmp11:=mapID2[msg.sender];
	tmp12:=mapID2[_from];
	tmp13:=evmadd(_fee,_value);
	tmp14:=tmp12<tmp13;
	tmp15:=!tmp14;
	tmp10:=evmadd(tmp11,tmp15);
	tmp16:=mapID2[msg.sender];
	tmp17:=tmp10<tmp16;
	tmp18:=!tmp17;
	assume(tmp18);

	tmp20:=mapID2[_from];
	tmp22:=mapID2[_value];
	tmp21:=evmadd(tmp22,_fee);
	tmp23:=mapID2[_value];
	tmp24:=tmp21<tmp23;
	tmp25:=!tmp24;
	tmp19:=evmadd(tmp20,tmp25);
	mapID2[None]:=tmp19	tmp27:=mapID2[msg.sender];
	tmp29:=mapID2[msg.sender];
	tmp30:=mapID2[_from];
	tmp31:=evmadd(_fee,_value);
	tmp32:=tmp30<tmp31;
	tmp33:=!tmp32;
	tmp28:=evmadd(tmp29,tmp33);
	tmp34:=mapID2[msg.sender];
	tmp35:=tmp28<tmp34;
	tmp36:=!tmp35;
	tmp26:=evmadd(tmp27,tmp36);
	mapID2[None]:=tmp26	mapID2[None]:=SUB(SLOAD(MapElement(2,0)),ADD(ISZERO(LT(ADD(SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_value)))),_fee),SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_value)))))),ISZERO(LT(ADD(SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,msg.sender)))),ISZERO(LT(SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_from)))),ADD(_fee,_value)))),SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,msg.sender))))))))	
    assert (sum(balances) == totalSupply);         
    assert (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);

}   
