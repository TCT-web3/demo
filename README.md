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