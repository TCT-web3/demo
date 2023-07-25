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

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmadd(a,b) == a+b);
function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmsub(a,b) == a-b);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmmul(a,b) == a*b);
function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 
var c_66795.totalSupply:  uint256;
var c_83c71.balanceOf:  [address] uint256;
var c_969fd.balanceOf:  [address] uint256;
procedure straightline_code ()
modifies c_66795.totalSupply,c_83c71.balanceOf,c_969fd.balanceOf;
{  
    var tx_origin: address;
	var tokenA:	address;
	var tokenB:	address;
	var liquidity:	uint256;
	var amountAMin:	uint256;
	var amountBMin:	uint256;
	var to:	address;

	var c_9019c.factory:  address;
	var c_6a5c4.getPair:  [address] [address] address;
	var c_66795.allowance:  [address] [address] uint256;
	var tmp1:  uint256;
	var tmp2:  bool;
	var tmp3:  uint256;
	var tmp4:  uint256;
	var tmp5:  bool;
	var tmp6:  bool;
	var c_66795.balanceOf:  [address] uint256;
	var tmp7:  uint256;
	var tmp8:  uint256;
	var tmp9:  bool;
	var tmp10:  bool;
	//var tmp11:  uint256;
	var tmp11:  address;
	var tmp12:  uint256;
	var tmp13:  uint256;
	var tmp14:  bool;
	var tmp15:  bool;
	var c_66795.unlocked:  uint256;
	var tmp16:  bool;
	var c_66795.reserve0:  uint256;
	var c_66795.reserve1:  uint256;
	var c_66795.blockTimestampLast:  uint256;
	var c_66795.token0:  address;
	var c_66795.token1:  address;

	
	var c_66795.factory:  address;
	var c_6a5c4.feeTo:  address;
	var c_66795.kLast:  uint256;
	var tmp17:  bool;

	var tmp18:  uint256;
	var tmp19:  bool;
	var tmp20:  uint256;
	var tmp21:  uint256;
	var tmp22:  uint256;
	var tmp23:  bool;
	//var tmp24:  uint256;
	var tmp24:  bool;
	var tmp25:  bool;
	var tmp26:  uint256;
	var tmp27:  uint256;
	var tmp28:  uint256;
	var tmp29:  bool;
	//var tmp30:  uint256;
	var tmp30:  bool;
	var tmp31:  uint256;
	var tmp32:  bool;
	var tmp33:  bool;
	var tmp34:  uint256;
	var tmp35:  bool;
	var tmp36:  uint256;
	var tmp37:  uint256;
	var tmp38:  bool;
	var tmp39:  bool;
	var tmp40:  uint256;
	var tmp41:  bool;
	var tmp42:  bool;
	var tmp43:  uint256;
	var tmp44:  uint256;
	var tmp45:  uint256;
	var tmp46:  uint256;
	var tmp47:  uint256;
	var tmp48:  uint256;
	var tmp49:  uint256;
	var tmp50:  uint256;
	var tmp51:  uint256;
	var tmp52:  bool;
	var tmp53:  bool;
	var tmp54:  bool;
	var tmp55:  uint256;
	var tmp56:  bool;
	var tmp57:  bool;
	var tmp58:  uint256;
	var tmp59:  bool;
	var tmp60:  bool;
	var tmp61:  uint256;
	var tmp62:  bool;
	var tmp63:  bool;
	//var tmp64:  uint256;
	var tmp64:  bool;
	var tmp65:  bool;
	//var tmp66:  uint256;
	var tmp66:  bool;
	var tmp67:  bool;
	var tmp68:  bool;
	var tmp69:  bool;
	var tmp70:  bool;
	var tmp71:  bool;
	
	var old_totalSupply: uint256;
	var old_reserveB: uint256;
	
	//---------------- MANUALLY ENTERED
	assume to != c_6a5c4.getPair[tokenA][tokenB];    //I didn't think of this condition until Boogie returned negative result.
	assume c_83c71.balanceOf[c_6a5c4.getPair[tokenA][tokenB]] !=0.0;
	assume c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]] !=0.0;
	
	//assume invariants
	assume (c_66795.reserve0 == c_83c71.balanceOf[c_6a5c4.getPair[tokenA][tokenB]]);
	assume (c_66795.reserve1 == c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]]);
	//========================================================================================
	old_totalSupply := c_66795.totalSupply;
	old_reserveB:= c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]];
	
	tmp1:=c_66795.allowance[tx_origin][256577013454289827829678403807674012776083424995];
	tmp2:= (tmp1==115792089237316195423570985008687907853269984665640564039457584007913129639935.0);
	assume(!tmp2);

	tmp3:=c_66795.allowance[tx_origin][256577013454289827829678403807674012776083424995];
	tmp4:=evmsub(tmp3,liquidity);
	tmp5:= (tmp4>tmp3);
	tmp6:=!tmp5;
	assume(tmp6);

	c_66795.allowance[tx_origin][256577013454289827829678403807674012776083424995]:=tmp4;

	tmp7:=c_66795.balanceOf[tx_origin];
	tmp8:=evmsub(tmp7,liquidity);
	tmp9:= (tmp8>tmp7);
	tmp10:=!tmp9;
	assume(tmp10);

	c_66795.balanceOf[tx_origin]:=tmp8;

	tmp11:=c_6a5c4.getPair[tokenA][tokenB];
	tmp12:=c_66795.balanceOf[tmp11];
	tmp13:=evmadd(tmp12,liquidity);
	tmp14:= (tmp12>tmp13);
	tmp15:=!tmp14;
	assume(tmp15);

	c_66795.balanceOf[tmp11]:=tmp13;

	tmp16:= (c_66795.unlocked==1.0);
	assume(tmp16);

	c_66795.unlocked:=0.0;

	tmp17:= (c_66795.kLast==0.0);
	assume(tmp17);

	tmp18:=c_66795.balanceOf[tmp11];
	tmp19:=tmp18==0.0;
	tmp20:=c_83c71.balanceOf[tmp11];
	tmp21:=evmmul(tmp18,tmp20);
	tmp22:=evmdiv(tmp21,tmp18);
	tmp23:= (tmp20==tmp22);
	tmp24:=(tmp19 || tmp23);
	assume(tmp24!=false);

	assume(c_66795.totalSupply!=0.0);

	tmp25:=tmp24==false;
	tmp26:=c_969fd.balanceOf[tmp11];
	tmp27:=evmmul(tmp18,tmp26);
	tmp28:=evmdiv(tmp27,tmp18);
	tmp29:= (tmp26==tmp28);
	tmp30:=(tmp25||tmp29);
	assume(tmp30!=false);

	assume(c_66795.totalSupply!=0.0);

	tmp31:=evmdiv(tmp21,c_66795.totalSupply);
	tmp32:= (tmp31>0.0);
	tmp33:=!tmp32;
	assume(!tmp33);

	tmp34:=evmdiv(tmp27,c_66795.totalSupply);
	tmp35:= (tmp34>0.0);
	assume(tmp35);

	tmp36:=c_66795.balanceOf[tmp11];
	tmp37:=evmsub(tmp36,tmp18);
	tmp38:= (tmp37>tmp36);
	tmp39:=!tmp38;
	assume(tmp39);
    // assert(tmp37==0.0);   This is added manually
	c_66795.balanceOf[tmp11]:=tmp37;

	tmp40:=evmsub(c_66795.totalSupply,tmp18);
	tmp41:= (tmp40>c_66795.totalSupply);
	tmp42:=!tmp41;
	assume(tmp42);

	c_66795.totalSupply:=tmp40;

	tmp43:=c_83c71.balanceOf[tmp11];
	tmp44:=evmsub(tmp43,tmp31);
	c_83c71.balanceOf[tmp11]:=tmp44;

	tmp45:=c_83c71.balanceOf[to];
	tmp46:=evmadd(tmp45,tmp31);
	c_83c71.balanceOf[to]:=tmp46;

	tmp47:=c_969fd.balanceOf[tmp11];
	tmp48:=evmsub(tmp47,tmp34);
	c_969fd.balanceOf[tmp11]:=tmp48;

	tmp49:=c_969fd.balanceOf[to];
	tmp50:=evmadd(tmp49,tmp34);
	c_969fd.balanceOf[to]:=tmp50;

	tmp51:=c_83c71.balanceOf[tmp11];
	tmp52:= (tmp51>5192296858534827628530496329220095.0);
	tmp53:=!tmp52;
	tmp54:=!tmp53;
	assume(!tmp54);

	tmp55:=c_969fd.balanceOf[tmp11];
	tmp56:= (tmp55>5192296858534827628530496329220095.0);
	tmp57:=!tmp56;
	assume(tmp57);

	tmp58:=evmadd(c_66795.reserve0,0.0);
	tmp59:= (c_66795.reserve0>tmp58);
	tmp60:=!tmp59;
	assume(tmp60);

	tmp61:=evmadd(c_66795.reserve1,0.0);
	tmp62:= (c_66795.reserve1>tmp61);
	tmp63:=!tmp62;
	assume(tmp63);

	c_66795.reserve0:=tmp51;

	c_66795.reserve1:=tmp55;

	//c_66795.blockTimestampLast:=MOD(BLOCKTIME,0x100000000);

	c_66795.unlocked:=1.0;

	tmp64:=(tokenA!=tokenB);
	assume(tmp64);

	tmp65:= (tokenA<tokenB);
	assume(tmp65);

	tmp66:=(tokenA!=0);
	assume(tmp66);

	tmp67:= (tokenA==tokenA);
	assume(tmp67);

	tmp68:= (tmp31<amountAMin);
	tmp69:=!tmp68;
	assume(tmp69);

	tmp70:= (tmp34<amountBMin);
	tmp71:=!tmp70;
	assume(tmp71);

	//Manually entered=============================
	//We want to prove the invariant:
	assert( evmdiv(c_83c71.balanceOf[c_6a5c4.getPair[tokenA][tokenB]] , old(c_83c71.balanceOf[c_6a5c4.getPair[tokenA][tokenB]])) == evmdiv(c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]] , old(c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]])));

	assert( evmdiv(c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]] , old(c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]])) == evmdiv(c_66795.totalSupply , old(c_66795.totalSupply)));
	
	assert (c_66795.reserve0 == c_83c71.balanceOf[c_6a5c4.getPair[tokenA][tokenB]]);
	assert (c_66795.reserve1 == c_969fd.balanceOf[c_6a5c4.getPair[tokenA][tokenB]]);

}