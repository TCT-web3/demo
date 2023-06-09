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

	tmp1:=_fee + _value;
	assert (0<=tmp1 && tmp1<TwoE256);                
	if (!(balances[_from] >= tmp1)) {return;}

	tmp2:=balances[_to] + _value;
	assert (0<=tmp2 && tmp2<TwoE256);    
	if (!(balances[_to] <= tmp2)) {return;}

	tmp3:=balances[msg.sender] + _fee;
	assert (0<=tmp3 && tmp3<TwoE256);  
	if (!(balances[msg.sender] <= tmp3)) {return;}

	balances[_to] := balances[_to] + _value;
	assert (0<=balances[_to] && balances[_to]<TwoE256);
	
	balances[msg.sender] := balances[msg.sender] + _fee;
	assert (0<=balances[msg.sender] && balances[msg.sender]<TwoE256);

	balances[_from] := balances[_from] - (_fee + _value);
	assert (0<=balances[_from] && balances[_from]<TwoE256);
 
	assert (sum(balances) == totalSupply);         
	assert (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);
}    