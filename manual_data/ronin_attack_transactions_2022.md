# Transações do ataque à Ronin Bridge (2022)

## 1. Levantamento fraudulento de 173 600 ETH

### `BlockchainTransaction`

```json
{
  "blockchain": "ethereum",
  "transaction_hash": "0xc28fad5e8d5e0ce6a2eaf67b6687be5d58113e16be590824d6cfa1a94467d0b7",
  "block_number": 14442835,
  "timestamp": 1648042149,
  "from_address": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "to_address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "status": 1,
  "value": 0,
  "input_data": "0x993e1c4200000000000000000000000000000000000000000000000000000000001e8480000000000000000000000000098b716b8aaf21512996dc57eb0615e2383e2f96000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000024c2dff6a3c7c480000000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000014a01175db2b62ed80a0973b4ea3581b22629026e3c6767125f14a98dc30194a533744ba284b5855cfbc34c1416e7106bd1d4ce84f13ce816370645aad66c0fcae4771b010984ea09911beeadcd3dab46621bc81071ba91ce24d5b7873bc6a34e34c6aafa563916059051649b3c1930425aa3a79a293cacf24a21bda3b2a46a1e3d39a6551c01f962ee0e333c2f7261b3077bb7b7544001d555df4bc2e6a5cae2b2dac3d1fe3875cd1d12fadbeb4c01f01e196aa36e395a94de074652971c646b4b3b7149b3121b0178bd67c4fa659087c5f7696d912dee9db37802a3393bf4bd799e22eb201e78d90dc3f57e99d8916cd0282face42324f3afa0d96b0a09c4f914f15cac9c11037b1b0102b7a3a587c5be368f324893ed06df7bdcd3817b1880bd6dada86df15bd50d275fc694a8914d1818a2d432f980a97892f303d5a893a3eec176f46957958ecb991c00000000000000000000000000000000000000000000",
  "calls": {
    "format": "semantic_call_tree_summary",
    "call_count": 24,
    "proxy_delegatecall": {
      "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
      "to": "0x8407dc57739bcda7aa53ca6f12f82f9d51c2f21e"
    },
    "recovered_validators": [
      "0x11360eacdedd59bc433afad4fc8f0417d1fbebab",
      "0x1a15a5e25811fe1349d636a5053a0e59d53961c9",
      "0x70bb1fb41c8c42f6ddd53a708e2b82209495e455",
      "0xb9e59d56fd1632fc250935182bdd5c59188b2302",
      "0xf224beff587362a88d859e899d0d80c080e1e812"
    ],
    "asset_calls": [
      {
        "type": "CALL",
        "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
        "to": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "function": "withdraw(uint256)",
        "amount": 173600000000000000000000
      },
      {
        "type": "CALL",
        "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
        "to": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
        "asset": "ETH",
        "value": 173600000000000000000000
      }
    ]
  },
  "fee": 19899000000000000
}
```

### `RoninCrossChainTransaction`

```json
{
  "id": null,
  "src_blockchain": "ronin",
  "src_transaction_hash": null,
  "src_from_address": null,
  "src_to_address": null,
  "src_fee": null,
  "src_fee_usd": null,
  "src_timestamp": null,
  "dst_blockchain": "ethereum",
  "dst_transaction_hash": "0xc28fad5e8d5e0ce6a2eaf67b6687be5d58113e16be590824d6cfa1a94467d0b7",
  "dst_from_address": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "dst_to_address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "dst_fee": 19899000000000000,
  "dst_fee_usd": null,
  "dst_timestamp": 1648042149,
  "deposit_id": 2000000,
  "depositor": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "recipient": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "src_contract_address": "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5",
  "dst_contract_address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
  "amount": 173600000000000000000000,
  "amount_usd": null
}
```

### Evento normalizado: `RoninTokenWithdrew`

```json
{
  "id": null,
  "blockchain": "ethereum",
  "transaction_hash": "0xc28fad5e8d5e0ce6a2eaf67b6687be5d58113e16be590824d6cfa1a94467d0b7",
  "address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "withdrawal_id": 2000000,
  "kind": "ERC20",
  "src_blockchain": "ronin",
  "withdrawer": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "input_token": "0xc99a6a985ed2cac1ef41640596c5a5f9f4e19ef5",
  "recipient": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "output_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
  "token_standard": "ERC20",
  "amount": 173600000000000000000000
}
```

