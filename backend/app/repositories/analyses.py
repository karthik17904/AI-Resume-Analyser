import sqlite3, json, os
from pathlib import Path
from typing import Optional
DB=Path(os.getenv('ANALYSER_DB',str(Path(__file__).resolve().parents[3]/'analyses.sqlite3')))

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, created_at TEXT, filename TEXT, job_title TEXT, score INTEGER, role TEXT, data TEXT)')
    return conn

def save(result):
    with connect() as conn:
        conn.execute('INSERT INTO analyses VALUES (?,?,?,?,?,?,?)',(result['id'],result['created_at'],result['filename'],result['job_title'],result['score'],result['predicted_role'],json.dumps(result)))

def list_recent(limit=100):
    with connect() as conn:return [dict(x) for x in conn.execute('SELECT id,created_at,filename,job_title,score,role FROM analyses ORDER BY created_at DESC LIMIT ?',(limit,)).fetchall()]

def get(analysis_id):
    with connect() as conn:
        row=conn.execute('SELECT data FROM analyses WHERE id=?',(analysis_id,)).fetchone()
        return json.loads(row['data']) if row else None

def remove(analysis_id):
    with connect() as conn:return bool(conn.execute('DELETE FROM analyses WHERE id=?',(analysis_id,)).rowcount)
