#!/usr/bin/env python3
"""
Qwalora Sigma-subset runner.

A dependency-free evaluator for the slice of the Sigma spec the range uses, so
grading stays deterministic and offline (no pySigma, no backend conversion).
It reads JSON-line events and a Sigma rule, and reports how many events match.

Supported:
  detection:
    <selection>:
      field: value                 # equals
      field|contains: value        # substring
      field|startswith: value
      field|endswith: value
      field: [a, b]                # any-of (OR)
    condition: "<sel>"  |  "<a> and <b>"  |  "<a> or <b>"  |  "not <sel>"
Nested fields use dotted keys (e.g. http.method). This is intentionally small;
richer Sigma features are out of scope for the lab and will raise.
"""
import json
import sys


def _get(event, field):
    cur = event
    for part in field.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _match_value(actual, op, expected):
    if actual is None:
        return False
    a = str(actual)
    if op == "equals":
        return a == str(expected)
    if op == "contains":
        return str(expected) in a
    if op == "startswith":
        return a.startswith(str(expected))
    if op == "endswith":
        return a.endswith(str(expected))
    raise ValueError(f"unsupported op: {op}")


def _match_selection(event, sel):
    """A selection is an AND over its fields; a list value is an OR."""
    for key, expected in sel.items():
        if "|" in key:
            field, op = key.split("|", 1)
        else:
            field, op = key, "equals"
        actual = _get(event, field)
        if isinstance(expected, list):
            if not any(_match_value(actual, op, v) for v in expected):
                return False
        else:
            if not _match_value(actual, op, expected):
                return False
    return True


def _eval_condition(event, detection):
    cond = str(detection.get("condition", "")).strip()
    sels = {k: v for k, v in detection.items() if k != "condition"}

    def sel_result(name):
        if name not in sels:
            raise ValueError(f"condition names unknown selection: {name}")
        return _match_selection(event, sels[name])

    tokens = cond.split()
    if not tokens:
        raise ValueError("empty condition")
    if len(tokens) == 1:
        return sel_result(tokens[0])
    if len(tokens) == 2 and tokens[0] == "not":
        return not sel_result(tokens[1])
    if len(tokens) == 3 and tokens[1] in ("and", "or"):
        a, b = sel_result(tokens[0]), sel_result(tokens[2])
        return (a and b) if tokens[1] == "and" else (a or b)
    raise ValueError(f"unsupported condition: {cond!r}")


def load_rule(path):
    import yaml  # PyYAML is the one small dep; present in CI + the lab image
    with open(path) as fh:
        rule = yaml.safe_load(fh)
    if "detection" not in rule:
        raise ValueError("rule has no 'detection' block")
    return rule


def run(rule_path, events_path):
    rule = load_rule(rule_path)
    detection = rule["detection"]
    matches = 0
    with open(events_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if _eval_condition(event, detection):
                matches += 1
    return matches


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: sigma_runner.py <rule.yml> <events.jsonl>", file=sys.stderr)
        sys.exit(2)
    print(run(sys.argv[1], sys.argv[2]))
