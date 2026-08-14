# Manual Attack Ground Truth

The `Expected signatures` column uses the project `SignatureType` names. When a
case is a known attack pattern but the current project does not yet implement a
reliable signature for it, the table says `coverage gap`.

## Signature Legend

- `PROOF_REPLAY`: the same logical source action / proof / nonce is consumed more
  than once, or multiple destination executions share a correlation that should
  be one-to-one.
- `LOCK_WITHOUT_MINT`: a source lock/deposit exists but no corresponding
  destination execution/mint/release is present in the dataset.
- `MINT_WITHOUT_LOCK`: a destination mint/release exists but no corresponding
  source lock/deposit is present.
- `AMOUNT_MISMATCH`, `OVER_MINT`, `OVER_RELEASE`: destination value differs from
  the source value, or the destination side creates/releases more value than the
  source side justifies.
- `CONTRACT_MISMATCH`: the source event claims a token/amount/contract relation
  that is not supported by the underlying transaction value or transfer events.
- `UNEXPECTED_EVENT_CALLER`: the destination event was emitted through an
  unexpected caller path.
- `DANGEROUS_TRACE_OPERATION`: transaction trace contains operations such as
  `CREATE`, `CREATE2`, or `SELFDESTRUCT`.

## ChainSwap

High-level incident pattern: the curated ChainSwap dataset currently contains
Ethereum destination-side `Receive()` transactions from the labelled ChainSwap
attacker address. The corresponding source-side lock/deposit transactions are
not present in the dataset yet.

For evaluation, each `chainswap_cross_chain_transactions` row is therefore a
destination-only CCTX and should be detected as:

- `MINT_WITHOUT_LOCK`: destination execution exists without an observed source
  lock/deposit transaction.

Expected current coverage:

| CCTX set | What happened | Expected signatures |
| --- | --- | --- |
| `chainswap:*` | Ethereum destination `Receive()` transaction with `dst_*` populated and `src_* = NULL`. | `MINT_WITHOUT_LOCK`. |

## Meter.io

High-level incident pattern: the Meter.io attacker abused an assumption in the
wrapped native token deposit path. The safe `depositEth` path checked that the
transaction value matched the amount later passed to the handler. The attacker
called the underlying ERC20-style deposit function directly, passed an arbitrary
amount in calldata, and avoided a real wrapped-token burn/lock/transfer on the
source side.

For these samples, the relevant evidence is:

- there is a source `Deposit` event;
- there is no matching source ERC20 `Transfer` proving that the wrapped native
  token was actually locked/burned/transferred into the handler;
- the source transaction value/calldata evidence does not support the amount
  later released/minted on the destination side.

Repeated nonce/correlation values are ignored for now. They are visible in the
manual data, but they are not the real exploit cause and should not drive the
Meter.io correctness labels yet.

Important coverage note: the current normalized Meter.io events often have
`amount_in = NULL`, so the existing `token_contract_attacks` implementation may
skip these rows until the source amount/calldata evidence is normalized. The
correct conceptual signature is still `CONTRACT_MISMATCH`: the source deposit is
not backed by the expected transaction value or ERC20 transfer evidence.

| CCTX | What happened | Why it is an attack | Expected signatures |
| --- | --- | --- | --- |
| `meterio:cctx_1` | BNB-side source `Deposit` followed by Moonriver destination `Transfer` and `ProposalEvent`. | The source deposit path produced a bridge deposit without matching ERC20 transfer/lock evidence for the wrapped native token amount. Destination value was released based on the calldata/proposal path rather than a properly backed source lock. | `CONTRACT_MISMATCH` conceptually; current implementation may need source amount normalization before it fires. |
| `meterio:cctx_2` | BNB-side source `Deposit` followed by Moonriver destination `Transfer` and `ProposalEvent`. | Same exploit pattern: direct deposit path accepted an unsupported wrapped native token amount and destination-side value was released without the expected source transfer/lock evidence. | `CONTRACT_MISMATCH` conceptually; current implementation may need source amount normalization before it fires. |
| `meterio:cctx_3` | BNB-side source `Deposit` followed by BNB-side `InternalTransfer` and `ProposalEvent`. | Same exploit pattern on BNB: the source `Deposit` exists, but the evidence of a real wrapped native token lock/burn/transfer is missing or inconsistent with the amount used downstream. | `CONTRACT_MISMATCH` conceptually; current implementation may need source amount normalization before it fires. |
| `meterio:cctx_4` | BNB deposit with correlation `3484` and no destination events in the dataset. | Pending/unknown. We do not yet have the true matching transaction(s), so this should not be treated as an attack label for now. | No expected signature for now. |
| `meterio:cctx_5` | Ethereum-side source `Deposit` followed by Ethereum-side `Transfer` and `ProposalEvent`. | Same exploit pattern on Ethereum/WETH: a source deposit was accepted without the expected wrapped token transfer/lock evidence matching the downstream released value. | `CONTRACT_MISMATCH` conceptually; current implementation may need source amount normalization before it fires. |
| `meterio:cctx_6` | Ethereum deposit with correlation `546` and no destination events in the dataset. | Pending/unknown. We do not yet have the true matching transaction(s), so this should not be treated as an attack label for now. | No expected signature for now. |

