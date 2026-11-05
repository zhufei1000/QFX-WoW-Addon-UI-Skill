#!/usr/bin/env python3
"""Index Blizzard's generated Lua documentation without executing Lua (Python 3.10+)."""

import argparse
import bisect
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

DOC_PATH = "Interface/AddOns/Blizzard_APIDocumentationGenerated"
REMOTE = "https://github.com/Gethe/wow-ui-source.git"
DEFAULT_INDEX = Path(__file__).resolve().parents[1] / "references" / "api-index"
SCHEMA = 1


def git(source, *args, data=None):
    result = subprocess.run(
        ["git", "-C", str(source), *args], input=data, capture_output=True, check=False
    )
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


class LuaTable(dict):
    def __init__(self, line):
        super().__init__()
        self.line = line


class LuaLiteralParser:
    """Restricted static table parser. Symbolic values stay explicitly tagged expressions."""

    token = re.compile(
        r"(?P<space>\s+)|(?P<comment>--\[(?P<ceq>=*)\[.*?\](?P=ceq)\]|--[^\n]*)"
        r"|(?P<long>\[(?P<leq>=*)\[.*?\](?P=leq)\])"
        r'''|(?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')'''
        r"|(?P<number>-?(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?))"
        r"|(?P<identifier>[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)*)"
        r"|(?P<punct>[{}\[\]=,;:()+*/%^#~&|<>.\-])", re.DOTALL
    )

    def __init__(self, text):
        self.tokens = []
        newlines = [m.start() for m in re.finditer("\n", text)]
        pos = 0
        while pos < len(text):
            match = self.token.match(text, pos)
            if not match:
                raise ValueError(f"unsupported Lua syntax at line {bisect.bisect_left(newlines, pos) + 1}: {text[pos:pos+40]!r}")
            kind = match.lastgroup
            if kind not in ("space", "comment"):
                self.tokens.append((kind, match.group(), bisect.bisect_left(newlines, pos) + 1))
            pos = match.end()
        self.pos = 0

    def peek(self, offset=0):
        return self.tokens[self.pos + offset][1] if self.pos + offset < len(self.tokens) else None

    def take(self, expected=None):
        if self.pos >= len(self.tokens):
            raise ValueError("unexpected end of Lua documentation")
        token = self.tokens[self.pos]
        self.pos += 1
        if expected is not None and token[1] != expected:
            raise ValueError(f"line {token[2]}: expected {expected!r}, got {token[1]!r}")
        return token

    @staticmethod
    def string(raw):
        escapes = {"a": "\a", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\", '"': '"', "'": "'"}
        def decode(match):
            value = match.group()[1:]
            if value.isdigit():
                return chr(int(value))
            if value.startswith("x"):
                return chr(int(value[1:], 16))
            if value.startswith("z"):
                return ""
            if value in ("\n", "\r\n"):
                return "\n"
            if value not in escapes:
                raise ValueError(f"unsupported Lua string escape: {match.group()!r}")
            return escapes[value]
        return re.sub(r"\\(?:\d{1,3}|x[0-9a-fA-F]{2}|z\s*|\r?\n|.)", decode, raw[1:-1])

    def value(self):
        if self.peek() == "{":
            return self.table()
        kind, raw, line = self.take()
        # Preserve symbolic/arithmetic expressions rather than evaluating client globals.
        if kind == "identifier" and raw not in ("true", "false", "nil") or self.peek() not in (",", ";", "}", "]"):
            tokens = [raw]
            depth = 1 if raw == "(" else 0
            while self.peek() is not None and (depth or self.peek() not in (",", ";", "}", "]")):
                item = self.take()[1]
                if item in ("(", "["):
                    depth += 1
                elif item in (")", "]"):
                    depth -= 1
                if depth < 0 or item in ("{", "}"):
                    raise ValueError(f"line {line}: unsupported expression")
                tokens.append(item)
            if depth:
                raise ValueError(f"line {line}: unbalanced expression")
            return {"lua_expression": " ".join(tokens)}
        if kind == "string":
            return self.string(raw)
        if kind == "long":
            match = re.fullmatch(r"\[(=*)\[(.*?)\]\1\]", raw, re.DOTALL)
            return match.group(2).removeprefix("\n")
        if kind == "number":
            if "x" in raw.lower():
                return int(raw, 16)
            return float(raw) if any(c in raw.lower() for c in ".e") else int(raw)
        if kind == "identifier":
            if raw in ("true", "false", "nil"):
                return {"true": True, "false": False, "nil": None}[raw]
        raise ValueError(f"line {line}: unsupported value {raw!r}")

    def table(self):
        _, _, line = self.take("{")
        result = LuaTable(line)
        array_index = 1
        while self.peek() != "}":
            if self.peek() is None:
                raise ValueError(f"unterminated table starting at line {line}")
            if self.peek() == "[":
                self.take("[")
                key = self.value()
                self.take("]")
                self.take("=")
                value = self.value()
            elif self.peek(1) == "=":
                key = self.take()[1]
                self.take("=")
                value = self.value()
            else:
                key, value = array_index, self.value()
                array_index += 1
            if key in result:
                raise ValueError(f"line {line}: duplicate table key {key!r}")
            result[key] = value
            if self.peek() not in (",", ";", "}"):
                raise ValueError(f"line {line}: expected table separator, got {self.peek()!r}")
            if self.peek() in (",", ";"):
                self.take()
        self.take("}")
        return result

    def document(self):
        self.take("local")
        variable = self.take()[1]
        self.take("=")
        document = self.table()
        document.variable = variable
        if self.peek() == ";":
            self.take()
        self.take("APIDocumentation")
        self.take(":")
        self.take("AddDocumentationTable")
        self.take("(")
        self.take(variable)
        self.take(")")
        if self.peek() == ";":
            self.take()
        if self.peek() is not None:
            raise ValueError(f"unexpected trailing Lua: {self.peek()!r}")
        return document


def array(value):
    if not value:
        return []
    if not isinstance(value, LuaTable) or set(value) != set(range(1, len(value) + 1)):
        raise ValueError("expected a contiguous Lua array")
    return list(value.values())


def plain(value, key=None):
    if isinstance(value, LuaTable):
        if (value and all(isinstance(k, int) for k in value)) or (not value and key in ("Arguments", "Returns", "Payload", "Fields", "Documentation")):
            return [plain(item) for item in array(value)]
        return {str(k): plain(v, k) for k, v in value.items()}
    return value


def strip_documentation(value):
    if isinstance(value, dict):
        return {k: strip_documentation(v) for k, v in value.items() if k != "Documentation"}
    if isinstance(value, list):
        return [strip_documentation(v) for v in value]
    return value


def records_from(document, filename):
    owner = document.get("Name", document.variable)
    namespace = document.get("Namespace", "")
    script_object = document.get("Type") == "ScriptObject"
    records = []
    common = {"owner": owner, "namespace": namespace, "environment": document.get("Environment"),
              "owner_type": document.get("Type"), "file": filename}
    def add(kind, name, node):
        records.append({**common, "kind": kind, "name": name, "line": node.line,
                        "contract": plain(node)})
    # The system record preserves all owner-level flags, environment and object metadata.
    meta = LuaTable(document.line)
    meta.update({k: v for k, v in document.items() if k not in ("Functions", "Events", "Tables", "Predicates")})
    add("system", owner, meta)
    for section in ("Functions", "Events", "Tables", "Predicates"):
        for node in array(document.get(section)):
            kind = node["Type"].lower()
            name = node.get("LiteralName") if kind == "event" else None
            if not name:
                name = node["Name"]
                if kind == "function":
                    name = f"{owner}:{name}" if script_object else f"{namespace}.{name}" if namespace else name
                    kind = "method" if script_object else "function"
                elif kind == "enumeration":
                    name = f"Enum.{name}"
            add(kind, name, node)
    return records


def json_write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def snapshot(source, ref, branch, client, out):
    source, out = Path(source).resolve(), Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"output directory is not empty; choose a new snapshot directory: {out}")
    commit = git(source, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    build = git(source, "show", f"{commit}:version.txt").decode().strip()
    tree = git(source, "ls-tree", "-r", commit, "--", DOC_PATH).decode().splitlines()
    entries = []
    for entry in tree:
        meta, filename = entry.split("\t", 1)
        mode, object_type, blob = meta.split()
        if object_type == "blob":
            entries.append((filename, blob))
    if not entries:
        raise ValueError(f"no generated documentation found at {commit}:{DOC_PATH}")
    # One batch reads all blobs; source and version come from one immutable commit.
    batch = git(source, "cat-file", "--batch", data=("\n".join(blob for _, blob in entries) + "\n").encode())
    pos, records, files = 0, [], []
    for filename, blob in entries:
        end = batch.index(b"\n", pos)
        header = batch[pos:end].decode().split()
        if len(header) != 3 or header[0] != blob or header[1] != "blob":
            raise ValueError(f"invalid git blob response for {filename}")
        size = int(header[2])
        content = batch[end + 1:end + 1 + size]
        pos = end + size + 2
        files.append({"file": filename, "git_blob": blob, "sha256": hashlib.sha256(content).hexdigest()})
        if filename.endswith(".lua"):
            try:
                records.extend(records_from(LuaLiteralParser(content.decode("utf-8-sig")).document(), filename))
            except (ValueError, KeyError, TypeError) as error:
                raise ValueError(f"{filename}: {error}") from error
    records.sort(key=lambda row: (row["kind"], row["name"], row["owner"]))
    ids = [(row["kind"], row["owner"], row["name"], row["file"]) for row in records]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate symbol identities in generated documentation")
    origin = git(source, "remote", "get-url", "origin").decode().strip().removesuffix(".git").rstrip("/")
    if origin.startswith("git@github.com:"):
        origin = "https://github.com/" + origin.removeprefix("git@github.com:")
    if not re.fullmatch(r"https://github\.com/[^/]+/[^/]+", origin):
        raise ValueError("snapshot source needs a GitHub origin URL for immutable source links")
    manifest = {
        "schema": SCHEMA, "client": client, "branch": branch, "build": build, "commit": commit,
        "repository": origin,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "All Lua documentation tables in Blizzard_APIDocumentationGenerated; not a complete runtime API inventory or proof of addon access.",
        "counts": dict(sorted(Counter(row["kind"] for row in records).items())),
        "files": files,
    }
    out.mkdir(parents=True, exist_ok=True)
    index = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in records)
    (out / "symbols.jsonl").write_text(index, encoding="utf-8", newline="\n")
    manifest["symbols_sha256"] = hashlib.sha256((out / "symbols.jsonl").read_bytes()).hexdigest()
    json_write(out / "manifest.json", manifest)
    print(json.dumps({"out": str(out), "build": build, "commit": commit, "files": len(files), "symbols": len(records), "counts": manifest["counts"]}, ensure_ascii=False))


