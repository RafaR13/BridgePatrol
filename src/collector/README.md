# Blockchain IDS -- Required Data per Signature

# Events

**LOCK event**\
(OVER_MINT, PREMATURE_RELAY, LOCK_WITHOUT_MINT, MINT_WITHOUT_LOCK,
UNAUTHORIZED_EMITTER)

**MINT event**\
(OVER_MINT, PREMATURE_RELAY, LOCK_WITHOUT_MINT, MINT_WITHOUT_LOCK,
PROOF_REPLAY, UNAUTHORIZED_EMITTER)

**DEPOSIT event**\
(FAKE_CUSTODY, UNAUTHORIZED_EMITTER)

**RELEASE event**\
(PROOF_REPLAY, UNAUTHORIZED_EMITTER)

**BURN event**\
(UNAUTHORIZED_EMITTER)

**TRANSFER event**\
(FAKE_CUSTODY, TOKEN_APPROVAL_ABUSE)

**APPROVAL event**\
(TOKEN_APPROVAL_ABUSE)

**UPGRADED event**\
(UNTRUSTED_VERIFIER_INJECTION)

**VERIFIER_UPDATED event**\
(UNTRUSTED_VERIFIER_INJECTION)

**OWNERSHIP_TRANSFERRED event**\
(UNTRUSTED_VERIFIER_INJECTION)

------------------------------------------------------------------------

# Event Identification

**event.type**\
(UNAUTHORIZED_EMITTER, OVER_MINT, PROOF_REPLAY, TOKEN_APPROVAL_ABUSE)

**tx_hash**\
(FAKE_CUSTODY, UNAUTHORIZED_EMITTER, OVER_MINT, PROOF_REPLAY,
TOKEN_APPROVAL_ABUSE, UNTRUSTED_VERIFIER_INJECTION, LOCK_WITHOUT_MINT,
MINT_WITHOUT_LOCK)

**block_number**\
(FAKE_CUSTODY, PREMATURE_RELAY, PROOF_REPLAY, LOCK_WITHOUT_MINT,
MINT_WITHOUT_LOCK, UNTRUSTED_VERIFIER_INJECTION)

**timestamp**\
(LOCK_WITHOUT_MINT)

**chain**\
(FAKE_CUSTODY, UNAUTHORIZED_EMITTER, TOKEN_APPROVAL_ABUSE,
UNTRUSTED_VERIFIER_INJECTION)

------------------------------------------------------------------------

# Addresses

**emitter_address**\
(UNAUTHORIZED_EMITTER)

**sender**\
(FAKE_CUSTODY)

**recipient**\
(FAKE_CUSTODY)

**custodian**\
(FAKE_CUSTODY)

**owner**\
(TOKEN_APPROVAL_ABUSE)

**spender**\
(TOKEN_APPROVAL_ABUSE)

**verifier_address**\
(UNTRUSTED_VERIFIER_INJECTION)

------------------------------------------------------------------------

# Tokens

**token**\
(FAKE_CUSTODY, OVER_MINT)

**amount**\
(FAKE_CUSTODY, OVER_MINT)

**value**\
(TOKEN_APPROVAL_ABUSE)

------------------------------------------------------------------------

# Cross‑chain Correlation

**deposit_id**\
(PREMATURE_RELAY, LOCK_WITHOUT_MINT, MINT_WITHOUT_LOCK, PROOF_REPLAY)

**cctx_id**\
(OVER_MINT, PREMATURE_RELAY, LOCK_WITHOUT_MINT, MINT_WITHOUT_LOCK)

**src_chain**\
(MINT_WITHOUT_LOCK)

**dst_chain**\
(MINT_WITHOUT_LOCK)

------------------------------------------------------------------------

# Account State

**sender_balance_before**\
(FAKE_CUSTODY)

**sender_balance_after**\
(FAKE_CUSTODY)

**custodian_balance_before**\
(FAKE_CUSTODY)

**custodian_balance_after**\
(FAKE_CUSTODY)

------------------------------------------------------------------------

# Allowances

**allowance(owner, spender)**\
(TOKEN_APPROVAL_ABUSE)

------------------------------------------------------------------------

# Contract / Bytecode Data

**code_hash**\
(UNAUTHORIZED_EMITTER, UNTRUSTED_VERIFIER_INJECTION)

**contract_bytecode**\
(UNTRUSTED_VERIFIER_INJECTION)

------------------------------------------------------------------------

# Block Data

**block_number (source)**\
(PREMATURE_RELAY)

**block_number (destination)**\
(PREMATURE_RELAY)

**src_confirmations**\
(PREMATURE_RELAY)

------------------------------------------------------------------------

# Time Metrics

**now_timestamp**\
(LOCK_WITHOUT_MINT)

**timeout_seconds**\
(LOCK_WITHOUT_MINT)

------------------------------------------------------------------------

# Aggregations

**occurrences**\
(PROOF_REPLAY)

**approvals_in_window**\
(TOKEN_APPROVAL_ABUSE)

------------------------------------------------------------------------

# Derived Data

**matched_transfer.tx_hash**\
(FAKE_CUSTODY)

**balance_deltas**\
(FAKE_CUSTODY)

------------------------------------------------------------------------

# Minimal Unique Field List

    chain
    event.type
    tx_hash
    block_number
    timestamp

    emitter_address
    sender
    recipient
    custodian
    owner
    spender
    verifier_address

    token
    amount
    value

    deposit_id
    cctx_id
    src_chain
    dst_chain

    sender_balance_before
    sender_balance_after
    custodian_balance_before
    custodian_balance_after

    allowance(owner,spender)

    code_hash
    contract_bytecode

    src_confirmations

    occurrences
    approvals_in_window
