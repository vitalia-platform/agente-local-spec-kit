#!/usr/bin/env python3
import os
import json

def load_schema(schema_path):
    """
    Carrega o schema JSON especificado do disco.
    
    Args:
        schema_path (str): Caminho absoluto para o arquivo de schema JSON.
        
    Returns:
        list: Uma lista contendo as chaves (keys) permitidas pelo schema.
    """
    if not os.path.exists(schema_path):
        print(f"⚠️ Schema não encontrado em {schema_path}")
        return []
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        try:
            schema_data = json.load(f)
            # O schema define as chaves esperadas. Retornamos apenas a lista de chaves.
            return list(schema_data.keys())
        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao decodificar schema {schema_path}: {e}")
            return []

def migrate_history(jsonl_path, expected_keys):
    """
    Lê o histórico de sessões linha a linha e mapeia as chaves antigas 
    para o formato novo definido pelo schema.
    
    Args:
        jsonl_path (str): Caminho absoluto para o arquivo session_history.jsonl
        expected_keys (list): Lista de chaves permitidas na versão atual do schema
    """
    if not os.path.exists(jsonl_path):
        print(f"⚠️ Arquivo de histórico não encontrado: {jsonl_path}")
        return

    migrated_lines = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                new_entry = {}
                
                # Mapeamento de chaves legadas para as chaves do schema v0.5.0
                for key in expected_keys:
                    if key == "machine_name":
                        new_entry[key] = entry.get("machine", entry.get("machine_name", "Unknown"))
                    elif key == "last_sync":
                        new_entry[key] = entry.get("timestamp", entry.get("last_sync", "Unknown"))
                    elif key == "steps":
                        new_entry[key] = entry.get("activities", entry.get("steps", ["N/A"]))
                    elif key == "next_step":
                        new_entry[key] = entry.get("p0", entry.get("next_step", "Unknown"))
                    elif key == "mode":
                        new_entry[key] = entry.get("mode", "auto")
                    else:
                        # Para chaves que não mudaram de nome (machine_id, task, status)
                        new_entry[key] = entry.get(key, "Unknown")
                        
                migrated_lines.append(new_entry)
            except json.JSONDecodeError:
                print(f"⚠️ Ignorando linha inválida: {line}")
                
    # Salvar backup antes de sobrescrever
    backup_path = f"{jsonl_path}.bak"
    os.rename(jsonl_path, backup_path)
    print(f"✅ Backup salvo em {backup_path}")
    
    # Escrever o novo arquivo migrado
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for entry in migrated_lines:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
    print(f"✅ Migração concluída com sucesso. {len(migrated_lines)} registros processados.")

def main():
    """
    Função principal que orquestra a migração:
    1. Carrega as chaves válidas a partir do session_history_schema.json
    2. Encontra o arquivo session_history.jsonl local do projeto
    3. Chama a função de migração
    """
    # Determinar diretório base (~/.vitalia/kit)
    kit_dir = os.path.expanduser("~/.vitalia/kit")
    schema_path = os.path.join(kit_dir, "config", "schemas", "session_history_schema.json")
    
    expected_keys = load_schema(schema_path)
    if not expected_keys:
        print("❌ Falha ao carregar schema. Abortando migração.")
        return
        
    print(f"🔍 Chaves esperadas pelo Schema v0.5.0: {expected_keys}")
    
    # Diretório do projeto atual
    cwd = os.getcwd()
    history_path = os.path.join(cwd, ".vitalia", "memory", "session", "data", "session_history.jsonl")
    
    print(f"🚀 Iniciando migração de {history_path}")
    migrate_history(history_path, expected_keys)

if __name__ == "__main__":
    main()
