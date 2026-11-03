"""Deterministic prompt-injection screen.

Runs on the raw customer message before any LLM sees it. It is deliberately
conservative: a miss here still cannot approve anything, because the final
decision is made by the rule-based policy engine, not by the model.
"""

import re
import unicodedata

# Common digit/symbol swaps used to dodge keyword filters ("1gn0re", "byp@ss").
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})

_PATTERNS = [
    r"\b(ignore|disregard|forget|override|bypass|skip)\b.{0,40}\b(instruction|instructions|rule|rules|guideline|guidelines|polic(y|ies)|guardrail|guardrails|check|checks|prompt|restrictions?)\b",
    r"\b(ignore|disregard|forget)\b (the|everything|all|anything)( of the)? (above|previous|prior|before)\b",
    r"\bprocess\b.{0,40}\bregardless\b",
    r"\bregardless of (the |your |any )?(rules?|polic(y|ies)|checks?|guidelines?|limits?)\b",
    r"\b(you are|you're) now\b",
    r"\b(act|behave) as (an?|the) (admin|administrator|developer|system|supervisor|manager)\b",
    r"\b(system|developer) (prompt|message|mode|override)\b",
    r"\bjailbreak|\bdan mode\b",
    r"\b(set|change|force|mark|update)\b.{0,20}\b(decision|state|status|verdict)\b.{0,20}\b(to|as)\b.{0,10}\b(approve|approved|refunded|accept)",
    r"\b(admin|administrator|supervisor|manager) (here|override|approval|has approved|authori[sz]ed)\b",
    r"\bnew (instructions?|polic(y|ies)|rules?)\b",
    r"\bpretend\b.{0,40}\b(policy|rules?|approved|admin)\b",
    r"</?(system|assistant|instructions?)>",
]
_COMPILED = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _PATTERNS]


def _normalise(message):
    text = unicodedata.normalize("NFKC", message)
    return text.lower().translate(_LEET)


def detect_prompt_injection(message):
    """Return the matched pattern text if the message looks like an injection attempt, else None."""
    if not message:
        return None
    text = _normalise(message)
    for pattern in _COMPILED:
        match = pattern.search(text)
        if match:
            return match.group(0)
    return None
