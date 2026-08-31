#!/usr/bin/env python3
# tmp_cleanup.py | Vitalia Kit — Domínio MAINTENANCE
# Atualizado em: 28-08-2026 09:00:00(GMT-04:00)
"""
Limpeza Interativa de Arquivos Temporários — Vitalia Kit (Domínio MAINTENANCE)
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap
health = kit_env_bootstrap.init()
from core.utils import get_current_datetime, get_timestamp


class TmpCleanup:
    def __init__(self, tmp_dir: Optional[Path] = None):
        self.tmp_dir = tmp_dir or (Path.home() / ".vitalia" / "kit" / "tmp")

    def scan_by_date(self) -> Dict[str, List[Path]]:
        if not self.tmp_dir.exists():
            return {}

        grouped: Dict[str, List[Path]] = {}
        for item in self.tmp_dir.iterdir():
            if item.is_file():
                mtime = os.path.getmtime(item)
                dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                grouped.setdefault(dt_str, []).append(item)

        return dict(sorted(grouped.items()))

    def display_matrix(self, grouped: Dict[str, List[Path]]) -> None:
        today_str = get_current_datetime().strftime("%Y-%m-%d")
        print("\n📊 Matriz de Arquivos Temporários (~/.vitalia/kit/tmp/):")
        print("=" * 65)
        print(f"{'#':<3} | {'Data':<12} | {'Qtd Arquivos':<14} | {'Tamanho Total':<14} | {'Status'}")
        print("-" * 65)

        for idx, (dt_str, files) in enumerate(grouped.items(), start=1):
            total_bytes = sum(f.stat().st_size for f in files)
            size_kb = total_bytes / 1024
            is_today = (dt_str == today_str)
            status = "🟢 HOJE (Preservar)" if is_today else "🟡 Antigo"
            print(f"{idx:<3} | {dt_str:<12} | {len(files):<14} | {size_kb:>8.2f} KB    | {status}")
        print("=" * 65)

    def clean_files(self, files: List[Path]) -> int:
        deleted = 0
        for f in files:
            try:
                f.unlink(missing_ok=True)
                deleted += 1
            except Exception as e:
                print(f"⚠️ Falha ao apagar {f.name}: {e}", file=sys.stderr)
        return deleted

    def run_interactive(self, auto_clean_old: bool = False) -> None:
        grouped = self.scan_by_date()
        if not grouped:
            print("✨ Pasta temporária já está limpa. Nenhum arquivo encontrado.")
            return

        self.display_matrix(grouped)
        today_str = get_current_datetime().strftime("%Y-%m-%d")

        if auto_clean_old:
            old_files = [f for dt, files in grouped.items() if dt != today_str for f in files]
            deleted = self.clean_files(old_files)
            print(f"🧹 Limpeza automática concluída: {deleted} arquivos antigos apagados.")
            return

        print("\nOpções de Limpeza:")
        print("  [a] (Recomendado) Apagar tudo EXCETO hoje")
        print("  [d] Selecionar datas específicas (ex: 1, 2)")
        print("  [n] (Padrão) Não apagar nada")
        print("  [t] Apagar TUDO (inclusive hoje)")

        if not sys.stdin.isatty():
            print("ℹ️ Executando em ambiente automatizado. Padrão: Não apagar nada.")
            return

        try:
            choice = input("\nEscolha uma opção [a/d/n/t] (Padrão: n): ").strip().lower() or "n"
            if choice == "a":
                old_files = [f for dt, files in grouped.items() if dt != today_str for f in files]
                deleted = self.clean_files(old_files)
                print(f"🧹 {deleted} arquivos de sessões anteriores apagados.")
            elif choice == "t":
                all_files = [f for files in grouped.values() for f in files]
                deleted = self.clean_files(all_files)
                print(f"🧹 {deleted} arquivos temporários apagados.")
            elif choice == "d":
                sel = input("Digite os números das datas separados por vírgula (ex: 1, 2): ")
                indices = [int(x.strip()) for x in sel.split(",") if x.strip().isdigit()]
                date_keys = list(grouped.keys())
                selected_files = []
                for i in indices:
                    if 1 <= i <= len(date_keys):
                        selected_files.extend(grouped[date_keys[i - 1]])
                deleted = self.clean_files(selected_files)
                print(f"🧹 {deleted} arquivos apagados nas datas selecionadas.")
            else:
                print("Operação cancelada. Nenhum arquivo foi apagado.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")


def main():
    parser = argparse.ArgumentParser(description="Limpeza Interativa de Arquivos Temporários — Vitalia Kit")
    parser.add_argument("--auto-clean-old", action="store_true", help="Apaga automaticamente arquivos de datas anteriores sem perguntar")
    args = parser.parse_args()

    cleaner = TmpCleanup()
    cleaner.run_interactive(auto_clean_old=args.auto_clean_old)


if __name__ == "__main__":
    main()
