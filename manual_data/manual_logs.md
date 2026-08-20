# Meter.io
## CCTX 1
### Source

```
id = AUTOINCREMENT

bridge = Meter
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xc7eb98e00d21ec2025fd97b8a84af141325531c0b54aacc37633514f2fd8ffdc
cctx_id =
block_number = 14992320
timestamp = 1644071350
log_index = 281

event_type = Deposit

correlation_id = 2559

src_blockchain = BNB
dst_blockchain = Moonriver

actor_from = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
actor_to = NULL
signer = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
relayer = NULL

token_in = 0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C
token_out = NULL
amount_in = NULL
amount_out = NULL

nonce = 2559
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
status = success
```

### Destination

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Moonriver
raw_table = 
raw_pk = 

transaction_hash = 0x689ff22ebf7f7aa6ecf0d60345979855442a09dfb7439c8553b2369e6e130409
cctx_id = 
block_number = 1442439
timestamp = 1644071526
log_index = 0

event_type = Transfer

correlation_id = 2559

src_blockchain = BNB
dst_blockchain = Moonriver

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
signer =
relayer =

token_in = NULL
token_out = 0x868892CCCEdbfF0b028f3B3595205ea91B99376B
amount_in = NULL
amount_out = 15000000000000000000000

nonce = 2559
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x868892CCCEdbfF0b028f3B3595205ea91B99376B
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","topic0":"0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","from":"0x0000000000000000000000000000000000000000","to":"0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01","value":"15000000000000000000000","token_symbol":"BNB.bsc","token_name":"BNB from BSC","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_from":"0xD33966215C372935858DB3C4749dFb62718D0554","tx_to":"0xF41e7FC4eC990298d36f667B93951c9dba65224e","tx_value":"0","tx_fee_movr":"0.000515732","tx_fee_wei":"515732000000000"}
```

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Moonriver
raw_table = 
raw_pk = 

transaction_hash = 0x689ff22ebf7f7aa6ecf0d60345979855442a09dfb7439c8553b2369e6e130409
cctx_id = 
block_number = 1442439
timestamp = 1644071526
log_index = 1

event_type = ProposalEvent

correlation_id = 2559

src_blockchain = BNB
dst_blockchain = Moonriver

actor_from = 0xD33966215C372935858DB3C4749dFb62718D0554
actor_to = 0xF41e7FC4eC990298d36f667B93951c9dba65224e
signer =
relayer =

token_in = NULL
token_out = 0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C
amount_in = NULL
amount_out = NULL

nonce = 2559
message_id = NULL
message_hash = 0x534C799930F183E6C6C82F109E7274BBC7160D831CEB4A634FF6B5B03780EE73
payload_hash = 0x534C799930F183E6C6C82F109E7274BBC7160D831CEB4A634FF6B5B03780EE73
proof_hash = NULL
guid = NULL

contract_address = 0xF41e7FC4eC990298d36f667B93951c9dba65224e
status = 33

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","topic0":"0x803c5a12f6bde629cea32e63d4b92d1b560816a6fb72e939d3c89e1cab650417","originChainID":"44","depositNonce":"25592559","proposal_status":"33","resourceID":"0x0000000000000000000000BB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C01","resource_token":"0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C","dataHash":"0x534C799930F183E6C6C82F109E7274BBC7160D831CEB4A634FF6B5B03780EE73","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_chainID_arg":"4","tx_depositNonce_arg":"2559","tx_resourceID_arg":"0x0000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c01","tx_data_amount":"15000000000000000000000","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_from":"0xD33966215C372935858DB3C4749dFb62718D0554","tx_to":"0xF41e7FC4eC990298d36f667B93951c9dba65224e","tx_value":"0","tx_fee_movr":"0.000515732","tx_fee_wei":"515732000000000"}
```

## CCTX 2
### Source

```
id = AUTOINCREMENT

bridge = Meter
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x5d7cd17bfeb944390667c76f4fc2786f748dc3eb363c01c24b92becaaf5690b4
cctx_id =
block_number = 14992642
timestamp = 1644072316
log_index = 199

event_type = Deposit

correlation_id = 2559

src_blockchain = BNB
dst_blockchain = Moonriver

actor_from = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
actor_to = NULL
signer = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
relayer = NULL

token_in = 0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C
token_out = NULL
amount_in = NULL
amount_out = NULL

nonce = 2559
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","topic0":"0xdbb69440df8433824a026ef190652f29929eb64b4d1d5d2a69be8afe3e6eaed8","destinationChainID_event_topic":"55","destinationChainID_input":"5","resourceID":"0x0000000000000000000000BB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C01","depositNonce_event_topic":"25612561","tx_data_amount":"15000000000000000000000","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_value":"8000000000000000","tx_fee":"1146545000000000"}
```

