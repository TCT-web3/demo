# TCT demo
## 1. solc metadata
The first demo of TCT using [metadata](https://docs.soliditylang.org/en/v0.8.19/metadata.html) and [Natspec](https://docs.soliditylang.org/en/latest/natspec-format.html).

- Install solc compiler locally: https://docs.soliditylang.org/en/develop/installing-solidity.html

- A tool to quickly switch between Solidity compiler versions: https://github.com/crytic/solc-select

- use the command to get the NatSpec
    ```shell
    solc --userdoc --devdoc re_victim.sol // under get-trace folder
    ```

    natspec content for `re_victim.sol`
    ```text
    ======= re_victim.sol:Attack =======
    Developer Documentation
    {"kind":"dev","methods":{},"version":1}
    User Documentation
    {"kind":"user","methods":{},"version":1}

    ======= re_victim.sol:EtherStore =======
    Developer Documentation
    {"kind":"dev","methods":{"leaves()":{"custom:experimental":"invariant: (forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply)"},"withdraw()":{"custom:experimental":"invariant: (forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply) "}},"version":1}
    User Documentation
    {"kind":"user","methods":{},"version":1}

    ======= re_victim.sol:EtherStoreChild =======
    Developer Documentation
    {"kind":"dev","methods":{"withdraw()":{"custom:experimental":"invariant: (forall x:address :: 0 <= balances[x] && balances[x] <= totalSupply) "}},"version":1}
    User Documentation
    {"kind":"user","methods":{},"version":1}
    ```

- use the command `solc --metadata re_victim.sol --output-dir re_victim_metadata_json` to get the metedata in folder `re_victim_metadata_json`. And we can extract from the key `"devdoc"` (NatSpec).

- **Rule to use tags**:
    - put the tag in front of interface, contract, function, event.
    - `@inheritdoc`: when we want to make the thereom inherited.
    - `@custom:tct/experimental`: we could put the thereom here where it won't be inherited.

## 2. Get the evm execution trace?
Get the evm execution trace using alchemy API `trace-replaytransaction`: https://docs.alchemy.com/reference/trace-replaytransaction. But the `vmtrace` is null. The vmTrace mode is one of the most enigmatic and rarely used, mainly because it was never really documented. 

Here is what we get in a `vmTrace` response:

- `VMTrace` represents a call and contains all subcalls
    - `code` EVM bytecode to be executed
    - `ops` list of VMOperation to be executed
- `VMOperation` represents a step of the execution
    - `pc` program counter
    - `cost` gas cost of the operation
    - `ex` the result of the execution, could be null if the operation has reverted
    - `sub` list of VMTrace subcalls
    - `op` opcode name
    - `idx` index in the call tree
- `VMExecutedOperation` represents side effects of executing the operation
    - `used` incorrectly named, shows the remaining gas
    - `push` the items to be placed on the stack
    - `mem` the memory delta
    - `store` the storage delta
- `MemoryDiff` represents a memory update
    - `off` memory offset where to write the data
    - `data` the bytes to write starting at the offset
- `StorageDiff` represents a storage write
    - `key` storage key to write to
    - `val` value to write

I build a `vm_trace.py` to get execution trace.
### How to use `vm_trace.py`?
Before you run, you have to make sure you run a Geth node on local machine.
- [1] Install Ethereum Client (Geth): https://geth.ethereum.org/docs/getting-started/installing-geth
- [2] Run a Local Ethereum Node: Once you have installed an Ethereum client, you need to run it to create a local blockchain. The specific command may vary depending on the client you are using. For example, if you are using Geth, you can run the following command to start a local node:
    ```shell
    geth --syncmode "full" --http --http.api eth,web3,debug --http.addr "localhost" --http.port "8545" console
    debug.traceTransaction("0x241bf4e3ea3edf32eff7257486a774430e600d5aae6340e70ebf44a9e51ca2e0")

    erigon --http --http.api eth,web3,debug --http.addr "localhost" --http.port "8545"
    debug.trace_replayTransaction("0x241bf4e3ea3edf32eff7257486a774430e600d5aae6340e70ebf44a9e51ca2e0")
    ```
- [3] Connect to Localhost Provider by running `python3 web3_check.py`. It should return True. If False, return to check if you install Geth correctly.

Then, we could run `vm_trace.py`
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r evm_trace_requirement.txt
ape --version # test if eth-ape is installed
python3 vm_trace.py --help # see how to use
python3 vm_trace.py trace <tx hash> # get tx hash
```

**Dependency:**
- ape: https://github.com/ApeWorX/ape
- eth-ape: https://docs.apeworx.io/ape/stable/userguides/quickstart.html
- ape-alchemy: https://github.com/ApeWorX/ape-alchemy

More details about `vmtrace` in official doc: https://ethereum-tests.readthedocs.io/_/downloads/en/latest/pdf/.

### Get trace from Remix VSCode plugin
Or we could use local [remix plugin](https://github.com/ethereum/remix-vscode). There are two ways to run & deploy contracts using local remix: remixd (which connect web ethereum) and locally run via `ganachi-cli` (https://trufflesuite.com/docs/ganache/quickstart/). Please refer to this link: https://medium.com/remix-ide/remix-in-vscode-compiling-debugging-metamask-remixd-42c4a61817e2.

For how to deploy and test the contract, follow this blog: https://blog.logrocket.com/develop-test-deploy-smart-contracts-ganache/.

after you successfully deploy a contract and issue an transaction, you could use this cmd to get trace of the transaction.

```bash
curl -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["<transaction hash>",{} ] }' http://localhost:8545 -o trace.json
```

then you will get a json file `trace.json` which contains the execution trace. And we process the raw json file to get the evm opcode trace. For example

```bash
python3 trace_process.py --trace_file trace.json --output trace1.txt
```

### How to get the trace of a reverted transaction?
More details are [here](get-trace/getRevertTrace.md).