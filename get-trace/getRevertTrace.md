# How to get the trace of a reverted transaction?
The file is `index3.js` and we have to use the API `debug_traceCall`. However, some framework even client do not support this. After some investigation, we have two approaches to do this.

## 1. Build a local private network
### goerli network
```shell
geth --goerli account new # create new account

geth --http --http.corsdomain https://remix.ethereum.org --goerli --vmdebug --allow-insecure-unlock --unlock “0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4” # start goerli network and connect to remix

geth --goerli attach # open another interactive terminal
> eth.accounts
["0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4", "0x9741cc9982265464ae3d84d96706f6a1f7265d8a"]
> miner.setEtherbase(eth.accounts[0])
true
> eth.coinbase
"0x97b35d326217bb5b15b92aa2f57874f7f26bd6e4"
> miner.start() # start to mine (add some fund to the account)

# then you could deploy the contract and use index3.js via `node index3.js` to get trace.
```

### Customized local network
do this within `TCTchain` folder.
```shell
geth init --datadir node1 genesis.json # network initialization

geth --datadir node1 --networkid 13756 --http --http.corsdomain https://remix.ethereum.org # start the network and connect to remix

# then follow the steps in goerli network section.
```

## 2. framework
the second approach is to use development framework that supports `debug_traceCall`. Here I recommend to use [foundry](https://book.getfoundry.sh/). 

Install foundry
```shell
$ curl -L https://foundry.paradigm.xyz | bash
```

After you sucessfully install foundry, use the command to install latest forge, cast, anvil, and chisel.
```shell
$ foundryup
```

and then use the command to start a local network.
```shell
$ anvil
```

then just deploy the contract and use `index3.js` to get trace.
