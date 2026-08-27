#!/usr/bin/env python3
import os
import sys
import argparse
import json
import subprocess

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("Erro: Este script requer Python 3.11+ (tomllib) ou o pacote 'tomli'.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Vitalia Hook Runner")
    parser.add_argument("file", help="Caminho para o arquivo .toml")
    parser.add_argument("--phase", choices=['before', 'after', 'none'], default='none', help="Fase dos hooks a executar")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Erro: Arquivo não encontrado: {args.file}", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(args.file, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print(f"Erro ao fazer parse do TOML: {e}", file=sys.stderr)
        sys.exit(1)
        
    cwd = os.getcwd()
    
    if args.phase in ['before', 'after']:
        hooks = data.get('hooks', {}).get(args.phase, [])
        if isinstance(hooks, str):
            hooks = [hooks]
            
        for cmd_template in hooks:
            cmd = cmd_template.replace("{{cwd}}", cwd)
            print(f"[Hook Runner] Executando hook ({args.phase}): {cmd}", file=sys.stderr)
            try:
                # Redirecionamos o stdout para stderr para não poluir o JSON de saída passiva
                subprocess.run(cmd, shell=True, check=True, stdout=sys.stderr, stderr=sys.stderr)
            except subprocess.CalledProcessError as e:
                print(f"[Hook Runner] ❌ Hook falhou com código {e.returncode}: {cmd}", file=sys.stderr)
                sys.exit(e.returncode)
                
    # Saída passiva para consumo da IA
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
