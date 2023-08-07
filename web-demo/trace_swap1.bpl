type uint256 = real;
const Zero : uint256;
axiom Zero == 0.0; 
const TwoE8 : uint256;
axiom TwoE8 == 32768.0; 

function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 

type address = int;
type bytes32 = int;
type uint8 = int;
const TwoE16 : uint256;
axiom TwoE16 == TwoE8 * TwoE8; 
const TwoE64 : uint256; 
axiom TwoE64 == TwoE16 * TwoE16 * TwoE16 * TwoE16;
const TwoE255 : uint256;
axiom TwoE255 == TwoE64 * TwoE64 * TwoE64 * TwoE16 * TwoE16 * TwoE16 * TwoE8;
const TwoE256 : uint256; 
axiom TwoE256 == TwoE64 * TwoE64 * TwoE64 * TwoE64;

function evmadd(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a+b < TwoE256 && a+b>=Zero ==> evmadd(a,b) == a+b);
axiom (forall a,b: uint256 :: a+b >= TwoE256 && a+b>=Zero ==> evmadd(a,b) == a+b-TwoE256);
axiom (forall a,b: uint256 :: evmadd(a,b)>=a ==> evmadd(a,b) == a+b);

function evmsub(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a>=b ==> evmsub(a,b) == a-b);
axiom (forall a,b: uint256 :: a-b < TwoE256 && a<b ==> evmsub(a,b) == a-b+TwoE256);
axiom (forall a,b: uint256 :: evmsub(a,b)<=a ==> evmsub(a,b) == a-b);

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmdiv(evmmul(a,b),a)==b ==> evmmul(a,b) == a*b);

function evmmod(a,b:uint256) returns (uint256);

function sum(m: [address] uint256) returns (uint256);
axiom (forall m: [address] uint256, a:address, v:uint256 :: sum(m[a:=v]) == sum(m) - m[a] + v);
axiom (forall m: [address] uint256 :: ((forall a:address :: Zero<=m[a]) ==> (forall a:address :: m[a]<=sum(m))));

function nondet() returns (uint256);

var UniswapV2ERC20.totalSupply:  [address] uint256;
var UniswapV2ERC20.balanceOf:  [address] [address] uint256;
var UniswapV2ERC20.allowance:  [address] [address] [address] uint256;
var UniswapV2ERC20.DOMAIN_SEPARATOR:  [address] bytes32;
var UniswapV2ERC20.nonces:  [address] [address] uint256;
var UniswapV2Factory.feeTo:  [address] address;
var UniswapV2Factory.feeToSetter:  [address] address;
var UniswapV2Factory.getPair:  [address] [address] [address] address;
var UniswapV2Factory.allPairs:  [int] address;
var UniswapV2Factory.swapFeeRate:  [address] uint256;
var UniswapV2Pair.totalSupply:  [address] uint256;
var UniswapV2Pair.balanceOf:  [address] [address] uint256;
var UniswapV2Pair.allowance:  [address] [address] [address] uint256;
var UniswapV2Pair.DOMAIN_SEPARATOR:  [address] bytes32;
var UniswapV2Pair.nonces:  [address] [address] uint256;
var UniswapV2Pair.factory:  [address] address;
var UniswapV2Pair.token0:  [address] address;
var UniswapV2Pair.token1:  [address] address;
var UniswapV2Pair.reserve0:  [address] uint256;
var UniswapV2Pair.reserve1:  [address] uint256;
var UniswapV2Pair.blockTimestampLast:  [address] uint256;
var UniswapV2Pair.price0CumulativeLast:  [address] uint256;
var UniswapV2Pair.price1CumulativeLast:  [address] uint256;
var UniswapV2Pair.kLast:  [address] uint256;
var UniswapV2Pair.unlocked:  [address] uint256;
var UniswapV2Pair.swapFeeRate:  [address] uint256;
var UniswapV2Router.factory:  [address] address;
var Test._feeToSetter:  [address] address;
var FancyToken.totalSupply:  [address] uint256;
var FancyToken.balanceOf:  [address] [address] uint256;
var FancyToken.allowance:  [address] [address] [address] uint256;
var FancyToken.decimals:  [address] uint8;
var amountIn:  uint256;
var amountOutMin:  uint256;
var path:  [int] address;
var to:  address;