### Destination

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Moonriver
raw_table =
raw_pk =

transaction_hash = 0xc7f764644e9af42714d98763b7e8dcf5e1de6b855b63e2c6ff2438e09b61ccc7
cctx_id =
block_number = 1442487
timestamp = 1644072468
log_index = 0

event_type = Transfer

correlation_id = 2559

src_blockchain = BNB
dst_blockchain = Moonriver

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
signer =
relayer =

token_in = NULL
token_out = 0x868892CCCEdbfF0b028f3B3595205ea91B99376B
amount_in = NULL
amount_out = 15000000000000000000000

nonce = 2559
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x868892CCCEdbfF0b028f3B3595205ea91B99376B
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","topic0":"0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","from":"0x0000000000000000000000000000000000000000","to":"0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01","value":"15000000000000000000000","token_symbol":"BNB.bsc","token_name":"BNB from BSC","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_from":"0xD33966215C372935858DB3C4749dFb62718D0554","tx_to":"0xF41e7FC4eC990298d36f667B93951c9dba65224e","tx_value":"0","tx_fee_movr":"0.000381332","tx_fee_wei":"381332000000000"}
```

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Moonriver
raw_table =
raw_pk =

transaction_hash = 0xc7f764644e9af42714d98763b7e8dcf5e1de6b855b63e2c6ff2438e09b61ccc7
cctx_id =
block_number = 1442487
timestamp = 1644072468
log_index = 1

event_type = ProposalEvent

correlation_id = 2559

src_blockchain = BNB
dst_blockchain = Moonriver

actor_from = 0xD33966215C372935858DB3C4749dFb62718D0554
actor_to = 0xF41e7FC4eC990298d36f667B93951c9dba65224e
signer =
relayer =

token_in = NULL
token_out = 0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C
amount_in = NULL
amount_out = NULL

nonce = 2559
message_id = NULL
message_hash = 0x534C799930F183E6C6C82F109E7274BBC7160D831CEB4A634FF6B5B03780EE73
payload_hash = 0x534C799930F183E6C6C82F109E7274BBC7160D831CEB4A634FF6B5B03780EE73
proof_hash = NULL
guid = NULL

contract_address = 0xF41e7FC4eC990298d36f667B93951c9dba65224e
status = 33

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","topic0":"0x803c5a12f6bde629cea32e63d4b92d1b560816a6fb72e939d3c89e1cab650417","originChainID":"44","depositNonce":"2559","proposal_status":"33","resourceID":"0x0000000000000000000000BB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C01","resource_token":"0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C","dataHash":"0x534C799930F183E6C6C82F109E7274BBC7160D831CEB4A634FF6B5B03780EE73","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_chainID_arg":"4","tx_depositNonce_arg":"2559","tx_resourceID_arg":"0x0000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c01","tx_data_amount":"15000000000000000000000","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_from":"0xD33966215C372935858DB3C4749dFb62718D0554","tx_to":"0xF41e7FC4eC990298d36f667B93951c9dba65224e","tx_value":"0","tx_fee_movr":"0.000381332","tx_fee_wei":"381332000000000"}
```

## CCTX 3
### Source

```
id = AUTOINCREMENT

bridge = Meter
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x63f37aff7e40b85b0a6b3fd414389f6011cc09b276dc8e13b6afa19061f7ed8e
cctx_id =
block_number = 14992190
timestamp = 1644070960
log_index = 335

event_type = Deposit

correlation_id = 1

src_blockchain = BNB
dst_blockchain = BNB

actor_from = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
actor_to = NULL
signer = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
relayer = NULL

token_in = 0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C
token_out = NULL
amount_in = NULL
amount_out = NULL

nonce = 1
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","topic0":"0xdbb69440df8433824a026ef190652f29929eb64b4d1d5d2a69be8afe3e6eaed8","destinationChainID_event_topic":"44","destinationChainID_input":"4","resourceID":"0x0000000000000000000000BB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C01","depositNonce_event_topic":"11","tx_data_amount":"3632795971816270126503","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_value":"8000000000000000","tx_fee":"1221605000000000"}
```

### Destination

```
id = AUTOINCREMENT

bridge = Meter
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xf70b4aa715c0a04079c56cd9036cc63cdb6101e400520a8f2c019ad2ced5358e
cctx_id =
block_number = 14992203
timestamp = 1644070999
log_index = NULL

event_type = InternalTransfer

correlation_id = 1

src_blockchain = BNB
dst_blockchain = BNB

actor_from = 0x5945241B772F400F537E21F1EF717C4C09AC3D51
actor_to = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
signer =
relayer = 0xD33966215C372935858DB3C4749dFb62718D0554

token_in = NULL
token_out = native:BNB
amount_in = NULL
amount_out = 3632795971816270126503

nonce = 1
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
status = success

extra_data = {"event_source":"BscScan internal transaction, not EVM log","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_chainID_arg":"4","tx_depositNonce_arg":"1","tx_resourceID_arg":"0x0000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c01","tx_data_amount":"3632795971816270126503","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","reason":"source caller is attacker, destination internal tx transfer is attacker"}
```