## Qubit

High-level incident pattern: attacker-triggered Ethereum-side deposits produced
BNB-side mints/transfers even though the underlying ETH value did not justify
the normalized `amount_in`. In the project model this is best represented as a
source token/contract/value mismatch.

All Qubit CCTXs below should be labelled with `CONTRACT_MISMATCH`. They should
not normally be labelled as `MINT_WITHOUT_LOCK`, because each destination event
has a corresponding normalized source `Deposit` event. They also should not be
labelled as `AMOUNT_MISMATCH` in the current normalized data because
`amount_in == amount_out` for the event pair; the issue is that the source
deposit itself is not backed by the transaction/token evidence.

| CCTX | Correlation | What happened | Expected signatures |
| --- | ---: | --- | --- |
| `qubit:cctx_1` | `73` | Ethereum `Deposit` for `1000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_2` | `84` | Ethereum `Deposit` for `100000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_3` | `85` | Ethereum `Deposit` for `100000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_4` | `86` | Ethereum `Deposit` for `190000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_5` | `87` | Ethereum `Deposit` for `499000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_6` | `88` | Ethereum `Deposit` for `999000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_7` | `89` | Ethereum `Deposit` for `999000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_8` | `90` | Ethereum `Deposit` for `999000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_9` | `91` | Ethereum `Deposit` for `999000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_10` | `92` | Ethereum `Deposit` for `199000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_11` | `93` | Ethereum `Deposit` for `199000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_12` | `94` | Ethereum `Deposit` for `199000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_13` | `95` | Ethereum `Deposit` for `5990000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_14` | `96` | Ethereum `Deposit` for `5990000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_15` | `97` | Ethereum `Deposit` for `59900000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_16` | `98` | Ethereum `Deposit` for `59900000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_17` | `99` | Ethereum `Deposit` for `59900000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_18` | `100` | Ethereum `Deposit` for `9999000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |
| `qubit:cctx_19` | `101` | Ethereum `Deposit` for `9999000000000000000000`, followed by BNB `Transfer` and `ProposalEvent`. | `CONTRACT_MISMATCH`. if it's ERC20, needs a corresponding transfer event. if its native token, needs tx.value() to match |

## Thorchain

High-level incident pattern: source-side Thorchain deposits/memos used in attack
datasets. The current project intentionally treats Thorchain as source-only: it
does not run missing-pair, destination caller, replay, or destination amount
checks for Thorchain. For this dataset, the correctness target is source-side
value consistency:

- in `thorchain_txs_and_logs.md`, the attacker was handling ETH through the
  Thorchain deposit path, but the transaction has `tx.value = 0` while the
  normalized `Deposit.amount_in` is non-zero;
- in `thorchain2_txs_and_logs.md`, `tx.value` is non-zero, but it does not
  correspond to the normalized `Deposit.amount_in`.

Therefore, the conceptual expected signature is `CONTRACT_MISMATCH`: the source
transaction value does not match the value represented by the normalized deposit
event. If the current code still lacks a Thorchain entry in
`TOKEN_CONTRACT_ATTACK_CONFIG`, implementation work is needed before this
conceptual label fires automatically.

- Future intended coverage should validate vault/router contract, memo
  semantics, token transfer evidence, transaction value, and deposit amount.
- If trace data later includes dangerous operations, `DANGEROUS_TRACE_OPERATION`
  may also apply.

### `thorchain_txs_and_logs.md`

These rows are non-zero `Deposit` events emitted by the observed Thorchain router
contract `0x42A5Ed456650a09Dc10EBc6361A7480fDd61f27B`. The key attack evidence
is that the transaction value is `0`, even though the source-side deposit event
records a non-zero amount and handles ETH-style memo semantics.

| CCTX | What happened | Expected signatures |
| --- | --- | --- |
| `thorchain:0x966cb083d116da2e0d1d115a99381db2200bd39ff75d38cfacdc17b1368f1159` | Source-side Thorchain `Deposit`, amount `14902768506358108867`, target asset `ETH.PERP-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0xb74f4860e24f04e9e32ace36735285d518a8a36bf8e8dcc868d7508bb60947c9` | Source-side Thorchain `Deposit`, amount `14117638765352811215`, target asset `ETH.PERP-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0xb56df76d4bf1384dc2744692d744de44efadcec7226c6255532a0d1ebdb5abcc` | Source-side Thorchain `Deposit`, amount `9151861513878140509`, target asset `ETH.SUSHI-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0x92b466c1908571c45b1a4e751550877a46c5f2ecbc308e01242ec6d2013ad88c` | Source-side Thorchain `Deposit`, amount `9666205268246093093`, target asset `ETH.YFI-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0x0d8d8194e7fb0853261d7bd2bae3eed2849f94ccf821547d50d5c535a0367ff7` | Source-side Thorchain `Deposit`, amount `14995688494938979878`, target asset `ETH.USDT-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0x7cf72852118597e6ff65226a17eae5a078b6de7af791a6324906d9d456f2b1b6` | Source-side Thorchain `Deposit`, amount `12014710724137118409`, target asset `ETH.YFI-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0x514c90c817c270663513e91492d77e9f7282598f5afc3711800e311b6e00be99` | Source-side Thorchain `Deposit`, amount `11872526478509754678`, target asset `ETH.YFI-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0xae3fab1e5cfae0a04f25155ec9047cf0f99df4ddf7dda1f1351ed4720fa3c030` | Source-side Thorchain `Deposit`, amount `10627124023622971309`, target asset `ETH.SUSHI-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |
| `thorchain:0x269c02a0f130f0e45a184526a4f2d60711f3e9e88db8b8e793ea3a84d21395d8` | Source-side Thorchain `Deposit`, amount `11763540452199587482`, target asset `ETH.ALCX-...`, but `tx.value = 0`. | `CONTRACT_MISMATCH`: ETH-handling deposit amount is not backed by `tx.value`. |

