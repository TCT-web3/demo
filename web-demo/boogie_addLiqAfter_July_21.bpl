procedure straightline_code ()
{  
    var msg.sender: address;
	var tokenA:	address;
	var tokenB:	address;
	var amountADesired:	uint256;
	var amountBDesired:	uint256;
	var amountAMin:	uint256;
	var amountBMin:	uint256;
	var to:	address;

	var c_ab263.factory:  address;
	var tokenA:  address;
	var tokenB:  address;
	var amountADesired:  uint256;
	var amountBDesired:  uint256;
	var amountAMin:  uint256;
	var amountBMin:  uint256;
	var to:  address;
	var c_c5ce5.getPair:  [address] [address] address;
	var tmp1:  uint256;
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
	var tmp18:  uint256;
	var tmp19:  uint256;
	var tmp20:  bool;
	var tmp21:  bool;
	var tmp22:  bool;
	var c_f8c9b.allowance:  [address] [address] uint256;
	var tmp23:  uint256;
	var tmp24:  uint256;
	var c_f8c9b.balanceOf:  [address] uint256;
	var tmp25:  uint256;
	var tmp26:  uint256;
	var tmp27:  uint256;
	var tmp28:  uint256;
	var tmp29:  uint256;
	var c_b31d7.allowance:  [address] [address] uint256;
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
	var tmp51:  uint256;
	var tmp52:  bool;
	var tmp53:  uint256;
	var tmp54:  uint256;
	var tmp55:  bool;
	var tmp56:  uint256;
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

	tmp1:=c_c5ce5.getPair[tokenA][tokenB];
	tmp2:=evmsub(tmp1,0);
	assume(tmp2!=0);

	tmp3:=evmsub(tokenA,tokenB);
	assume(tmp3!=0);

	tmp4:= (tokenA<tokenB);
	assume(!tmp4);

	tmp5:=evmsub(tokenB,0);
	assume(tmp5!=0);

	tmp6:= (tokenA==tokenB);
	assume(!tmp6);

	tmp7:= (c_005aa.reserve1==0);
	tmp8:=!tmp7;
	assume(tmp8);

	tmp9:=!tmp8;
	assume(tmp9);

	tmp10:= (amountADesired>0);
	assume(tmp10);

	tmp11:= (c_005aa.reserve1>0);
	tmp12:=!tmp11;
	assume(!tmp12);

	tmp13:= (c_005aa.reserve0>0);
	assume(tmp13);

	tmp14:=!tmp13;
	tmp15:=evmmul(amountADesired,c_005aa.reserve0);
	tmp16:=evmdiv(tmp15,amountADesired);
	tmp17:= (c_005aa.reserve0==tmp16);
	tmp18:=evmor(tmp14,tmp17);
	assume(tmp18!=0);

	assume(c_005aa.reserve1!=0);

	tmp19:=evmdiv(tmp15,c_005aa.reserve1);
	tmp20:= (tmp19>amountBDesired);
	assume(!tmp20);

	tmp21:= (tmp19<amountBMin);
	tmp22:=!tmp21;
	assume(tmp22);

	tmp23:=c_f8c9b.allowance[msg_sender][msg_sender];
	tmp24:=evmsub(tmp23,amountADesired);
	c_f8c9b.allowance[msg_sender][msg_sender]:=tmp24;

	tmp25:=c_f8c9b.balanceOf[msg_sender];
	tmp26:=evmsub(tmp25,amountADesired);
	c_f8c9b.balanceOf[msg_sender]:=tmp26;

	tmp27:=c_c5ce5.getPair[tokenA][tokenB];
	tmp28:=c_f8c9b.balanceOf[c_c5ce5.getPair[tokenA][tokenB]];
	tmp29:=evmadd(tmp28,amountADesired);
	c_f8c9b.balanceOf[c_c5ce5.getPair]:=tmp29;

	tmp30:=c_b31d7.allowance[msg_sender][msg_sender];
	tmp31:=evmsub(tmp30,tmp19);
	c_b31d7.allowance[msg_sender][msg_sender]:=tmp31;

	tmp32:=c_b31d7.balanceOf[msg_sender];
	tmp33:=evmsub(tmp32,tmp19);
	c_b31d7.balanceOf[msg_sender]:=tmp33;

	tmp34:=c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]];
	tmp35:=evmadd(tmp34,tmp19);
	c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]:=tmp35;

	tmp36:= (c_005aa.unlocked==1);
	assume(tmp36);

	c_005aa.unlocked:=0;

	tmp37:=c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]];
	tmp38:=evmsub(tmp37,c_005aa.reserve0);
	tmp39:= (tmp38>c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]);
	tmp40:=!tmp39;
	assume(tmp40);

	tmp41:=c_f8c9b.balanceOf[c_005aa.token0];
	tmp42:=evmsub(tmp41,c_005aa.reserve1);
	tmp43:= (tmp42>c_f8c9b.balanceOf[c_005aa.token0]);
	tmp44:=!tmp43;
	assume(tmp44);

	tmp45:= (c_005aa.kLast==0);
	assume(tmp45);

	tmp46:=evmsub(c_005aa.totalSupply,0);
	assume(tmp46!=0);

	tmp47:=tmp46==0;
	tmp48:=evmmul(tmp38,c_005aa.totalSupply);
	tmp49:=evmdiv(tmp48,tmp38);
	tmp50:= (c_005aa.totalSupply==tmp49);
	tmp51:=evmor(tmp47,tmp50);
	assume(tmp51!=0);

	assume(c_005aa.reserve0!=0);

	tmp52:=tmp51==0;
	tmp53:=evmmul(tmp42,c_005aa.totalSupply);
	tmp54:=evmdiv(tmp53,tmp42);
	tmp55:= (c_005aa.totalSupply==tmp54);
	tmp56:=evmor(tmp52,tmp55);
	assume(tmp56!=0);

	assume(c_005aa.reserve1!=0);

	tmp57:=evmdiv(tmp48,c_005aa.reserve0);
	tmp58:=evmdiv(tmp53,c_005aa.reserve1);
	tmp59:= (tmp57<tmp58);
	assume(!tmp59);

	tmp60:= (tmp58>0);
	assume(tmp60);

	tmp61:=evmadd(c_005aa.totalSupply,tmp58);
	tmp62:= (c_005aa.totalSupply>tmp61);
	tmp63:=!tmp62;
	assume(tmp63);

	c_005aa.totalSupply:=tmp61;

	tmp64:=c_005aa.balanceOf[to];
	tmp65:=evmadd(c_005aa.balanceOf[to],tmp58);
	tmp66:= (tmp64>tmp65);
	tmp67:=!tmp66;
	assume(tmp67);

	c_005aa.balanceOf[to]:=tmp65;

	tmp68:= (c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]]>5192296858534827628530496329220095);
	tmp69:=!tmp68;
	tmp70:=!tmp69;
	assume(!tmp70);

	tmp71:= (c_f8c9b.balanceOf[c_005aa.token0]>5192296858534827628530496329220095);
	tmp72:=!tmp71;
	assume(tmp72);

	tmp73:=evmadd(c_005aa.reserve0,0);
	tmp74:= (c_005aa.reserve0>tmp73);
	tmp75:=!tmp74;
	assume(tmp75);

	tmp76:=evmadd(c_005aa.reserve1,0);
	tmp77:= (c_005aa.reserve1>tmp76);
	tmp78:=!tmp77;
	assume(tmp78);

	c_005aa.reserve0:=c_b31d7.balanceOf[c_c5ce5.getPair[tokenA][tokenB]];

	c_005aa.reserve1:=c_f8c9b.balanceOf[c_005aa.token0];

	c_005aa.blockTimestampLast:=MOD(BLOCKTIME,0x100000000);

	c_005aa.unlocked:=1;

