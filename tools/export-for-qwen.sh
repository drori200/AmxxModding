#!/usr/bin/env bash
# Export local project evidence with explicit arguments and a retained diagnostic log.
set -Eeuo pipefail

if (( $# > 1 )); then
  printf '%s\n' 'Usage: bash tools/export-for-qwen.sh [NEW_OUTPUT_DIRECTORY]' >&2
  exit 2
fi

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export_dir="${1:-$HOME/Documents/AmxxModding-PC-transfer-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
if [[ -e "$export_dir" || -L "$export_dir" ]]; then
  printf 'Output already exists; choose a new directory: %s\n' "$export_dir" >&2
  exit 1
fi
mkdir -p -- "$export_dir"
export_dir="$(cd -- "$export_dir" && pwd)"
log_file="$export_dir/export.log"
exec > >(tee -- "$log_file") 2>&1
stage='initialization'

on_error() {
  local code="$1" line="$2" command="$3"
  printf '\n[FAILED] stage=%s exit=%s line=%s\n' "$stage" "$code" "$line"
  printf '[FAILED] shell command: %s\n' "$command"
  printf '[FAILED] log: %s\n' "$log_file"
  printf '%s\n' '[FAILED] No EXPORT_COMPLETE.txt marker was created. Preserve this log; this folder is incomplete.'
  exit "$code"
}
trap 'on_error "$?" "$LINENO" "$BASH_COMMAND"' ERR

run() {
  printf '\n[%s] RUN' "$(date -u +%FT%TZ)"
  printf ' %q' "$@"
  printf '\n'
  "$@"
}

fail() {
  printf '\n[FAILED] stage=%s: %s\n[FAILED] log: %s\n' "$stage" "$*" "$log_file"
  exit 1
}

cd -- "$repo_root"
stage='preflight'
printf '[INFO] started=%s\n[INFO] repository=%s\n[INFO] export=%s\n[INFO] log=%s\n' "$(date -u +%FT%TZ)" "$repo_root" "$export_dir" "$log_file"
[[ "$export_dir" != "$repo_root" && "$export_dir" != "$repo_root/"* ]] || fail 'Choose an output directory outside the repository.'
for tool in git tar sha256sum python3 du df date; do
  command -v "$tool" || fail "Required command is missing: $tool"
done
run git --version
run tar --version
run df -h -- "$export_dir"
branch="$(git branch --show-current)"
commit="$(git rev-parse HEAD)"
printf '[INFO] branch=%s\n[INFO] commit=%s\n' "$branch" "$commit"
[[ "$branch" == 'codex/pawn-foundation-checkpoint' ]] || fail 'Switch to codex/pawn-foundation-checkpoint before export.'
worktree_status="$(git status --porcelain)"
if [[ -n "$worktree_status" ]]; then
  printf '[INFO] uncommitted files:\n%s\n' "$worktree_status"
  fail 'Save and review uncommitted changes before exporting. Nothing was staged or discarded.'
fi

for item in .cache/research .compiler .thirdparty node_modules dist research/PC_TRANSFER.md; do
  [[ -e "$item" ]] || fail "Required export input is missing: $repo_root/$item"
  printf '[INPUT] %s\n' "$repo_root/$item"
done
run du -sh -- .cache/research .compiler .thirdparty node_modules dist

originals_dir="$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("research/pawn/prior/original-artifacts.json").read_text())["original_workspace"])')"
artifacts=(
  .pptx-build/pawn-course/build-detailed-course.mjs
  .pptx-build/pawn-course/build-pawn-course.mjs
  output/pawn-zero-to-hero-course.pptx
  output/pawn-zero-to-hero-detailed-course.pptx
)
for item in "${artifacts[@]}"; do
  [[ -f "$originals_dir/$item" ]] || fail "Original artifact is missing: $originals_dir/$item"
  printf '[INPUT] %s\n' "$originals_dir/$item"
done

stage='Git bundle'
printf '%s\n' "$commit" > "$export_dir/SOURCE_COMMIT.txt"
run git bundle create "$export_dir/history.bundle" --all
run git bundle verify "$export_dir/history.bundle"

stage='research cache archive'
run tar --checkpoint=10000 --checkpoint-action=echo -czf "$export_dir/research-cache.tar.gz" -- .cache/research
stage='production cache archive'
run tar -czf "$export_dir/production-cache.tar.gz" -- .compiler .thirdparty node_modules dist
stage='original artifacts archive'
run tar -C "$originals_dir" -czf "$export_dir/original-artifacts.tar.gz" -- "${artifacts[@]}"

stage='checksums'
[[ "$(git rev-parse HEAD)" == "$commit" && -z "$(git status --porcelain)" ]] || fail 'The source checkout changed during export; stop writers and retry.'
run cp -- research/PC_TRANSFER.md "$export_dir/START_HERE.md"
cd -- "$export_dir"
payload=(history.bundle research-cache.tar.gz production-cache.tar.gz original-artifacts.tar.gz SOURCE_COMMIT.txt START_HERE.md)
printf '\n[INFO] Hashing payload files into SHA256SUMS\n'
sha256sum -- "${payload[@]}" > SHA256SUMS
run sha256sum -c SHA256SUMS
printf 'Verified export of commit %s at %s\n' "$commit" "$(date -u +%FT%TZ)" > EXPORT_COMPLETE.txt
stage='complete'
printf '\n[SUCCESS] Transfer this entire folder: %s\n' "$export_dir"
printf '[SUCCESS] Diagnostic log: %s\n' "$log_file"
