#!/usr/bin/env python3
"""
validate.py - check a worker.json listing against worker.schema.json

Usage:
    python validate.py listings/trading-book-audit.json [more.json ...]

Uses `jsonschema` when installed (pip install jsonschema). Without it, falls back to a small
built-in checker that covers exactly the constructs used in this schema: type, required,
properties, additionalProperties, enum, const, pattern, minimum, maxLength, minItems, maxItems,
items, allOf/if/then/else. The fallback prints a note so a catalogue knows which path ran.

Exit code 0 = valid, 1 = problems found, 2 = usage/IO error.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "worker.schema.json"

TYPES = {
    "object": dict, "array": list, "string": str,
    "integer": int, "number": (int, float), "boolean": bool,
}


def check(node, schema, path, errs):
    t = schema.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        if not any(isinstance(node, TYPES[x]) for x in types):
            errs.append(f"{path}: expected type {types}, got {type(node).__name__}")
            return
        if "integer" in types and isinstance(node, bool):
            errs.append(f"{path}: expected integer, got bool")
            return

    if "const" in schema and node != schema["const"]:
        errs.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and node not in schema["enum"]:
        errs.append(f"{path}: must be one of {schema['enum']}")

    if isinstance(node, str):
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errs.append(f"{path}: does not match pattern {schema['pattern']}")
        if "maxLength" in schema and len(node) > schema["maxLength"]:
            errs.append(f"{path}: longer than {schema['maxLength']}")

    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if "minimum" in schema and node < schema["minimum"]:
            errs.append(f"{path}: below minimum {schema['minimum']}")

    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errs.append(f"{path}: needs at least {schema['minItems']} items")
        if "maxItems" in schema and len(node) > schema["maxItems"]:
            errs.append(f"{path}: allows at most {schema['maxItems']} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for i, v in enumerate(node):
                check(v, item_schema, f"{path}[{i}]", errs)

    if isinstance(node, dict):
        for req in schema.get("required", []):
            if req not in node:
                errs.append(f"{path}: missing required field '{req}'")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for k in node:
                if k not in props:
                    errs.append(f"{path}: unknown field '{k}'")
        for k, v in node.items():
            if k in props:
                check(v, props[k], f"{path}.{k}", errs)

    for sub in schema.get("allOf", []):
        check(node, sub, path, errs)

    for branch in ("if", "then", "else"):
        if branch in schema:
            probe = []
            check(node, schema["if"], path, probe)
            if branch == "if":
                continue
            if (not probe and branch == "then") or (probe and branch == "else"):
                check(node, schema[branch], path, errs)


def main(argv):
    files = [a for a in argv[1:] if not a.startswith("-")]
    if not files:
        print(__doc__)
        return 2
    if not SCHEMA_PATH.exists():
        print(f"schema not found: {SCHEMA_PATH}")
        return 2
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    engine = "builtin"
    try:
        import jsonschema  # type: ignore
        engine = "jsonschema"
    except Exception:  # noqa: BLE001
        print("note: jsonschema not installed - using built-in checker (same rules as this schema)")

    bad = 0
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"MISSING  {f}")
            bad += 1
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"INVALID  {f}: not parseable JSON ({exc})")
            bad += 1
            continue

        errs = []
        if engine == "jsonschema":
            import jsonschema  # type: ignore
            v = jsonschema.Draft7Validator(schema)
            errs = [f"{'.'.join(str(x) for x in e.absolute_path)}: {e.message}"
                    for e in v.iter_errors(doc)]
        else:
            check(doc, schema, "$", errs)

        # rules the schema cannot express
        if isinstance(doc, dict):
            caps = doc.get("capabilities") or []
            for i, c in enumerate(caps):
                if isinstance(c, dict) and not str(c.get("worked_example", "")).startswith("https://"):
                    errs.append(f"capabilities[{i}]: worked_example must be a public https link")
            sub = doc.get("substrate") or {}
            if sub.get("runs_on") in ("seller_metal", "either") and not sub.get("data_handling"):
                errs.append("substrate.data_handling is required when the seller runs the metal")

        if errs:
            bad += 1
            print(f"FAIL     {f}")
            for e in errs:
                print(f"   - {e}")
        else:
            kind = doc.get("kind", "?") if isinstance(doc, dict) else "?"
            price = ((doc.get("terms") or {}).get("price") or {}).get("amount_sat") if isinstance(doc, dict) else None
            print(f"OK       {f}  (kind={kind}, price_sat={price}) [{engine}]")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