procedure straightline_code ()
modifies UniswapV2ERC20.totalSupply, UniswapV2ERC20.balanceOf, UniswapV2ERC20.allowance, UniswapV2ERC20.DOMAIN_SEPARATOR, UniswapV2ERC20.nonces, UniswapV2Factory.feeTo, UniswapV2Factory.feeToSetter, UniswapV2Factory.getPair, UniswapV2Factory.allPairs, UniswapV2Factory.swapFeeRate, UniswapV2Pair.totalSupply, UniswapV2Pair.balanceOf, UniswapV2Pair.allowance, UniswapV2Pair.DOMAIN_SEPARATOR, UniswapV2Pair.nonces, UniswapV2Pair.factory, UniswapV2Pair.token0, UniswapV2Pair.token1, UniswapV2Pair.reserve0, UniswapV2Pair.reserve1, UniswapV2Pair.blockTimestampLast, UniswapV2Pair.price0CumulativeLast, UniswapV2Pair.price1CumulativeLast, UniswapV2Pair.kLast, UniswapV2Pair.unlocked, UniswapV2Pair.swapFeeRate, UniswapV2Router.factory, Test._feeToSetter, FancyToken.totalSupply, FancyToken.balanceOf, FancyToken.allowance, FancyToken.decimals, amountIn, amountOutMin, path, to;
{
    var tx_origin: address;
    var entry_contract: address;
    var BLOCKTIME: uint256;
	var tmp1:  bool;
	var tmp2:  bool;
	var tmp3:  bool;
	var tmp4:  address;
	var tmp5:  bool;
	var tmp6:  bool;
	var tmp7:  bool;
	var tmp8:  bool;
	var tmp9:  bool;
	var tmp10:  uint256;
	var tmp11:  bool;
	var tmp12:  bool;
	var tmp13:  bool;
	var tmp14:  uint256;
	var tmp15:  uint256;
	var tmp16:  bool;
	var tmp17:  bool;
	var tmp18:  bool;
	var tmp19:  uint256;
	var tmp20:  uint256;
	var tmp21:  bool;
	var tmp22:  bool;
	var tmp23:  bool;
	var tmp24:  uint256;
	var tmp25:  uint256;
	var tmp26:  bool;
	var tmp27:  bool;
	var tmp28:  uint256;
	var tmp29:  bool;
	var tmp30:  bool;
	var tmp31:  uint256;
	var tmp32:  bool;
	var tmp33:  bool;
	var tmp34:  uint256;
	var tmp35:  bool;
	var tmp36:  bool;
	var tmp37:  uint256;
	var tmp38:  uint256;
	var tmp39:  uint256;
	var tmp40:  uint256;
	var tmp41:  address;
	var tmp42:  uint256;
	var tmp43:  uint256;
	var tmp44:  bool;
	var tmp45:  bool;
	var tmp46:  bool;
	var tmp47:  bool;
	var tmp48:  uint256;
	var tmp49:  bool;
	var tmp50:  bool;
	var tmp51:  address;
	var tmp52:  bool;
	var tmp53:  bool;
	var tmp54:  bool;
	var tmp55:  bool;
	var tmp56:  bool;
	var tmp57:  bool;
	var tmp58:  bool;
	var tmp59:  bool;
	var tmp60:  bool;
	var tmp61:  bool;
	var tmp62:  bool;
	var tmp63:  bool;
	var tmp64:  uint256;
	var tmp65:  bool;
	var tmp66:  bool;
	var tmp67:  uint256;
	var tmp68:  uint256;
	var tmp69:  uint256;
	var tmp70:  uint256;
	var tmp71:  uint256;
	var tmp72:  bool;
	var tmp73:  bool;
	var tmp74:  uint256;
	var tmp75:  bool;
	var tmp76:  uint256;
	var tmp77:  bool;
	var tmp78:  bool;
	var tmp79:  uint256;
	var tmp80:  bool;
	var tmp81:  bool;
	var tmp82:  uint256;
	var tmp83:  bool;
	var tmp84:  bool;
	var tmp85:  uint256;
	var tmp86:  bool;
	var tmp87:  uint256;
	var tmp88:  bool;
	var tmp89:  bool;
	var tmp90:  uint256;
	var tmp91:  bool;
	var tmp92:  bool;
	var tmp93:  bool;
	var tmp94:  bool;
	var tmp95:  uint256;
	var tmp96:  uint256;
	var tmp97:  bool;
	var tmp98:  bool;
	var tmp99:  bool;
	var tmp100:  uint256;
	var tmp101:  uint256;
	var tmp102:  bool;
	var tmp103:  bool;
	var tmp104:  uint256;
	var tmp105:  bool;
	var tmp106:  bool;
	var tmp107:  bool;
	var tmp108:  uint256;
	var tmp109:  uint256;
	var tmp110:  bool;
	var tmp111:  bool;
	var tmp112:  bool;
	var tmp113:  uint256;
	var tmp114:  uint256;
	var tmp115:  bool;
	var tmp116:  bool;
	var tmp117:  uint256;
	var tmp118:  bool;
	var tmp119:  bool;
	var tmp120:  bool;
	var tmp121:  uint256;
	var tmp122:  uint256;
	var tmp123:  bool;
	var tmp124:  bool;
	var tmp125:  bool;
	var tmp126:  uint256;
	var tmp127:  uint256;
	var tmp128:  bool;
	var tmp129:  bool;
	var tmp130:  bool;
	var tmp131:  uint256;
	var tmp132:  uint256;
	var tmp133:  bool;
	var tmp134:  bool;
	var tmp135:  bool;
	var tmp136:  bool;
	var tmp137:  bool;
	var tmp138:  bool;
	var tmp139:  bool;
	var tmp140:  bool;
	var tmp141:  bool;
	var tmp142:  uint256;
	var tmp143:  bool;
	var tmp144:  bool;
	var tmp145:  uint256;
	var tmp146:  bool;
	var tmp147:  bool;
	var tmp148:  uint256;

	// declare-vars
	var decl_factory: address;


	// def-vars
	var pair:  address;
	var tokenB:  address;
	var tokenA:  address;
	var factory:  address;
	factory:=UniswapV2Router.factory[entry_contract];
	tokenA:= path[0];
	tokenB:= path[1];
	pair:= UniswapV2Factory.getPair[factory][tokenA][tokenB];

	// hypothesis 
	assume(to != pair);
	assume(tx_origin != pair);
	assume(UniswapV2Factory.swapFeeRate[factory] == 0.0);
	assume(UniswapV2Factory.swapFeeRate[pair] == 0.0);
	assume(UniswapV2Pair.reserve0[pair] == UniswapV2ERC20.balanceOf[path[0]][pair]);
	assume(UniswapV2Pair.reserve1[pair] == UniswapV2ERC20.balanceOf[path[1]][pair]);
	assume(FancyToken.totalSupply[path[0]] < TwoE255);
	assume(FancyToken.totalSupply[path[1]] < TwoE255);
	assume(UniswapV2Pair.token0[pair] == path[0]);
	assume(UniswapV2Pair.token1[pair] == path[1]);

	tmp1:=(path[0]!=path[1]);
	assume(tmp1);

	tmp2:= (path[0]<path[1]);
	assume(tmp2);

	tmp3:=(path[0]!=0);
	assume(tmp3);

	tmp4:=UniswapV2Factory.getPair[entry_contract][path[0]][path[1]];
	tmp5:= (path[0]==path[0]);
	assume(tmp5);

	tmp6:= (amountIn>0.0);
	assume(tmp6);

	tmp7:= (UniswapV2Pair.reserve0[tmp4]>0.0);
	tmp8:=!tmp7;
	assume(!tmp8);

	tmp9:= (UniswapV2Pair.reserve1[tmp4]>0.0);
	assume(tmp9);

	tmp10:=evmsub(1000.0,UniswapV2Factory.swapFeeRate[UniswapV2Router.factory[entry_contract]]);
	tmp11:= (tmp10>1000.0);
	tmp12:=!tmp11;
	assume(tmp12);

	tmp13:=!tmp12;
	tmp14:=evmmul(amountIn,tmp10);
	tmp15:=evmdiv(tmp14,amountIn);
	tmp16:= (tmp10==tmp15);
	tmp17:=tmp13||tmp16;
	assume(tmp17);

	tmp18:=!tmp17;
	tmp19:=evmmul(tmp14,UniswapV2Pair.reserve1[tmp4]);
	tmp20:=evmdiv(tmp19,tmp14);
	tmp21:= (UniswapV2Pair.reserve1[tmp4]==tmp20);
	tmp22:=tmp18||tmp21;
	assume(tmp22);

	tmp23:=!tmp22;
	tmp24:=evmmul(UniswapV2Pair.reserve0[tmp4],1000.0);
	tmp25:=evmdiv(tmp24,UniswapV2Pair.reserve0[tmp4]);
	tmp26:= (1000.0==tmp25);
	tmp27:=tmp23||tmp26;
	assume(tmp27);

	tmp28:=evmadd(tmp24,tmp14);
	tmp29:= (tmp24>tmp28);
	tmp30:=!tmp29;
	assume(tmp30);

	assume(tmp28!=Zero);

	tmp31:=evmdiv(tmp19,tmp28);
	tmp32:= (tmp31<amountOutMin);
	tmp33:=!tmp32;
	assume(tmp33);

	// insert invariant of FancyToken
	assume(forall x:address :: Zero <= FancyToken.balanceOf[path[0]][x] && FancyToken.balanceOf[path[0]][x] <= FancyToken.totalSupply[path[0]]);
	assume(sum(FancyToken.balanceOf[path[0]]) == FancyToken.totalSupply[path[0]]);

	tmp34:=FancyToken.balanceOf[path[0]][tx_origin];
	tmp35:= (tmp34<amountIn);
	tmp36:=!tmp35;
	assume(tmp36);

	tmp37:=FancyToken.allowance[path[0]][tx_origin][entry_contract];
	tmp38:=evmsub(tmp37,amountIn);
	FancyToken.allowance[path[0]][tx_origin][entry_contract]:=tmp38;

	tmp39:=FancyToken.balanceOf[path[0]][tx_origin];
	tmp40:=evmsub(tmp39,amountIn);
	FancyToken.balanceOf[path[0]][tx_origin]:=tmp40;

	tmp41:=UniswapV2Factory.getPair[factory][path[0]][path[1]];
	tmp42:=FancyToken.balanceOf[path[0]][tmp41];
	tmp43:=evmadd(tmp42,amountIn);
	FancyToken.balanceOf[path[0]][tmp41]:=tmp43;

	assert(forall x:address :: Zero <= FancyToken.balanceOf[path[0]][x] && FancyToken.balanceOf[path[0]][x] <= FancyToken.totalSupply[path[0]]);
	assert(sum(FancyToken.balanceOf[path[0]]) == FancyToken.totalSupply[path[0]]);

	tmp44:=(path[0]!=path[1]);
	assume(tmp44);

	tmp45:= (path[0]<path[1]);
	assume(tmp45);

	tmp46:=(path[0]!=0);
	assume(tmp46);

	tmp47:= (path[0]==path[0]);
	assume(tmp47);

	tmp48:=nondet(); //EXTCODESIZE
	tmp49:=tmp48==Zero;
	tmp50:=!tmp49;
	assume(tmp50);

	tmp51:=UniswapV2Factory.getPair[entry_contract][path[0]][path[1]];
	tmp52:= (UniswapV2Pair.unlocked[tmp51]==1.0);
	assume(tmp52);

	UniswapV2Pair.unlocked[tmp51]:=0.0;

	tmp53:= (tmp31>0.0);
	assume(tmp53);

	tmp54:= (0.0<UniswapV2Pair.reserve0[tmp51]);
	tmp55:=!tmp54;
	assume(!tmp55);

	tmp56:= (tmp31<UniswapV2Pair.reserve1[tmp51]);
	assume(tmp56);

	tmp57:= (to==UniswapV2Pair.token0[tmp51]);
	tmp58:=!tmp57;
	tmp59:=!tmp58;
	assume(!tmp59);

	tmp60:= (to==UniswapV2Pair.token1[tmp51]);
	tmp61:=!tmp60;
	assume(tmp61);

	tmp62:= (tmp31>0.0);
	tmp63:=!tmp62;
	assume(!tmp63);

	// insert invariant of FancyToken
	assume(forall x:address :: Zero <= FancyToken.balanceOf[path[1]][x] && FancyToken.balanceOf[path[1]][x] <= FancyToken.totalSupply[path[1]]);
	assume(sum(FancyToken.balanceOf[path[1]]) == FancyToken.totalSupply[path[1]]);

	tmp64:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51];
	tmp65:= (tmp64<tmp31);
	tmp66:=!tmp65;
	assume(tmp66);

	tmp67:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51];
	tmp68:=evmsub(tmp67,tmp31);
	FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51]:=tmp68;

	tmp69:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][to];
	tmp70:=evmadd(tmp69,tmp31);
	FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][to]:=tmp70;

	assert(forall x:address :: Zero <= FancyToken.balanceOf[path[1]][x] && FancyToken.balanceOf[path[1]][x] <= FancyToken.totalSupply[path[1]]);
	assert(sum(FancyToken.balanceOf[path[1]]) == FancyToken.totalSupply[path[1]]);


	tmp71:=evmsub(UniswapV2Pair.reserve0[tmp51],0.0);
	tmp72:= (tmp71>UniswapV2Pair.reserve0[tmp51]);
	tmp73:=!tmp72;
	assume(tmp73);

	tmp74:=FancyToken.balanceOf[tmp51][tmp51];
	tmp75:= (tmp74>tmp71);
	assume(tmp75);

	tmp76:=evmsub(UniswapV2Pair.reserve0[tmp51],0.0);
	tmp77:= (tmp76>UniswapV2Pair.reserve0[tmp51]);
	tmp78:=!tmp77;
	assume(tmp78);

	tmp79:=evmsub(tmp74,tmp76);
	tmp80:= (tmp79>tmp74);
	tmp81:=!tmp80;
	assume(tmp81);

	tmp82:=evmsub(UniswapV2Pair.reserve1[tmp51],tmp31);
	tmp83:= (tmp82>UniswapV2Pair.reserve1[tmp51]);
	tmp84:=!tmp83;
	assume(tmp84);

	tmp85:=FancyToken.balanceOf[tmp51][tmp51];
	tmp86:= (tmp85>tmp82);
	assume(tmp86);

	tmp87:=evmsub(UniswapV2Pair.reserve1[tmp51],tmp31);
	tmp88:= (tmp87>UniswapV2Pair.reserve1[tmp51]);
	tmp89:=!tmp88;
	assume(tmp89);

	tmp90:=evmsub(tmp85,tmp87);
	tmp91:= (tmp90>tmp85);
	tmp92:=!tmp91;
	assume(tmp92);

	tmp93:= (tmp79>0.0);
	assume(tmp93);

	assume(tmp93);

	tmp94:=!tmp93;
	tmp95:=evmmul(tmp79,UniswapV2Pair.swapFeeRate[tmp51]);
	tmp96:=evmdiv(tmp95,tmp79);
	tmp97:= (UniswapV2Pair.swapFeeRate[tmp51]==tmp96);
	tmp98:=tmp94||tmp97;
	assume(tmp98);

	tmp99:=!tmp98;
	tmp100:=evmmul(tmp74,1000.0);
	tmp101:=evmdiv(tmp100,tmp74);
	tmp102:= (1000.0==tmp101);
	tmp103:=tmp99||tmp102;
	assume(tmp103);

	tmp104:=evmsub(tmp100,tmp95);
	tmp105:= (tmp104>tmp100);
	tmp106:=!tmp105;
	assume(tmp106);

	tmp107:=!tmp106;
	tmp108:=evmmul(tmp90,UniswapV2Pair.swapFeeRate[tmp51]);
	tmp109:=evmdiv(tmp108,tmp90);
	tmp110:= (UniswapV2Pair.swapFeeRate[tmp51]==tmp109);
	tmp111:=tmp107||tmp110;
	assume(tmp111);

	tmp112:=!tmp111;
	tmp113:=evmmul(tmp85,1000.0);
	tmp114:=evmdiv(tmp113,tmp85);
	tmp115:= (1000.0==tmp114);
	tmp116:=tmp112||tmp115;
	assume(tmp116);

	tmp117:=evmsub(tmp113,tmp108);
	tmp118:= (tmp117>tmp113);
	tmp119:=!tmp118;
	assume(tmp119);

	tmp120:=!tmp119;
	tmp121:=evmmul(UniswapV2Pair.reserve0[tmp51],UniswapV2Pair.reserve1[tmp51]);
	tmp122:=evmdiv(tmp121,UniswapV2Pair.reserve0[tmp51]);
	tmp123:= (UniswapV2Pair.reserve1[tmp51]==tmp122);
	tmp124:=tmp120||tmp123;
	assume(tmp124);

	tmp125:=!tmp124;
	tmp126:=evmmul(tmp121,1000000.0);
	tmp127:=evmdiv(tmp126,tmp121);
	tmp128:= (1000000.0==tmp127);
	tmp129:=tmp125||tmp128;
	assume(tmp129);

	tmp130:=!tmp129;
	tmp131:=evmmul(tmp104,tmp117);
	tmp132:=evmdiv(tmp131,tmp104);
	tmp133:= (tmp117==tmp132);
	tmp134:=tmp130||tmp133;
	assume(tmp134);

	tmp135:= (tmp131<tmp126);
	tmp136:=!tmp135;
	assume(tmp136);

	tmp137:= (tmp74>5192296858534827628530496329220095.0);
	tmp138:=!tmp137;
	tmp139:=!tmp138;
	assume(!tmp139);

	tmp140:= (tmp85>5192296858534827628530496329220095.0);
	tmp141:=!tmp140;
	assume(tmp141);

	tmp142:=evmadd(UniswapV2Pair.reserve0[tmp51],0.0);
	tmp143:= (UniswapV2Pair.reserve0[tmp51]>tmp142);
	tmp144:=!tmp143;
	assume(tmp144);

	tmp145:=evmadd(UniswapV2Pair.reserve1[tmp51],0.0);
	tmp146:= (UniswapV2Pair.reserve1[tmp51]>tmp145);
	tmp147:=!tmp146;
	assume(tmp147);

	UniswapV2Pair.reserve0[tmp51]:=tmp74;

	UniswapV2Pair.reserve1[tmp51]:=tmp85;

	tmp148:=evmmod(BLOCKTIME,4294967296.0);
	UniswapV2Pair.blockTimestampLast[tmp51]:=tmp148;

	UniswapV2Pair.unlocked[tmp51]:=1.0;

	factory:=UniswapV2Router.factory[entry_contract];
	pair:= UniswapV2Factory.getPair[factory][tokenA][tokenB];

	// (post) insert postcondition of swapExactTokensForTokens
	assert( old( UniswapV2ERC20.balanceOf[path[0]][pair] ) * old( UniswapV2ERC20.balanceOf[path[1]][pair] ) ==  UniswapV2ERC20.balanceOf[path[0]][pair] * UniswapV2ERC20.balanceOf[path[1]][pair] );
}