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
axiom (forall m: [address] uint256 :: ((forall a:address :: 0<=m[a]) ==> (forall a,b:address :: (a!=b) ==> m[a]+m[b]<=sum(m))));    

function add(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0 ==> add(a,b) == a+b);

function sub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> sub(a,b) == a-b);

var balances: [address] uint256;

procedure straightline_code ()
  modifies balances;
{  
	var msg.sender: address ;
	var _to: address;
	var tmp1: uint256;
	var tmp2: uint256;
	var tmp3: uint256;

	assume (totalSupply<TwoE256);
	assume	(_to != msg.sender);    
	
	assume (sum(balances) == totalSupply);
	assume (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);            

	tmp1:= add(balances[_to],balances[msg.sender]);

	balances[_to] := tmp1;
	
	balances[msg.sender] := 0 ;

	assert (sum(balances) == totalSupply);         
	assert (forall x:address :: 0<=balances[x] && balances[x]<=totalSupply);
}    