### Todos os logs do receipt

#### Log 66 — `WETH Withdrawal`

```json
{
  "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
  "log_index": 66,
  "event": "Withdrawal(address indexed src, uint256 wad)",
  "decoded": {
    "src": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
    "wad": 173600000000000000000000
  },
  "topics": [
    "0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65",
    "0x0000000000000000000000001a2a1c938ce3ec39b6d47113c7955baa9dd454f2"
  ],
  "data": "0x0000000000000000000000000000000000000000000024c2dff6a3c7c4800000"
}
```

#### Log 67 — `Ronin TokenWithdrew`

```json
{
  "address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "log_index": 67,
  "event": "TokenWithdrew(uint256 indexed withdrawalId, address indexed owner, address indexed tokenAddress, uint256 tokenNumber)",
  "decoded": {
    "withdrawalId": 2000000,
    "owner": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
    "tokenAddress": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "tokenNumber": 173600000000000000000000
  },
  "topics": [
    "0x86174ea401f083b9bb1bdebca3068f27fb023c7091365ed2a8a02b8d75cf0e52",
    "0x00000000000000000000000000000000000000000000000000000000001e8480",
    "0x000000000000000000000000098b716b8aaf21512996dc57eb0615e2383e2f96",
    "0x000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
  ],
  "data": "0x0000000000000000000000000000000000000000000024c2dff6a3c7c4800000"
}
```

## 2. Levantamento fraudulento de 25 500 000 USDC

### `BlockchainTransaction`

```json
{
  "blockchain": "ethereum",
  "transaction_hash": "0xed2c72ef1a552ddaec6dd1f5cddf0b59a8f37f82bdda5257d9c7c37db7bb9b08",
  "block_number": 14442840,
  "timestamp": 1648042264,
  "from_address": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "to_address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "status": 1,
  "value": 0,
  "input_data": "0x993e1c4200000000000000000000000000000000000000000000000000000000001e8481000000000000000000000000098b716b8aaf21512996dc57eb0615e2383e2f96000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000000017312e71180000000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000000000000000000000000000000000000000014a016734b276131c27fa94464db17b44ca517b0a9134b15ee4b776596725741cc7836beea1681dda98a83406515981e1d315d5eba13a0173a5a9688f9f920d7a3f7a1c01155c24a2d7a2ffb02530cf58da40c528301dfc22b21b16267dbf4eba2cd3d087276142bddd1d82404b2e75bd12993606a0c7c7626aa74c4d90bd7e4558fbe4261c01067c5aaba1b8e5bb686cda9efdae909aff86dc83f5be79f13af3ee677fb1791175e0b03401bdf7aa6e604eb995c7670384e6fadef3d687a00fd6d33cd47a0dde1c01dad673b6630394d15f8cca8975351d8272390a6c8bb1cb07cc2b04e8d7ea7a867e56a99e9d0c17a8e0629cebda86ee5a5f8b42610494ad0ed0245ffe9b5287631c012f1fb5b4c2b3718ea69197a5239316fbb9b805be3cdf8420324765ab53144b006b3148921458e629ea254df2c383175ca250e6442b8904a0f50ffdf465f6aa6f1b00000000000000000000000000000000000000000000",
  "calls": {
    "format": "semantic_call_tree_summary",
    "call_count": 22,
    "proxy_delegatecall": {
      "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
      "to": "0x8407dc57739bcda7aa53ca6f12f82f9d51c2f21e"
    },
    "recovered_validators": [
      "0x11360eacdedd59bc433afad4fc8f0417d1fbebab",
      "0x1a15a5e25811fe1349d636a5053a0e59d53961c9",
      "0x70bb1fb41c8c42f6ddd53a708e2b82209495e455",
      "0xb9e59d56fd1632fc250935182bdd5c59188b2302",
      "0xf224beff587362a88d859e899d0d80c080e1e812"
    ],
    "asset_calls": [
      {
        "type": "STATICCALL",
        "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
        "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "function": "balanceOf(address)"
      },
      {
        "type": "CALL",
        "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
        "to": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "function": "transfer(address,uint256)",
        "recipient": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
        "amount": 25500000000000
      }
    ]
  },
  "fee": 21978200000000000
}
```