def load_snapshot(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["schema"] != SCHEMA:
        raise ValueError("unsupported snapshot schema")
    data = (directory / "symbols.jsonl").read_bytes()
    if hashlib.sha256(data).hexdigest() != manifest["symbols_sha256"]:
        raise ValueError(f"snapshot index checksum mismatch: {directory}")
    return manifest, [json.loads(line) for line in data.decode("utf-8").splitlines() if line]


def search(args):
    manifest, records = load_snapshot(args.index)
    query = args.query.casefold()
    def matches(row):
        if args.kind and row["kind"] != args.kind:
            return False
        if args.namespace and row["namespace"] != args.namespace:
            return False
        values = [row["name"], row["contract"].get("Name", "")]
        for field in row["contract"].get("Fields", []):
            if "Name" in field:
                values.extend([field["Name"], f"{row['name']}.{field['Name']}"])
        if args.exact:
            return query in [value.casefold() for value in values]
        haystack = json.dumps(row, ensure_ascii=False) if args.details else " ".join(values + [row["owner"], row["namespace"], row["file"]])
        return query in haystack.casefold()
    found = [row for row in records if matches(row)]
    result = {"client": manifest["client"], "branch": manifest["branch"], "build": manifest["build"],
              "commit": manifest["commit"], "scope": manifest["scope"], "total": len(found), "results": []}
    for row in found[:args.limit]:
        link = f"{manifest['repository']}/blob/{manifest['commit']}/{row['file']}#L{row['line']}"
        shown = dict(row)
        if not args.details:
            shown["contract"] = strip_documentation(row["contract"])
        shown["source_url"] = link
        result["results"].append(shown)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if found else 1


def changes(old, new, prefix=""):
    if isinstance(old, dict) and isinstance(new, dict):
        result = []
        for key in sorted(set(old) | set(new)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in old:
                result.append({"path": path, "change": "added", "after": new[key]})
            elif key not in new:
                result.append({"path": path, "change": "removed", "before": old[key]})
            else:
                result.extend(changes(old[key], new[key], path))
        return result
    if isinstance(old, list) and isinstance(new, list):
        result = []
        for index in range(max(len(old), len(new))):
            path = f"{prefix}[{index}]"
            if index >= len(old):
                result.append({"path": path, "change": "added", "after": new[index]})
            elif index >= len(new):
                result.append({"path": path, "change": "removed", "before": old[index]})
            else:
                result.extend(changes(old[index], new[index], path))
        return result
    if type(old) is not type(new) or old != new:
        return [{"path": prefix, "change": "changed", "before": old, "after": new}]
    return []


def compare(before, after, include_documentation=False):
    old_meta, old = load_snapshot(before)
    new_meta, new = load_snapshot(after)
    if old_meta["client"] != new_meta["client"]:
        raise ValueError("cannot compare different client families")
    if old_meta["repository"] != new_meta["repository"]:
        raise ValueError("cannot compare different source repositories")
    def keyed(rows):
        return {(row["kind"], row["owner"], row["name"], row["file"]): row for row in rows}
    old, new = keyed(old), keyed(new)
    altered = []
    for key in sorted(old.keys() & new.keys()):
        a, b = old[key]["contract"], new[key]["contract"]
        if not include_documentation:
            a, b = strip_documentation(a), strip_documentation(b)
        delta = changes(a, b)
        if delta:
            altered.append({"kind": key[0], "owner": key[1], "name": key[2], "file": key[3], "changes": delta})
    old_files = {row["file"]: row["sha256"] for row in old_meta["files"]}
    new_files = {row["file"]: row["sha256"] for row in new_meta["files"]}
    summary = lambda meta: {key: meta[key] for key in ("client", "branch", "build", "commit")}
    identity = lambda row: {key: row[key] for key in ("kind", "owner", "name", "file", "line")}
    return {"before": summary(old_meta), "after": summary(new_meta),
            "include_documentation": include_documentation,
            "cross_branch": old_meta["branch"] != new_meta["branch"],
            "added": [identity(new[key]) for key in sorted(new.keys() - old.keys())],
            "removed": [identity(old[key]) for key in sorted(old.keys() - new.keys())],
            "changed": altered,
            "files_changed": sorted(key for key in old_files.keys() | new_files.keys() if old_files.get(key) != new_files.get(key)),
            "caveat": "Documentation delta only; inspect same-build FrameXML and test in game. PTR/Beta changes do not establish Live availability."}


def refresh(args):
    cache = Path(args.cache).expanduser().resolve()
    if not (cache / ".git").exists():
        if cache.exists() and any(cache.iterdir()):
            raise ValueError(f"cache is not an empty directory: {cache}")
        cache.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(["git", "clone", "--filter=blob:none", "--sparse", "--single-branch", "--branch", args.branch, REMOTE, str(cache)], check=False)
        if result.returncode:
            raise ValueError("source clone failed")
        git(cache, "sparse-checkout", "set", DOC_PATH)
    remote = git(cache, "remote", "get-url", "origin").decode().strip()
    if remote.removesuffix(".git").rstrip("/") != REMOTE.removesuffix(".git"):
        raise ValueError("cache origin is not Gethe/wow-ui-source")
    if git(cache, "status", "--porcelain").strip():
        raise ValueError("source cache contains local changes; use a clean dedicated cache")
    git(cache, "fetch", "--depth=1", "origin", args.branch)
    commit = git(cache, "rev-parse", "FETCH_HEAD").decode().strip()
    # A clean, dedicated sparse cache lets checkout prefetch blobs in one batch.
    git(cache, "sparse-checkout", "set", DOC_PATH)
    git(cache, "checkout", "--detach", commit)
    snapshot(cache, commit, args.branch, "retail", args.out)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    snap = sub.add_parser("snapshot", help="Create a pinned snapshot from an existing git source checkout")
    snap.add_argument("--source", required=True)
    snap.add_argument("--ref", default="HEAD")
    snap.add_argument("--branch", required=True, help="Provenance label, not an inferred client family")
    snap.add_argument("--client", required=True, help="Explicit client family, e.g. retail, classic-era")
    snap.add_argument("--out", required=True)
    fetch = sub.add_parser("refresh", help="Fetch current Retail docs into a dedicated cache and create a new snapshot")
    fetch.add_argument("--branch", choices=("live", "ptr", "ptr2", "beta"), default="live")
    fetch.add_argument("--cache", default=str(Path.home() / ".cache" / "qfx-wow-api" / "source"))
    fetch.add_argument("--out", required=True)
    find = sub.add_parser("search", help="Search the bundled index or a selected snapshot")
    find.add_argument("query")
    find.add_argument("--index", default=str(DEFAULT_INDEX))
    find.add_argument("--exact", action="store_true", help="Match qualified or unqualified symbol name exactly")
    find.add_argument("--kind")
    find.add_argument("--namespace")
    find.add_argument("--details", action="store_true", help="Include/search documentation text and nested fields")
    find.add_argument("--limit", type=int, default=10)
    diff = sub.add_parser("diff", help="Compare contracts, including nested restriction metadata")
    diff.add_argument("before")
    diff.add_argument("after")
    diff.add_argument("--include-documentation", action="store_true")
    diff.add_argument("--out", help="Write the full JSON report to a new file")
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            snapshot(args.source, args.ref, args.branch, args.client, args.out)
        elif args.command == "refresh":
            refresh(args)
        elif args.command == "search":
            if args.limit < 1:
                raise ValueError("--limit must be positive")
            return search(args)
        else:
            report = compare(args.before, args.after, args.include_documentation)
            if args.out:
                target = Path(args.out)
                if target.exists():
                    raise ValueError(f"report already exists: {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                json_write(target, report)
                print(json.dumps({"out": str(target.resolve()), **{key: len(report[key]) for key in ("added", "removed", "changed", "files_changed")}}, ensure_ascii=False))
            else:
                print(json.dumps(report, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
