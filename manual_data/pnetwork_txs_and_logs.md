# pNetwork pBTC-on-BSC attack transactions and logs

Source: pNetwork post-mortem, "pNetwork post-mortem pBTC-on-BSC exploit"  
URL: https://medium.com/pnetwork/pnetwork-post-mortem-pbtc-on-bsc-exploit-170890c58d5f

The attacker created contracts on BSC that emitted `Redeem` logs compatible with
the pNetwork off-chain listener. The legitimate pBTC token contract emitted a
zero-value peg-out request, while the attacker-created contracts emitted
faulty non-zero `Redeem` events. Because of a Rust log extraction bug, these
faulty logs were accepted and processed.

Attacker: `0x2bf5693dd3a5cea1139c4510fdce120cf042c934`  
Legitimate pBTC-on-BSC token contract: `0xed28a457a5a76596ac48d87c0f577020f6ea1c4c`  
Bitcoin recipient observed in the exploit logs: `3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky`

This file keeps the attack-relevant logs. The second and third transactions
emit many repeated malicious `Redeem` logs; the curated entries below preserve
the invariant needed by the detector: non-zero `Redeem` emitted by an
attacker-created contract instead of the pBTC token contract.

## Bitcoin counterparts

These BSC transactions are peg-out/redeem source-side transactions. The
destination side is Bitcoin, where pNetwork released BTC to the recipient
addresses encoded in the `Redeem` logs.

The Bitcoin counterparts below were matched by:

- the Bitcoin recipient address present in the BSC `Redeem` log;
- the Bitcoin transaction timestamp, shortly after the BSC transaction;
- the output value, which is consistently about `99.75%` of the BSC redeem
  amount, suggesting a `0.25%` operational fee/retention.

| BSC attack tx | BSC redeem amount | Bitcoin counterpart | Bitcoin output | Bitcoin timestamp |
|---|---:|---|---:|---|
| `0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551` | `0.276945556038761144 BTC` | `a1d874153a7c245b1387289c49cb8843a3666fd92df418ad2756351d3f47de0c` | `0.27625319 BTC` to `3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky` | `2021-09-19 17:22:03 UTC` |
| `0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab` | `1.384727780193805721 BTC` per malicious redeem | `0c83bcd3162517760e2869750e9c1b546ca07069195e002cf076d5db84992e0b` | `100` outputs of `1.38126597 BTC` | `2021-09-19 17:35:24 UTC` |
| `0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6` | `1.377838587257518130 BTC` per malicious redeem | `660c4b6856ecc7726391dd8263da1cf09cef732200ddac835e480209f9b58251` | `100` outputs of `1.37439399 BTC` | `2021-09-19 17:42:08 UTC` |

The first Bitcoin transaction is a direct payout to
`3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky`. The second and third are batch payouts:
each has `101` outputs, of which `100` are recipient outputs and the remaining
output appears to be change back to `1JyQu3czAAkQLzQVFE4tkpCuGiYrHMvGWj`.

## CCTX 1

```python
BlockchainTransaction(
    cctx_id = "pnetwork:cctx_1",
    blockchain = "bsc",
    transaction_hash = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551",
    block_number = 11056047,
    timestamp = 1632072029,
    from_address = "0x2bf5693dd3a5cea1139c4510fdce120cf042c934",
    to_address = None,
    status = 1,
    value = 0,
    input_data = None,
    calls = {"type": "CREATE", "from": "0x2bf5693dd3a5cea1139c4510fdce120cf042c934", "to": "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6", "value": "0x0", "gasUsed": "0x14d1a", "calls": [{"type": "SELFDESTRUCT", "from": "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6"}], "extra_data": {"trace_source": "receipt_inferred", "receipt_contract_address": "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6", "post_transaction_code": "0x"}},
    fee = 1705480000000000
)
```

