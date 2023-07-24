type address = int;
type uint256 = real;
const TwoE16 : uint256;
axiom TwoE16 == 65536.0; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 *32768.0;
const TwoE256 : uint256; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function add(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: add(a,b) == a+b);
function sub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: sub(a,b) == a-b);

// function evmor(a,b:uint256) returns (uint256);
// axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b>=0 ==> sub(a,b) == a-b);
// axiom (forall a,b: uint256 :: a-b < TwoE256 && a-b<0 ==> sub(a,b) == a-b+TwoE256);

function mul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: mul(a,b) == a*b);
function preciseDiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: preciseDiv(a,b) == a / b); 

procedure straightline_code ()
{   
	var msg_sender: address;
	var tokenA:	address;
	var tokenB:	address;
	var amountADesired:	uint256;
	var amountBDesired:	uint256;
	var amountAMin:	uint256;
	var amountBMin:	uint256;
	var to:	address;

	var c_ab263.factory:  address;
	var c_c5ce5.getPair:  [address] [address] address;
	var tmp1:  address;    //var tmp1:  uint256;
	var tmp2:  uint256;
	var tmp3:  uint256;
	var tmp4:  bool;
	var tmp5:  uint256;
	var c_005aa.reserve0:  uint256;
	var c_005aa.reserve1:  uint256;
	var c_005aa.blockTimestampLast:  uint256;
	var tmp6:  bool;
	var tmp7:  bool;
	var tmp8:  bool;
	var tmp9:  bool;
	var tmp10:  bool;
	var tmp11:  bool;
	var tmp12:  bool;
	var tmp13:  bool;
	var tmp14:  bool;
	var tmp15:  uint256;
	var tmp16:  uint256;
	var tmp17:  bool;
	//var tmp18:  uint256;
	var tmp18:  bool;
	var tmp19:  uint256;
	var tmp20:  bool;
	var tmp21:  bool;
	var tmp22:  bool;
	var c_f8c9b.allowance:  [address] [address] uint256;   //tokenA = c_f8c9b
	var tmp23:  uint256;
	var tmp24:  uint256;
	var c_f8c9b.balanceOf:  [address] uint256;
	var tmp25:  uint256;
	var tmp26:  uint256;
	//var tmp27:  uint256;
	var tmp27:  address;
	var tmp28:  uint256;
	var tmp29:  uint256;
	var c_b31d7.allowance:  [address] [address] uint256;  //tokenB = c_b31d7
	var tmp30:  uint256;
	var tmp31:  uint256;
	var c_b31d7.balanceOf:  [address] uint256;
	var tmp32:  uint256;
	var tmp33:  uint256;
	var tmp34:  uint256;
	var tmp35:  uint256;
	var c_005aa.unlocked:  uint256;
	var tmp36:  bool;
	var c_005aa.token0:  address;
	var c_005aa.token1:  address;
	var tmp37:  uint256;
	var tmp38:  uint256;
	var tmp39:  bool;
	var tmp40:  bool;
	var tmp41:  uint256;
	var tmp42:  uint256;
	var tmp43:  bool;
	var tmp44:  bool;
	var c_005aa.factory:  address;
	var c_c5ce5.feeTo:  address;
	var c_005aa.kLast:  uint256;
	var tmp45:  bool;
	var c_005aa.totalSupply:  uint256;
	var tmp46:  uint256;
	var tmp47:  bool;
	var tmp48:  uint256;
	var tmp49:  uint256;
	var tmp50:  bool;
	//var tmp51:  uint256;
	var tmp51:  bool;
	var tmp52:  bool;
	var tmp53:  uint256;
	var tmp54:  uint256;
	var tmp55:  bool;
	//var tmp56:  uint256;
	var tmp56:  bool;
	var tmp57:  uint256;
	var tmp58:  uint256;
	var tmp59:  bool;
	var tmp60:  bool;
	var tmp61:  uint256;
	var tmp62:  bool;
	var tmp63:  bool;
	var c_005aa.balanceOf:  [address] uint256;
	var tmp64:  uint256;
	var tmp65:  uint256;
	var tmp66:  bool;
	var tmp67:  bool;
	var tmp68:  bool;
	var tmp69:  bool;
	var tmp70:  bool;
	var tmp71:  bool;
	var tmp72:  bool;
	var tmp73:  uint256;
	var tmp74:  bool;
	var tmp75:  bool;
	var tmp76:  uint256;
	var tmp77:  bool;
	var tmp78:  bool;

	//---------------- MANUALLY ENTERED
	assume tokenA != tokenB;
	assume msg_sender != c_c5ce5.getPair[tokenA][tokenB];    //I didn't think of this condition until Boogie returned negative result.
	assume c_f8c9b.balanceOf[c_c5ce5.getPair[tokenA][tokenB]] !=0.0;
	assume c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]] !=0.0;
	assume c_005aa.totalSupply!=0.0;
	
	//assume invariants
	assume (c_005aa.reserve1 == c_f8c9b.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]);
	assume (c_005aa.reserve0 == c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]);


	assume (tokenA!=tokenB);
	assume(tokenB!=0);

	tmp10:= (amountADesired>0.0);
	assume(tmp10);

	tmp11:= (c_005aa.reserve1>0.0);
	assume(tmp11);
	tmp13:= (c_005aa.reserve0>0.0);
	assume(tmp13);


	tmp15:=mul(amountADesired,c_005aa.reserve0);
	
	assume(c_005aa.reserve1!=0.0);

	tmp19:=preciseDiv(tmp15,c_005aa.reserve1);    //tmp19 is amountBOptimal
	assume(tmp19<=amountBDesired);
	assume(tmp19>=amountBMin);

	tmp25:=c_f8c9b.balanceOf[msg_sender];
	tmp26:=sub(tmp25,amountADesired);
	c_f8c9b.balanceOf[msg_sender]:=tmp26;      //transfer tokenA out of msg_sender's account

	tmp27:=c_c5ce5.getPair[tokenA][tokenB];
	tmp28:=c_f8c9b.balanceOf[tmp27];
	tmp29:=add(tmp28,amountADesired);
	c_f8c9b.balanceOf[tmp27]:=tmp29;		   //transfer tokenA into pair's account

	tmp32:=c_b31d7.balanceOf[msg_sender];
	tmp33:=sub(tmp32,tmp19);
	c_b31d7.balanceOf[msg_sender]:=tmp33;      //transfer tokenB out of msg_sender's account

	tmp34:=c_b31d7.balanceOf[tmp27];
	tmp35:=add(tmp34,tmp19);
	c_b31d7.balanceOf[tmp27]:=tmp35;           //transfer tokenB out of pair's account

	tmp36:= (c_005aa.unlocked==1.0);
	assume(tmp36);

	c_005aa.unlocked:=0.0;

	tmp37:=c_b31d7.balanceOf[tmp27];
	tmp38:=sub(tmp37,c_005aa.reserve0);
	tmp39:= (tmp38>tmp37);
	tmp40:=!tmp39;
	assume(tmp40);

	//tmp41:=c_f8c9b.balanceOf[c_005aa.token0];   //This line doens't make sense. If it was changed to the next line, it would be correct.
	tmp41:=c_f8c9b.balanceOf[tmp27];
	tmp42:=sub(tmp41,c_005aa.reserve1);
	tmp43:= (tmp42>tmp41);
	tmp44:=!tmp43;
	assume(tmp44);

	tmp46:=sub(c_005aa.totalSupply,0.0);
	assume(tmp46!=0.0);

	tmp48:=mul(tmp38,c_005aa.totalSupply);
	tmp49:=preciseDiv(tmp48,tmp38);
	tmp50:= (c_005aa.totalSupply==tmp49);
	assume(tmp50);

	assume(c_005aa.reserve0!=0.0);

	tmp53:=mul(tmp42,c_005aa.totalSupply);
	tmp54:=preciseDiv(tmp53,tmp42);
	tmp55:= (c_005aa.totalSupply==tmp54);
	assume(tmp55);

	assume(c_005aa.reserve1!=0.0);

	tmp57:=preciseDiv(tmp48,c_005aa.reserve0);
	tmp58:=preciseDiv(tmp53,c_005aa.reserve1);
	tmp59:= (tmp57<tmp58);
	assume(!tmp59);

	tmp60:= (tmp58>0.0);
	assume(tmp60);
	
	
	tmp61:=add(c_005aa.totalSupply,tmp58);

	c_005aa.totalSupply:=tmp61;

	tmp64:=c_005aa.balanceOf[to];
	tmp65:=add(tmp64,tmp58);	
	c_005aa.balanceOf[to]:=tmp65;

	
	
	c_005aa.reserve0:=tmp37;

	c_005aa.reserve1:=tmp41;

	//c_005aa.blockTimestampLast:=MOD(BLOCKTIME,0x100000000);

	c_005aa.unlocked:=1.0;


	//--------------------- MANUALLY ENTERED
	//We want to prove the invariant:
	assert( preciseDiv(c_f8c9b.balanceOf[c_c5ce5.getPair[tokenA][tokenB]] , old(c_f8c9b.balanceOf[c_c5ce5.getPair[tokenA][tokenB]])) == preciseDiv(c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]] , old(c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]])));
	assert( preciseDiv(c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]] , old(c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]])) == preciseDiv(c_005aa.totalSupply , old(c_005aa.totalSupply)));
	
	//Finally, dont forget to prove the invariant
	assert (c_005aa.reserve1 == c_f8c9b.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]);
	assert (c_005aa.reserve0 == c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]);
}    