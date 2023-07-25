/*
procedure straightline_code ()
{  
	var a: real; 
    var d: real;   
    var b: real;   
	//assume (a!=0.0 && b!=0.0);
	assert ( (b-d*b/a)/b == (a-d)/a );
}
*/

type uint256 = real;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmadd(a,b) == a+b);
function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmsub(a,b) == a-b);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmmul(a,b) == a*b);
function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 
var liqT_totalSupply: uint256; // This is var c_66795.totalSupply
var reserve_of_tokenB: uint256;   // This is var tmp26
procedure straightline_code ()
modifies liqT_totalSupply, reserve_of_tokenB;
{  
    var liqT_to_remove: uint256;   // This is var tmp18
	var tmp27: uint256;
	var tmp34: uint256;
	assume (reserve_of_tokenB!=0.0 && liqT_totalSupply!=0.0);
	tmp27:=evmmul(liqT_to_remove,reserve_of_tokenB);
	tmp34:=evmdiv(tmp27,liqT_totalSupply);
	liqT_totalSupply:=evmsub(liqT_totalSupply,liqT_to_remove);
	reserve_of_tokenB:=evmsub(reserve_of_tokenB,tmp34);
	
	assert( evmdiv(reserve_of_tokenB, old(reserve_of_tokenB)) == evmdiv(liqT_totalSupply , old(liqT_totalSupply)));
}



/*
type uint256 = real;
procedure straightline_code ()
{  
	var liqT_totalSupply: uint256; // This is var c_66795.totalSupply
    var liqT_to_remove: uint256;   // This is var tmp18
    var reserve_of_tokenB: uint256;   // This is var tmp26
	var tmp27: uint256;
	var tmp34: uint256;
	assume (reserve_of_tokenB!=0.0 && liqT_totalSupply!=0.0);
	tmp27:= liqT_to_remove * reserve_of_tokenB;
	tmp34:= tmp27 / liqT_totalSupply;
	liqT_totalSupply:= liqT_totalSupply - liqT_to_remove;
	reserve_of_tokenB:= reserve_of_tokenB - tmp34;
	
	assert( (reserve_of_tokenB / old(reserve_of_tokenB)) 
	     == (liqT_totalSupply / old(liqT_totalSupply))
		  );
}*/