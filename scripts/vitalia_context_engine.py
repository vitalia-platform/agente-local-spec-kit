#!/usr/bin/env python3
import os
import argparse
import glob
import re
import hashlib
import socket
import json
import yaml
import subprocess
from datetime import datetime, timedelta, timezone

class ContextEnvironment:
    def __init__(self, session_dir):
        self.session_dir = session_dir
        self.data_dir = os.path.join(session_dir, 'data')
        self.state_dir = os.path.join(session_dir, 'state')
        self.shards_dir = os.path.join(session_dir, 'shards')
        self.machine_id = self._get_machine_id()
        self.machine_name = socket.gethostname()

    def _get_machine_id(self):
        return hashlib.sha256(socket.gethostname().encode()).hexdigest()[:8]

    def get_timestamp(self):
        now = datetime.now(timezone.utc) - timedelta(hours=4)
        return now.strftime('%d-%m-%Y %H:%M:%S(GMT-04:00)')

    def init_dirs(self):
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.shards_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)

class SemaphoreManager:
    def __init__(self, env: ContextEnvironment):
        self.env = env
        self.filepath = os.path.join(self.env.state_dir, 'semaphore.json')

    def check(self):
        if not os.path.exists(self.filepath):
            return (False, None, None)
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            status = data.get('status', 'LIVRE')
            machine_id = data.get('machine_id')
            expires_at = data.get('expires_at')
            return (status == 'LOCKED', machine_id, expires_at)
        except Exception:
            return (False, None, None)

    def set(self, status):
        self.env.init_dirs()
        tmppath = os.path.join(self.env.state_dir, 'semaphore.tmp')
        
        if status == 'LOCKED':
            expires_at = (datetime.now(timezone.utc) - timedelta(hours=4) + timedelta(minutes=10)).strftime('%d-%m-%Y %H:%M:%S(GMT-04:00)')
            machine_id = self.env.machine_id
        else:
            expires_at = None
            machine_id = None
            
        data = {
            "status": status,
            "machine_id": machine_id,
            "expires_at": expires_at,
            "updated_at": self.env.get_timestamp()
        }
        
        with open(tmppath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmppath, self.filepath)

class ShardManager:
    def __init__(self, env: ContextEnvironment):
        self.env = env

    def read_yaml(self, filepath):
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return yaml.safe_load(f) or {}
            except yaml.YAMLError:
                return {}

    def write_yaml(self, filepath, data_dict):
        allowed_keys = {'machine_name', 'machine_id', 'mode', 'steps', 'next_step', 'last_sync', 'task', 'status', 'p0', 'machine'}
        filtered = {k: v for k, v in data_dict.items() if k in allowed_keys}
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.safe_dump(filtered, f, default_flow_style=False, sort_keys=False)

    def load_all_shards(self):
        shards = []
        for filepath in glob.glob(os.path.join(self.env.shards_dir, '*.yaml')):
            shards.append(self.read_yaml(filepath))
        return shards

class EventPublisher:
    def __init__(self, env: ContextEnvironment):
        self.env = env

    def git_pull(self):
        try:
            env_vars = os.environ.copy()
            env_vars['GIT_TERMINAL_PROMPT'] = '0'
            subprocess.run(["git", "pull", "--rebase"], cwd=self.env.session_dir, env=env_vars, timeout=15, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Sincronização remota via Git concluída (pull)")
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout no git pull (15s excedidos). Trabalhando offline.")
        except Exception as e:
            print(f"⚠️  Falha no git pull: {e}. Trabalhando offline.")

    def git_push(self):
        try:
            env_vars = os.environ.copy()
            env_vars['GIT_TERMINAL_PROMPT'] = '0'
            subprocess.run(["git", "add", "."], cwd=self.env.session_dir, env=env_vars, timeout=15, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "commit", "-m", f"chore(context): consolidação automática [{self.env.machine_id}]"], cwd=self.env.session_dir, env=env_vars, timeout=15, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push"], cwd=self.env.session_dir, env=env_vars, timeout=15, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Sincronização remota via Git concluída (push)")
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout no git push (15s excedidos). Confirmações apenas locais.")
        except Exception as e:
            print(f"⚠️  Falha no git push: {e}. Confirmações apenas locais.")

