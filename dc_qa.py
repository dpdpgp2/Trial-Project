"""
dc_qa.py  —  Ask-the-Analyst: GitHub Issues queue -> grounded answers -> qa_log.json.

Queue = open issues labeled 'analyst-question' (created by dashboard/api/ask.js).
Each run: sanitize + answer the oldest 5, comment + close their issues, append to
qa_log.json (the export source — answered items persist after issues close).
Unanswered questions stay open and are retried next run. Non-fatal by contract.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

import dc_ai

LOG_PATH = os.path.join(os.path.dirname(__file__), "qa_log.json")
LABEL = "analyst-question"
MAX_PER_RUN, MAX_Q_CHARS, MIN_Q_CHARS, MAX_LOG = 5, 300, 10, 200


def _gh(method, path, token, body=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(body).encode() if body is not None else None, method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "User-Agent": "dc-pipeline"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "ignore") or "null")


def _extract_q(issue):
    body = issue.get("body") or ""
    m = re.search(r"\{.*\}", body, re.S)
    if m:
        try:
            return (json.loads(m.group(0)).get("q") or "").strip()
        except Exception:
            pass
    return (issue.get("title") or "").removeprefix("Q: ").strip()


def _close(issue, token, repo, comment):
    n = issue["number"]
    try:
        _gh("POST", f"/repos/{repo}/issues/{n}/comments", token, {"body": comment})
        _gh("PATCH", f"/repos/{repo}/issues/{n}", token, {"state": "closed"})
    except Exception as e:
        print(f"  [qa] close #{n}: {e}")


def _load_log():
    try:
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def run(tabs, computed, register):
    """Answer queued dashboard questions. -> public qa list (newest first, <=20)."""
    log = _load_log()
    out = list(log)
    try:
        from dc_export import _SECRET_PATTERNS
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY") or "dpdpgp2/Trial-Project"
        if not token:
            return out[:MAX_LOG]
        issues = _gh("GET", f"/repos/{repo}/issues?labels={LABEL}&state=open"
                            f"&sort=created&direction=asc&per_page={MAX_PER_RUN}", token)
        if not issues:
            return out[:MAX_LOG]
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        pending = []
        for it in issues:
            q = _extract_q(it)
            entry = {"id": f"q-{it['number']}", "q": q[:MAX_Q_CHARS],
                     "asked_at": it.get("created_at"), "a": None,
                     "answered_at": None, "evidence_ids": [], "state_cites": []}
            if (len(q) > MAX_Q_CHARS or len(q) < MIN_Q_CHARS
                    or any(re.search(p, q) for p in _SECRET_PATTERNS)):
                entry.update(status="rejected", answered_at=now)
                _close(it, token, repo,
                       "Rejected by sanitation (length or content). Ask again in 10-300 plain characters.")
                log.insert(0, entry)
            else:
                pending.append((it, entry))

        answers = {}
        key = os.environ.get("OPENROUTER_API_KEY")
        if pending and key:
            ok, note, _rem = dc_ai.test_connection(key)
            if ok:
                answers = dc_ai.answer_questions(
                    key, tabs, computed, register, [{"id": e["id"], "q": e["q"]} for _, e in pending])
            else:
                print(f"  [qa] answering skipped ({note})")

        still_open = []
        for it, entry in pending:
            ans = answers.get(entry["id"])
            if ans:
                entry.update(status="answered", a=ans["a"], answered_at=now,
                             evidence_ids=[i for i in ans["evidence_ids"] if i in (register or {})],
                             state_cites=ans.get("state_cites") or [])
                _close(it, token, repo, ans["a"])
                log.insert(0, entry)
            else:
                still_open.append(dict(entry, status="pending"))  # retried next run

        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log[:MAX_LOG], f, ensure_ascii=False, indent=1)
        out = still_open + log
        n_ans = sum(1 for e in log[:MAX_PER_RUN] if e.get("status") == "answered")
        print(f"  Q&A -> {n_ans} answered, {len(still_open)} pending")
    except Exception as e:
        print(f"  [qa] non-fatal error: {e}")
    return out[:MAX_LOG]
