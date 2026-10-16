import os, re, requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
JENKINS_URL = os.environ["JENKINS_URL"].rstrip("/")
AUTH = (os.environ["JENKINS_USER"], os.environ["JENKINS_TOKEN"])
JOB = os.environ.get("JENKINS_JOB", "deploy-project")

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/submit")
def submit():
    name = request.form.get("project_name", "").strip().lower()
    email = request.form.get("email", "").strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,30}", name):
        return jsonify(error="Use 3-31 chars: lowercase letters, digits, hyphen"), 400
    r = requests.post(f"{JENKINS_URL}/job/{JOB}/buildWithParameters",
                      params={"PROJECT_NAME": name, "SUBMITTED_BY": email},
                      auth=AUTH, timeout=10)
    if r.status_code not in (200, 201):
        return jsonify(error=f"Jenkins returned {r.status_code}"), 502
    queue_id = r.headers["Location"].rstrip("/").split("/")[-1]
    return jsonify(queue_id=queue_id)

@app.get("/status")
def status():
    qid = request.args.get("queue_id", "")
    if not qid.isdigit():
        return jsonify(error="bad id"), 400
    q = requests.get(f"{JENKINS_URL}/queue/item/{qid}/api/json", auth=AUTH, timeout=10)
    if q.status_code == 404:
        return jsonify(state="UNKNOWN")
    item = q.json()
    if item.get("cancelled"):
        return jsonify(state="CANCELLED")
    if "executable" not in item:
        return jsonify(state="QUEUED")
    num = item["executable"]["number"]
    b = requests.get(f"{JENKINS_URL}/job/{JOB}/{num}/api/json", auth=AUTH, timeout=10).json()
    if b["building"]:
        return jsonify(state="BUILDING", build=num)
    return jsonify(state=b["result"], build=num, url=b.get("description"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
