"""Build the golden set: ten diffs, each with one seeded issue.

Each variant below is one small edit to sample_app that plants a known bug.
Run this after you change sample_app or add a variant:

    python eval/golden/make_cases.py

It rewrites eval/golden/*.diff, eval/golden/cases.json, and the demo diffs.
"""
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
APP = ROOT / "sample_app"
GOLDEN = ROOT / "eval" / "golden"
DEMO_DIFFS = ROOT / "demos" / "diffs"

VARIANTS = [
    {
        "id": "01-sql-injection", "file": "app/db.py", "severity": "critical",
        "issue": "User input is formatted straight into the SQL string.",
        "old": '    query = "SELECT * FROM users WHERE email = ?"\n'
               "    return conn.execute(query, (email,)).fetchone()\n",
        "new": "    query = f\"SELECT * FROM users WHERE email = '{email}'\"\n"
               "    return conn.execute(query).fetchone()\n",
        "marker": "query = f\"SELECT",
    },
    {
        "id": "02-pagination-off-by-one", "file": "app/db.py", "severity": "major",
        "issue": "Page 1 skips the first page of results.",
        "old": "    offset = (page - 1) * page_size\n",
        "new": "    offset = page * page_size\n",
        "marker": "offset = page * page_size",
    },
    {
        "id": "03-unhandled-none", "file": "app/orders.py", "severity": "major",
        "issue": "find_order can return None, and the result is indexed anyway.",
        "old": "    order = db.find_order(conn, order_id)\n"
               "    if order is None:\n"
               '        raise OrderNotFound(f"order {order_id} does not exist")\n'
               '    return order["status"]\n',
        "new": "    order = db.find_order(conn, order_id)\n"
               '    return order["status"]\n',
        "marker": 'return order["status"]',
    },
    {
        "id": "04-hardcoded-secret", "file": "app/auth.py", "severity": "critical",
        "issue": "A signing secret is committed to the repo.",
        "old": 'SECRET = os.environ.get("SHOP_SECRET", "")\n',
        "new": 'SECRET = "shop-signing-secret-2026-do-not-share"\n',
        "marker": 'SECRET = "shop-signing-secret',
    },
    {
        "id": "05-mutable-default", "file": "app/orders.py", "severity": "minor",
        "issue": "A list as a default argument is shared between calls.",
        "old": "def create_order(conn, user_id, items, code=None):\n",
        "new": "def create_order(conn, user_id, items=[], code=None):\n",
        "marker": "items=[]",
    },
    {
        "id": "06-divide-by-zero", "file": "app/pricing.py", "severity": "major",
        "issue": "An empty list now divides by zero.",
        "old": "    if not items:\n        return 0.0\n    total = 0.0\n",
        "new": "    total = 0.0\n",
        "marker": "total = 0.0",
    },
    {
        "id": "07-cross-file-percent", "file": "app/orders.py", "severity": "major",
        "issue": "apply_discount expects a fraction. 15 raises ValueError.",
        "old": "    return pricing.add_tax(subtotal)\n",
        "new": "    if subtotal > 100:\n"
               "        subtotal = pricing.apply_discount(subtotal, 15)\n"
               "    return pricing.add_tax(subtotal)\n",
        "marker": "pricing.apply_discount(subtotal, 15)",
    },
    {
        "id": "08-swallowed-exception", "file": "app/orders.py", "severity": "major",
        "issue": "A failed insert is swallowed and the caller gets None.",
        "old": "    return db.insert_order(conn, user_id, total)\n",
        "new": "    try:\n"
               "        return db.insert_order(conn, user_id, total)\n"
               "    except Exception:\n"
               "        pass\n",
        "marker": "except Exception:",
    },
    {
        "id": "09-inverted-expiry", "file": "app/auth.py", "severity": "critical",
        "issue": "The comparison is inverted. Expired tokens pass, valid ones fail.",
        "old": "    return now < expires_at\n",
        "new": "    return now > expires_at\n",
        "marker": "return now > expires_at",
    },
    {
        "id": "10-password-in-logs", "file": "app/auth.py", "severity": "critical",
        "issue": "The plaintext password is written to the log.",
        "old": "    user = db.find_user_by_email(conn, email)\n    if user is None:\n",
        "new": '    print(f"login attempt: {email} / {password}")\n'
               "    user = db.find_user_by_email(conn, email)\n    if user is None:\n",
        "marker": "{password}",
    },
]

# A change with no bug in it. Day 4 uses it to show false positives.
STYLE_ONLY = {
    "id": "style-only", "file": "app/pricing.py",
    "old": "def add_tax(total):\n    return round(total * (1 + TAX_RATE), 2)\n",
    "new": "def add_tax(total):\n"
           '    """Return total with sales tax added."""\n'
           "    with_tax = total * (1 + TAX_RATE)\n"
           "    return round(with_tax, 2)\n",
}

DEMOS = {
    "day01.diff": ["06-divide-by-zero", "05-mutable-default"],
    "day04.diff": ["style-only", "03-unhandled-none"],
    "day06.diff": ["07-cross-file-percent"],
    "day07.diff": ["07-cross-file-percent", "02-pagination-off-by-one"],
}


def apply_variants(variants):
    """Return {file: (old_text, new_text)} after applying every variant."""
    changed = {}
    for variant in variants:
        path = variant["file"]
        old_text = (APP / path).read_text()
        new_text = changed[path][1] if path in changed else old_text
        if variant["old"] not in new_text:
            raise SystemExit(f"{variant['id']}: the old text is not in {path}")
        new_text = new_text.replace(variant["old"], variant["new"], 1)
        changed[path] = (old_text, new_text)
    return changed


def make_diff(changed):
    parts = []
    for path in sorted(changed):
        old_text, new_text = changed[path]
        lines = difflib.unified_diff(
            old_text.splitlines(keepends=True), new_text.splitlines(keepends=True),
            fromfile="a/" + path, tofile="b/" + path)
        parts.append(f"diff --git a/{path} b/{path}\n" + "".join(lines))
    return "".join(parts)


def line_of(text, marker):
    for number, line in enumerate(text.splitlines(), start=1):
        if marker in line:
            return number
    raise SystemExit(f"marker not found: {marker}")


def main():
    by_id = {variant["id"]: variant for variant in VARIANTS}
    by_id["style-only"] = STYLE_ONLY
    cases = []
    for variant in VARIANTS:
        changed = apply_variants([variant])
        (GOLDEN / (variant["id"] + ".diff")).write_text(make_diff(changed))
        new_text = changed[variant["file"]][1]
        cases.append({
            "id": variant["id"],
            "diff": f"eval/golden/{variant['id']}.diff",
            "expected": [{"file": variant["file"],
                          "line": line_of(new_text, variant["marker"]),
                          "severity": variant["severity"],
                          "issue": variant["issue"]}],
        })
    (GOLDEN / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    for name, ids in DEMOS.items():
        changed = apply_variants([by_id[i] for i in ids])
        (DEMO_DIFFS / name).write_text(make_diff(changed))
    print(f"wrote {len(cases)} golden cases and {len(DEMOS)} demo diffs")


if __name__ == "__main__":
    main()
