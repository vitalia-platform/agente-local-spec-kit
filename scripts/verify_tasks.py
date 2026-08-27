import os
import sys
import re
import json
import requests
from typing import List, Dict

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.environ.get("REVIEW_LLM_PROFILE", "qwen3:4b")

def extract_tasks_from_markdown(filepath: str) -> List[Dict[str, str]]:
    tasks = []
    if not os.path.exists(filepath):
        return tasks
    
    with open(filepath, 'r') as f:
        content = f.read()

    matches = re.finditer(r'- \[\s*\]\s+(T\d{3}[-A-Z0-9]*)\s*(.*?)(?=\n- \[\s*\]|\n\n|\Z)', content, re.DOTALL)
    for match in matches:
        tasks.append({
            "id": match.group(1).strip(),
            "content": match.group(2).strip()
        })
    return tasks

def check_task_with_llm(task: Dict[str, str], rule_text: str) -> bool:
    prompt = f"""
    Você é um juiz de conformidade cirúrgico.
    REGRA DE CONSTITUIÇÃO:
    {rule_text}

    TAREFA PROPOSTA:
    [{task['id']}] {task['content']}

    A Tarefa Proposta viola a Regra de Constituição?
    Responda APENAS com um JSON estrito: {{"violation": true, "reason": "motivo..."}} ou {{"violation": false, "reason": "ok"}}
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "temperature": 0.0
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json().get("response", "{}").strip()
        if result.startswith("```json"):
            result = result[7:]
        elif result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()
        verdict = json.loads(result)
        return verdict.get("violation", False), verdict.get("reason", "")
    except Exception as e:
        print(f"Erro na inferência do LLM para a tarefa {task['id']}: {e}")
        try:
            print(f"Raw result: {result}")
        except:
            pass
        return True, "Falha de inferência. Revisão humana obrigatória."

def main():
    tasks_file = sys.argv[1] if len(sys.argv) > 1 else ".vitalia/specs/active/tasks.md"
    print(f"[Task Verifier] Iniciando Verificação Híbrida (Código + LLM) em {tasks_file}...")
    print(f"[Task Verifier] Modelo ativo: {MODEL_NAME}")
    
    tasks = extract_tasks_from_markdown(tasks_file)
    if not tasks:
        print("[Task Verifier] Nenhuma tarefa encontrada ou arquivo inexistente.")
        exit(0)
    
    medical_gate_rule = "Nunca permita que uma tarefa implemente lógica clínica de saúde sem revisão de um especialista aprovado."
    
    violations_found = False
    for task in tasks:
        print(f"Checando {task['id']}...")
        is_violating, reason = check_task_with_llm(task, medical_gate_rule)
        if is_violating:
            print(f"⛔ VIOLAÇÃO BLOQUEANTE ({task['id']}): {reason}")
            violations_found = True
        else:
            print(f"✅ {task['id']} aprovada.")
            
    if violations_found:
        print("\n[BLOCKED] O workflow foi interrompido. Corrija o tasks.md antes de rodar /vitalia-spec-implement.")
        exit(1)
    else:
        print("\n[PASS] Todas as tarefas aderem à constituição. Liberado para /vitalia-spec-implement.")
        exit(0)

if __name__ == "__main__":
    main()
