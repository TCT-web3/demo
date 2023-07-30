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

//c_c13e7 is router
//c_7fb0a is factory
//c_a15b5 is pair
//c_667ac is path[0]
//c_2d94d is path[1]
var c_667ac.balanceOf:  [address] uint256;
var c_2d94d.balanceOf:  [address] uint256;
procedure straightline_code ()
modifies c_667ac.balanceOf, c_2d94d.balanceOf;
{  
    var tx_origin: address;
	var amountIn:	uint256;
	var amountOutMin:	uint256;
	var path:	[int] address;
	var to:	address;

	var c_c13e7.factory:  address;         
	var c_7fb0a.swapFeeRate:  uint256;     
	var tmp1:  uint256;
	var tmp2:  bool;
	var tmp3:  uint256;
	var c_7fb0a.getPair:  [address] [address] address;
	var c_a15b5.reserve0:  uint256;              
	var c_a15b5.reserve1:  uint256;
	var c_a15b5.blockTimestampLast:  uint256;
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
	var c_667ac.allowance:  [address] [address] uint256;    
	var tmp33:  uint256;
	var tmp34:  uint256;

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
	var tmp46:  bool;
	var c_a15b5.unlocked:  uint256;
	var tmp47:  bool;
	var tmp48:  bool;
	var tmp49:  bool;
	var tmp50:  bool;
	var tmp51:  bool;
	var c_a15b5.token0:  address;
	var c_a15b5.token1:  address;
	var tmp52:  bool;
	var tmp53:  bool;
	var tmp54:  bool;
	var tmp55:  bool;
	var tmp56:  bool;
	var tmp57:  bool;
	var tmp58:  bool;
     
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
	var c_a15b5.swapFeeRate:  uint256;
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

	//---------------- MANUALLY ENTERED
	var pair:address;
	var old_token0_bal, old_token1_bal: uint256;
	
	pair:=c_7fb0a.getPair[path[0]][path[1]];
	assume to != pair;    
	assume tx_origin != pair;   
	//assume c_667ac.balanceOf[pair] !=0.0;
	//assume c_2d94d.balanceOf[pair] !=0.0;
	assume c_7fb0a.swapFeeRate == 0.0;
	assume c_a15b5.swapFeeRate == 0.0;
	
	//assume invariants
	assume c_a15b5.reserve1 == c_667ac.balanceOf[pair];
	assume c_a15b5.reserve0 == c_2d94d.balanceOf[pair];
	//========================================================================================
	old_token0_bal := c_667ac.balanceOf[pair];
	old_token1_bal := c_2d94d.balanceOf[pair];
	
	assume(path[0]>=path[1]);
	assume(path[1]!=0);

	tmp4:= (path[0]==path[1]);
	assume(!tmp4);

	tmp5:= (amountIn>0.0);
	assume(tmp5);

	tmp6:= (c_a15b5.reserve1>0.0);
	tmp7:=!tmp6;
	assume(!tmp7);

	tmp8:= (c_a15b5.reserve0>0.0);
	assume(tmp8);

	tmp9:=evmsub(1000.0,c_7fb0a.swapFeeRate);  //tmp9=1000
	
	
	tmp13:=evmmul(amountIn,tmp9);      //tmp13=amountIn*1000

	tmp18:=evmmul(tmp13,c_a15b5.reserve0);   //tmp18=amountIn*1000*reserve0

	tmp23:=evmmul(c_a15b5.reserve1,1000.0);	//tmp23=reserve1*1000
	

	tmp27:=evmadd(tmp23,tmp13);       //tmp27=amountIn*1000+reserve1*1000
	
	assume(tmp27!=0.0);

	tmp30:=evmdiv(tmp18,tmp27);       //tmp30= amountIn*reserve0/(amountIn+reserve1), which is amountOut
	assume(tmp30>=amountOutMin);

	tmp35:=c_667ac.balanceOf[tx_origin];
	tmp36:=evmsub(tmp35,amountIn);
	c_667ac.balanceOf[tx_origin]:=tmp36;    //path[0].balanceOf[tx_origin] -= amountIn

	tmp37:=c_7fb0a.getPair[path[0]][path[1]];
	tmp38:=c_667ac.balanceOf[tmp37];
	tmp39:=evmadd(tmp38,amountIn);
	c_667ac.balanceOf[tmp37]:=tmp39;        //path[0].balanceOf[pair]+=amountIn
//ok
	
	//unlock

	tmp48:= (tmp30>0.0);
	assume(tmp48);
//ok
	assume(tmp30<c_a15b5.reserve0);

	assume(c_a15b5.reserve1>0.0);

	assume(to!=c_a15b5.token0);
	assume(to!=c_a15b5.token1);

	tmp59:=c_2d94d.balanceOf[tmp37];	
	tmp60:=evmsub(tmp59,tmp30);
	c_2d94d.balanceOf[tmp37]:=tmp60;      //path[1].balanceOf[pair]-=tmp30

	tmp61:=c_2d94d.balanceOf[to];
	tmp62:=evmadd(tmp61,tmp30);
	c_2d94d.balanceOf[to]:=tmp62;		  //path[1].balanceOf[to]+=tmp30

	tmp63:=evmsub(c_a15b5.reserve0,tmp30);
	tmp64:= (tmp63>c_a15b5.reserve0);
	tmp65:=!tmp64;
	assume(tmp65);

	tmp66:=c_2d94d.balanceOf[tmp37];
	tmp67:= (tmp66>tmp63);
	assume(!tmp67);

	tmp68:=evmsub(c_a15b5.reserve1,0.0);


	tmp71:=c_667ac.balanceOf[tmp37];
	tmp72:= (tmp71>tmp68);
	assume(tmp72);

	tmp73:=evmsub(c_a15b5.reserve1,0.0);


	tmp76:=evmsub(tmp71,tmp73);
	tmp77:= (tmp76>tmp71);
	tmp78:=!tmp77;
	assume(tmp78);

	tmp79:= (tmp76>0.0);
	assume(tmp79);

	tmp80:=evmmul(0.0,c_a15b5.swapFeeRate);
	tmp81:=evmdiv(tmp80,0.0);
	

	
	tmp85:=evmmul(tmp66,1000.0);


	tmp89:=evmsub(tmp85,tmp80);



	tmp93:=evmmul(tmp76,c_a15b5.swapFeeRate);



	tmp98:=evmmul(tmp71,1000.0);


	tmp102:=evmsub(tmp98,tmp93);



	tmp106:=evmmul(c_a15b5.reserve0,c_a15b5.reserve1);



	tmp111:=evmmul(tmp106,1000000.0);



	tmp116:=evmmul(tmp89,tmp102);


	tmp120:= (tmp116<tmp111);
	tmp121:=!tmp120;
	assume(tmp121);

	tmp122:= (tmp66>5192296858534827628530496329220095.0);
	tmp123:=!tmp122;
	tmp124:=!tmp123;
	assume(!tmp124);

	tmp125:= (tmp71>5192296858534827628530496329220095.0);
	tmp126:=!tmp125;
	assume(tmp126);

	tmp127:=evmadd(c_a15b5.reserve0,0.0);


	tmp130:=evmadd(c_a15b5.reserve1,0.0);


	c_a15b5.reserve0:=tmp66;

	c_a15b5.reserve1:=tmp71;

	//c_a15b5.blockTimestampLast:=MOD(BLOCKTIME,0x100000000);

	c_a15b5.unlocked:=1.0;

	//prove the "x*y==k" property
	assert evmmul(old(c_667ac.balanceOf[pair]), old(c_2d94d.balanceOf[pair])) == evmmul(c_667ac.balanceOf[pair], c_2d94d.balanceOf[pair]);
	//assert invariants
	assert c_a15b5.reserve1 == c_667ac.balanceOf[pair];
	assert c_a15b5.reserve0 == c_2d94d.balanceOf[pair];
}