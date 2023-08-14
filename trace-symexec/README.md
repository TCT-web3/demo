# Running the demo
## Step 0: Setup
The following must be installed: Python and Ganache.
## Step 1: Get the tx hash from Remix
1. Go to [Remix](https://remix.ethereum.org). Click `Upload folder`. Upload the `uniswapv2-solc0.8` folder. Select the `test.sol` file.
2. Click `File Explorer` in the left bar. Select the `test.sol` file.
3. Click `Solidity Compiler` in the left bar. Under compiler, select `0.8.18`. This is the compiler version we are using. Click `Compile test.sol`.
4. Click `Deploy & Run Transactions` in the left bar. Under environment, select either `Custom - External Http Provider` or `Dev - Ganache Provider`. Type the RPC Server address and click OK. Set the gas limit to a high number, such as `67219750`. Click `Deploy`. 
5. Scroll down and find `Deployed Contracts`. Click whichever contract you would like to deploy.
6. Navigate to Ganache. You should see the contract that was deployed.
## Step 2: Convert into trace
1. Use the below command to get the json trace. This command works best on macOS. If you are using Windows, go to the web-demo folder and find the curl_trace.sh file. There's a separate command for Windows.
    ```shell
    curl -H "Content-Type: application/json" --data '{"jsonrpc":"2.0", "id": 1, "method": "debug_traceTransaction", "params": ["<transaction hash>",{} ] }' <server> | json_pp > trace-<name>.json
    ```
2. Go to the web-demo folder and select the `convert_trace.py` file. In the main method, enter all the necessary arguments to run the file.
3. In the file, when a `CALL` or `STATICCALL` happens, there will be a `KeyError`. This is because we manually map the contract addresses to their contract names. This requires the knowledge of the organization of the Solidity code. You may use our trace files as a reference point. Go to the `deployment_info.json` file, type the contract address, then map it to the contract name. Repeat this for all `KeyErrors`. In our case, the function hashes should already be in the `deployment_info.json` file.
4. The output file will be a txt file. We will use it in the next step.
### Step 3: Run the symbolic execution engine
Go to the trace-symexec folder (this folder). There are a couple options you can choose from there:  
1. Run the command `./run_demo.sh`. This will run the traces we have provided and also run their respective Boogie output files. Currently, the `addLiquidity` and `removeLiquidity` demos will not run the Boogie file. 
2. In the `run_demo.sh` file, scroll down to `### individual`. You can copy and paste any command into Terminal and run each example individually.  
3. Run the following commands for the file you just ouputted with `convert_trace.py`. The commands are:
    ```shell
    python3 src/symexec.py ../uniswapv2-solc0.8/test.sol ../web-demo/uploads/<theorem file> ../web-demo/<trace file>
    boogie <boogie file>
    ```