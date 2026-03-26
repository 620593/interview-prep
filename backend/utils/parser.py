"""
utils/parser.py — Safe JSON extraction from LLM responses.
LLMs often wrap JSON in ```json ... ``` — this strips that and parses.

FIX 8: Replaced greedy regex (which breaks on trailing text after closing brace)
        with a bracket-counting approach that finds the outermost JSON boundary.
"""
import json
import re


def _find_json_boundaries(text: str) -> tuple[int, int] | None:
    """
    Scan `text` for the outermost JSON object `{...}` or array `[...]` using a
    bracket-counting approach.  Returns (start, end+1) indices or None.

    This avoids the greedy-regex pitfall where re.DOTALL matches from the first `{`
    to the very last `}` in a string, even across multiple disjoint JSON objects.
    """
    for opener, closer in [('{', '}'), ('[', ']')]:
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == '\\' and in_string:
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    return start, i + 1
    return None


def extract_json(text: str) -> dict | list:
    """Extract and parse the first top-level JSON object or array from `text`."""
    # Strip common LLM markdown fencing
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

    # Fast path — try direct parse on the whole cleaned string first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # FIX 8: bracket-counting approach instead of greedy regex
    boundaries = _find_json_boundaries(cleaned)
    if boundaries:
        start, end = boundaries
        candidate = cleaned[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Found JSON-like block but failed to parse it: {exc}\n"
                f"Block (first 300 chars): {candidate[:300]}"
            ) from exc

    raise ValueError(f"No valid JSON found in LLM response:\n{text[:300]}")