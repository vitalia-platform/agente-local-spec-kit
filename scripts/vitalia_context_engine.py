#!/usr/bin/env python3
import os
import argparse
import glob
import re
import hashlib
import socket
import json
import yaml
from datetime import datetime, timedelta

def generate_id(category, content):
    return hashlib.sha256(f"{category}{content[:128]}".encode()).hexdigest()[:16]

def get_machine_id():
    return hashlib.sha256(socket.gethostname().encode()).hexdigest()[:8]

def get_machine_name():
    return socket.gethostname()

def read_jsonl(filepath):
    if not os.path.exists(filepath):
        return []
    result = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return result

def append_jsonl(filepath, entry_dict):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry_dict) + '\n')

def read_shard_yaml(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError:
            return {}

def write_shard_yaml(filepath, data_dict):
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data_dict, f, default_flow_style=False, sort_keys=False)

def upsert_machines_json(session_dir, machine_id, name):
    filepath = os.path.join(session_dir, 'data', 'machines.json')
    data = {"machines": {}}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    if "machines" not in data:
        data["machines"] = {}
    
    data["machines"][machine_id] = {
        "name": name,
        "last_seen": get_timestamp()
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def check_semaphore(session_dir):
    filepath = os.path.join(session_dir, 'DASHBOARD.md')
    if not os.path.exists(filepath):
        return (False, None, None)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'## Semáforo de Sincronização\n\n- \*\*Status:\*\* (LOCKED|LIVRE)\s*\n- \*\*Máquina:\*\* (.*?)\s*\n- \*\*Expira em:\*\* (.*?)\s*\n', content)
    if match:
        status, machine_id, expires_at = match.groups()
        is_locked = (status == 'LOCKED')
        return (is_locked, machine_id if machine_id != 'N/A' else None, expires_at if expires_at != 'N/A' else None)
    return (False, None, None)

