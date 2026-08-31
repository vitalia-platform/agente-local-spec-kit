#!/usr/bin/env python3
# verify_tasks.py | Vitalia Kit — Compatibility Shim
# Atualizado em: 28-08-2026 09:00:00(GMT-04:00)
"""
Compatibility Shim para o Avaliador Local hooks/llm_judge.py.
"""
import sys
from pathlib import Path

_scripts_root = str(Path(__file__).resolve().parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

from hooks.llm_judge import main

if __name__ == "__main__":
    main()
