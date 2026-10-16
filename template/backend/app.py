import os, psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def conn():
    return psycopg2.connect(host=os.environ["DB_HOST"], dbname=os.environ["DB_NAME"],
                            user=os.environ["DB_USER"], password=os.environ["DB_PASS"])

@app.get("/api/health")
def health():
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT 1")
    return jsonify(status="ok", project=os.environ.get("PROJECT_NAME"))

@app.get("/api/notes")
def list_notes():
    with conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, text FROM notes ORDER BY id DESC")
        return jsonify([{"id": r[0], "text": r[1]} for r in cur.fetchall()])

@app.post("/api/notes")
def add_note():
    with conn() as c, c.cursor() as cur:
        cur.execute("INSERT INTO notes(text) VALUES (%s)", (request.json["text"],))
    return jsonify(ok=True), 201
