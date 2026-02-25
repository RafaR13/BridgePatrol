import os
import time
from web3 import Web3

class RPCManager:
    def __init__(self, chain_name, rpc_list):
        self.chain_name = chain_name
        self.rpc_entries = rpc_list if isinstance(rpc_list, list) else [rpc_list]
        self.urls = self._resolve_urls()
        
        if not self.urls:
            raise RuntimeError(f"Could not resolve any RPC URLs for chain: {chain_name}")
        
        self.current_index = 0
        self._init_web3()

    def _resolve_urls(self):
        """Resolves entry as Env Var first, falls back to direct URL string."""
        resolved = []
        for entry in self.rpc_entries:
            # Try to get from environment
            env_val = os.getenv(entry)
            if env_val:
                resolved.append(env_val)
            elif entry.startswith("http"):
                resolved.append(entry)
            else:
                print(f"[!] Warning: Could not resolve RPC entry '{entry}' as Env Var or URL.")
        return resolved

    def _init_web3(self):
        self.w3 = Web3(Web3.HTTPProvider(self.urls[self.current_index], request_kwargs={"timeout": 30}))

    def rotate_rpc(self):
        """Switches to the next available RPC URL."""
        self.current_index = (self.current_index + 1) % len(self.urls)
        new_url = self.urls[self.current_index]
        print(f"[*] [{self.chain_name}] Rotating to: {new_url}")
        self._init_web3()

    def call_with_failover(self, func_name, *args, **kwargs):
        """Executes a Web3.eth function with automatic failover."""
        attempts = len(self.urls)
        while attempts > 0:
            try:
                target_func = getattr(self.w3.eth, func_name)

                if callable(target_func):
                    return target_func(*args, **kwargs)
                
                if args or kwargs:
                    raise TypeError(f"'{func_name}' is not callable (property), but args/kwargs were provided")
                
                return target_func

            except Exception as e:
                print(f"[!] Error on {self.urls[self.current_index]}: {e}")
                self.rotate_rpc()
                attempts -= 1
                time.sleep(1)
        
        raise ConnectionError(f"CRITICAL: All RPCs failed for {self.chain_name}")
    
    def get_block_number(self):
        return self.call_with_failover("block_number")