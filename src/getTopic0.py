from eth_utils import keccak, to_hex

def get_topic0(event_signature: str) -> str:
    """Calcula o topic0 (keccak256 completo)"""
    signature_bytes = event_signature.encode("utf-8")
    hash_bytes = keccak(signature_bytes)
    return to_hex(hash_bytes)

def function_selector(signature: str) -> str:
    """Calcula os primeiros 4 bytes do keccak (function selector)"""
    hash_bytes = keccak(signature.encode("utf-8"))
    return to_hex(hash_bytes[:4])

def normalize_sig(sig: str) -> str:
    """Remove espaços da assinatura"""
    return "".join(sig.split())

def main():
    print("Topic0 / Keccak-256 CLI (events) + Function selector (calls)")
    print("Exemplos:")
    print("  Event:    Withdraw(address,uint256)")
    print("  Function: transfer(address,uint256)")
    print("Dica: NÃO incluir 'event'/'function' nem nomes de params, só tipos.\n")

    while True:
        s = input("Assinatura (ENTER para sair): ").strip()
        if not s:
            break

        s_norm = normalize_sig(s)

        topic0 = get_topic0(s_norm)
        selector = function_selector(s_norm)

        print(f"\nAssinatura normalizada: {s_norm}")
        print(f"topic0 (event):         {topic0}")
        print(f"selector (function):    {selector}")
        print("-" * 50)

if __name__ == "__main__":
    main()

# Exemplos úteis para o teu IDS
"""eventos = [
    "Transfer(address,address,uint256)",
    "LockedERC20(address,address,address,uint256,uint256)",
    "StateSynced(uint256,address,bytes)",
    "Withdraw(address,uint256)"
]"""