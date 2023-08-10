type uint256 = real;
const Zero : uint256;
axiom Zero == 0.0; 
const TwoE8 : uint256;
axiom TwoE8 == 32768.0; 

function evmdiv(a,b: uint256) returns (uint256);
axiom (forall a, b : uint256:: evmdiv(a,b) == a / b); 

function evmmul(a,b:uint256) returns (uint256);
axiom (forall a,b: uint256 :: evmdiv(evmmul(a,b),a)==b ==> evmmul(a,b) == a*b);

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
	var tmp34:  address;
	var tmp35:  uint256;
	var tmp36:  bool;
	var tmp37:  bool;
	var tmp38:  uint256;
	var tmp39:  uint256;
	var tmp40:  uint256;
	var tmp41:  uint256;
	var tmp42:  uint256;
	var tmp43:  uint256;
	var tmp44:  uint256;
	var tmp45:  bool;
	var tmp46:  bool;
	var tmp47:  bool;
	var tmp48:  bool;
	var tmp49:  bool;
	var tmp50:  bool;
	var tmp51:  address;
	var tmp52:  uint256;
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
	var tmp64:  bool;
	var tmp65:  bool;
	var tmp66:  bool;
	var tmp67:  uint256;
	var tmp68:  bool;
	var tmp69:  bool;
	var tmp70:  uint256;
	var tmp71:  uint256;
	var tmp72:  uint256;
	var tmp73:  uint256;
	var tmp74:  uint256;
	var tmp75:  uint256;
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
	var tmp87:  bool;
	var tmp88:  bool;
	var tmp89:  uint256;
	var tmp90:  uint256;
	var tmp91:  bool;
	var tmp92:  bool;
	var tmp93:  bool;
	var tmp94:  uint256;
	var tmp95:  uint256;
	var tmp96:  bool;
	var tmp97:  bool;
	var tmp98:  uint256;
	var tmp99:  bool;
	var tmp100:  bool;
	var tmp101:  bool;
	var tmp102:  uint256;
	var tmp103:  uint256;
	var tmp104:  bool;
	var tmp105:  bool;
	var tmp106:  bool;
	var tmp107:  uint256;
	var tmp108:  uint256;
	var tmp109:  bool;
	var tmp110:  bool;
	var tmp111:  uint256;
	var tmp112:  bool;
	var tmp113:  bool;
	var tmp114:  bool;
	var tmp115:  uint256;
	var tmp116:  uint256;
	var tmp117:  bool;
	var tmp118:  bool;
	var tmp119:  bool;
	var tmp120:  uint256;
	var tmp121:  uint256;
	var tmp122:  bool;
	var tmp123:  bool;
	var tmp124:  bool;
	var tmp125:  uint256;
	var tmp126:  uint256;
	var tmp127:  bool;
	var tmp128:  bool;
	var tmp129:  bool;
	var tmp130:  bool;
	var tmp131:  bool;
	var tmp132:  bool;
	var tmp133:  bool;
	var tmp134:  bool;
	var tmp135:  bool;
	var tmp136:  uint256;
	var tmp137:  bool;
	var tmp138:  bool;
	var tmp139:  uint256;
	var tmp140:  bool;
	var tmp141:  bool;
	var tmp142:  uint256;

	// declare-vars
	var decl_factory: address;
	var decl_pair: address;
	var decl_tokenA: address;
	var decl_tokenB: address;


	// def-vars
	var pair:  address;
	var tokenB:  address;
	var tokenA:  address;
	var factory:  address;
	factory:= UniswapV2Router.factory[entry_contract];
	tokenA:= path[0];
	tokenB:= path[1];
	pair:= UniswapV2Factory.getPair[factory][tokenA][tokenB];

	// hypothesis 
	assume(to != pair);
	assume(tx_origin != pair);
	assume(UniswapV2Factory.swapFeeRate[factory] == 0.0);
	assume(UniswapV2Pair.swapFeeRate[pair] == 0.0);
	assume(UniswapV2Pair.reserve0[pair] == FancyToken.balanceOf[tokenB][pair]);
	assume(UniswapV2Pair.reserve1[pair] == FancyToken.balanceOf[tokenA][pair]);
	assume(FancyToken.totalSupply[tokenB] < TwoE255);
	assume(FancyToken.totalSupply[tokenA] < TwoE255);
	assume(UniswapV2Pair.token0[pair] == path[1]);
	assume(UniswapV2Pair.token1[pair] == path[0]);

	// insert invariant of entry contract

	tmp1:=(path[0]!=path[1]);
	assume(tmp1);

	tmp2:= (path[0]<path[1]);
	assume(!tmp2);

	tmp3:=(path[1]!=0);
	assume(tmp3);

	tmp4:=UniswapV2Factory.getPair[UniswapV2Router.factory[entry_contract]][path[0]][path[1]];
	tmp5:= (path[0]==path[1]);
	assume(!tmp5);

	tmp6:= (amountIn>0.0);
	assume(tmp6);

	tmp7:= (UniswapV2Pair.reserve1[tmp4]>0.0);
	tmp8:=!tmp7;
	assume(!tmp8);

	tmp9:= (UniswapV2Pair.reserve0[tmp4]>0.0);
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
	tmp19:=evmmul(tmp14,UniswapV2Pair.reserve0[tmp4]);
	tmp20:=evmdiv(tmp19,tmp14);
	tmp21:= (UniswapV2Pair.reserve0[tmp4]==tmp20);
	tmp22:=tmp18||tmp21;
	assume(tmp22);

	tmp23:=!tmp22;
	tmp24:=evmmul(UniswapV2Pair.reserve1[tmp4],1000.0);
	tmp25:=evmdiv(tmp24,UniswapV2Pair.reserve1[tmp4]);
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

	tmp34:=UniswapV2Factory.getPair[UniswapV2Router.factory[entry_contract]][path[0]][path[1]];
	// insert invariant of FancyToken
	assume(forall x:address :: 0.0 <= FancyToken.balanceOf[path[0]][x] && FancyToken.balanceOf[path[0]][x] <= FancyToken.totalSupply[path[0]]);
	assume(sum( FancyToken.balanceOf[path[0]] ) == FancyToken.totalSupply[path[0]]);

	tmp35:=FancyToken.balanceOf[path[0]][tx_origin];
	tmp36:= (tmp35<amountIn);
	tmp37:=!tmp36;
	assume(tmp37);

	tmp38:=FancyToken.allowance[path[0]][tx_origin][entry_contract];
	tmp39:=evmsub(tmp38,amountIn);
	FancyToken.allowance[path[0]][tx_origin][entry_contract]:=tmp39;

	tmp40:=FancyToken.balanceOf[path[0]][tx_origin];
	tmp41:=evmsub(tmp40,amountIn);
	FancyToken.balanceOf[path[0]][tx_origin]:=tmp41;

	tmp42:=FancyToken.balanceOf[path[0]][tmp34];
	tmp43:=evmadd(amountIn,tmp42);
	FancyToken.balanceOf[path[0]][tmp34]:=tmp43;

	tmp44:=FancyToken.balanceOf[path[0]][tmp34];
	tmp45:= (tmp44<amountIn);
	tmp46:=!tmp45;
	assume(tmp46);

	assume(forall x:address :: 0.0 <= FancyToken.balanceOf[path[0]][x] && FancyToken.balanceOf[path[0]][x] <= FancyToken.totalSupply[path[0]]);
	assume(sum( FancyToken.balanceOf[path[0]] ) == FancyToken.totalSupply[path[0]]);
	tmp47:=(path[0]!=path[1]);
	assume(tmp47);

	tmp48:= (path[0]<path[1]);
	assume(!tmp48);

	tmp49:=(path[1]!=0);
	assume(tmp49);

	tmp50:= (path[0]==path[1]);
	assume(!tmp50);

	tmp51:=UniswapV2Factory.getPair[UniswapV2Router.factory[entry_contract]][path[0]][path[1]];
	tmp52:=nondet(); //EXTCODESIZE
	tmp53:=tmp52==Zero;
	tmp54:=!tmp53;
	assume(tmp54);

	tmp55:= (UniswapV2Pair.unlocked[tmp51]==1.0);
	assume(tmp55);

	UniswapV2Pair.unlocked[tmp51]:=0.0;

	tmp56:= (tmp31>0.0);
	assume(tmp56);

	assume(tmp56);

	tmp57:= (tmp31<UniswapV2Pair.reserve0[tmp51]);
	tmp58:=!tmp57;
	assume(!tmp58);

	tmp59:= (0.0<UniswapV2Pair.reserve1[tmp51]);
	assume(tmp59);

	tmp60:= (to==UniswapV2Pair.token0[tmp51]);
	tmp61:=!tmp60;
	tmp62:=!tmp61;
	assume(!tmp62);

	tmp63:= (to==UniswapV2Pair.token1[tmp51]);
	tmp64:=!tmp63;
	assume(tmp64);

	tmp65:= (tmp31>0.0);
	tmp66:=!tmp65;
	assume(!tmp66);

	// insert invariant of FancyToken
	assume(forall x:address :: 0.0 <= FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][x] && FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][x] <= FancyToken.totalSupply[UniswapV2Pair.token0[tmp51]]);
	assume(sum( FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]] ) == FancyToken.totalSupply[UniswapV2Pair.token0[tmp51]]);

	tmp67:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51];
	tmp68:= (tmp67<tmp31);
	tmp69:=!tmp68;
	assume(tmp69);

	tmp70:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51];
	tmp71:=evmsub(tmp70,tmp31);
	FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51]:=tmp71;

	tmp72:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][to];
	tmp73:=evmadd(tmp72,tmp31);
	FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][to]:=tmp73;

	assume(forall x:address :: 0.0 <= FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][x] && FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][x] <= FancyToken.totalSupply[UniswapV2Pair.token0[tmp51]]);
	assume(sum( FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]] ) == FancyToken.totalSupply[UniswapV2Pair.token0[tmp51]]);
	tmp74:=FancyToken.balanceOf[UniswapV2Pair.token0[tmp51]][tmp51];
	tmp75:=FancyToken.balanceOf[UniswapV2Pair.token1[tmp51]][tmp51];
	tmp76:=evmsub(UniswapV2Pair.reserve0[tmp51],tmp31);
	tmp77:= (tmp76>UniswapV2Pair.reserve0[tmp51]);
	tmp78:=!tmp77;
	assume(tmp78);

	tmp79:=evmsub(tmp74,tmp76);
	tmp80:= (tmp79>tmp74);
	tmp81:=!tmp80;
	assume(tmp81);

	tmp82:=evmsub(UniswapV2Pair.reserve1[tmp51],0.0);
	tmp83:= (tmp82>UniswapV2Pair.reserve1[tmp51]);
	tmp84:=!tmp83;
	assume(tmp84);

	tmp85:=evmsub(tmp75,tmp82);
	tmp86:= (tmp85>tmp75);
	tmp87:=!tmp86;
	assume(tmp87);

	tmp88:=!tmp87;
	tmp89:=evmmul(tmp79,UniswapV2Pair.swapFeeRate[tmp51]);
	tmp90:=evmdiv(tmp89,tmp79);
	tmp91:= (UniswapV2Pair.swapFeeRate[tmp51]==tmp90);
	tmp92:=tmp88||tmp91;
	assume(tmp92);

	tmp93:=!tmp92;
	tmp94:=evmmul(tmp74,1000.0);
	tmp95:=evmdiv(tmp94,tmp74);
	tmp96:= (1000.0==tmp95);
	tmp97:=tmp93||tmp96;
	assume(tmp97);

	tmp98:=evmsub(tmp94,tmp89);
	tmp99:= (tmp98>tmp94);
	tmp100:=!tmp99;
	assume(tmp100);

	tmp101:=!tmp100;
	tmp102:=evmmul(tmp85,UniswapV2Pair.swapFeeRate[tmp51]);
	tmp103:=evmdiv(tmp102,tmp85);
	tmp104:= (UniswapV2Pair.swapFeeRate[tmp51]==tmp103);
	tmp105:=tmp101||tmp104;
	assume(tmp105);

	tmp106:=!tmp105;
	tmp107:=evmmul(tmp75,1000.0);
	tmp108:=evmdiv(tmp107,tmp75);
	tmp109:= (1000.0==tmp108);
	tmp110:=tmp106||tmp109;
	assume(tmp110);

	tmp111:=evmsub(tmp107,tmp102);
	tmp112:= (tmp111>tmp107);
	tmp113:=!tmp112;
	assume(tmp113);

	tmp114:=!tmp113;
	tmp115:=evmmul(UniswapV2Pair.reserve0[tmp51],UniswapV2Pair.reserve1[tmp51]);
	tmp116:=evmdiv(tmp115,UniswapV2Pair.reserve0[tmp51]);
	tmp117:= (UniswapV2Pair.reserve1[tmp51]==tmp116);
	tmp118:=tmp114||tmp117;
	assume(tmp118);

	tmp119:=!tmp118;
	tmp120:=evmmul(tmp115,1000000.0);
	tmp121:=evmdiv(tmp120,tmp115);
	tmp122:= (1000000.0==tmp121);
	tmp123:=tmp119||tmp122;
	assume(tmp123);

	tmp124:=!tmp123;
	tmp125:=evmmul(tmp98,tmp111);
	tmp126:=evmdiv(tmp125,tmp98);
	tmp127:= (tmp111==tmp126);
	tmp128:=tmp124||tmp127;
	assume(tmp128);

	tmp129:= (tmp125<tmp120);
	tmp130:=!tmp129;
	assume(tmp130);

	tmp131:= (tmp74>5192296858534827628530496329220095.0);
	tmp132:=!tmp131;
	tmp133:=!tmp132;
	assume(!tmp133);

	tmp134:= (tmp75>5192296858534827628530496329220095.0);
	tmp135:=!tmp134;
	assume(tmp135);

	tmp136:=evmadd(UniswapV2Pair.reserve0[tmp51],0.0);
	tmp137:= (UniswapV2Pair.reserve0[tmp51]>tmp136);
	tmp138:=!tmp137;
	assume(tmp138);

	tmp139:=evmadd(UniswapV2Pair.reserve1[tmp51],0.0);
	tmp140:= (UniswapV2Pair.reserve1[tmp51]>tmp139);
	tmp141:=!tmp140;
	assume(tmp141);

	UniswapV2Pair.reserve0[tmp51]:=tmp74;

	UniswapV2Pair.reserve1[tmp51]:=tmp75;

	tmp142:=evmmod(BLOCKTIME,4294967296.0);
	UniswapV2Pair.blockTimestampLast[tmp51]:=tmp142;

	UniswapV2Pair.unlocked[tmp51]:=1.0;

	decl_factory:=UniswapV2Router.factory[entry_contract];
	decl_tokenA:=path[0];
	decl_tokenB:=path[1];
	decl_pair:=UniswapV2Factory.getPair[factory][tokenA][tokenB] ;

	// (post) insert postcondition of swapExactTokensForTokens
	assert( old( FancyToken.balanceOf[decl_tokenA][decl_pair] ) * old( FancyToken.balanceOf[decl_tokenB][decl_pair] ) == ( FancyToken.balanceOf[decl_tokenA][decl_pair] * FancyToken.balanceOf[decl_tokenB][decl_pair] ) );

	// (post) insert invariant of entry contract
}