```python
BlockchainTransaction(
    cctx_id = "pnetwork:cctx_1",
    blockchain = "bitcoin",
    transaction_hash = "a1d874153a7c245b1387289c49cb8843a3666fd92df418ad2756351d3f47de0c",
    block_number = 701293,
    timestamp = 1632072123,
    from_address = "1JyQu3czAAkQLzQVFE4tkpCuGiYrHMvGWj",
    to_address = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    status = 1,
    value = 27625319,
    input_data = None,
    calls = None,
    fee = 35280
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_1:burned:0",
    transaction_hash = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551",
    cctx_id = "pnetwork:cctx_1",
    event_type = "Burned",
    block_number = 11056047,
    timestamp = 1632072029,
    log_index = 0,
    correlation_id = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551:0",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6",
    actor_to = "0x0000000000000000000000000000000000000000",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Burned\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_1:transfer:1",
    transaction_hash = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551",
    cctx_id = "pnetwork:cctx_1",
    event_type = "Transfer",
    block_number = 11056047,
    timestamp = 1632072029,
    log_index = 1,
    correlation_id = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551:1",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6",
    actor_to = "0x0000000000000000000000000000000000000000",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Transfer\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_1:redeem-legit:2",
    transaction_hash = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551",
    cctx_id = "pnetwork:cctx_1",
    event_type = "Redeem",
    block_number = 11056047,
    timestamp = 1632072029,
    log_index = 2,
    correlation_id = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551:2",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6",
    actor_to = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Redeem\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_1:redeem-attack:3",
    transaction_hash = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551",
    cctx_id = "pnetwork:cctx_1",
    event_type = "Redeem",
    block_number = 11056047,
    timestamp = 1632072029,
    log_index = 3,
    correlation_id = "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551:3",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6",
    actor_to = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 276945556038761144,
    amount_out = None,
    contract_address = "0xe569bf0e2593dd8966ee2f02d2c7865182fcfee6",
    status = "1",
    extra_data = "{\"event\":\"Redeem\",\"is_faulty\":true,\"reason\":\"Redeem emitted by attacker-created contract\"}"
)
```

## CCTX 2

```python
BlockchainTransaction(
    cctx_id = "pnetwork:cctx_2",
    blockchain = "bsc",
    transaction_hash = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6",
    block_number = 11056387,
    timestamp = 1632073052,
    from_address = "0x2bf5693dd3a5cea1139c4510fdce120cf042c934",
    to_address = None,
    status = 1,
    value = 0,
    input_data = None,
    calls = {"type": "CREATE", "from": "0x2bf5693dd3a5cea1139c4510fdce120cf042c934", "to": "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0", "value": "0x0", "gasUsed": "0x9d6f4", "calls": [{"type": "SELFDESTRUCT", "from": "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0"}], "extra_data": {"trace_source": "receipt_inferred", "receipt_contract_address": "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0", "post_transaction_code": "0x"}},
    fee = 12897040000000000
)
```

```python
BlockchainTransaction(
    cctx_id = "pnetwork:cctx_2",
    blockchain = "bitcoin",
    transaction_hash = "660c4b6856ecc7726391dd8263da1cf09cef732200ddac835e480209f9b58251",
    block_number = 701297,
    timestamp = 1632073328,
    from_address = "multiple",
    to_address = "multiple",
    status = 1,
    value = 13743939900,
    input_data = None,
    calls = None,
    fee = 1279200
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_2:burned:0",
    transaction_hash = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6",
    cctx_id = "pnetwork:cctx_2",
    event_type = "Burned",
    block_number = 11056387,
    timestamp = 1632073052,
    log_index = 0,
    correlation_id = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6:0",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0",
    actor_to = "0x0000000000000000000000000000000000000000",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Burned\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_2:transfer:1",
    transaction_hash = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6",
    cctx_id = "pnetwork:cctx_2",
    event_type = "Transfer",
    block_number = 11056387,
    timestamp = 1632073052,
    log_index = 1,
    correlation_id = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6:1",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0",
    actor_to = "0x0000000000000000000000000000000000000000",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Transfer\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_2:redeem-legit:2",
    transaction_hash = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6",
    cctx_id = "pnetwork:cctx_2",
    event_type = "Redeem",
    block_number = 11056387,
    timestamp = 1632073052,
    log_index = 2,
    correlation_id = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6:2",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0",
    actor_to = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Redeem\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_2:redeem-attack",
    transaction_hash = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6",
    cctx_id = "pnetwork:cctx_2",
    event_type = "Redeem",
    block_number = 11056387,
    timestamp = 1632073052,
    log_index = 4,
    correlation_id = "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6:4",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0",
    actor_to = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 1377838587257518130,
    amount_out = None,
    contract_address = "0xe7bd71d3f0f68ca90d85a63fd89e041657dc99b0",
    status = "1",
    extra_data = "{\"event\":\"Redeem\",\"is_faulty\":true,\"reason\":\"Redeem emitted by attacker-created contract\",\"repeated_faulty_logs_in_receipt\":true,\"repeated_faulty_log_count\":100}"
)
```

