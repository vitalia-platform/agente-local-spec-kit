#!/usr/bin/env python3
# scan_environment.py | Vitalia Kit
"""
Executa a varredura do ambiente (via kit_env_bootstrap) e retorna o status em JSON.
"""
import sys
import json
import kit_env_bootstrap

def main():
    health = kit_env_bootstrap.init()
    print(json.dumps(health, indent=2, ensure_ascii=False))
    
    # Se houver script chamando, o código de saída 0 indica OK.
    sys.exit(0 if health["status"] == "HEALTHY" else 1)

if __name__ == "__main__":
    main()