### `RoninCrossChainTransaction`

```json
{
  "id": null,
  "src_blockchain": "ronin",
  "src_transaction_hash": null,
  "src_from_address": null,
  "src_to_address": null,
  "src_fee": null,
  "src_fee_usd": null,
  "src_timestamp": null,
  "dst_blockchain": "ethereum",
  "dst_transaction_hash": "0xed2c72ef1a552ddaec6dd1f5cddf0b59a8f37f82bdda5257d9c7c37db7bb9b08",
  "dst_from_address": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "dst_to_address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "dst_fee": 21978200000000000,
  "dst_fee_usd": null,
  "dst_timestamp": 1648042264,
  "deposit_id": 2000001,
  "depositor": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "recipient": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "src_contract_address": "0x0b7007c13325c48911f73a2dad5fa5dcbf808adc",
  "dst_contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "amount": 25500000000000,
  "amount_usd": null
}
```

### Evento normalizado: `RoninTokenWithdrew`

```json
{
  "id": null,
  "blockchain": "ethereum",
  "transaction_hash": "0xed2c72ef1a552ddaec6dd1f5cddf0b59a8f37f82bdda5257d9c7c37db7bb9b08",
  "address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "withdrawal_id": 2000001,
  "kind": "ERC20",
  "src_blockchain": "ronin",
  "withdrawer": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "input_token": "0x0b7007c13325c48911f73a2dad5fa5dcbf808adc",
  "recipient": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "output_token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "token_standard": "ERC20",
  "amount": 25500000000000
}
```

### Evento normalizado: `Transfer`

```json
{
  "id": null,
  "blockchain": "ethereum",
  "transaction_hash": "0xed2c72ef1a552ddaec6dd1f5cddf0b59a8f37f82bdda5257d9c7c37db7bb9b08",
  "block_number": 14442840,
  "log_index": 29,
  "token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "from_address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "to_address": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
  "amount": 25500000000000,
  "trigger_event_topic": "0x86174ea401f083b9bb1bdebca3068f27fb023c7091365ed2a8a02b8d75cf0e52",
  "trigger_contract_address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2"
}
```

### Todos os logs do receipt

#### Log 29 — `USDC Transfer`

```json
{
  "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
  "log_index": 29,
  "event": "Transfer(address indexed from, address indexed to, uint256 value)",
  "decoded": {
    "from": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
    "to": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
    "value": 25500000000000
  },
  "topics": [
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
    "0x0000000000000000000000001a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
    "0x000000000000000000000000098b716b8aaf21512996dc57eb0615e2383e2f96"
  ],
  "data": "0x000000000000000000000000000000000000000000000000000017312e711800"
}
```

#### Log 30 — `Ronin TokenWithdrew`

```json
{
  "address": "0x1a2a1c938ce3ec39b6d47113c7955baa9dd454f2",
  "log_index": 30,
  "event": "TokenWithdrew(uint256 indexed withdrawalId, address indexed owner, address indexed tokenAddress, uint256 tokenNumber)",
  "decoded": {
    "withdrawalId": 2000001,
    "owner": "0x098b716b8aaf21512996dc57eb0615e2383e2f96",
    "tokenAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "tokenNumber": 25500000000000
  },
  "topics": [
    "0x86174ea401f083b9bb1bdebca3068f27fb023c7091365ed2a8a02b8d75cf0e52",
    "0x00000000000000000000000000000000000000000000000000000000001e8481",
    "0x000000000000000000000000098b716b8aaf21512996dc57eb0615e2383e2f96",
    "0x000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
  ],
  "data": "0x000000000000000000000000000000000000000000000000000017312e711800"
}
```

## Fontes

- [Transação de 173 600 ETH — Etherscan](https://etherscan.io/tx/0xc28fad5e8d5e0ce6a2eaf67b6687be5d58113e16be590824d6cfa1a94467d0b7)
- [Transação de 25,5 milhões de USDC — Etherscan](https://etherscan.io/tx/0xed2c72ef1a552ddaec6dd1f5cddf0b59a8f37f82bdda5257d9c7c37db7bb9b08)
- [Forta — indicadores e transações do ataque](https://www.forta.org/blog/ronin-hack)
