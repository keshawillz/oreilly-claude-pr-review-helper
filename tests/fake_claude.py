"""A stand-in for the Claude API so this repo's tests run offline and cost nothing.

This is NOT a model. It finds a handful of seeded patterns with plain string checks
and answers in the same JSON shapes the real API uses. That is enough to exercise
every code path in this repo: structured output, the retry, the tool loop, prompt
caching fields, the MCP request, and batch submission.

Run it by hand to try the demos without spending tokens:

    python tests/fake_claude.py            # prints the two exports to copy
"""
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REQUESTS = []          # every request body the fake received, for tests to inspect
HEADERS = []           # the matching request headers
SEEN_PREFIXES = set()  # cached prefixes, to mimic cache write then cache read

ADDED_RULES = [
    ('query = f"SELECT', "critical", 0.95, "User input is formatted into the SQL string.",
     "Use a parameterized query with ? placeholders."),
    ("offset = page * page_size", "major", 0.9, "Page 1 now skips the first page of rows.",
     "Use (page - 1) * page_size."),
    ("items=[]", "minor", 0.75, "A list default is shared between calls.",
     "Default to None and create the list inside the function."),
    ("except Exception:", "major", 0.85, "The insert error is swallowed and the caller gets None.",
     "Let the exception propagate or log and re-raise."),
    ("return now > expires_at", "critical", 0.95, "The expiry check is inverted.",
     "Return now < expires_at."),
    ("{password}", "critical", 0.97, "The plaintext password is written to the log.",
     "Remove the password from the log line."),
    ('SECRET = "', "critical", 0.96, "A signing secret is committed to the repo.",
     "Read it from the environment."),
    ("with_tax =", "minor", 0.4, "The temporary variable could be inlined.", "Inline it."),
]
REMOVED_RULES = [
    ("if not items:", "total = 0.0", "major", 0.9,
     "An empty list now divides by zero.", "Keep the empty-list guard."),
    ("if order is None:", 'return order["status"]', "major", 0.88,
     "find_order can return None and the result is indexed.", "Raise OrderNotFound when it is None."),
]


def walk_diff(diff_text):
    """Yield (file, new_line_number, text) for visible lines, and collect removed lines."""
    visible, removed = [], []
    current, number = None, 0
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            current = line[4:].strip().removeprefix("b/")
        elif line.startswith("@@"):
            number = int(line.split("+")[1].split(",")[0].split(" ")[0])
        elif current is None or line.startswith("---") or line.startswith("diff "):
            continue
        elif line.startswith("-"):
            removed.append((current, line[1:]))
        elif line.startswith("+") or line.startswith(" "):
            visible.append((current, number, line[1:], line.startswith("+")))
            number += 1
    return visible, removed


def fake_findings(diff_text, read_pricing):
    visible, removed = walk_diff(diff_text)
    findings = []

    def add(file, line, severity, confidence, issue, suggestion):
        findings.append({"severity": severity, "file": file, "line": line, "issue": issue,
                         "suggestion": suggestion, "confidence": confidence})

    for file, number, text, was_added in visible:
        for marker, severity, confidence, issue, suggestion in ADDED_RULES:
            if was_added and marker in text:
                add(file, number, severity, confidence, issue, suggestion)
        # The cross-file bug is only visible after reading pricing.py through a tool.
        if was_added and "apply_discount(subtotal, 15)" in text and read_pricing:
            add(file, number, "major", 0.9, "apply_discount expects a fraction, and 15 raises ValueError.",
                "Pass 0.15.")
    for gone, report_at, severity, confidence, issue, suggestion in REMOVED_RULES:
        for removed_file, removed_text in removed:
            if gone in removed_text:
                for file, number, text, _ in visible:
                    if file == removed_file and report_at in text:
                        add(file, number, severity, confidence, issue, suggestion)
    return findings


def message_text(message):
    content = message["content"]
    if isinstance(content, str):
        return content
    return "\n".join(str(block.get("text") or block.get("content") or "") for block in content)


def answer(body):
    messages = body["messages"]
    diff_text = message_text(messages[0])
    everything = "\n".join(message_text(m) for m in messages)
    tool_names = [t.get("name") for t in body.get("tools", [])]
    content, stop_reason = [], "end_turn"

    wants_pricing = "get_file" in tool_names and "apply_discount(" in diff_text
    if wants_pricing and "tool_result" not in json.dumps(messages):
        content = [{"type": "tool_use", "id": "toolu_fake_1", "name": "get_file",
                    "input": {"path": "app/pricing.py"}}]
        stop_reason = "tool_use"
    elif "output_config" in body:
        findings = fake_findings(diff_text, "fraction between 0 and 1" in everything)
        if os.environ.get("FAKE_CLAUDE_BAD_LINE") and "Your last answer had these problems" not in everything:
            findings.insert(0, {"severity": "major", "file": findings[0]["file"] if findings else "app/x.py",
                                "line": 9999, "issue": "Invented line.", "suggestion": "None.",
                                "confidence": 0.9})
        payload = {"findings": findings}
        if "suggested_tests" in json.dumps(body["output_config"]):
            payload["suggested_tests"] = []
        content = [{"type": "text", "text": json.dumps(payload)}]
    else:
        lines = [f"{f['file']} line {f['line']}: {f['issue']} {f['suggestion']}"
                 for f in fake_findings(diff_text, False)]
        text = "\n".join(lines) or "No problems found."
        if body.get("max_tokens", 1024) < 100:
            text, stop_reason = text[:80], "max_tokens"
        content = [{"type": "text", "text": text}]

    usage = {"input_tokens": len(json.dumps(messages)) // 4, "output_tokens": len(json.dumps(content)) // 4,
             "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    system = body.get("system")
    if isinstance(system, list) and any("cache_control" in block for block in system):
        prefix = json.dumps([body.get("tools"), system], sort_keys=True)
        size = len(prefix) // 4
        if prefix in SEEN_PREFIXES:
            usage["cache_read_input_tokens"] = size
        else:
            SEEN_PREFIXES.add(prefix)
            usage["cache_creation_input_tokens"] = size
    return {"id": "msg_fake", "type": "message", "role": "assistant", "model": body.get("model", "fake"),
            "content": content, "stop_reason": stop_reason, "stop_sequence": None, "usage": usage}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        REQUESTS.append(body)
        HEADERS.append({k.lower(): v for k, v in self.headers.items()})
        if "/batches" in self.path:
            reply = {"id": "msgbatch_fake", "type": "message_batch", "processing_status": "in_progress",
                     "request_counts": {"processing": len(body["requests"]), "succeeded": 0, "errored": 0,
                                        "canceled": 0, "expired": 0},
                     "created_at": "2026-01-01T00:00:00Z", "expires_at": "2026-01-02T00:00:00Z",
                     "ended_at": None, "cancel_initiated_at": None, "archived_at": None, "results_url": None}
        else:
            reply = answer(body)
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):      # keep test output quiet
        pass


def start(port=0):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


if __name__ == "__main__":
    server, url = start(8765)
    print("Fake Claude is listening. In another terminal, run:\n")
    print(f"  export ANTHROPIC_BASE_URL={url}\n  export ANTHROPIC_API_KEY=fake-key\n")
    threading.Event().wait()