class ViewRenderer:
    def __init__(self, env: ContextEnvironment):
        self.env = env

    def read_jsonl(self, filepath):
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
        
    def generate_view_md(self, jsonl_filename, output_filename, title):
        jsonl_path = os.path.join(self.env.data_dir, jsonl_filename)
        md_path = os.path.join(self.env.session_dir, output_filename)
        
        entries = self.read_jsonl(jsonl_path)
        
        content = f"<!-- {output_filename} | Atualizado em: {self.env.get_timestamp()} -->\n\n"
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

    def generate_session_state(self, shards):
        active_feature = "Nenhuma"
        p0 = "Definir o escopo"
        
        if shards:
            best_shard = shards[-1]
            active_feature = best_shard.get('task', 'Nenhuma')
            p0 = best_shard.get('p0', best_shard.get('next_step', 'Definir o escopo'))
            
        state_path = os.path.join(self.env.session_dir, 'SESSION_STATE.md')
        content = f"<!-- SESSION_STATE.md | Atualizado em: {self.env.get_timestamp()} -->\n\n"
        content += "# Estado da Sessão\n"
        content += f"**Feature ativa:** {active_feature}\n\n"
        content += f"## Próximo Passo (P0)\n- {p0}\n\n"
        content += "**Arquivos em edição:**\nNenhum\n"
        
        with open(state_path, 'w', encoding='utf-8') as f:
            f.write(content)

