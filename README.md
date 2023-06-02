# TCT demo
The first demo of TCT using [metadata](https://docs.soliditylang.org/en/v0.8.19/metadata.html) and [Natspec](https://docs.soliditylang.org/en/latest/natspec-format.html).

- Install solc compiler locally: https://docs.soliditylang.org/en/develop/installing-solidity.html

- A tool to quickly switch between Solidity compiler versions: https://github.com/crytic/solc-select

- use the command to get the NatSpec
    ```shell
    solc --userdoc --devdoc re_victim.sol
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
    - @inheritdoc: when we want to make the thereom inherited.
    - @custom:tct/experimental we could put the thereom here where it won't be inherited.

## Get the evm execution trace?
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

I build a `evm_trace.py` to get execution trace.
- eth-ape: https://docs.apeworx.io/ape/stable/userguides/quickstart.html
- ape-alchemy: https://github.com/ApeWorX/ape-alchemy