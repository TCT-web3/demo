
https://bolenzhang.github.io/2018/04/29/%E4%BB%A5%E5%A4%AA%E5%9D%8A%E7%A7%81%E9%93%BE%E6%90%AD%E5%BB%BA%E5%8F%8A%E6%99%BA%E8%83%BD%E5%90%88%E7%BA%A6%E9%83%A8%E7%BD%B2/


```shell
geth --goerli account new

geth --goerli 

geth --http --http.corsdomain https://remix.ethereum.org --goerli --vmdebug --allow-insecure-unlock --unlock “0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4”

geth --http --goerli --miner.etherbase '0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4' --mine

geth --goerli attach
> eth.accounts
["0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4", "0x9741cc9982265464ae3d84d96706f6a1f7265d8a"]
> miner.setEtherbase(eth.accounts[0])
true
> eth.coinbase
"0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4"
```


```shell
geth init --datadir node1 genesis.json

geth --networkid 191 --nodiscover --http --http.addr "127.0.0.1" --http.port 8545 --http.api personal,eth,net,web3 --allow-insecure-unlock --datadir node1 console

geth --datadir node1 --networkid 13756 --http --http.corsdomain https://remix.ethereum.org
```