```
id = AUTOINCREMENT

bridge = Meter
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xf70b4aa715c0a04079c56cd9036cc63cdb6101e400520a8f2c019ad2ced5358e
cctx_id =
block_number = 14992203
timestamp = 1644070999
log_index = 163

event_type = ProposalEvent

correlation_id = 1

src_blockchain = BNB
dst_blockchain = BNB

actor_from = 0xD33966215C372935858DB3C4749dFb62718D0554
actor_to = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
signer =
relayer = 0xD33966215C372935858DB3C4749dFb62718D0554

token_in = NULL
token_out = 0xBB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C
amount_in = NULL
amount_out = NULL

nonce = 1
message_id = NULL
message_hash = 0x2F2A977CCA4FD1E6F8B8861228E6E3581EF5BC22ABEE28BE98F6840CF93D9648
payload_hash = 0x2F2A977CCA4FD1E6F8B8861228E6E3581EF5BC22ABEE28BE98F6840CF93D9648
proof_hash = NULL
guid = NULL

contract_address = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
status = 3

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","topic0":"0x803c5a12f6bde629cea32e63d4b92d1b560816a6fb72e939d3c89e1cab650417","originChainID":"4","depositNonce":"1","proposal_status":"3","resourceID":"0x0000000000000000000000BB4CDB9CBD36B01BD1CBAEBF2DE08D9173BC095C01","dataHash":"0x2F2A977CCA4FD1E6F8B8861228E6E3581EF5BC22ABEE28BE98F6840CF93D9648","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_chainID_arg":"4","tx_depositNonce_arg":"1","tx_resourceID_arg":"0x0000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c01","tx_data_amount":"3632795971816270126503","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01"}
```

## CCTX 4
### Source

```
id = AUTOINCREMENT

bridge = Meter
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xc4d7e160c7652f2db22681aa2777c5b37937bf30375c5b2c6b2bd172ae984950
cctx_id =
block_number = 14990769
timestamp = 1644066697
log_index = 439

event_type = Deposit

correlation_id = 3484

src_blockchain = BNB
dst_blockchain = Meter

actor_from = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
actor_to = NULL
signer = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
relayer = NULL

token_in = 0xBD2949F67DCDc549c6Ebe98696449Fa79D988A9F
token_out = NULL
amount_in = NULL
amount_out = NULL

nonce = 3484
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xFd55eBc7bBde603A048648C6eAb8775c997C1001
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","topic0":"0xdbb69440df8433824a026ef190652f29929eb64b4d1d5d2a69be8afe3e6eaed8","destinationChainID_input":"3","resourceID":"0x0000000000000000000000bd2949f67dcdc549c6ebe98696449fa79d988a9f01","tx_data_amount":"136099263357745292326","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_value":"8000000000000000","tx_fee":"120276000000000","note":"destination Meter transaction not identified"}
```

### Destination

```
UNKNOWN
```

## CCTX 5
### Source

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x2d3987963b77159cfe4f820532d729b0364c7f05511f23547765c75b110b629c
cctx_id =
block_number = 14146530
timestamp = 1644071232
log_index = 217

event_type = Deposit

correlation_id = 1

src_blockchain = Ethereum
dst_blockchain = Ethereum

actor_from = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
actor_to = NULL
signer = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
relayer = NULL

token_in = 0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2
token_out = NULL
amount_in = NULL
amount_out = NULL

nonce = 1
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xa2A22B46B8df38cd7C55E6bf32Ea5a32637Cf2b1
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","topic0":"0xdbb69440df8433824a026ef190652f29929eb64b4d1d5d2a69be8afe3e6eaed8","destinationChainID_input":"1","resourceID":"0x0000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc201","tx_data_amount":"422508708639363167140","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_value_eth":"0.005","tx_fee_eth":"0.010902466510126471"}
```

### Destination

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xd619ace8a8cca2f7eb72dbc0a896fc2d4d8b20aa11f4d747f1a5333305bbb875
cctx_id =
block_number = 14146583
timestamp = 1644071846
log_index = 0

event_type = Transfer

correlation_id = 1

src_blockchain = Ethereum
dst_blockchain = Ethereum

actor_from = UNKNOWN
actor_to = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
signer =
relayer = 0xD33966215C372935858DB3C4749dFb62718D0554

token_in = NULL
token_out = 0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2
amount_in = NULL
amount_out = 422508708639363167140

nonce = 1
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","token_symbol":"WETH","value":"422508708639363167140","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_chainID_arg":"1","tx_depositNonce_arg":"1","tx_resourceID_arg":"0x0000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc201","tx_data_amount":"422508708639363167140","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_from":"0xD33966215C372935858DB3C4749dFb62718D0554","tx_to":"0xa2A22B46B8df38cd7C55E6bf32Ea5a32637Cf2b1","tx_value":"0","tx_fee_eth":"0.00274110353947332","note":"actor_from not confirmed from scanner text"}
```

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xd619ace8a8cca2f7eb72dbc0a896fc2d4d8b20aa11f4d747f1a5333305bbb875
cctx_id =
block_number = 14146583
timestamp = 1644071846
log_index = 1

