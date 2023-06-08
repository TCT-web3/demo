type address;
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
tmp1:=mapID2[_from];
tmp2:=_fee+_value;
tmp3:=tmp1<tmp2;
tmp4:=tmp3==0;
assume(tmp4);
tmp6:=mapID2[_fee];
tmp5:=tmp6+0;
tmp7:=mapID2[_fee];
tmp8:=tmp5<tmp7;
tmp9:=tmp8==0;
assume(tmp9);
tmp11:=mapID2[caller address];
tmp13:=mapID2[_fee];
tmp12:=tmp13+0;
tmp14:=mapID2[_fee];
tmp15:=tmp12<tmp14;
tmp16:=tmp15==0;
tmp10:=tmp11+tmp16;
tmp17:=mapID2[caller address];
tmp18:=tmp10<tmp17;
tmp19:=tmp18==0;
assume(tmp19);
