#!/usr/bin/env bash
# Copy each suite's _shared files into the skills that link to them.
#
# A skill links a shared file as references/<name> or assets/<name> in its
# SKILL.md. For every such link whose <name> exists in skills/<suite>/_shared/,
# this script copies the file into the skill directory. Vendored files a skill
# no longer links are removed. Files that exist only in a skill's own
# references/ or assets/ are left alone.
#
# Edit _shared, run this, commit the copies. Safe to re-run: unchanged files
# are not rewritten. Exit 1 if a link resolves to nothing.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
status=0

for shared in "$root"/skills/*/_shared; do
  [ -d "$shared" ] || continue
  suite_dir="$(dirname "$shared")"

  for skill_md in "$suite_dir"/*/SKILL.md; do
    skill_dir="$(dirname "$skill_md")"
    skill="$(basename "$skill_dir")"
    linked="$(grep -oE '\]\((references|assets)/[^)#[:space:]]+' "$skill_md" | sed 's/^](//' | sort -u || true)"

    for rel in $linked; do
      name="$(basename "$rel")"
      if [ -f "$shared/$name" ]; then
        mkdir -p "$skill_dir/$(dirname "$rel")"
        if ! cmp -s "$shared/$name" "$skill_dir/$rel"; then
          cp "$shared/$name" "$skill_dir/$rel"
          echo "vendored  $skill/$rel"
        fi
      elif [ ! -f "$skill_dir/$rel" ]; then
        echo "MISSING   $skill/$rel (not in _shared, not in the skill)" >&2
        status=1
      fi
    done

    # Prune vendored copies that the skill no longer links.
    for sub in references assets; do
      [ -d "$skill_dir/$sub" ] || continue
      for f in "$skill_dir/$sub"/*; do
        [ -f "$f" ] || continue
        name="$(basename "$f")"
        if [ -f "$shared/$name" ] && ! grep -qx "$sub/$name" <<<"$linked"; then
          rm "$f"
          echo "removed   $skill/$sub/$name"
        fi
      done
      rmdir "$skill_dir/$sub" 2>/dev/null || true
    done
  done
done

exit "$status"
