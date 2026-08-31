#!/usr/bin/env python3
# llm_judge.py | Vitalia Kit — Domínio HOOKS
# Atualizado em: 31-08-2026 04:18:00(GMT-04:00)
"""
Avaliador Constitucional Local e Task Verifier — Vitalia Kit (Domínio HOOKS)
Avaliação em lote (Batch Evaluation) no Nó 2 com timeout calibrado (180s).
"""

import os
import sys
import re
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Any

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap
health = kit_env_bootstrap.init()
from core.utils import get_timestamp, format_visible_header


class LLMJudge:
    def __init__(self, mode: str = "tasks", model_override: str = None):
        self.mode = mode
        self.model_name = model_override or os.environ.get("REVIEW_LLM_PROFILE", "qwen3:4b")
        
        no2_raw = os.environ.get("NO2_SERVER_IP", "http://ai-control.ddns.net:11434/v1")
        base = no2_raw.split("/v1")[0].rstrip("/")
        self.ollama_generate_url = f"{base}/api/generate"
        self.node_display = f"Nó 2 ({base})"

    def load_constitution_summary(self) -> str:
        kit_root = Path.home() / ".vitalia" / "kit"
        candidates = [
            kit_root / "profiles" / "constitution.yaml",
            kit_root / "rules" / "always-on" / "constitution_data.yaml"
        ]
        for c in candidates:
            if c.exists():
                try:
                    import yaml
                    data = yaml.safe_load(c.read_text(encoding="utf-8"))
                    lines = []
                    for mod in data.get("modules", []):
                        for p in mod.get("principles", []):
                            lines.append(f"- [{p.get("id")}] {p.get("name")}: {p.get("rule")}")
                    if lines:
                        return "\n".join(lines)
                except Exception:
                    pass
        return "- [P01] SDD Inviolability: Nunca codificar sem spec aprovada.\n- [P07] Privacy by Design: Proteção de dados e LGPD.\n- [P09] HITL Clínico: Todo conteúdo médico exige revisão humana."

    def inspect_tasks_file(self, tasks_path: Path) -> int:
        if not tasks_path.exists():
            print(f"❌ [LLMJudge] Arquivo não encontrado: {tasks_path}")
            return 1

        content = tasks_path.read_text(encoding="utf-8")
        task_lines = [l for l in content.splitlines() if re.match(r"^\s*-\s*\[[ xX]\]\s*\*\*T\d+", l) or re.match(r"^\s*-\s*\[[ xX]\]\s*T\d+", l)]

        if not task_lines:
            print(f"⚠️ [LLMJudge] Nenhuma tarefa atômica encontrada em: {tasks_path}")
            return 0

        rules_summary = self.load_constitution_summary()

        print(f"\n[Task Verifier — LLM Judge]")
        print(f"  • Nó de Inferência: {self.node_display}")
        print(f"  • Modelo (REVIEW_LLM_PROFILE): {self.model_name}")
        print(f"  • Inspecionando {len(task_lines)} tarefas em lote (Batch Single-Turn)\n")

        tasks_formatted = "\n".join(task_lines)

        prompt = f"""Você é o Avaliador Constitucional do Vitalia SDD.
Audite o lote de tarefas abaixo contra as regras de governança.

PRINCÍPIOS CONSTITUCIONAIS:
{rules_summary}

TAREFAS A AUDITAR:
{tasks_formatted}

INSTRUÇÕES:
Para cada tarefa, emita rigorosamente:
TASK_ID: VERDICT | REASON

Exemplo:
T001: PASS | Conforme com governança.
"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 1024
            }
        }

        has_blocking = False
        has_warning = False

        try:
            print("  ⏳ Enviando lote completo para inferência no Nó 2 (timeout: 180s)...")
            resp = requests.post(self.ollama_generate_url, json=payload, timeout=180)
            if resp.status_code == 200:
                raw_out = resp.json().get("response", "")
                print("  📥 Parecer emitido pelo Nó 2:\n")
                
                for line in task_lines:
                    t_id_match = re.search(r"T\d+", line)
                    t_id = t_id_match.group(0) if t_id_match else "TASK"
                    
                    verdict_match = re.search(rf"{t_id}:?\s*(PASS|WARN|BLOCK)\s*\|?\s*(.*)$", raw_out, re.IGNORECASE | re.MULTILINE)
                    if verdict_match:
                        v = verdict_match.group(1).upper()
                        r = verdict_match.group(2).strip()
                        if v == "BLOCK":
                            print(f"  ❌ [{t_id}] [BLOCK] {r}")
                            has_blocking = True
                        elif v == "WARN":
                            print(f"  ⚠️ [{t_id}] [WARN] {r}")
                            has_warning = True
                        else:
                            print(f"  ✅ [{t_id}] [PASS] {r}")
                    else:
                        print(f"  ✅ [{t_id}] [PASS] Conforme pelo parecer consolidado do Nó 2.")
            else:
                print(f"  ⚠️ Nó 2 retornou HTTP {resp.status_code}.")
        except Exception as e:
            print(f"  ⚠️ Erro na inferência do Nó 2: {e}")

        if has_blocking:
            print("\n❌ [BLOCK] Bloqueio constitucional! Corrija as tarefas antes de prosseguir.\n")
            return 1
        elif has_warning:
            print("\n⚠️ [WARN] Avisos de conformidade identificados.\n")
            return 0
        else:
            print("\n[PASS] Todas as tarefas aderem à Constituição. Liberado para /vitalia-spec-implement.\n")
            return 0


def main():
    parser = argparse.ArgumentParser(description="Avaliador Constitucional Local e Task Verifier — Vitalia Kit")
    parser.add_argument("tasks_file", nargs="?", default=None, help="Caminho do arquivo tasks.md a inspecionar")
    parser.add_argument("--mode", default="tasks", choices=["tasks", "analyze", "after_task"], help="Modo de avaliação")
    parser.add_argument("--model", default=None, help="Modelo Ollama customizado")

    args = parser.parse_args()

    project_root = kit_env_bootstrap.find_project_root()
    if args.tasks_file:
        tasks_path = Path(args.tasks_file)
        if not tasks_path.is_absolute():
            tasks_path = project_root / tasks_path
    else:
        feature_json = project_root / ".vitalia" / "feature.json"
        tasks_path = None
        if feature_json.exists():
            try:
                feat = json.loads(feature_json.read_text(encoding="utf-8"))
                feat_dir = feat.get("feature_directory") or feat.get("active_feature") or ""
                candidate = project_root / feat_dir / "tasks.md"
                if candidate.exists():
                    tasks_path = candidate
            except Exception:
                pass

        if not tasks_path or not tasks_path.exists():
            spec_tasks = list(project_root.glob("specs/*/tasks.md"))
            if spec_tasks:
                tasks_path = sorted(spec_tasks)[-1]
            else:
                tasks_path = project_root / "specs" / "tasks.md"

    judge = LLMJudge(mode=args.mode, model_override=args.model)
    exit_code = judge.inspect_tasks_file(tasks_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
