from web3.auto import w3
import binascii

key_file_path = "/Users/billy/Library/Ethereum/goerli/keystore/UTC--2023-07-20T07-58-34.125121000Z--97b35d326217bb5b15b92aa2f57874f7f26bd6e4"

with open(key_file_path) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, 'billy')

print(binascii.b2a_hex(private_key))
