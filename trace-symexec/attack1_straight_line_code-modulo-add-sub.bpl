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

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0 ==> evmadd(a,b) == a+b-TwoE256);


function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> sub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b<0 ==> sub(a,b) == a-b+TwoE256);


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

	assume (0<=_value && _value<TwoE255 && 0<=_fee && _fee<TwoE255);           
	assume (totalSupply<TwoE255);    
	
	assume (sum(balances) == totalSupply);
	assume (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);            

	tmp1:=add(_fee , _value);            
	if (!(balances[_from] >= tmp1)) {return;}

	tmp2:=add(balances[_to] , _value);  
	if (!(balances[_to] <= tmp2)) {return;}

	tmp3:=add(balances[msg.sender] , _fee);
	if (!(balances[msg.sender] <= tmp3)) {return;}

	balances[_to] := add(balances[_to] , _value);
	
	balances[msg.sender] := add(balances[msg.sender] , _fee);

	balances[_from] := sub(balances[_from] , _fee + _value);
 
	assert (sum(balances) == totalSupply);         
	assert (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);
}    