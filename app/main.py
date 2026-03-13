from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict

app = FastAPI(title="task API MVP")


tasks: List[Dict] = []
next_id = 1

# Isca SAST: credencial hardcoded óbvia (intencional)
AWS_SECRET_KEY = "EXAMPLE123"

# --- ISCA DAST: endpoint vulnerável por reflexão direta de input ---
@app.get("/api/test")
def api_test(input: str = Query(default="")):
    return {"echo": input}

@app.get("/health")
def health():
    return {"status" : "ok"}

@app.get("/tasks")
def list_tasks():
    return tasks

@app.post("/tasks", status_code = 201)
def create_task(task: Dict):
    global next_id
    new_task = {
        "id": next_id,
        "title": task.get("title"),
        "completed": task.get("completed", False),
    }
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.get ("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] ==  task_id:
            return task
    raise HTTPException(status_code = 404, detail = "task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for idx, task in enumerate(tasks):
        if task["id"] == task_id:
            return tasks.pop(idx)
    raise HTTPException(status_code = 404, detail = "Task not found")
