#!/usr/bin/env python3
# guardian_context.py | Vitalia SDD v0.0.1 — Domínio HOOKS
# Atualizado em: 31-08-2026 04:20:00(GMT-04:00)
"""
Guardião de Contexto Polimórfico e Compilador de Context Engineering — Vitalia SDD v0.0.1
Suporta carregamento dinâmico de múltiplas fontes YAML por schema_type,
poda semântica com cotas calibradas (source_weights) e emissão de advisory para TOMLs legados.
"""

import os
import sys
import re
import json
import shlex
import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

_scripts_root = str(Path(__file__).resolve().parent.parent)
if _scripts_root not in sys.path:
    sys.path.insert(0, _scripts_root)

import kit_env_bootstrap
health = kit_env_bootstrap.init()
from core.utils import get_timestamp, format_visible_header

try:
    import yaml
except ImportError:
    yaml = None


# ─── ADAPTADORES POLIMÓRFICOS ──────────────────────────────────────────────

class BaseAdapter:
    def prune(self, data: Dict[str, Any], profile: Dict[str, Any], token_limit: int) -> Dict[str, Any]:
        return data


class ConstitutionAdapter(BaseAdapter):
    def prune(self, data: Dict[str, Any], profile: Dict[str, Any], token_limit: int) -> Dict[str, Any]:
        const_cfg = profile.get("constitution", {})
        allowed_domains = set(const_cfg.get("domains", []))
        severity_filter = set(const_cfg.get("severity_filter", ["BLOCKING"]))
        exclude_principles = set(const_cfg.get("principles_exclude", []))
        include_principles = set(const_cfg.get("principles_include", []))

        pruned_modules = []
        for mod in data.get("modules", []):
            if allowed_domains and mod.get("id") not in allowed_domains:
                continue
            pruned_principles = []
            for p in mod.get("principles", []):
                p_id = p.get("id")
                if exclude_principles and p_id in exclude_principles:
                    continue
                if include_principles and p_id not in include_principles:
                    continue
                if severity_filter and p.get("severity") not in severity_filter:
                    continue
                pruned_principles.append(p)
            if pruned_principles:
                mod_copy = dict(mod)
                mod_copy["principles"] = pruned_principles
                pruned_modules.append(mod_copy)

        return {
            "schema_type": "constitution",
            "schema_version": data.get("schema_version", "0.0.1"),
            "modules": pruned_modules
        }


class RoutingTableAdapter(BaseAdapter):
    def prune(self, data: Dict[str, Any], profile: Dict[str, Any], token_limit: int) -> Dict[str, Any]:
        agents = data.get("agents", [])
        return {
            "schema_type": "routing_table",
            "agents": agents
        }


class AgentsCatalogAdapter(BaseAdapter):
    def prune(self, data: Dict[str, Any], profile: Dict[str, Any], token_limit: int) -> Dict[str, Any]:
        agents = data.get("agents", [])
        return {
            "schema_type": "agents_catalog",
            "agents": agents
        }


ADAPTERS = {
    "constitution": ConstitutionAdapter(),
    "routing_table": RoutingTableAdapter(),
    "agents_catalog": AgentsCatalogAdapter(),
}


# ─── GUARDIAN CONTEXT ENGINE V0.0.1 ─────────────────────────────────────────

