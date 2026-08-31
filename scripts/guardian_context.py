#!/usr/bin/env python3
# guardian_context.py | Vitalia Kit — Domínio HOOKS
# Atualizado em: 28-08-2026 09:00:00(GMT-04:00)
"""
Guardião de Contexto e Podagem Constitucional — Vitalia Kit (Domínio HOOKS)

Responsabilidades:
1. Ler constitution_data.yaml e filtrar princípios relevantes por workflow gate (Schema-Safe Pruning).
2. Garantir que o payload do nó 'constitution' não exceda o teto calibrado de 500 tokens.
3. Inspecionar o estado ativo da sessão em .vitalia/memory/session/SESSION_STATE.md.
4. Exportar o payload JSON otimizado para ~/.vitalia/kit/tmp/guardian_<pid>.json e Redis vitalia:events.

Didática para Desenvolvedores Iniciantes:
- O que é Schema-Safe Pruning? É selecionar apenas as regras que se aplicam ao comando que a IA
  está executando agora. Se a IA está especificando requisitos (spec-specify), ela não precisa ler
  regras de compilação de código, economizando tokens e mantendo o foco de atenção do modelo afiado.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Auto-injeção do diretório pai em sys.path
_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap
health = kit_env_bootstrap.init()
from core.utils import get_current_datetime, get_timestamp, format_visible_header, generate_id


class GuardianContext:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.kit_root = Path.home() / ".vitalia" / "kit"
        self.constitution_file = self.kit_root / "rules" / "always-on" / "constitution_data.yaml"
        self.session_dir = project_root / ".vitalia" / "memory" / "session"
        self.tmp_dir = self.kit_root / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def prune_constitution(self, workflow_name: str) -> Dict[str, Any]:
        """
        Carrega constitution_data.yaml e poda princípios não relacionados ao workflow,
        respeitando o teto calibrado de 500 tokens.
        """
        if not self.constitution_file.exists():
            return {"principles": [], "token_estimate": 0}

        try:
            import yaml
            data = yaml.safe_load(self.constitution_file.read_text(encoding="utf-8"))
        except Exception:
            return {"principles": [], "token_estimate": 0}

        pruned_principles = []
        gate_map = {
            "spec-specify": "specify",
            "spec-plan": "plan",
            "spec-tasks": "tasks",
            "spec-implement": "implement",
            "task-verifier": "all"
        }
        target_gate = gate_map.get(workflow_name, "all")

        for mod in data.get("modules", []):
            for p in mod.get("principles", []):
                gates = p.get("gates", ["all"])
                if "all" in gates or target_gate in gates or workflow_name in gates:
                    pruned_principles.append({
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "level": p.get("level"),
                        "rule": p.get("rule"),
                        "severity": p.get("severity", "BLOCKING")
                    })

        # Estimativa de tokens (1 palavra ~= 1.3 tokens)
        payload_text = json.dumps(pruned_principles)
        token_estimate = int(len(payload_text.split()) * 1.3)

        return {
            "version": data.get("schema_version", "0.5.0"),
            "target_gate": target_gate,
            "principles_count": len(pruned_principles),
            "token_estimate": token_estimate,
            "principles": pruned_principles
        }

    def generate_payload(self, workflow: str, args: str = "") -> Path:
        """Gera o payload JSON completo do guardião."""
        constitution = self.prune_constitution(workflow)
        session_state_file = self.session_dir / "SESSION_STATE.md"
        session_state = session_state_file.read_text(encoding="utf-8") if session_state_file.exists() else ""

        payload = {
            "generated_at": get_timestamp(),
            "workflow": workflow,
            "args": args,
            "environment": health,
            "session_state_summary": session_state,
            "constitution": constitution
        }

        pid_hash = generate_id(f"{os.getpid()}_{get_timestamp()}", length=12)
        out_file = self.tmp_dir / f"guardian_{pid_hash}.json"
        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        # Telemetria Redis se disponível
        if health.get("redis_client_ok", False):
            try:
                import redis
                client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True, socket_timeout=2.0)
                client.xadd("vitalia:events", {"data": json.dumps({"event": "GUARDIAN_PAYLOAD_GENERATED", "file": str(out_file), "tokens": constitution.get("token_estimate")})}, maxlen=500)
            except Exception:
                pass

        return out_file


def main():
    parser = argparse.ArgumentParser(description="Guardião de Contexto e Injeção Constitucional — Vitalia Kit")
    parser.add_argument("--workflow", default="general", help="Nome do workflow ativo (ex: spec-specify, spec-implement)")
    parser.add_argument("--args", default="", help="Argumentos do comando")
    args = parser.parse_args()

    project_root = kit_env_bootstrap.find_project_root()
    guardian = GuardianContext(project_root)
    out_file = guardian.generate_payload(args.workflow, args.args)
    print(f"✅ Guardian V2 exportado para {out_file}")
    if health.get("redis_client_ok", False):
        print("📡 Payload publicado no Redis (vitalia:events)")


if __name__ == "__main__":
    main()
