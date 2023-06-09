type address;
type uint256 = int;>
var totalSupply: uint256;
const TwoE16 : uint256;
axiom TwoE16 == 65536; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768;
const TwoE256 : int; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;


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
    var tmp3: uint256;

    assume (0<=_value && _value<TwoE255+1 && 0<=_fee && _fee<TwoE255);           
    assume (totalSupply<TwoE255);    
    
    assume (sum(balances) == totalSupply);
    assume (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);            
tmp1:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_from))];
tmp2:=evmadd(_fee,_value);
tmp3:=tmp1<tmp2;
tmp4:=tmp3==0;
assume(tmp4);
tmp6:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_value))];
tmp5:=evmadd(tmp6,_fee);
tmp7:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_value))];
tmp8:=tmp5<tmp7;
tmp9:=tmp8==0;
assume(tmp9);
tmp11:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,msg.sender))];
tmp12:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_from))];
tmp13:=evmadd(_fee,_value);
tmp14:=tmp12<tmp13;
tmp15:=tmp14==0;
tmp10:=evmadd(tmp11,tmp15);
tmp16:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,msg.sender))];
tmp17:=tmp10<tmp16;
tmp18:=tmp17==0;
assume(tmp18);
tmp20:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,ISZERO(LT(SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_from)))),ADD(_fee,_value)))))];
tmp22:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_value))];
tmp21:=evmadd(tmp22,_fee);
tmp23:=mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_value))];
tmp24:=tmp21<tmp23;
tmp25:=tmp24==0;
tmp19:=evmadd(tmp20,tmp25);
mapID2[AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,ISZERO(LT(SLOAD(MapElement(2,AND(1461501637330902918203684832716283019655932542975,AND(1461501637330902918203684832716283019655932542975,_from)))),ADD(_fee,_value)))))]:=tmp19	
    assert (sum(balances) == totalSupply);         
    assert (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);
}   
