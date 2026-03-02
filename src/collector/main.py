import argparse
import os
import shutil
from dotenv import load_dotenv

from .config import load_yaml, build_chain_cfgs
from .rpc import rpc_web3
from .pipeline import collect_data, CallSpec


def clear_output_dir(out_dir: str):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)


def resolve_block_range(args, chain, w3_manager):
    head = w3_manager.get_block_number()
    safe_head = max(0, head - chain.confirmations)

    if args.from_block is not None and args.to_block is not None:
        from_block = args.from_block
        to_block = args.to_block
    else:
        from_block = max(0, safe_head - args.last_n_blocks)
        to_block = safe_head

    return head, safe_head, from_block, to_block


def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", default="../configs/chains.yml")
    ap.add_argument("--collectors", default="../configs/collectors.yml")
    ap.add_argument("--out", default="out")

    ap.add_argument("--from-block", type=int, default=None)
    ap.add_argument("--to-block", type=int, default=None)
    ap.add_argument("--last-n-blocks", type=int, default=2000)
    ap.add_argument("--chunk-size", type=int, default=500)

    # novos toggles (opcional, mas útil)
    ap.add_argument("--no-blocks", action="store_true", help="Do not collect block headers")
    ap.add_argument("--no-codes", action="store_true", help="Do not collect contract code for emitters")
    ap.add_argument("--code-block", default="latest", help="Block tag for eth_getCode (latest or hex/int supported by node)")
    ap.add_argument("--include-bytecode", action="store_true", help="Store full bytecode in codes.jsonl (bigger files)")
    args = ap.parse_args()

    clear_output_dir(args.out)

    chains_doc = load_yaml(args.chains)
    collectors_doc = load_yaml(args.collectors)
    chain_cfgs = build_chain_cfgs(chains_doc)

    for collector_name, col in collectors_doc["collectors"].items():
        chain = chain_cfgs[col["chain"]]

        # create RPC manager
        w3_manager = rpc_web3(chain.name, chain.rpc_url_list)

        head, safe_head, from_block, to_block = resolve_block_range(args, chain, w3_manager)

        # (Opcional) eth_call specs.
        #  - balanceOf(token, bridge)
        #  - allowance(owner, spender)
        #  - verifier()/validators()/quorum() do bridge
        extra_calls = []  # type: list[CallSpec]

        counters = collect_data(
            w3_manager=w3_manager,
            chain=chain,
            collector_name=collector_name,
            addresses=col.get("addresses"),
            topic0_list=col.get("topic0"),
            from_block=from_block,
            to_block=to_block,
            chunk_size=args.chunk_size,
            out_dir=args.out,
            collect_block_headers=not args.no_blocks,
            collect_emitter_code=not args.no_codes,
            code_block=args.code_block,
            include_bytecode=args.include_bytecode,
            extra_calls=extra_calls if extra_calls else None,
        )

        print(
            f"[{collector_name} | {chain.name}] head={head} safe_head={safe_head} "
            f"range=[{from_block},{to_block}] -> {counters}"
        )


if __name__ == "__main__":
    main()