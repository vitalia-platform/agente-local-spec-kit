# scan_environment.py | Atualizado em: 19-08-2026 20:12:00(GMT-04:00)
"""
Hook de Scan Passivo de Ambiente — Vitalia Kit
Invocado pelo hook before do brainstorming.toml.
Detecta tecnologias e flags de domínio no projeto atual.
Escreve ~/.vitalia/kit/tmp/env_context.json para consumo pelo prompt.

Separação garantida: lê o --cwd passado como argumento,
nunca hardcoda paths de projetos específicos.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

VITALIA_TMP = Path.home() / ".vitalia" / "kit" / "tmp"
OUTPUT_FILE = VITALIA_TMP / "env_context.json"


def detect_technologies(cwd: Path) -> dict:
    """Detecta tecnologias presentes no projeto pelo sistema de arquivos."""
    detected = {}

    # Redis
    indicators_redis = [
        cwd / "docker-compose.yml",
        cwd / "docker-compose.yaml",
    ]
    for f in indicators_redis:
        if f.exists() and "redis" in f.read_text(errors="ignore").lower():
            detected["redis"] = True
            break
    if not detected.get("redis"):
        # Checar requirements.txt / pyproject.toml / package.json
        for dep_file in ["requirements.txt", "pyproject.toml", "package.json", "Pipfile"]:
            fp = cwd / dep_file
            if fp.exists() and "redis" in fp.read_text(errors="ignore").lower():
                detected["redis"] = True
                break

    # Celery
    for dep_file in ["requirements.txt", "pyproject.toml", "Pipfile"]:
        fp = cwd / dep_file
        if fp.exists() and "celery" in fp.read_text(errors="ignore").lower():
            detected["celery"] = True
            break

    # PostgreSQL / pgvector
    for dep_file in ["requirements.txt", "pyproject.toml", "Pipfile", ".env", ".env.example"]:
        fp = cwd / dep_file
        if fp.exists():
            content = fp.read_text(errors="ignore").lower()
            if "psycopg" in content or "postgresql" in content:
                detected["postgresql"] = True
            if "pgvector" in content:
                detected["pgvector"] = True

    # Docker
    if (cwd / "Dockerfile").exists() or (cwd / "docker-compose.yml").exists():
        detected["docker"] = True

    # Auth0 / IDaaS
    for dep_file in ["requirements.txt", "pyproject.toml", "package.json", ".env", ".env.example"]:
        fp = cwd / dep_file
        if fp.exists() and "auth0" in fp.read_text(errors="ignore").lower():
            detected["auth0_configured"] = True
            break

    return detected


def detect_domain_flags(cwd: Path) -> dict:
    """Detecta flags de domínio (saúde, privacidade) nos arquivos de spec e config."""
    flags = {}

    health_keywords = [
        r"\bhipaa\b", r"\blgpd\b", r"\bgdpr\b", r"\bphi\b", r"\bpii\b",
        r"\bhealth[_ ]data\b", r"\bdado[s]?[_ ]de[_ ]saúde\b",
        r"\bbiom[aá]rker\b", r"\bexame\b", r"\bpaciente\b", r"\bcl[íi]nico\b",
    ]

    scan_dirs = ["specs", ".vitalia", "docs", "."]
    scan_extensions = [".md", ".toml", ".yaml", ".yml", ".txt"]

    for scan_dir in scan_dirs:
        target = cwd / scan_dir
        if not target.exists():
            continue
        glob_pattern = "**/*" if scan_dir != "." else "*"
        for ext in scan_extensions:
            for fp in target.glob(f"{glob_pattern}{ext}"):
                try:
                    content = fp.read_text(errors="ignore").lower()
                    for kw in health_keywords:
                        if re.search(kw, content):
                            flags["health_data_detected"] = True
                            if re.search(r"\bhipaa\b", content):
                                flags["hipaa_required"] = True
                            if re.search(r"\blgpd\b", content):
                                flags["lgpd_required"] = True
                            if re.search(r"\bgdpr\b", content):
                                flags["gdpr_required"] = True
                            break
                except Exception:
                    pass
            if flags.get("health_data_detected"):
                break

    return flags


def main():
    parser = argparse.ArgumentParser(
        description="Vitalia Kit — Scan Passivo de Ambiente"
    )
    parser.add_argument(
        "--cwd",
        type=str,
        default=os.getcwd(),
        help="Diretório raiz do projeto a ser analisado.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve()

    if not cwd.exists():
        print(f"[scan_environment] AVISO: --cwd '{cwd}' não existe. Usando vazio.", file=sys.stderr)
        context = {"error": f"cwd not found: {cwd}", "technologies": {}, "domain_flags": {}}
    else:
        technologies = detect_technologies(cwd)
        domain_flags = detect_domain_flags(cwd)
        context = {
            "scanned_cwd": str(cwd),
            "technologies": technologies,
            "domain_flags": domain_flags,
        }

    VITALIA_TMP.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(context, indent=2, ensure_ascii=False))

    print(f"[scan_environment] OK — tecnologias detectadas: {list(technologies.keys())}")
    print(f"[scan_environment] flags de domínio: {list(domain_flags.keys())}")
    print(f"[scan_environment] resultado em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
