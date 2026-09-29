#!/usr/bin/env bash
# Write each suite's plugin manifest and both marketplace indexes.
#
# Reads every skills/<suite>/suite.yaml and writes:
#   skills/<suite>/.claude-plugin/plugin.json   one per suite
#   .claude-plugin/marketplace.json             Claude marketplace, every suite
#   .grok-plugin/marketplace.json               Grok marketplace, every suite
#
# The manifest sets no skills path, so hosts use the default skills/ directory
# inside the suite. Edit suite.yaml, never the generated files. JSON has no
# comments and both validators warn on unknown keys, so the generated files are
# marked in .gitattributes instead of in their contents. Safe to re-run:
# unchanged files are not rewritten.
#
#   --check     write nothing; exit 1 if a generated file is missing or differs
#   --upstream  write nothing; print the remote entries for the xai-org
#               plugin-marketplace catalog, pinned to HEAD
#
# Needs python3 (standard library only). suite.yaml is read as a small YAML
# subset: scalar keys, one list (keywords), one map (author).
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
mode="${1:-write}"
case "$mode" in
  write|--check|--upstream) ;;
  *) echo "usage: $0 [--check|--upstream]" >&2; exit 2 ;;
esac

sha=""
if [ "$mode" = "--upstream" ]; then
  sha="$(git -C "$root" rev-parse HEAD)"
  if ! git -C "$root" diff --quiet HEAD -- skills; then
    echo "warning: skills/ has uncommitted changes; the entries pin HEAD, not the working tree" >&2
  fi
  if git -C "$root" rev-parse --verify -q origin/main >/dev/null \
     && ! git -C "$root" merge-base --is-ancestor HEAD origin/main; then
    echo "warning: HEAD is not on origin/main; pin a commit that is public" >&2
  fi
fi

exec python3 - "$root" "$mode" "$sha" <<'PY'
import json, os, re, sys

root, mode, sha = sys.argv[1], sys.argv[2], sys.argv[3]
REPO = "shinytoyrobots/skill-suites"
REQUIRED = ["name", "displayName", "version", "description", "keywords", "category",
            "author", "homepage", "repository", "license"]


def parse_suite(path):
    """Parse the suite.yaml subset: `key: value`, `key:` + `  - item`, `key:` + `  sub: value`."""
    data, key = {}, None
    with open(path) as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line.startswith(" "):
                k, sep, v = line.partition(":")
                if not sep:
                    sys.exit(f"{path}:{n}: expected 'key: value'")
                key, v = k.strip(), v.strip()
                data[key] = unquote(v) if v else None
                continue
            item = line.strip()
            if key is None:
                sys.exit(f"{path}:{n}: indented line with no parent key")
            if item.startswith("- "):
                if data[key] is None:
                    data[key] = []
                data[key].append(unquote(item[2:].strip()))
            else:
                k, sep, v = item.partition(":")
                if not sep:
                    sys.exit(f"{path}:{n}: expected 'sub: value'")
                if data[key] is None:
                    data[key] = {}
                data[key][k.strip()] = unquote(v.strip())
    missing = [k for k in REQUIRED if not data.get(k)]
    if missing:
        sys.exit(f"{path}: missing {', '.join(missing)}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", data["name"]):
        sys.exit(f"{path}: name must be kebab-case")
    icon = data.get("icon")
    if icon:
        target = os.path.normpath(os.path.join(os.path.dirname(path), icon))
        if not icon.startswith("./") or not target.startswith(os.path.dirname(path) + os.sep):
            sys.exit(f"{path}: icon must be a ./ path inside the suite")
        if not os.path.isfile(target):
            sys.exit(f"{path}: icon {icon} does not exist")
    return data


def unquote(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


suites = []
skills_root = os.path.join(root, "skills")
for d in sorted(os.listdir(skills_root)):
    path = os.path.join(skills_root, d, "suite.yaml")
    if os.path.isfile(path):
        suites.append((d, parse_suite(path)))
if not suites:
    sys.exit("no skills/*/suite.yaml found")


def manifest(s):
    m = {
        "name": s["name"],
        "displayName": s["displayName"],
        "version": s["version"],
        "description": s["description"],
        "author": s["author"],
        "homepage": s["homepage"],
        "repository": s["repository"],
        "license": s["license"],
        "keywords": s["keywords"],
    }
    # Optional. The plugin manifest carries it; neither marketplace has a field for it.
    if s.get("icon"):
        m["icon"] = s["icon"]
    return m


owner = {"name": suites[0][1]["author"]["name"], "url": suites[0][1]["author"]["url"]}

claude_market = {
    "name": "skill-suites",
    "owner": owner,
    "metadata": {"description": "Agent Skills suites: groups of skills that work together, one plugin per suite."},
    "plugins": [
        {
            "name": s["name"],
            "source": f"./skills/{d}",
            "description": s["description"],
            "version": s["version"],
            "author": s["author"],
            "homepage": s["homepage"],
            "repository": s["repository"],
            "license": s["license"],
            "keywords": s["keywords"],
            "category": s["category"],
        }
        for d, s in suites
    ],
}

grok_market = {
    "name": "skill-suites",
    "description": "Agent Skills suites: groups of skills that work together, one plugin per suite.",
    "owner": owner,
    "plugins": [
        {
            "name": s["name"],
            "description": s["description"],
            "version": s["version"],
            "category": s["category"],
            "source": {"type": "local", "path": f"./skills/{d}"},
            "homepage": s["homepage"],
            "keywords": s["keywords"],
        }
        for d, s in suites
    ],
}


def dump(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


if mode == "--upstream":
    entries = [
        {
            "name": s["name"],
            "description": s["description"],
            "category": s["category"],
            "source": {"source": "url", "url": f"https://github.com/{REPO}.git", "sha": sha, "path": f"skills/{d}"},
            "homepage": s["homepage"],
            "keywords": s["keywords"],
        }
        for d, s in suites
    ]
    sys.stdout.write(dump(entries))
    sys.exit(0)

outputs = {os.path.join("skills", d, ".claude-plugin", "plugin.json"): dump(manifest(s)) for d, s in suites}
outputs[os.path.join(".claude-plugin", "marketplace.json")] = dump(claude_market)
outputs[os.path.join(".grok-plugin", "marketplace.json")] = dump(grok_market)

stale = 0
for rel, text in outputs.items():
    path = os.path.join(root, rel)
    current = open(path).read() if os.path.isfile(path) else None
    if current == text:
        continue
    if mode == "--check":
        print(f"stale     {rel}", file=sys.stderr)
        stale = 1
        continue
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    print(f"rendered  {rel}")
sys.exit(stale)
PY
