from web3.auto import w3
import binascii

key_file_path = "/Users/billy/Library/Ethereum/rinkeby/keystore/UTC--2023-07-08T09-07-25.779700000Z--8ca598d518af8e104f2d9e1ceb9dc6307c8bc02d"

with open(key_file_path) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, 'billy')

print(binascii.b2a_hex(private_key))