event_type = ProposalEvent

correlation_id = 1

src_blockchain = Ethereum
dst_blockchain = Ethereum

actor_from = 0xD33966215C372935858DB3C4749dFb62718D0554
actor_to = 0xa2A22B46B8df38cd7C55E6bf32Ea5a32637Cf2b1
signer =
relayer = 0xD33966215C372935858DB3C4749dFb62718D0554

token_in = NULL
token_out = 0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2
amount_in = NULL
amount_out = NULL

nonce = 1
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xa2A22B46B8df38cd7C55E6bf32Ea5a32637Cf2b1
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"executeProposal(uint8 chainID, uint64 depositNonce, bytes data, bytes32 resourceID)","tx_chainID_arg":"1","tx_depositNonce_arg":"1","tx_resourceID_arg":"0x0000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc201","tx_data_amount":"422508708639363167140","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","note":"message_hash/payload_hash not confirmed from scanner text"}
```

## CCTX 6
### Source

```
id = AUTOINCREMENT

bridge = Meter
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xdfea6413c7eb3068093dcbbe65bcc9ba635e227c35e57fe482bb5923c89e31f7
cctx_id =
block_number = 14146589
timestamp = 1644071981
log_index = 314

event_type = Deposit

correlation_id = 546

src_blockchain = Ethereum
dst_blockchain = Meter

actor_from = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
actor_to = NULL
signer = 0x8d3d13cac607B7297Ff61A5E1E71072758AF4D01
relayer = NULL

token_in = 0xC02aaa39b223FE8D0A0e5C4F27eAD9083C756Cc2
token_out = NULL
amount_in = NULL
amount_out = NULL