def set_semaphore(session_dir, status, machine_id):
    filepath = os.path.join(session_dir, 'DASHBOARD.md')
    
    if status == 'LOCKED':
        expires_at = (datetime.utcnow() - timedelta(hours=4) + timedelta(minutes=5)).strftime('%d-%m-%Y %H:%M:%S(GMT-04:00)')
    else:
        expires_at = 'N/A'
        machine_id = 'N/A'
        
    semaphore_block = f"## Semáforo de Sincronização\n\n- **Status:** {status}\n- **Máquina:** {machine_id}\n- **Expira em:** {expires_at}\n"
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content, count = re.subn(r'## Semáforo de Sincronização\n\n- \*\*Status:\*\* .*?\n- \*\*Máquina:\*\* .*?\n- \*\*Expira em:\*\* .*?\n', semaphore_block, content)
        if count == 0:
            new_content = content + "\n\n" + semaphore_block
    else:
        new_content = f"<!-- DASHBOARD.md | Atualizado em: {get_timestamp()} -->\n\n# Dashboard de Contexto\n\n" + semaphore_block
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def generate_grounding_yaml(session_dir):
    """T006: Merge global grounding-domains.yaml + local JSONL entries -> grounding-domains-local.yaml.
    Entries without a scope_decision remain pending and are NOT included in the output yaml.
    """
    kit_dir = os.path.expanduser('~/.vitalia/kit')
    global_path = os.path.join(kit_dir, 'config', 'grounding-domains.yaml')
    jsonl_path = os.path.join(session_dir, 'data', 'grounding-domains.jsonl')
    output_path = os.path.join(session_dir, 'grounding-domains-local.yaml')

    global_data = {}
    if os.path.exists(global_path):
        try:
            with open(global_path, 'r', encoding='utf-8') as f:
                global_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"⚠️  grounding-domains.yaml global mal-formado: {e}")
    else:
        print(f"⚠️  grounding-domains.yaml global não encontrado em {global_path}")

    base_version = global_data.get('version', 'unknown')
    domains = dict(global_data.get('domains', {}))
    exempt_domains = list(global_data.get('exempt_domains', []))

    entries = read_jsonl(jsonl_path)

    scope_map = {}
    for e in entries:
        if e.get('type') == 'scope_decision' and 'target_id' in e and 'scope' in e:
            scope_map[e['target_id']] = e['scope']

    local_entries_count = 0
    pending_count = 0
    for e in entries:
        eid = e.get('id')
        etype = e.get('type')
        if etype == 'scope_decision':
            continue
        if etype == 'exempt':
            desc = e.get('domain_description', '')
            if desc and desc not in exempt_domains:
                exempt_domains.append(desc)
                local_entries_count += 1
            continue
        scope = scope_map.get(eid)
        if scope is None:
            pending_count += 1
            continue
        if scope == 'rejected':
            continue
        if etype == 'new_domain':
            domain_key = e.get('domain', '')
            if domain_key and domain_key not in domains:
                domains[domain_key] = {
                    'description': e.get('description', ''),
                    'mandatory_search': True,
                    'authoritative_sources': e.get('authoritative_sources', []),
                    'source': f"local | {e.get('timestamp', '')} | machine: {e.get('machine_id', '')}"
                }
                local_entries_count += 1
        elif etype == 'new_source':
            domain_key = e.get('domain', '')
            if domain_key and domain_key in domains:
                existing = domains[domain_key].get('authoritative_sources', [])
                for src in e.get('authoritative_sources', []):
                    if src not in existing:
                        existing.append(src)
                domains[domain_key]['authoritative_sources'] = existing
                local_entries_count += 1

    output = {
        'base_version': base_version,
        'local_entries': local_entries_count,
        'pending_curadoria': pending_count,
        'last_generated': get_timestamp(),
        'domains': domains,
        'exempt_domains': exempt_domains
    }
    header = (
        f"# grounding-domains-local.yaml | GERADO pelo vitalia_context_engine.py\n"
        f"# NAO EDITE ESTE ARQUIVO — use data/grounding-domains.jsonl para customizar\n"
        f"# Ultima geracao: {get_timestamp()}\n"
        f"# Pendentes de curacao: {pending_count}\n\n"
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        yaml.safe_dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✅ grounding-domains-local.yaml gerado ({local_entries_count} locais, {pending_count} pendentes)")
    return pending_count

def generate_dashboard(session_dir, shards, machines, grounding_pending=0):
    project_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(session_dir))))
    is_locked, lock_machine, expires_at = check_semaphore(session_dir)
    status_str = "LOCKED" if is_locked else "LIVRE"
    lock_machine = lock_machine or "N/A"
    expires_at = expires_at or "N/A"
    
    semaphore_block = f"## Semáforo de Sincronização\n\n- **Status:** {status_str}\n- **Máquina:** {lock_machine}\n- **Expira em:** {expires_at}\n"
    
    readme_content = f"<!-- DASHBOARD.md | Atualizado em: {get_timestamp()} -->\n\n"
    readme_content += f"# Dashboard de Contexto: {project_name}\n\n"
    readme_content += semaphore_block + "\n"
    
    readme_content += "## Shards Ativos\n\n"
    readme_content += "| Máquina | Tarefa Atual | Etapas | Status | Último Sync | Próximo Passo (P0) |\n"
    readme_content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    
    for s in shards:
        machine_name = machines.get("machines", {}).get(s.get('machine_id', ''), {}).get("name", s.get('machine', 'Unknown'))
        stale_badge = check_staleness(s.get('last_sync', 'Unknown'))
        readme_content += f"| **{machine_name}** ({s.get('machine_id', 'Unknown')}) | {s.get('task', 'Unknown')} | {s.get('steps', 'Unknown')} | {s.get('status', 'Unknown')} | {stale_badge}{s.get('last_sync', 'Unknown')} | {s.get('p0', 'Unknown')} |\n"

    readme_content += "\n## Arquitetura de Contexto\n\n```mermaid\ngraph TD\n"
    readme_content += f"  Raiz[\"Repositório Raiz ({project_name})\"]\n"
    for s in shards:
        safe_id = s.get('machine_id', 'Unknown').replace('-', '_').replace(' ', '_')
        machine_name = machines.get("machines", {}).get(s.get('machine_id', ''), {}).get("name", s.get('machine', 'Unknown'))
        safe_machine = machine_name.replace('(', '').replace(')', '').replace('"', '')
        readme_content += f"  {safe_id}[\"Shard: {safe_machine}\"] --> Raiz\n"
    readme_content += "```\n"

    # T008: Guard Rails de Grounding section
    local_yaml_path = os.path.join(session_dir, 'grounding-domains-local.yaml')
    global_yaml_path = os.path.expanduser('~/.vitalia/kit/config/grounding-domains.yaml')
    global_status = "✅ Ativo" if os.path.exists(global_yaml_path) else "⚠️ Ausente"
    if os.path.exists(local_yaml_path):
        from datetime import timedelta
        local_mtime = datetime.fromtimestamp(os.path.getmtime(local_yaml_path)) - timedelta(hours=4)
        local_date = local_mtime.strftime('%d-%m-%Y %H:%M')
        local_status = f"✅ Presente — {local_date}"
        local_link = "[grounding-domains-local.yaml](./grounding-domains-local.yaml)"
    else:
        local_status = "⚠️ Ausente (rodar --action init)"
        local_link = "N/A"
    pending_badge = f"⚠️ {grounding_pending} entradas aguardando curação" if grounding_pending > 0 else "✅ 0 pendentes"
    readme_content += "\n## Guard Rails de Grounding\n\n"
    readme_content += "| Arquivo | Status | Pendentes |\n"
    readme_content += "| :--- | :--- | :--- |\n"
    readme_content += f"| `grounding-domains.yaml` (global) | {global_status} | — |\n"
    readme_content += f"| {local_link} (projeto) | {local_status} | {pending_badge} |\n"

    dashboard_path = os.path.join(session_dir, 'DASHBOARD.md')
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

