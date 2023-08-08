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
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=0.0 ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=0.0 ==> evmadd(a,b) == a+b-TwoE256);
axiom (forall a,b: uint256 :: evmadd(a,b)>=a ==> evmadd(a,b) == a+b);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a>=b ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a<b ==> evmsub(a,b) == a-b+TwoE256);
axiom (forall a,b: uint256 :: evmsub(a,b)<=a ==> evmsub(a,b) == a-b);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: /*evmdiv(evmmul(a,b),a)==b ==> */evmmul(a,b) == a*b);
function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 




function evmmod(a,b:uint256) returns (uint256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: 0.0<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));    


var FancyToken.balanceOf:  [address] [address] uint256;
procedure straightline_code ()
modifies FancyToken.balanceOf;
{  
    var tx_origin: address;
	var entry_contract: address;
    var BLOCKTIME: uint256;
	
	var amountIn:	uint256;
	var amountOutMin:	uint256;
	var path:	[int] address;
	var to:	address;

	//var UniswapV2Router_c14bf3_.factory:  address;
	var UniswapV2Router.factory:  [address] address;
	//var UniswapV2Factory_cf465d_.swapFeeRate:  uint256;
	var UniswapV2Factory.swapFeeRate:  [address] uint256;
	var tmp1:  uint256;
	var tmp2:  bool;
	var tmp3:  uint256;
	/*
	var UniswapV2Factory_cf465d_.getPair:  [address] [address] address;
	var UniswapV2Pair_c53464_.reserve0:  uint256;
	var UniswapV2Pair_c53464_.reserve1:  uint256;
	var UniswapV2Pair_c53464_.blockTimestampLast:  uint256;
	*/
	var UniswapV2Factory.getPair:  [address] [address] [address] address;
	var UniswapV2Pair.reserve0:  [address] uint256;
	var UniswapV2Pair.reserve1:  [address] uint256;
	var UniswapV2Pair.blockTimestampLast:  [address] uint256;
	var tmp4:  bool;
	var tmp5:  bool;
	var tmp6:  bool;
	var tmp7:  bool;
	var tmp8:  bool;
	var tmp9:  uint256;
	var tmp10:  bool;
	var tmp11:  bool;
	var tmp12:  bool;
	var tmp13:  uint256;
	var tmp14:  uint256;
	var tmp15:  bool;
	var tmp16:  bool;
	var tmp17:  bool;
	var tmp18:  uint256;
	var tmp19:  uint256;
	var tmp20:  bool;
	var tmp21:  bool;
	var tmp22:  bool;
	var tmp23:  uint256;
	var tmp24:  uint256;
	var tmp25:  bool;
	var tmp26:  bool;
	var tmp27:  uint256;
	var tmp28:  bool;
	var tmp29:  bool;
	var tmp30:  uint256;
	var tmp31:  bool;
	var tmp32:  bool;
	//var FancyToken_ce8e7d_.allowance:  [address] [address] uint256;
	var FancyToken.allowance:  [address] [address] [address] uint256;
	
	var tmp33:  uint256;
	var tmp34:  uint256;
	//var FancyToken_ce8e7d_.balanceOf:  [address] uint256;
	
	var tmp35:  uint256;
	var tmp36:  uint256;
	var tmp37:  address;
	var tmp38:  uint256;
	var tmp39:  uint256;
	var tmp40:  uint256;
	var tmp41:  bool;
	var tmp42:  uint256;
	var tmp43:  bool;
	var tmp44:  bool;
	var tmp45:  bool;
	//var UniswapV2Pair_c53464_.unlocked:  uint256;
	var UniswapV2Pair.unlocked:  [address] uint256;
	var tmp46:  bool;
	var tmp47:  bool;
	var tmp48:  bool;
	var tmp49:  bool;
	var tmp50:  bool;
	//var UniswapV2Pair_c53464_.token0:  address;
	//var UniswapV2Pair_c53464_.token1:  address;
	var UniswapV2Pair.token0:  [address] address;
	var UniswapV2Pair.token1:  [address] address;
	var tmp51:  bool;
	var tmp52:  bool;
	var tmp53:  bool;
	var tmp54:  bool;
	var tmp55:  bool;
	var tmp56:  bool;
	var tmp57:  bool;
	//var FancyToken_c1a5bd_.balanceOf:  [address] uint256;
	var tmp58:  address;
	var tmp59:  uint256;
	var tmp60:  uint256;
	var tmp61:  uint256;
	var tmp62:  uint256;
	var tmp63:  uint256;
	var tmp64:  bool;
	var tmp65:  bool;
	var tmp66:  uint256;
	var tmp67:  bool;
	var tmp68:  uint256;
	var tmp69:  bool;
	var tmp70:  bool;
	var tmp71:  uint256;
	var tmp72:  bool;
	var tmp73:  uint256;
	var tmp74:  bool;
	var tmp75:  bool;
	var tmp76:  uint256;
	var tmp77:  bool;
	var tmp78:  bool;
	var tmp79:  bool;
	//var UniswapV2Pair_c53464_.swapFeeRate:  uint256;
	var UniswapV2Pair.swapFeeRate:  [address] uint256;
	var tmp80:  uint256;
	var tmp81:  uint256;
	var tmp82:  bool;
	var tmp83:  uint256;
	var tmp84:  bool;
	var tmp85:  uint256;
	var tmp86:  uint256;
	var tmp87:  bool;
	var tmp88:  bool;
	var tmp89:  uint256;
	var tmp90:  bool;
	var tmp91:  bool;
	var tmp92:  bool;
	var tmp93:  uint256;
	var tmp94:  uint256;
	var tmp95:  bool;
	var tmp96:  bool;
	var tmp97:  bool;
	var tmp98:  uint256;
	var tmp99:  uint256;
	var tmp100:  bool;
	var tmp101:  bool;
	var tmp102:  uint256;
	var tmp103:  bool;
	var tmp104:  bool;
	var tmp105:  bool;
	var tmp106:  uint256;
	var tmp107:  uint256;
	var tmp108:  bool;
	var tmp109:  bool;
	var tmp110:  bool;
	var tmp111:  uint256;
	var tmp112:  uint256;
	var tmp113:  bool;
	var tmp114:  bool;
	var tmp115:  bool;
	var tmp116:  uint256;
	var tmp117:  uint256;
	var tmp118:  bool;
	var tmp119:  bool;
	var tmp120:  bool;
	var tmp121:  bool;
	var tmp122:  bool;
	var tmp123:  bool;
	var tmp124:  bool;
	var tmp125:  bool;
	var tmp126:  bool;
	var tmp127:  uint256;
	var tmp128:  bool;
	var tmp129:  bool;
	var tmp130:  uint256;
	var tmp131:  bool;
	var tmp132:  bool;
	var tmp133:  uint256;
	
	var FancyToken.totalSupply: [address] uint256;
	
	var factory, pair: address;
	var token0, token1: address;

	
	factory:=UniswapV2Router.factory[entry_contract];
	pair:=UniswapV2Factory.getPair[factory][path[0]][path[1]];
	
//Hypothesis
	assume FancyToken.totalSupply[path[0]]<TwoE255;
	assume FancyToken.totalSupply[path[1]]<TwoE255;
	assume to != pair;    
	assume tx_origin != pair;   
	assume(UniswapV2Pair.token0[pair]==path[1] && UniswapV2Pair.token1[pair]==path[0]);
	assume UniswapV2Pair.swapFeeRate[pair] == 0.0;
	assume UniswapV2Factory.swapFeeRate[factory] == 0.0;
//////////////////////////////////////////////////////


	assume UniswapV2Pair.reserve0[pair] == FancyToken.balanceOf[path[1]][pair];
	assume UniswapV2Pair.reserve1[pair] == FancyToken.balanceOf[path[0]][pair];

	assume(path[0]!=path[1]);

	assume(path[0]>=path[1]);

	assume(path[1]!=0);

	tmp5:= (amountIn>0.0);
	assume(tmp5);

	tmp6:= (UniswapV2Pair.reserve1[pair]>0.0);
	tmp7:=!tmp6;
	assume(!tmp7);

	tmp8:= (UniswapV2Pair.reserve0[pair]>0.0);
	assume(tmp8);

	tmp9:=evmsub(1000.0,UniswapV2Factory.swapFeeRate[factory]);
	tmp10:= (tmp9>1000.0);
	tmp11:=!tmp10;
	assume(tmp11);

	tmp12:=!tmp11;
	tmp13:=evmmul(amountIn,tmp9);
	tmp14:=evmdiv(tmp13,amountIn);
	tmp15:= (tmp9==tmp14);
	tmp16:=tmp12||tmp15;
	assume(tmp16);


	tmp17:=!tmp16;
	tmp18:=evmmul(tmp13,UniswapV2Pair.reserve0[pair]);
	tmp19:=evmdiv(tmp18,tmp13);
	tmp20:= (UniswapV2Pair.reserve0[pair]==tmp19);
	tmp21:=tmp17||tmp20;
	assume(tmp21);

	tmp22:=!tmp21;
	tmp23:=evmmul(UniswapV2Pair.reserve1[pair],1000.0);
	tmp24:=evmdiv(tmp23,UniswapV2Pair.reserve1[pair]);
	tmp25:= (1000.0==tmp24);
	tmp26:=tmp22||tmp25;
	assume(tmp26);

	tmp27:=evmadd(tmp23,tmp13);
	tmp28:= (tmp23>tmp27);
	tmp29:=!tmp28;
	assume(tmp29);

	assume(tmp27!=0.0);

	tmp30:=evmdiv(tmp18,tmp27);


	tmp37:=UniswapV2Factory.getPair[factory][path[0]][path[1]];
	tmp38:=FancyToken.balanceOf[path[0]][tmp37];
	tmp39:=tmp38+amountIn;
	FancyToken.balanceOf[path[0]][tmp37]:=tmp39;


	assume token0==path[1] && token1==path[0];


	tmp58:=UniswapV2Factory.getPair[factory][path[0]][path[1]];
	tmp59:=FancyToken.balanceOf[path[1]][tmp58];
	assume(tmp59>=tmp30);
	tmp60:=evmsub(tmp59,tmp30);
	FancyToken.balanceOf[path[1]][tmp58]:=tmp60;

	
	

	

//ok
	tmp63:=evmsub(UniswapV2Pair.reserve0[pair],tmp30);
	tmp64:= (tmp63>UniswapV2Pair.reserve0[pair]);
	tmp65:=!tmp64;
	assume(tmp65);

	tmp66:=FancyToken.balanceOf[path[1]][tmp58];
	tmp67:= (tmp66>tmp63);
	assume(!tmp67);

	tmp68:=evmsub(UniswapV2Pair.reserve1[pair],0.0);
	tmp69:= (tmp68>UniswapV2Pair.reserve1[pair]);
	tmp70:=!tmp69;
	assume(tmp70);
//ok
	tmp71:=FancyToken.balanceOf[path[0]][tmp58];
	tmp72:= (tmp71>tmp68);
	//assume(tmp72);    //This is a contradiction. reserve1 should equal token0.balanceof[pair].

	tmp73:=evmsub(UniswapV2Pair.reserve1[pair],0.0);
	tmp74:= (tmp73>UniswapV2Pair.reserve1[pair]);
	tmp75:=!tmp74;
	assume(tmp75);
//ok
	tmp76:=evmsub(tmp71,tmp73);
	tmp77:= (tmp76>tmp71);
	tmp78:=!tmp77;
	assume(tmp78);

	tmp79:= (tmp76>0.0);   
	assume(tmp79);   

	tmp80:=evmmul(0.0,UniswapV2Pair.swapFeeRate[pair]);
	tmp81:=evmdiv(tmp80,0.0);
	tmp82:= (UniswapV2Pair.swapFeeRate[pair]==tmp81);
	assume(tmp82);
//assert(tmp80==0.0*UniswapV2Pair.swapFeeRate[pair]);

	tmp84:=false;
	tmp85:=evmmul(tmp66,1000.0);
	tmp86:=evmdiv(tmp85,tmp66);
	tmp87:= (1000.0==tmp86);
	tmp88:=tmp84||tmp87;
	assume(tmp88);
//assert(tmp85==tmp66*1000.0);
	tmp89:=evmsub(tmp85,tmp80);
	tmp90:= (tmp89>tmp85);
	tmp91:=!tmp90;
	assume(tmp91);

	tmp92:=!tmp91;
	tmp93:=evmmul(tmp76,UniswapV2Pair.swapFeeRate[pair]);
	tmp94:=evmdiv(tmp93,tmp76);
	tmp95:= (UniswapV2Pair.swapFeeRate[pair]==tmp94);
	tmp96:=tmp92||tmp95;
	assume(tmp96);

	tmp97:=!tmp96;
	tmp98:=evmmul(tmp71,1000.0);
	tmp99:=evmdiv(tmp98,tmp71);
	tmp100:= (1000.0==tmp99);
	tmp101:=tmp97||tmp100;
	assume(tmp101);

	tmp102:=evmsub(tmp98,tmp93);
	tmp103:= (tmp102>tmp98);
	tmp104:=!tmp103;
	assume(tmp104);

	tmp105:=!tmp104;
	tmp106:=evmmul(UniswapV2Pair.reserve0[pair],UniswapV2Pair.reserve1[pair]);
	tmp107:=evmdiv(tmp106,UniswapV2Pair.reserve0[pair]);
	tmp108:= (UniswapV2Pair.reserve1[pair]==tmp107);
	tmp109:=tmp105||tmp108;
	assume(tmp109);
//assert(tmp106==UniswapV2Pair.reserve0[pair]*UniswapV2Pair.reserve1[pair]);

	tmp110:=!tmp109;
	tmp111:=evmmul(tmp106,1000000.0);
	tmp112:=evmdiv(tmp111,tmp106);
	tmp113:= (1000000.0==tmp112);
	tmp114:=tmp110||tmp113;
	assume(tmp114);

	tmp115:=!tmp114;
	tmp116:=evmmul(tmp89,tmp102);
	tmp117:=evmdiv(tmp116,tmp89);
	tmp118:= (tmp102==tmp117);
	tmp119:=tmp115||tmp118;
	assume(tmp119);
//ok
	tmp120:= (tmp116<tmp111);
	tmp121:=!tmp120;
	//assume(tmp121);   //This SEEMS a contradiction.

	tmp122:= (tmp66>5192296858534827628530496329220095.0);
	tmp123:=!tmp122;
	tmp124:=!tmp123;
	assume(!tmp124);

	tmp125:= (tmp71>5192296858534827628530496329220095.0);
	tmp126:=!tmp125;
	assume(tmp126);

	tmp127:=evmadd(UniswapV2Pair.reserve0[pair],0.0);
	tmp128:= (UniswapV2Pair.reserve0[pair]>tmp127);
	tmp129:=!tmp128;
	assume(tmp129);

	tmp130:=evmadd(UniswapV2Pair.reserve1[pair],0.0);
	tmp131:= (UniswapV2Pair.reserve1[pair]>tmp130);
	tmp132:=!tmp131;
	assume(tmp132);

	UniswapV2Pair.reserve0[pair]:=tmp66;

	UniswapV2Pair.reserve1[pair]:=tmp71;

	tmp133:=evmmod(BLOCKTIME,4294967296.0);
	UniswapV2Pair.blockTimestampLast[pair]:=tmp133;

	UniswapV2Pair.unlocked[pair]:=1.0;

	// (post) insert invariant of UniswapV2Pair
	assert(UniswapV2Pair.reserve0[pair] == FancyToken.balanceOf[path[1]][pair] && UniswapV2Pair.reserve1[pair] == FancyToken.balanceOf[path[0]][pair]);

	// postcondition
	
	assert(old(FancyToken.balanceOf[path[0]][pair]) * old(FancyToken.balanceOf[path[1]][pair]) ==  FancyToken.balanceOf[path[0]][pair] * FancyToken.balanceOf[path[1]][pair]);
//assert(false);
}