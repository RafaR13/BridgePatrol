# Signature → Required Data Mapping

# 1. Mint Without Corresponding Lock

## Description (In Plain Words)
A Mint occurred on the destination chain without a valid Lock on the source chain.

## Logical Condition
For every Mint(dstChain) there must exist exactly one Lock(srcChain) such that:
- depositId matches
- token mapping is valid
- amount matches (minus fees if applicable)
- Lock transaction is finalized

If no matching Lock exists → ALERT.

## Required Data

### Source Chain
- Lock event:
  - depositId
  - token address
  - amount
  - sender
  - blockNumber
  - blockHash

### Destination Chain
- Mint event:
  - depositId
  - token address
  - amount
  - recipient
  - blockNumber

### Metadata
- Token mapping (srcToken ↔ dstToken)
- Confirmation threshold per chain

---

# 2. Amount Mismatch (Over-Mint)

## Description
Minted amount exceeds locked amount.

## Logical Condition
Mint.amount ≤ Lock.amount − fees

If Mint.amount > Lock.amount → ALERT.

## Required Data
- Lock.amount
- Mint.amount
- depositId
- Fee policy (if protocol-defined)

---

# 3. Replay Attack (Proof Reused)

## Description
The same proof or depositId is used more than once.

## Logical Condition
Each proofHash or depositId must be consumed exactly once.

If:
- proofHash already used
OR
- depositId already finalized

→ ALERT.

## Required Data
- Mint / Release events
- proofHash
- depositId
- Local registry of consumed proofs


---

# 4. Deposit Event Without Real Transfer (Fake Custody)

## Description
A Deposit event was emitted but no real token transfer occurred.

## Logical Condition
For every Deposit event:
- There must be a Transfer(from → custodian)
OR
- Sender balance decreases
OR
- Custodian balance increases

If not → ALERT.

## Required Data
- Deposit event
- ERC20 Transfer event
- Execution trace (recommended)
- Balance before/after (via eth_call)


---

# 5. Event From Unauthorized Contract (Event Forgery)

## Description
An event was emitted by an untrusted or malicious contract.

## Logical Condition
For each Lock/Mint event:
- event.address ∈ official allowlist
- bytecodeHash == expectedHash

If not → ALERT.

## Required Data
- event.address
- Allowlist of official contracts
- eth_getCode (bytecode hash)


---

# 6. Premature Relay (Before Finality)

## Description
Mint executed before source transaction finality.

## Logical Condition
Mint.blockNumber − Lock.blockNumber ≥ confirmationThreshold

If less → ALERT.

## Required Data
- Lock.blockNumber
- Mint.blockNumber
- Confirmation threshold
- Block hashes (for reorg detection)


---

# 7. Lock Without Mint (Incomplete Flow)

## Description
Lock occurred but no Mint was ever observed.

## Logical Condition
After a time window ΔT:
- Lock exists
- No corresponding Mint

→ ALERT.

## Required Data
- Lock event
- Mint event
- depositId
- Timestamp


---

# 8. Validator Set Manipulation

## Description
Unexpected or malicious change in validator set.

## Logical Condition
If:
- ValidatorSetUpdated outside governance window
OR
- Quorum size decreases unexpectedly

→ ALERT.

## Required Data
- ValidatorSetUpdated events
- Signer addresses
- Required quorum
- Block timestamp


---

# 9. Untrusted Verifier Injection

## Description
Verifier contract replaced with malicious implementation.

## Logical Condition
Verifier.address ∈ allowlist
AND
bytecodeHash == expectedHash

If not → ALERT.

## Required Data
- Verifier contract address
- Bytecode hash
- Upgrade events


---

# 10. Token Approval Abuse

## Description
Suspicious or excessive token approvals related to bridge contracts.

## Logical Condition
If:
- Approval.value == MAX_UINT
AND
- High frequency or abnormal reuse

→ ALERT.

## Required Data
- Approval events
- Transfer events
- Allowance queries


---

# Data Collection Requirements Summary

To support the majority of detection signatures, the IDS must collect:

## Core Events
- Lock
- Mint
- Burn
- Release
- ERC20 Transfer
- Approval
- ValidatorSetUpdated

## Core Fields
- depositId
- msgHash
- proofHash
- nonce
- token address
- amount
- sender
- recipient
- blockNumber
- blockHash
- transactionHash
- event.address

## Required RPC Calls
- eth_getLogs
- eth_getTransactionReceipt
- eth_getBlockByNumber
- eth_getCode
- eth_call (balance / allowance)

## Advanced (For Stronger Detection)
- debug_traceTransaction
- Balance snapshots
- Signature payload extraction
- Contract bytecode fingerprinting