nonce = 546
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0xa2A22B46B8df38cd7C55E6bf32Ea5a32637Cf2b1
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","topic0":"0xdbb69440df8433824a026ef190652f29929eb64b4d1d5d2a69be8afe3e6eaed8","destinationChainID_input":"3","resourceID":"0x0000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc201","tx_data_amount":"1500000000000000000000","tx_data_recipient":"0x8d3d13cac607b7297ff61a5e1e71072758af4d01","tx_value_eth":"0.001","tx_fee_eth":"0.010018764605905928","note":"destination Meter transaction not identified"}
```

### Destination

```
UNKNOWN
```

# Qubit Bridge
## CCTX 1
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x60227798c91b76cca3ce5b21ebcbb89cf8da341a77d7b2938e1a913e996f0bd8
cctx_id =
block_number = 13840636
timestamp = 1639984426
log_index = 254

event_type = Deposit

correlation_id = 73

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xa1Eb8C3Ab52582957f949E5eaA824485d0DCFe10
actor_to = NULL
signer = 0xa1Eb8C3Ab52582957f949E5eaA824485d0DCFe10
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 1000000000000000
amount_out = NULL

nonce = 73
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"False","semantic_status":"legitimate_deposit","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x4e2d8f3f8d519dec01b9a7c36cf220441b6756cd605af3cd481048da9b1a6cfe
cctx_id =
block_number = 13633900
timestamp = 1639984595
log_index = 540

event_type = Transfer

correlation_id = 73

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 1000000000000000

nonce = 73
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"1000000000000000","token_symbol":"qXETH/xETH","attack":"False","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x4e2d8f3f8d519dec01b9a7c36cf220441b6756cd605af3cd481048da9b1a6cfe
cctx_id =
block_number = 13633900
timestamp = 1639984595
log_index = 537

event_type = ProposalEvent

correlation_id = 73

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 73
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"73","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"1000000000000000","attack":"False","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 2
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x7f537463d055f32b49050a7e2179461666a9494deb7045d7825d72c210168298
cctx_id =
block_number = 14090105
timestamp = 1643318381
log_index = 684

event_type = Deposit

correlation_id = 84

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xD01Ae1A708614948B2B5e0B7AB5be6AFA01325c7
actor_to = NULL
signer = 0xD01Ae1A708614948B2B5e0B7AB5be6AFA01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 100000000000000000
amount_out = NULL

nonce = 84
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"False","semantic_status":"legitimate_deposit","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x8c5877d1b618f29f6a3622cb610ace08ca96e04d8218f587072a3f91e8545bdc
cctx_id =
block_number = 14741733
timestamp = 1643318520
log_index = 406

event_type = Transfer

correlation_id = 84

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 100000000000000000

nonce = 84
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"100000000000000000","token_symbol":"qXETH/xETH","attack":"False","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x8c5877d1b618f29f6a3622cb610ace08ca96e04d8218f587072a3f91e8545bdc
cctx_id =
block_number = 14741733
timestamp = 1643318520
log_index = 403

event_type = ProposalEvent

correlation_id = 84

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 84
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"84","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"100000000000000000","attack":"False","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 3
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xff6fa990d4f6cf85592f7fb32840539e6dad20fda4e547acb1a4bbb969d99ba9
cctx_id =
block_number = 14090126
timestamp = 1643318632
log_index = 51

event_type = Deposit

correlation_id = 85

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xD01Ae1A708614948B2B5e0B7AB5be6AFA01325c7
actor_to = NULL
signer = 0xD01Ae1A708614948B2B5e0B7AB5be6AFA01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 100000000000000000
amount_out = NULL

nonce = 85
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"False","semantic_status":"legitimate_deposit","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x881a68c9c9aa36590e41dc65ca260decdce7d18dff365067cb592d3a8d0733ef
cctx_id =
block_number = 14741827
timestamp = 1643318802
log_index = 137

event_type = Transfer

correlation_id = 85

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 100000000000000000

nonce = 85
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"100000000000000000","token_symbol":"qXETH/xETH","attack":"False","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x881a68c9c9aa36590e41dc65ca260decdce7d18dff365067cb592d3a8d0733ef
cctx_id =
block_number = 14741827
timestamp = 1643318802
log_index = 134

event_type = ProposalEvent

correlation_id = 85

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 85
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"85","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"100000000000000000","attack":"False","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 4
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xac7292e7d0ec8ebe1c94203d190874b2aab30592327b6cc875d00f18de6f3133
cctx_id =
block_number = 14090170
timestamp = 1643319241
log_index = 3

event_type = Deposit

correlation_id = 86

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 190000000000000000000
amount_out = NULL

nonce = 86
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x61ca8bc28f5b2ee87f9a10c3d8fff790658e345a1e407f9e5c3f22b48106ccff
cctx_id =
block_number = 14742022
timestamp = 1643319392
log_index = 149

event_type = Transfer

correlation_id = 86

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 190000000000000000000

nonce = 86
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"190000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x61ca8bc28f5b2ee87f9a10c3d8fff790658e345a1e407f9e5c3f22b48106ccff
cctx_id =
block_number = 14742022
timestamp = 1643319392
log_index = 146

event_type = ProposalEvent

correlation_id = 86

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 86
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"86","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"190000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 5
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xc7e964fa3b0e8d2df6d92d96e57d7eb6cebf7ca581807cab96d4f3aafa98ba12
cctx_id =
block_number = 14090187
timestamp = 1643319489
log_index = 127

event_type = Deposit

correlation_id = 87

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 499000000000000000000
amount_out = NULL

nonce = 87
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xf6008ab482538669f9a8431bfd42e0b45c7253797425707f0edeef57690a4dbe
cctx_id =
block_number = 14742132
timestamp = 1643319722
log_index = 54

event_type = Transfer

correlation_id = 87

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 499000000000000000000

nonce = 87
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"499000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xf6008ab482538669f9a8431bfd42e0b45c7253797425707f0edeef57690a4dbe
cctx_id =
block_number = 14742132
timestamp = 1643319722
log_index = 51

event_type = ProposalEvent

correlation_id = 87

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 87
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"87","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"499000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 6
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x006a8a6e58e26384aa7dd7951d57f51136049601a772a40fcde34722191ed3f8
cctx_id =
block_number = 14090190
timestamp = 1643319547
log_index = 82

event_type = Deposit

correlation_id = 88

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 999000000000000000000
amount_out = NULL

nonce = 88
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xd8bba1555568280325ef6c9552fb5c7646692c17a42f7ff69b5f82bbd78d2d86
cctx_id =
block_number = 14742148
timestamp = 1643319770
log_index = 623

event_type = Transfer

correlation_id = 88

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 999000000000000000000

nonce = 88
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"999000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xd8bba1555568280325ef6c9552fb5c7646692c17a42f7ff69b5f82bbd78d2d86
cctx_id =
block_number = 14742148
timestamp = 1643319770
log_index = 620

event_type = ProposalEvent

correlation_id = 88

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 88
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"88","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"999000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 7
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x6f24d176e178f80e15daa4a2c03106404584be6469a29077defd2c9e788e58c4
cctx_id =
block_number = 14090195
timestamp = 1643319678
log_index = 359

event_type = Deposit

correlation_id = 89

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 999000000000000000000
amount_out = NULL

nonce = 89
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xa961a639fc91f7d8d0ffc2bc6f05d3cee292e4249e8a1539bd84785763b930a8
cctx_id =
block_number = 14742171
timestamp = 1643319839
log_index = 381

event_type = Transfer

correlation_id = 89

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 999000000000000000000

nonce = 89
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"999000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xa961a639fc91f7d8d0ffc2bc6f05d3cee292e4249e8a1539bd84785763b930a8
cctx_id =
block_number = 14742171
timestamp = 1643319839
log_index = 378

event_type = ProposalEvent

correlation_id = 89

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 89
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"89","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"999000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 8
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xf56fe06b0e7af7ef393fe0fa15aa173891940f800c3ac14db7a81c62ebad9663
cctx_id =
block_number = 14090195
timestamp = 1643319678
log_index = 360

event_type = Deposit

correlation_id = 90

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 999000000000000000000
amount_out = NULL

nonce = 90
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xa32713ffc0337b59ff0bb0e342336ddc1d447ca8c3ff508cbebbd7271d7a3410
cctx_id =
block_number = 14742187
timestamp = 1643319887
log_index = 173

event_type = Transfer

correlation_id = 90

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 999000000000000000000

nonce = 90
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"999000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xa32713ffc0337b59ff0bb0e342336ddc1d447ca8c3ff508cbebbd7271d7a3410
cctx_id =
block_number = 14742187
timestamp = 1643319887
log_index = 170

event_type = ProposalEvent

correlation_id = 90

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 90
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"90","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"999000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 9
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xb9c5e0ed27bbb5237a6fa4549784ba740059253f57453a8c4cf1f80f71b09cf5
cctx_id =
block_number = 14090195
timestamp = 1643319678
log_index = 361

event_type = Deposit

correlation_id = 91

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 999000000000000000000
amount_out = NULL

nonce = 91
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xdc4206b67c5b6fb501b1727741bf67acd033030d022fe20eb5614bf38da48207
cctx_id =
block_number = 14742202
timestamp = 1643319932
log_index = 386

event_type = Transfer

correlation_id = 91

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 999000000000000000000

nonce = 91
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"999000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xdc4206b67c5b6fb501b1727741bf67acd033030d022fe20eb5614bf38da48207
cctx_id =
block_number = 14742202
timestamp = 1643319932
log_index = 383

event_type = ProposalEvent

correlation_id = 91

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 91
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"91","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"999000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 10
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x478d83f2ad909c64a9a3d807b3d8399bb67a997f9721fc5580ae2c51fab92acf
cctx_id =
block_number = 14090197
timestamp = 1643319691
log_index = 115

event_type = Deposit

correlation_id = 92

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 199000000000000000000
amount_out = NULL

nonce = 92
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x38692d17fdc9c3da9c1cb234108d78011b086235ce5da2220675a2cf05393cc8
cctx_id =
block_number = 14742218
timestamp = 1643319980
log_index = 367

event_type = Transfer

correlation_id = 92

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 199000000000000000000

nonce = 92
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"199000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x38692d17fdc9c3da9c1cb234108d78011b086235ce5da2220675a2cf05393cc8
cctx_id =
block_number = 14742218
timestamp = 1643319980
log_index = 364

event_type = ProposalEvent

correlation_id = 92

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 92
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"92","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"199000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 11
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xd0d86c51770877c80edb018d2c69ed23ca834694e3ca43159a9b9b889ac4ad4d
cctx_id =
block_number = 14090198
timestamp = 1643319699
log_index = 70

event_type = Deposit

correlation_id = 93

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 199000000000000000000
amount_out = NULL

nonce = 93
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x63ed93293f85a11a00e16e29a55e41631e8da8d0f638c185eda48a9606f836c5
cctx_id =
block_number = 14742234
timestamp = 1643320028
log_index = 1227

event_type = Transfer

correlation_id = 93

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 199000000000000000000

nonce = 93
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"199000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x63ed93293f85a11a00e16e29a55e41631e8da8d0f638c185eda48a9606f836c5
cctx_id =
block_number = 14742234
timestamp = 1643320028
log_index = 1224

event_type = ProposalEvent

correlation_id = 93

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 93
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"93","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"199000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 12
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xeb9f622e54253b3fa14dcee243bc9345a8fbc562168e973093ffc86d7f8a5829
cctx_id =
block_number = 14090201
timestamp = 1643319716
log_index = 88

event_type = Deposit

correlation_id = 94

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 199000000000000000000
amount_out = NULL

nonce = 94
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x67337d605bb144ec8acab51e7fc1f3c75927e1e1bedc01addb118fb11fbefb36
cctx_id =
block_number = 14742250
timestamp = 1643320076
log_index = 385

event_type = Transfer

correlation_id = 94

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 199000000000000000000

nonce = 94
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"199000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x67337d605bb144ec8acab51e7fc1f3c75927e1e1bedc01addb118fb11fbefb36
cctx_id =
block_number = 14742250
timestamp = 1643320076
log_index = 382

event_type = ProposalEvent

correlation_id = 94

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 94
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"94","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"199000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 13
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xbdedb13d78bcb2f4eb48241c0ed0b299264458021d6e8f331e08a1c9bd96f943
cctx_id =
block_number = 14090210
timestamp = 1643319860
log_index = 88

event_type = Deposit

correlation_id = 95

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 5990000000000000000000
amount_out = NULL

nonce = 95
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xea23aed9096b6e6248d3c55b822b0b30c25efa3f984a2c36c6e30b36a2e45d4f
cctx_id =
block_number = 14742267
timestamp = 1643320127
log_index = 246

event_type = Transfer

correlation_id = 95

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 5990000000000000000000

nonce = 95
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"5990000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xea23aed9096b6e6248d3c55b822b0b30c25efa3f984a2c36c6e30b36a2e45d4f
cctx_id =
block_number = 14742267
timestamp = 1643320127
log_index = 243

event_type = ProposalEvent

correlation_id = 95

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 95
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"95","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"5990000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 14
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x940315691510a8f6b2690d3df4608ae1dd710c665bc76e40954fa8092a5fc541
cctx_id =
block_number = 14090216
timestamp = 1643319932
log_index = 461

event_type = Deposit

correlation_id = 96

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 5990000000000000000000
amount_out = NULL

nonce = 96
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x2ce666d0ec8c976f6895b1ac52f648b5f5e025c42a956c767bf4fbae0982819e
cctx_id =
block_number = 14742285
timestamp = 1643320181
log_index = 239

event_type = Transfer

correlation_id = 96

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 5990000000000000000000

nonce = 96
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"5990000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x2ce666d0ec8c976f6895b1ac52f648b5f5e025c42a956c767bf4fbae0982819e
cctx_id =
block_number = 14742285
timestamp = 1643320181
log_index = 236

event_type = ProposalEvent

correlation_id = 96

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 96
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"96","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"5990000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 15
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0xa6282e604eab18390be3abf2f4f0039dbdbcc3f4cf15e4d3ade296b8684a0486
cctx_id =
block_number = 14090223
timestamp = 1643320073
log_index = 229

event_type = Deposit

correlation_id = 97

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 59900000000000000000000
amount_out = NULL

nonce = 97
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x50946e3e4ccb7d39f3512b7ecb75df66e6868b9af0eee8a7e4b61ef8a459518e
cctx_id =
block_number = 14742312
timestamp = 1643320262
log_index = 372

event_type = Transfer

correlation_id = 97

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 59900000000000000000000

nonce = 97
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"59900000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x50946e3e4ccb7d39f3512b7ecb75df66e6868b9af0eee8a7e4b61ef8a459518e
cctx_id =
block_number = 14742312
timestamp = 1643320262
log_index = 369

event_type = ProposalEvent

correlation_id = 97

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 97
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"97","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"59900000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 16
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x501f8541dc7cc594cd0ee245c8710ca12084529b596a3fc0d702f4a77f70b848
cctx_id =
block_number = 14090230
timestamp = 1643320175
log_index = 279

event_type = Deposit

correlation_id = 98

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 59900000000000000000000
amount_out = NULL

nonce = 98
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x8f5bdea436d944432fcc11dab2ad43dc600d6a9f7083e56af17bcea8b2a2dde2
cctx_id =
block_number = 14742505
timestamp = 1643320844
log_index = 1326

event_type = Transfer

correlation_id = 98

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 59900000000000000000000

nonce = 98
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"59900000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x8f5bdea436d944432fcc11dab2ad43dc600d6a9f7083e56af17bcea8b2a2dde2
cctx_id =
block_number = 14742505
timestamp = 1643320844
log_index = 1332

event_type = ProposalEvent

correlation_id = 98

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 98
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"98","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"59900000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 17
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x580206541ab2916d2ef9b89e5bf6e833031700d01f2ea372ec0bec331f38225b
cctx_id =
block_number = 14090230
timestamp = 1643320175
log_index = 451

event_type = Deposit

correlation_id = 99

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 59900000000000000000000
amount_out = NULL

nonce = 99
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xff162a19a69614a8dc1630ed437a974725c3a40e6b6ed3f626663c051c946753
cctx_id =
block_number = 14742511
timestamp = 1643320862
log_index = 1895

event_type = Transfer

correlation_id = 99

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 59900000000000000000000

nonce = 99
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"59900000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0xff162a19a69614a8dc1630ed437a974725c3a40e6b6ed3f626663c051c946753
cctx_id =
block_number = 14742511
timestamp = 1643320862
log_index = 1892

event_type = ProposalEvent

correlation_id = 99

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 99
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"99","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"59900000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 18
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x3dfa33b5c6150bf3d64f49cb97eba351f99e4dff7119ef458e40f51160bf77ec
cctx_id =
block_number = 14090234
timestamp = 1643320241
log_index = 333

event_type = Deposit

correlation_id = 100

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 9999000000000000000000
amount_out = NULL

nonce = 100
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x33628dcc2ca6cd89a96d241bdf17cdc8785cf4322dcaf2c79766c990579aea02
cctx_id =
block_number = 14742533
timestamp = 1643320928
log_index = 1971

event_type = Transfer

correlation_id = 100

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 9999000000000000000000

nonce = 100
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"9999000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x33628dcc2ca6cd89a96d241bdf17cdc8785cf4322dcaf2c79766c990579aea02
cctx_id =
block_number = 14742533
timestamp = 1643320928
log_index = 1968

event_type = ProposalEvent

correlation_id = 100

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 100
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"100","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"9999000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
## CCTX 19
### Source

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = Ethereum
raw_table =
raw_pk =

transaction_hash = 0x9cf9e457aade4a0421eb188cfb5d17694c614c139b1fa0122930d5df27228349
cctx_id =
block_number = 14090234
timestamp = 1643320241
log_index = 379

event_type = Deposit

correlation_id = 101

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
actor_to = NULL
signer = 0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7
relayer = NULL

token_in = 0x0000000000000000000000000000000000000000
token_out = NULL
amount_in = 9999000000000000000000
amount_out = NULL

nonce = 101
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6
status = success

extra_data = {"event_signature":"Deposit(uint8,bytes32,uint64)","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","tokenAddress_resolved":"0x0000000000000000000000000000000000000000","tx_function":"deposit(uint8 destinationDomainID, bytes32 resourceID, bytes data)","attack":"True","semantic_status":"fake_deposit_no_assets_locked","note":"Qubit/QBridge: Deposit event accepted by relayer; for attack=True no real ETH/ERC20 was locked because transferFrom to zero address/EOA did not revert."}
```

