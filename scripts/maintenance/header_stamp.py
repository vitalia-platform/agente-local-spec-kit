#!/usr/bin/env python3
# header_stamp.py | Vitalia Kit — Domínio MAINTENANCE
# Atualizado em: 28-08-2026 09:00:00(GMT-04:00)
"""
Carimbo Temporal Inteligente e Defensivo — Vitalia Kit (Domínio MAINTENANCE)
"""

import os
import sys
import time
import subprocess
import py_compile
import argparse
from pathlib import Path
from typing import List, Tuple, Optional

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap
health = kit_env_bootstrap.init()
from core.utils import get_timestamp


class HeaderStamp:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def stamp_file_defensive(self, file_path: Path, dry_run: bool = False) -> Tuple[bool, str]:
        if not file_path.exists() or not file_path.is_file():
            return False, "Arquivo não existe"

        ext = file_path.suffix.lower()
        if ext not in [".py", ".md", ".sh", ".ts", ".js", ".json", ".yaml", ".yml"]:
            return False, "Extensão ignorada"

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return False, f"Erro de leitura: {e}"

        lines = content.splitlines()
        ts = get_timestamp()
        file_name = file_path.name

        if ext == ".py" or ext in [".sh", ".yaml", ".yml"]:
            stamp_line = f"# {file_name} | Atualizado em: {ts}"
        elif ext == ".md":
            stamp_line = f"<!-- {file_name} | Atualizado em: {ts} -->"
        elif ext in [".js", ".ts"]:
            stamp_line = f"// {file_name} | Atualizado em: {ts}"
        else:
            return False, "Sem formato de comentário suportado"

        new_lines = []
        if lines and lines[0].startswith("#!"):
            new_lines.append(lines[0])
            if len(lines) > 1 and ("Atualizado em:" in lines[1] or "<!--" in lines[1] or "//" in lines[1]):
                new_lines.append(stamp_line)
                new_lines.extend(lines[2:])
            else:
                new_lines.append(stamp_line)
                new_lines.extend(lines[1:])
        else:
            if lines and ("Atualizado em:" in lines[0] or "<!--" in lines[0] or "//" in lines[0]):
                new_lines.append(stamp_line)
                new_lines.extend(lines[1:])
            else:
                new_lines.append(stamp_line)
                new_lines.extend(lines)

        new_content = "\n".join(new_lines) + "\n"

        if dry_run:
            return True, f"[DRY-RUN] Carimbo pronto para: {file_path.name}"

        if ext == ".py":
            temp_check = file_path.with_suffix(".py.chk")
            try:
                temp_check.write_text(new_content, encoding="utf-8")
                py_compile.compile(str(temp_check), doraise=True)
                temp_check.unlink(missing_ok=True)
            except py_compile.PyCompileError as syn_err:
                temp_check.unlink(missing_ok=True)
                return False, f"❌ ERRO SINTÁTICO PREVENIDO: {syn_err}"

        try:
            file_path.write_text(new_content, encoding="utf-8")
            return True, f"✅ Carimbado com sucesso: {file_path.name}"
        except Exception as e:
            return False, f"Falha na gravação: {e}"

    def stamp_staged_files(self) -> int:
        cmd = ["git", "-C", str(self.project_root), "diff", "--cached", "--name-only", "--diff-filter=ACM"]
        try:
            start_time = time.time()
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            files = [self.project_root / f.strip() for f in proc.stdout.splitlines() if f.strip()]
            
            stamped = 0
            for f in files:
                ok, msg = self.stamp_file_defensive(f)
                if ok:
                    subprocess.run(["git", "-C", str(self.project_root), "add", str(f)])
                    stamped += 1
            
            elapsed = (time.time() - start_time) * 1000
            print(f"🏷️ [header_stamp] {stamped} arquivos staged carimbados em {elapsed:.2f}ms")
            return stamped
        except Exception as e:
            print(f"⚠️ [header_stamp] Erro ao carimbar staged: {e}", file=sys.stderr)
            return 0

    def scan_and_stamp(self, target_dir: Path, dry_run: bool = False) -> int:
        print(f"[header_stamp] Varrendo diretório: {target_dir}")
        start_time = time.time()
        
        count = 0
        for p in target_dir.rglob("*"):
            if p.is_file() and not any(part.startswith(".") for part in p.parts):
                ok, msg = self.stamp_file_defensive(p, dry_run=dry_run)
                if ok:
                    count += 1
                    print(f"  {msg}")

        elapsed = time.time() - start_time
        if elapsed > 2.0:
            print(f"⚠️ [header_stamp] AVISO DE PERFORMANCE: Varredura levou {elapsed:.2f}s (limite tolerado: 2.0s).", file=sys.stderr)
        else:
            print(f"✅ [header_stamp] {count} arquivos processados em {elapsed:.2f}s.")
        return count


def main():
    parser = argparse.ArgumentParser(
        description="Carimbo Temporal Inteligente e Defensivo — Vitalia Kit",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--staged", action="store_true", help="Carimba apenas arquivos no git staging")
    parser.add_argument("--scan", default=None, help="Varre e carimba recursivamente o diretório indicado")
    parser.add_argument("--dry-run", action="store_true", help="Simula o carimbo sem gravar em disco")

    args = parser.parse_args()

    project_root = kit_env_bootstrap.find_project_root()
    stamper = HeaderStamp(project_root)

    if args.staged:
        stamper.stamp_staged_files()
    elif args.scan:
        scan_dir = Path(args.scan)
        if not scan_dir.is_absolute():
            scan_dir = project_root / scan_dir
        stamper.scan_and_stamp(scan_dir, dry_run=args.dry_run)
    else:
        stamper.stamp_staged_files()


if __name__ == "__main__":
    main()