class DashboardRenderer:
    def __init__(self, env: ContextEnvironment):
        self.env = env
        self.view_renderer = ViewRenderer(env)

    def render(self, shards, machines, is_locked, lock_machine, grounding_pending):
        my_machine_name = self.env.machine_name
        project_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(self.env.session_dir))))
        status_str = "LOCKED" if is_locked else "LIVRE"
        
        badge_status = f"![Status](https://img.shields.io/badge/Status-{status_str}-{'cf222e' if is_locked else '2ea44f'}?style=for-the-badge&logo=github&logoColor=white)"
        badge_semaforo = f"![Semáforo](https://img.shields.io/badge/Semáforo-{'Bloqueado' if is_locked else 'Desbloqueado'}-{'critical' if is_locked else 'success'}?style=for-the-badge)"
        badge_modo = "![Modo](https://img.shields.io/badge/Modo-Integrado%20(Full%20Observability)-8250df?style=for-the-badge)"
        badge_sync = "![Sync](https://img.shields.io/badge/Sync-Multi--Machine%20Cloud-0969da?style=for-the-badge)"
        badge_grounding = f"![Grounding](https://img.shields.io/badge/Grounding-{grounding_pending}%20Pendentes-{'red' if grounding_pending > 0 else 'green'}?style=for-the-badge)"
        
        mermaid_content = "  Cloud((\"Nuvem Central (.vitalia)<br/>origin/main\"))\n"
        for s in shards:
            safe_id = s.get('machine_id', 'Unknown').replace('-', '_').replace(' ', '_')
            machine_name = machines.get("machines", {}).get(s.get('machine_id', ''), {}).get("name", s.get('machine', s.get('machine_name', 'Unknown')))
            safe_machine = machine_name.replace('(', '').replace(')', '').replace('"', '')
            is_active = (safe_machine == my_machine_name)
            status_txt = "● Ativo (Em Sessão)" if is_active else "● " + str(s.get('status', 'Concluído'))
            modo_txt = "Integrado" if is_active else "Standalone"
            mermaid_content += f"  M_{safe_id}[\"{safe_machine} ({safe_id})<br/>{status_txt}<br/>Modo: {modo_txt}\"]\n"
            
        mermaid_content += "\n"
        for s in shards:
            safe_id = s.get('machine_id', 'Unknown').replace('-', '_').replace(' ', '_')
            mermaid_content += f"  Cloud <-->|\"{s.get('last_sync', 'Unknown')}\"| M_{safe_id}\n"
            
        mermaid_content += "\n  style Cloud stroke:#0969da,stroke-width:2px,fill:#ddf4ff,color:#0969da\n"
        for s in shards:
            safe_id = s.get('machine_id', 'Unknown').replace('-', '_').replace(' ', '_')
            if s.get('machine_id') == self.env.machine_id:
                mermaid_content += f"  style M_{safe_id} stroke:#2ea44f,stroke-width:2px,fill:#dafbe1,color:#1a7f37\n"
            else:
                mermaid_content += f"  style M_{safe_id} stroke:#6e7781,stroke-width:1px,fill:#f6f8fa,color:#57606a\n"

        shards_table = ""
        active_shard = None
        for s in shards:
            safe_id = s.get('machine_id', 'Unknown')
            machine_name = machines.get("machines", {}).get(safe_id, {}).get("name", s.get('machine', s.get('machine_name', 'Unknown')))
            task = s.get('task', 'Unknown')
            status = s.get('status', 'Unknown')
            p0 = s.get('p0', s.get('next_step', 'Unknown'))
            sync = s.get('last_sync', 'Unknown')
            is_active = (machine_name == my_machine_name)
            if is_active:
                active_shard = s
                
            env_badge = '<span style="background-color:#8250df;color:white;padding:2px 6px;border-radius:4px;font-size:11px;">Integrado</span>' if is_active else '<span style="background-color:#57606a;color:white;padding:2px 6px;border-radius:4px;font-size:11px;">Standalone</span>'
            status_badge = f'<span style="color:#2ea44f;font-weight:bold;">● {status}</span>' if is_active else f'<span style="color:#2ea44f;">● {status}</span>'
            
            shards_table += f"    <tr>\n      <td><strong>{machine_name}</strong><br/><code>{safe_id}</code></td>\n      <td>{task}</td>\n      <td align=\"center\">{env_badge}</td>\n      <td align=\"center\">{status_badge}</td>\n      <td>{sync}</td>\n      <td>{p0}</td>\n    </tr>\n"

        sessao_ativa = ""
        if active_shard:
            sessao_ativa += f"- **Feature Ativa:** {active_shard.get('task', 'Unknown')}\n"
            sessao_ativa += f"- **Máquina em Execução:** `{self.env.machine_name}` (`{self.env.machine_id}`)\n"
            sessao_ativa += f"- **Semáforo:** `{status_str}`\n"
            sessao_ativa += f"- **Próximo Passo (P0):**\n  > {active_shard.get('p0', active_shard.get('next_step', 'Unknown'))}\n"

        local_yaml_path = os.path.join(self.env.session_dir, 'grounding-domains-local.yaml')
        global_status = "✅ Ativo" 
        if os.path.exists(local_yaml_path):
            local_status = "✅ Presente"
            local_link = "[grounding-domains-local.yaml](./grounding-domains-local.yaml)"
        else:
            local_status = "⚠️ Ausente"
            local_link = "N/A"
        pending_badge = f"⚠️ {grounding_pending} aguardando curação" if grounding_pending > 0 else "✅ 0 pendentes"

        kit_dir = os.path.expanduser('~/.vitalia/kit')
        template_path = os.path.join(kit_dir, 'config', 'templates', 'dashboard_template.md')
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            template = "# Dashboard\n{sessao_ativa}\n```mermaid\ngraph TD\n{mermaid_content}\n```\n<table>{shards_table}</table>"
            
        hist_path = os.path.join(self.env.data_dir, 'session_history.jsonl')
        historico_sessoes = ""
        if os.path.exists(hist_path):
            hist_lines = self.view_renderer.read_jsonl(hist_path)
            for entry in reversed(hist_lines):
                ts = entry.get('timestamp') or entry.get('date') or entry.get('ended_at', 'Desconhecida')
                mach = entry.get('machine', entry.get('machine_name', 'Unknown'))
                mach_id = entry.get('machine_id', 'Unknown')
                task = entry.get('task', 'Unknown')
                summary = entry.get('summary', entry.get('activities', 'Sem resumo.'))
                if isinstance(summary, list):
                    summary = "\n  - ".join([""] + summary).strip()
                p0 = entry.get('p0', entry.get('next_step', 'Unknown'))
                
                historico_sessoes += f"### ✅ Sessão Encerrada em {ts}\n"
                historico_sessoes += f"- **Máquina:** `{mach}` (`{mach_id}`)\n"
                historico_sessoes += f"- **Tarefa:** {task}\n"
                historico_sessoes += f"- **Atividades:**\n  - {summary}\n"
                historico_sessoes += f"- **Próximo Passo:** {p0}\n\n---\n\n"

        dec_path = os.path.join(self.env.data_dir, 'decisions.jsonl')
        decisoes_arquiteturais = ""
        if os.path.exists(dec_path):
            dec_lines = self.view_renderer.read_jsonl(dec_path)
            for entry in reversed(dec_lines):
                mach_id = entry.get('machine_id', 'Unknown')
                dec_title = entry.get('title', entry.get('category', 'Decisão'))
                dec_content = entry.get('decision', entry.get('content', '...'))
                decisoes_arquiteturais += f"| **Máquina** (`{mach_id}`) | **{dec_title}** | {dec_content} |\n"

        readme_content = template.format(
            timestamp=self.env.get_timestamp(),
            project_name=project_name,
            badge_status=badge_status,
            badge_semaforo=badge_semaforo,
            badge_modo=badge_modo,
            badge_sync=badge_sync,
            badge_grounding=badge_grounding,
            mermaid_content=mermaid_content,
            shards_table=shards_table,
            sessao_ativa=sessao_ativa,
            global_status=global_status,
            local_status=local_status,
            local_link=local_link,
            pending_badge=pending_badge,
            historico_sessoes=historico_sessoes,
            decisoes_arquiteturais=decisoes_arquiteturais
        )

        dashboard_path = os.path.join(self.env.session_dir, 'README.md')
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        old_dashboard = os.path.join(self.env.session_dir, 'DASHBOARD.md')
        if os.path.exists(old_dashboard):
            os.remove(old_dashboard)