### `thorchain2_txs_and_logs.md`

These rows are Thorchain `Deposit` events emitted by
`0xc145990e84155416144c532e31f89b840ca8c2ce`. The key attack evidence is the
inverse of the first Thorchain file: `tx.value` is non-zero, but the normalized
`Deposit.amount_in` is `0`, so the transaction value does not correspond to the
amount represented by the source event.

| CCTX | What happened | Expected signatures |
| --- | --- | --- |
| `thorchain:0x3d4c09bcf91f48a2de347c95f9aaa0d880ed796fa97dd28d9ec4a362b8697b8c` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x87cc796b3591145a2af8db9dafc115077a10fbccd8a1d7d76db4ee2375748dd3` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xc75b9ef9a2f8ffe3ba20a8f5f7133d8b9c25e5baa918ff4c9eade879d33a4c58` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xe4efe2027d595a8fb454445275cd0c1942f6d3c436df7d020a0ae8170a790c41` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x6325fc986c965c789153d5b33cb949640b843ece82219dd31ad96e2b78dda45a` | Source `Deposit` with `amount_in = 0`, target asset `ETH.DODO-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x82222fbbb2621493221e6af6895cab9b27dc9efc2d8a55c9242df22f99992327` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xa5f09545d9c190f02eade25cfd765981c30ca269597e9c9299e57d01ed10ed92` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xd72f7cec0f035df194f917f3baacbde2fc8254391c81823b2bf20ad1069593a5` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x5b6b42c1fecf027d5efcd12c20fc4bf55486e438c580cd3eead326238ffacfa6` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x47f1fb95da94576105d92f6320f77c8e1d2bfb9f9944460822c8ecc90ee02339` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xa5a383678852d3bdee8c8fb8c70892cc044c780cb47f353f39f0cc9f3ef66421` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x39decf95d9d9728f80ab0bda1bdfeee85cce98bba39b66790a2202619b44bc9f` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x78cd7021ac99027c464c4464ca7e1b57d1827e3959b10700e6e080661a40c779` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xc5c224fb8bea0fde468fb50aba45e890bb6b694fbe47e007e994f0d3eb303971` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x32933c28281489256949842b9f4c9f85a6e557553dce2aee35f2f52110cfc0c9` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xfe9597c29e557bdc31fbe31bb4709d57457023b9e66c4ad7ebe443c39b10d8ca` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xc1d1c1367b3ba3ef409b9ab78fd1ec7bc8a822aabef81b944a72f4ac278bb139` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x1d1b826718681f474e704f85a0b03ad8b051804d23cd818d4ecebb471514f509` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xfe739dc4092785b9024c60cd94ea2ab3368c69c7e471aa9facb95106650390c6` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x9bce82d88d9bf3f505735effd6006069214dc17414ef261bcb5595a861008f30` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x846fe82570ed32c252adaa13fa8eb37e89aca03c03ea1ac413f7c4eb109d1489` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xd58d1ef6d6e49eb99d0524128c16115893396fd05877ef4856fce474b5ba09a7` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x347926a5af7c8434f27ddfcfd14a42ac1525b0fcb3e6803203a83c89276660e3` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xe30f53e7f8d153c50c53574b7055098ba5949948c33674ec779d19fee73170dc` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ETH`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xdd391866cfe27e2a2e17fe902106163b0a93d3cfeaa9707b555fb20ef3817d7d` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xe71529643934723a0da66825e51d3c0fcacda791be724f633ad7987ab58a5c13` | Source `Deposit` with `amount_in = 0`, target asset `ETH.DODO-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x365a7753b2d51c5ac1671337bd571c3540056b89c3fd51be5f6ccf01f8437998` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xac512c2cbb47801b2bf505465b4b7ca3e3b95e54302a461991223f04445d26ac` | Source `Deposit` with `amount_in = 0`, target asset `ETH.KYL-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xb23beeb4c72755230ce655d1c45cba1c662e55e4aa1f47a4a3b0ef4a3cf4362e` | Source `Deposit` with `amount_in = 0`, target asset `ETH.KYL-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x3c0377b41d3b0d709cf5fe15767422b91faab724a12816c4650833e551406e36` | Source `Deposit` with `amount_in = 0`, target asset `ETH.DODO-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xe8091da4913917336b071a1001517f9c4431586a2e57899acbfd8759ce5c051f` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xbc68035ce2c8a2c549604ff7db59e07931f39040758b138190338fa697338db3` | Source `Deposit` with `amount_in = 0`, target asset `ETH.AAVE-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x5da19c1c5c2f6bbdf9d4fb0e6ff16a0df6d6d7fe1f8e95ca755e5b3c6aada458` | Source `Deposit` with `amount_in = 0`, target asset `ETH.HEGIC-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xe7363af16e5cdc56f2743a3b78258934695c6b091b3345af9cd286411cf93088` | Source `Deposit` with `amount_in = 0`, target asset `ETH.ALCX-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x4f61a1590c4aa2a30ffab1735f5273b72bc1fbb63f90d5faf1b380312913bb55` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x91cd37d7e59f2c6a96e002059d03218045eda4e2b487c1e70619162826e57afa` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x5b5a971dcf5e8a2b551e2e9cf3eacf3c30d49a3289afc4eadf1a1d3ef5af87d4` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x9d60d243c01c735e2db88c044e77142d5d1d6d3cb21a0bd16f496a6a2327c70b` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0xfe4b3fe42ef4edc9a33791dc415d7bf22bf0c4a77b270a46b06f2ec4f5664313` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x03c90ba802f5cc14fb21912e8ecd3501c09d60f7335293a1d4b2b9f4500d29c5` | Source `Deposit` with `amount_in = 0`, target asset `ETH.YFI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
| `thorchain:0x8fef62a0837c9e41429de427e7c8692df66004c74cf25cb70127b36df1b44036` | Source `Deposit` with `amount_in = 0`, target asset `ETH.SUSHI-...`. | `CONTRACT_MISMATCH`: non-zero `tx.value` does not match `Deposit.amount_in`. |
