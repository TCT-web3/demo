# demo
The first demo of TCT

- Install solc compiler locally: https://docs.soliditylang.org/en/develop/installing-solidity.html

- A tool to quickly switch between Solidity compiler versions: https://github.com/crytic/solc-select

- Natspec: https://docs.soliditylang.org/en/latest/natspec-format.html

- use the command to get the spec
    ```shell
    solc --userdoc --devdoc re_victim.sol
    ```

    natspec content for `re_victim.sol`
    ```
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