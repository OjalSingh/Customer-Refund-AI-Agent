"""Loads the policy files as clauses keyed by their [SECTION-ID] headers.

The policy engine cites these ids, so every decision can be traced back to the
exact text that justified it.
"""

import re
from functools import lru_cache

from agent.paths import POLICY_DIR

_HEADER = re.compile(r"^\[([A-Z0-9-]+)\]\s*$", re.MULTILINE)


@lru_cache(maxsize=1)
def load_clauses():
    clauses = {}
    for path in sorted(POLICY_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        headers = list(_HEADER.finditer(text))
        for i, match in enumerate(headers):
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            body = text[match.start():end].strip()
            clause_id = match.group(1)
            entry = clauses.setdefault(clause_id, {"id": clause_id, "sources": [], "text": ""})
            entry["sources"].append(path.name)
            entry["text"] = (entry["text"] + "\n\n" + body).strip()
    return clauses


def clause_text(clause_id):
    if clause_id is None:
        return None
    clause = load_clauses().get(clause_id)
    return clause["text"] if clause else None