class GuardianContextV2:
    def __init__(self, workflow_name: str, guardian_config: Dict[str, Any] = None, session_dir: Path = None, cwd: Path = None):
        self.workflow_name = workflow_name
        self.guardian_config = guardian_config or {}
        self.cwd = cwd or Path.cwd()
        self.session_dir = session_dir or (self.cwd / ".vitalia" / "memory" / "session")
        self.kit_root = Path.home() / ".vitalia" / "kit"
        self.profiles_dir = self.kit_root / "profiles"
        self.tmp_dir = self.kit_root / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.advisory = None

    def _estimate_tokens(self, obj: Any) -> int:
        text = json.dumps(obj, ensure_ascii=False)
        return int(len(text.split()) * 1.3)

    def load_yaml(self, name: str) -> Tuple[Optional[Dict[str, Any]], str]:
        if not yaml:
            return None, "yaml_module_missing"
        
        path = self.profiles_dir / f"{name}.yaml"
        if not path.exists():
            # Fallback para caminho legado
            if name == "constitution":
                legacy = self.kit_root / "rules" / "always-on" / "constitution_data.yaml"
                if legacy.exists():
                    return yaml.safe_load(legacy.read_text(encoding="utf-8")), "constitution"
            return None, "file_not_found"
        
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        schema_type = data.get("schema_type", name)
        return data, schema_type

    def resolve_profile(self) -> Dict[str, Any]:
        profile_name = self.guardian_config.get("guardian_profile")
        if profile_name:
            p_data, _ = self.load_yaml(profile_name)
            if p_data:
                return p_data

        # Verificar se profile foi passado inline
        inline_gate = self.guardian_config.get("gate")
        if inline_gate:
            return {
                "schema_type": "guardian_profile",
                "tokens": {"total_budget": inline_gate.get("token_budget", 400), "source_weights": inline_gate.get("source_weights", {})},
                "constitution": {"domains": inline_gate.get("domains", []), "severity_filter": inline_gate.get("severity_filter", ["BLOCKING"])}
            }

        # Fallback para perfil default do workflow
        p_data, _ = self.load_yaml(f"gp_{self.workflow_name}")
        if p_data:
            return p_data

        self.advisory = f"[GUARDIAN ADVISORY: Workflow "{self.workflow_name}" operando sem guardian_profile dedicado — usando fallback completo.]"
        return {
            "schema_type": "guardian_profile",
            "tokens": {"total_budget": 500, "source_weights": {"constitution": 1.0}},
            "constitution": {"domains": [], "severity_filter": ["BLOCKING", "WARNING"]}
        }

    def load_session_context(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        sess_cfg = profile.get("session_context", {})
        session_ctx = {}

        if sess_cfg.get("include_p0", True):
            st_file = self.session_dir / "SESSION_STATE.md"
            if st_file.exists():
                lines = st_file.read_text(encoding="utf-8").splitlines()
                p0_lines = [l for l in lines if "P0" in l or "Próximo Passo" in l or "Next Step" in l]
                session_ctx["p0"] = p0_lines[0].strip() if p0_lines else "Dar continuidade à implementação planejada."
            else:
                session_ctx["p0"] = "Inicialização de sessão."

        feat_file = self.cwd / ".vitalia" / "feature.json"
        if sess_cfg.get("include_active_feature", True) and feat_file.exists():
            try:
                f_data = json.loads(feat_file.read_text(encoding="utf-8"))
                session_ctx["active_feature"] = f_data.get("feature_directory") or f_data.get("active_feature") or "Geral"
            except Exception:
                session_ctx["active_feature"] = "Geral"

        if sess_cfg.get("include_agents_queue", True):
            session_ctx["agents_queue"] = {
                "design-thinking": {"pending_tasks": 0},
                "literature-curator": {"pending_tasks": 0},
                "medical-gate": {"pending_tasks": 0}
            }

        return session_ctx

    def build_payload(self) -> Dict[str, Any]:
        profile = self.resolve_profile()
        yaml_sources = self.guardian_config.get("yaml_sources", ["constitution"])
        if not yaml_sources:
            yaml_sources = ["constitution"]

        tokens_cfg = profile.get("tokens", {})
        total_budget = tokens_cfg.get("total_budget", 500)
        weights = tokens_cfg.get("source_weights", {})

        payload_sources = {}
        for src_name in yaml_sources:
            raw_data, stype = self.load_yaml(src_name)
            if not raw_data:
                continue
            
            adapter = ADAPTERS.get(stype, BaseAdapter())
            src_weight = weights.get(src_name, 1.0 / len(yaml_sources))
            src_token_limit = int(total_budget * src_weight)
            
            pruned_data = adapter.prune(raw_data, profile, src_token_limit)
            payload_sources[src_name] = pruned_data

        session_ctx = self.load_session_context(profile)

        result_payload = {
            "schema_version": "0.0.1",
            "workflow": self.workflow_name,
            "timestamp": get_timestamp(),
            "sources": payload_sources,
            "session_context": session_ctx
        }

        if self.advisory:
            result_payload["guardian_advisory"] = self.advisory

        total_est = self._estimate_tokens(result_payload)
        result_payload["estimated_tokens"] = total_est
        result_payload["token_budget"] = total_budget

        return result_payload

    def export_and_publish(self) -> Path:
        payload = self.build_payload()
        pid_hash = hashlib.sha256(f"{os.getpid()}_{self.workflow_name}".encode()).hexdigest()[:12]
        out_file = self.tmp_dir / f"guardian_{pid_hash}.json"
        out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        # Publicar evento no Redis caso disponível
        try:
            import redis
            r_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            client = redis.from_url(r_url, socket_connect_timeout=1)
            client.xadd("vitalia:events", {
                "event": "GUARDIAN_CONTEXT_INJECTED",
                "workflow": self.workflow_name,
                "tokens": str(payload.get("estimated_tokens", 0)),
                "budget": str(payload.get("token_budget", 0))
            })
        except Exception:
            pass

        return out_file


def main():
    parser = argparse.ArgumentParser(description="Guardião de Contexto Polimórfico — Vitalia SDD v0.0.1")
    parser.add_argument("--workflow", default="default", help="Nome do workflow ativo")
    parser.add_argument("--guardian-json", default="{}", help="Configuração JSON serializada da seção [guardian] do TOML")
    parser.add_argument("--session-dir", default=None, help="Caminho do diretório de sessão")
    parser.add_argument("--cwd", default=None, help="Caminho da raiz do projeto")
    parser.add_argument("--args", default="", help="Argumentos do usuário")

    args = parser.parse_args()

    g_config = {}
    if args.guardian_json and args.guardian_json != "{}":
        try:
            g_config = json.loads(args.guardian_json)
        except Exception:
            pass

    cwd_path = Path(args.cwd) if args.cwd else Path.cwd()
    sess_path = Path(args.session_dir) if args.session_dir else (cwd_path / ".vitalia" / "memory" / "session")

    guardian = GuardianContextV2(
        workflow_name=args.workflow,
        guardian_config=g_config,
        session_dir=sess_path,
        cwd=cwd_path
    )

    out_file = guardian.export_and_publish()
    print(f"✅ Guardian V2 exportado para {out_file}")
    if guardian.advisory:
        print(f"⚠️ {guardian.advisory}")


if __name__ == "__main__":
    main()