### Destination

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x490336f417c9569843d74363ca8d943d1d2674325a43560408d728638d7bcdb5
cctx_id =
block_number = 14742619
timestamp = 1643321192
log_index = 1494

event_type = Transfer

correlation_id = 101

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0x0000000000000000000000000000000000000000
actor_to = 0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
amount_in = NULL
amount_out = 9999000000000000000000

nonce = 101
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f
status = success

extra_data = {"event_signature":"Transfer(address,address,uint256)","from":"0x0000000000000000000000000000000000000000","to":"0xA6b1bb565E33B54AC58b4640237Fdc91D87d3b61","value":"9999000000000000000000","token_symbol":"qXETH/xETH","attack":"True","note":"Destination-side mint inferred from Qubit qXETH minting flow; token contract/log_index confirmed from BscScan logs; mint recipient is the first Transfer.to address."}
```

```
id = AUTOINCREMENT

bridge = Qubit
blockchain = BNB
raw_table =
raw_pk =

transaction_hash = 0x490336f417c9569843d74363ca8d943d1d2674325a43560408d728638d7bcdb5
cctx_id =
block_number = 14742619
timestamp = 1643321192
log_index = 1491

event_type = ProposalEvent

correlation_id = 101

src_blockchain = Ethereum
dst_blockchain = BNB

actor_from = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545
actor_to = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
signer =
relayer = 0xEB645B4c35cf160e47F0A49c03DB087c421AB545

token_in = NULL
token_out = 0x0000000000000000000000000000000000000000
amount_in = NULL
amount_out = NULL

nonce = 101
message_id = NULL
message_hash = NULL
payload_hash = NULL
proof_hash = NULL
guid = NULL

contract_address = 0x4d8aE68fCAe98Bf93299548545933c0D273BA23a
status = success

extra_data = {"event_signature":"ProposalEvent(uint8,uint64,uint8,bytes32,bytes32)","tx_function":"voteProposal(uint8 originDomainID, uint64 depositNonce, bytes32 resourceID, bytes data)","originDomainID":"Ethereum","depositNonce":"101","resourceID":"0x0000000000000000000000002f422fe9ea622049d6f73f81a906b9b8cff03b7f01","amount":"9999000000000000000000","attack":"True","handler_bsc":"0x4d8ae68fcae98bf93299548545933c0d273ba23a","note":"Qubit wiki confirms voteProposal on BSC was called by relayer after observing Ethereum Deposit event; BSC QBridge contract/log fields confirmed from BscScan."}
```