def generate_session_state(session_dir, shards):
    active_feature = "Nenhuma"
    p0 = "Definir o escopo"
    
    if shards:
        best_shard = shards[-1]
        active_feature = best_shard.get('task', 'Nenhuma')
        p0 = best_shard.get('p0', 'Definir o escopo')
        
    state_path = os.path.join(session_dir, 'SESSION_STATE.md')
    content = f"<!-- SESSION_STATE.md | Atualizado em: {get_timestamp()} -->\n\n"
    content += "# Estado da Sessão\n"
    content += f"**Feature ativa:** {active_feature}\n\n"
    content += f"## Próximo Passo (P0)\n- {p0}\n\n"
    content += "**Arquivos em edição:**\nNenhum\n"
    
    with open(state_path, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_view_md(session_dir, jsonl_filename, output_filename, title):
    jsonl_path = os.path.join(session_dir, 'data', jsonl_filename)
    md_path = os.path.join(session_dir, output_filename)
    
    entries = read_jsonl(jsonl_path)
    
    content = f"<!-- {output_filename} | Atualizado em: {get_timestamp()} -->\n\n"
    content += f"# {title}\n\n"
    
    seen_ids = set()
    for entry in entries:
        eid = entry.get('id')
        if eid and eid in seen_ids:
            continue
        if eid:
            seen_ids.add(eid)
            
        content += f"- "
        if 'content' in entry:
            content += f"{entry['content']}"
        elif 'decision' in entry:
            content += f"{entry['decision']}"
        elif 'learning' in entry:
            content += f"{entry['learning']}"
        else:
            content += f"{json.dumps(entry, ensure_ascii=False)}"
        
        if 'machine_id' in entry:
            content += f" `[{entry['machine_id']}]`"
        content += "\n"
        
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_timestamp():
    # Retorna o timestamp no formato esperado (GMT-04:00)
    now = datetime.utcnow() - timedelta(hours=4)
    return now.strftime('%d-%m-%Y %H:%M:%S(GMT-04:00)')

def parse_shard(filepath):
    shard = {
        'machine': 'Unknown',
        'machine_id': 'Unknown',
        'last_sync': 'Unknown',
        'task': 'Unknown',
        'steps': 'Unknown',
        'status': 'Unknown',
        'p0': 'Unknown'
    }
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith('# Shard:'):
                match = re.search(r'# Shard: (.*) \((.*)\)', line)
                if match:
                    shard['machine'] = match.group(1)
                    shard['machine_id'] = match.group(2)
            elif line.startswith('**Último sync:**'):
                shard['last_sync'] = line.replace('**Último sync:**', '').strip()
            elif line.startswith('**Tarefa:**'):
                shard['task'] = line.replace('**Tarefa:**', '').strip()
            elif line.startswith('**Etapas:**'):
                shard['steps'] = line.replace('**Etapas:**', '').strip()
            elif line.startswith('**Status:**'):
                shard['status'] = line.replace('**Status:**', '').strip()
            elif line.startswith('## Próximo Passo (P0)'):
                current_section = 'p0'
                shard['p0'] = ''
            elif current_section == 'p0' and line:
                if not line.startswith('##'):
                    shard['p0'] += line + ' '
                else:
                    current_section = None
    except Exception as e:
        print(f"Error parsing shard {filepath}: {e}")
    
    shard['p0'] = shard['p0'].strip() if shard['p0'] != 'Unknown' else 'Unknown'
    return shard

def check_staleness(last_sync_str):
    try:
        # Extrai DD-MM-YYYY HH:MM:SS ignorando o fuso
        time_str = last_sync_str.split('(')[0].strip()
        last_sync = datetime.strptime(time_str, '%d-%m-%Y %H:%M:%S')
        now = datetime.utcnow() - timedelta(hours=4)
        if (now - last_sync).total_seconds() > 24 * 3600:
            return "⚠️ "
    except:
        pass
    return ""

def init_context(session_dir):
    os.makedirs(session_dir, exist_ok=True)
    os.makedirs(os.path.join(session_dir, 'shards'), exist_ok=True)
    
    data_dir = os.path.join(session_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    for f in ['learnings.jsonl', 'decisions.jsonl', 'session_history.jsonl', 'grounding-domains.jsonl']:
        filepath = os.path.join(data_dir, f)
        if not os.path.exists(filepath):
            open(filepath, 'w').close()
            print(f"✅ Criado {filepath}")
            
    machines_path = os.path.join(data_dir, 'machines.json')
    if not os.path.exists(machines_path):
        with open(machines_path, 'w', encoding='utf-8') as f:
            f.write('{"machines": {}}\n')
        print(f"✅ Criado {machines_path}")

    # T009: Create initial grounding-domains-local.yaml if absent
    local_yaml = os.path.join(session_dir, 'grounding-domains-local.yaml')
    if not os.path.exists(local_yaml):
        generate_grounding_yaml(session_dir)

def consolidate_context(session_dir):
    is_locked, lock_machine, expires_at = check_semaphore(session_dir)
    if is_locked:
        try:
            exp_time = datetime.strptime(expires_at.split('(')[0].strip(), '%d-%m-%Y %H:%M:%S')
            now = datetime.utcnow() - timedelta(hours=4)
            if now < exp_time:
                print(f"❌ Abortado: Semáforo LOCKED por {lock_machine} até {expires_at}")
                return
        except:
            pass
            
    my_machine_id = get_machine_id()
    set_semaphore(session_dir, 'LOCKED', my_machine_id)
    print(f"🔒 Semáforo adquirido por {my_machine_id}")
    
    shards_dir = os.path.join(session_dir, 'shards')
    shards = []
    
    for filepath in glob.glob(os.path.join(shards_dir, '*.yaml')):
        shards.append(read_shard_yaml(filepath))
        
    data_dir = os.path.join(session_dir, 'data')
    machines_path = os.path.join(data_dir, 'machines.json')
    machines = {}
    if os.path.exists(machines_path):
        with open(machines_path, 'r', encoding='utf-8') as f:
            try:
                machines = json.load(f)
            except:
                pass
                
    # T007: generate grounding yaml and capture pending count for dashboard
    pending = generate_grounding_yaml(session_dir)
    generate_dashboard(session_dir, shards, machines, grounding_pending=pending)
    generate_session_state(session_dir, shards)
    generate_view_md(session_dir, 'learnings.jsonl', 'LEARNINGS.md', 'Aprendizados da Sessão')
    generate_view_md(session_dir, 'decisions.jsonl', 'DECISIONS.md', 'Decisões Arquiteturais')
    generate_view_md(session_dir, 'session_history.jsonl', 'SESSION_HISTORY.md', 'Histórico de Sessões')
    
    set_semaphore(session_dir, 'LIVRE', 'N/A')
    print(f"🔓 Semáforo liberado")
    print("✅ Consolidação concluída")

def migrate_context(session_dir):
    print("🚀 Iniciando migração...")
    for md_file, jsonl_file in [('LEARNINGS.md', 'learnings.jsonl'), ('DECISIONS.md', 'decisions.jsonl')]:
        md_path = os.path.join(session_dir, md_file)
        jsonl_path = os.path.join(session_dir, 'data', jsonl_file)
        
        if os.path.exists(md_path) and not md_path.endswith('.bak'):
            with open(md_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            existing = read_jsonl(jsonl_path)
            existing_ids = {e.get('id') for e in existing if 'id' in e}
            
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    content = line[2:]
                    entry_id = generate_id('migration', content)
                    if entry_id not in existing_ids:
                        entry = {
                            "id": entry_id,
                            "content": content,
                            "ts_confidence": "estimated",
                            "machine_id": "pre-migration",
                            "timestamp": get_timestamp()
                        }
                        append_jsonl(jsonl_path, entry)
                        existing_ids.add(entry_id)
            
            os.rename(md_path, md_path + '.bak')
            print(f"✅ Migrado {md_file} para JSONL e renomeado para .bak")

    shards_dir = os.path.join(session_dir, 'shards')
    for filepath in glob.glob(os.path.join(shards_dir, '*.md')):
        if not filepath.endswith('.bak'):
            shard = parse_shard(filepath)
            mid = shard.get('machine_id', 'Unknown')
            if mid == 'Unknown':
                mid = get_machine_id()
            yaml_path = os.path.join(shards_dir, f"{mid}.yaml")
            write_shard_yaml(yaml_path, shard)
            os.rename(filepath, filepath + '.bak')
            print(f"✅ Migrado shard {os.path.basename(filepath)} para {os.path.basename(yaml_path)}")
        
    consolidate_context(session_dir)

def main():
    parser = argparse.ArgumentParser(description="Vitalia Context Engine")
    parser.add_argument("--action", choices=['init', 'start', 'end', 'consolidate', 'update-shard', 'migrate'], required=True)
    parser.add_argument("--session-dir", default=".vitalia/memory/session")
    parser.add_argument("--machine-id", default="local")
    
    args = parser.parse_args()
    
    if args.action == 'init':
        init_context(args.session_dir)
    elif args.action == 'consolidate':
        consolidate_context(args.session_dir)
    elif args.action == 'migrate':
        migrate_context(args.session_dir)
    elif args.action == 'update-shard':
        print("update-shard via script")

if __name__ == "__main__":
    main()