## CCTX 3

```python
BlockchainTransaction(
    cctx_id = "pnetwork:cctx_3",
    blockchain = "bsc",
    transaction_hash = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab",
    block_number = 11056315,
    timestamp = 1632072836,
    from_address = "0x2bf5693dd3a5cea1139c4510fdce120cf042c934",
    to_address = None,
    status = 1,
    value = 0,
    input_data = None,
    calls = {"type": "CREATE", "from": "0x2bf5693dd3a5cea1139c4510fdce120cf042c934", "to": "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d", "value": "0x0", "gasUsed": "0x9d6f4", "calls": [{"type": "SELFDESTRUCT", "from": "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d"}], "extra_data": {"trace_source": "receipt_inferred", "receipt_contract_address": "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d", "post_transaction_code": "0x"}},
    fee = 12897040000000000
)
```

```python
BlockchainTransaction(
    cctx_id = "pnetwork:cctx_3",
    blockchain = "bitcoin",
    transaction_hash = "0c83bcd3162517760e2869750e9c1b546ca07069195e002cf076d5db84992e0b",
    block_number = 701295,
    timestamp = 1632072924,
    from_address = "multiple",
    to_address = "multiple",
    status = 1,
    value = 13812659700,
    input_data = None,
    calls = None,
    fee = 919200
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_3:burned:0",
    transaction_hash = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab",
    cctx_id = "pnetwork:cctx_3",
    event_type = "Burned",
    block_number = 11056315,
    timestamp = 1632072836,
    log_index = 0,
    correlation_id = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab:0",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d",
    actor_to = "0x0000000000000000000000000000000000000000",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Burned\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_3:transfer:1",
    transaction_hash = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab",
    cctx_id = "pnetwork:cctx_3",
    event_type = "Transfer",
    block_number = 11056315,
    timestamp = 1632072836,
    log_index = 1,
    correlation_id = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab:1",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d",
    actor_to = "0x0000000000000000000000000000000000000000",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Transfer\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_3:redeem-legit:2",
    transaction_hash = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab",
    cctx_id = "pnetwork:cctx_3",
    event_type = "Redeem",
    block_number = 11056315,
    timestamp = 1632072836,
    log_index = 2,
    correlation_id = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab:2",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d",
    actor_to = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 0,
    amount_out = None,
    contract_address = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    status = "1",
    extra_data = "{\"event\":\"Redeem\",\"is_faulty\":false}"
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_txs_and_logs.md",
    raw_pk = "pnetwork:cctx_3:redeem-attack",
    transaction_hash = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab",
    cctx_id = "pnetwork:cctx_3",
    event_type = "Redeem",
    block_number = 11056315,
    timestamp = 1632072836,
    log_index = 15,
    correlation_id = "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab:15",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d",
    actor_to = "3LngKgsXQAnm5cLP43PZUGGvMau9uUzhky",
    token_in = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",
    token_out = "BTC",
    amount_in = 1384727780193805721,
    amount_out = None,
    contract_address = "0x47cf548e8eaa96ce25bf352253a0c8100d4f4c7d",
    status = "1",
    extra_data = "{\"event\":\"Redeem\",\"is_faulty\":true,\"reason\":\"Redeem emitted by attacker-created contract\",\"repeated_faulty_logs_in_receipt\":true,\"repeated_faulty_log_count\":100}"
)
```