def generate_grounding_yaml(session_dir):
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

    def read_jsonl_loc(filepath):
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

    entries = read_jsonl_loc(jsonl_path)

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

    def get_timestamp_loc():
        now = datetime.now(timezone.utc) - timedelta(hours=4)
        return now.strftime('%d-%m-%Y %H:%M:%S(GMT-04:00)')

    output = {
        'base_version': base_version,
        'local_entries': local_entries_count,
        'pending_curadoria': pending_count,
        'last_generated': get_timestamp_loc(),
        'domains': domains,
        'exempt_domains': exempt_domains
    }
    header = (
        f"# grounding-domains-local.yaml | GERADO pelo vitalia_context_engine.py\n"
        f"# NAO EDITE ESTE ARQUIVO — use data/grounding-domains.jsonl para customizar\n"
        f"# Ultima geracao: {get_timestamp_loc()}\n"
        f"# Pendentes de curacao: {pending_count}\n\n"
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        yaml.safe_dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✅ grounding-domains-local.yaml gerado ({local_entries_count} locais, {pending_count} pendentes)")
    return pending_count

def init_context(session_dir):
    env = ContextEnvironment(session_dir)
    env.init_dirs()
    for f in ['learnings.jsonl', 'decisions.jsonl', 'session_history.jsonl', 'grounding-domains.jsonl']:
        filepath = os.path.join(env.data_dir, f)
        if not os.path.exists(filepath):
            open(filepath, 'w').close()
            print(f"✅ Criado {filepath}")
            
    machines_path = os.path.join(env.data_dir, 'machines.json')
    if not os.path.exists(machines_path):
        with open(machines_path, 'w', encoding='utf-8') as f:
            f.write('{"machines": {}}\n')
        print(f"✅ Criado {machines_path}")

def consolidate_context(session_dir):
    env = ContextEnvironment(session_dir)
    sem_manager = SemaphoreManager(env)
    shard_manager = ShardManager(env)
    publisher = EventPublisher(env)
    view_renderer = ViewRenderer(env)
    dashboard_renderer = DashboardRenderer(env)

    is_locked, lock_machine, expires_at = sem_manager.check()
    if is_locked:
        try:
            exp_time = datetime.strptime(expires_at.split('(')[0].strip(), '%d-%m-%Y %H:%M:%S')
            now = datetime.now(timezone.utc) - timedelta(hours=4)
            if now < exp_time:
                print(f"❌ Abortado: Semáforo LOCKED por {lock_machine} até {expires_at}")
                return
        except:
            pass
            
    sem_manager.set('LOCKED')
    print(f"🔒 Semáforo adquirido por {env.machine_id}")
    
    publisher.git_pull()
    shards = shard_manager.load_all_shards()
        
    machines_path = os.path.join(env.data_dir, 'machines.json')
    machines = {}
    if os.path.exists(machines_path):
        with open(machines_path, 'r', encoding='utf-8') as f:
            try:
                machines = json.load(f)
            except:
                pass
                
    pending = generate_grounding_yaml(session_dir)
    sem_manager.set('LIVRE')
    print(f"🔓 Semáforo liberado")

    dashboard_renderer.render(shards, machines, False, None, pending)
    view_renderer.generate_session_state(shards)
    view_renderer.generate_view_md('learnings.jsonl', 'LEARNINGS.md', 'Aprendizados da Sessão')
    view_renderer.generate_view_md('decisions.jsonl', 'DECISIONS.md', 'Decisões Arquiteturais')
    view_renderer.generate_view_md('session_history.jsonl', 'SESSION_HISTORY.md', 'Histórico de Sessões')
    
    publisher.git_push()
    print("✅ Consolidação concluída")

def migrate_context(session_dir):
    print("🚀 Migração para schema 0.5.0 foi externalizada para script próprio.")

def main():
    parser = argparse.ArgumentParser(description="Vitalia Context Engine (OOP Refactored)")
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

if __name__ == "__main__":
    main()
