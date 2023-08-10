# Running the demo
## Install Flask
```shell
pip3 install flask
```
## Check files
After you get the transaction hash, also add the contract address and function selector into your theorem file under ```entry-for-real```.  
Depending on what method you used to get the trace, in the ```get_trace()``` method of the ```server.py``` file, when you ```curl``` the trace, you might have to change the web address. For example, I used ```truffle develop``` to get the trace, and the web address was ```http://127.0.0.1:9545``` as opposed to Remix which defaults to ```7545```.  

Right now, the ```symexec.py``` and ```convert_trace.py``` do not support incorrect entry points.
## Run the demo
1. Start the server:
```shell
python3 server.py
```
2. Navigate to the web address (http://127.0.0.1:5000). 
3. Enter the transaction hash and select your theorem file.
4. Check results!
