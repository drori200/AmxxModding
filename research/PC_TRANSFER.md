# Move this project from the laptop to the Qwen PC

The laptop and PC do not need to share a network or be online at the same time.
Copy the export folder through a USB drive or your personal cloud storage.
These instructions assume the destination PC runs CachyOS/Linux.

This transfers the committed project and Git history, the retained research
cache, a production-environment snapshot, and the four original teaching/build
artifacts. Complete Codex chat transcripts, installed model weights, and the
Half-Life game installation are separate; they are not included.

## 1. On the laptop: create the export

Finish saving your files and stop research builds/watch processes before export
so the cache does not change while being archived. The repository was clean when
this guide was prepared. The commands below stop if tracked or untracked
non-ignored changes need attention; review and preserve such changes before
retrying. Do not discard them just to make export succeed.

Run the whole block in a terminal on the laptop. It runs in a subshell so its
error-handling options do not change your interactive shell.

```bash
(
set -eu
cd /home/crowg/Documents/GitHub/AmxxModding

if [ -n "$(git status --porcelain)" ]; then
  printf '%s\n' 'Save and review the uncommitted work before exporting.' >&2
  exit 1
fi
if [ "$(git branch --show-current)" != "codex/pawn-foundation-checkpoint" ]; then
  printf '%s\n' 'Use the codex/pawn-foundation-checkpoint branch for this export.' >&2
  exit 1
fi

export_dir="$HOME/Documents/AmxxModding-PC-transfer"
mkdir -p "$export_dir"

git rev-parse HEAD > "$export_dir/SOURCE_COMMIT.txt"
git bundle create "$export_dir/history.bundle" --all
git bundle verify "$export_dir/history.bundle"

tar -czf "$export_dir/research-cache.tar.gz" .cache/research
tar -czf "$export_dir/production-cache.tar.gz" .compiler .thirdparty node_modules dist

tar -C /home/crowg/Documents/Codex/2026-09-07/explore-x20 +  -czf "$export_dir/original-artifacts.tar.gz" +  .pptx-build/pawn-course/build-detailed-course.mjs +  .pptx-build/pawn-course/build-pawn-course.mjs +  output/pawn-zero-to-hero-course.pptx +  output/pawn-zero-to-hero-detailed-course.pptx

cp research/PC_TRANSFER.md "$export_dir/START_HERE.md"
cd "$export_dir"
sha256sum history.bundle research-cache.tar.gz production-cache.tar.gz +  original-artifacts.tar.gz SOURCE_COMMIT.txt START_HERE.md > SHA256SUMS
sha256sum -c SHA256SUMS
printf '\nTransfer this entire folder: %s\n' "$export_dir"
)
```

Every checksum should report `OK`. If any command fails, fix the cause and rerun
the export before using its output; files left by a failed attempt are not a
complete verified export. Reusing this export directory replaces its named
snapshot files. Keep an older export elsewhere if you want to retain it.

The laptop's research cache was about 838 MB before compression when inspected.
The production folders were much smaller. Allow a few GB of free space for
archives, restoration, and future test runs; exact sizes will change.

The earlier `project.tar.gz` export is optional here. Cloning `history.bundle`
restores the committed files and their history, including both Qwen handoff
documents. A bundle supports offline cloning; it cannot itself receive pushes.
[Git bundle documentation](https://git-scm.com/docs/git-bundle)

## 2. Carry the export to the PC

Choose either route:

- **USB:** copy the entire `AmxxModding-PC-transfer` folder to a USB drive,
  safely eject it, then copy it onto the PC.
- **Personal cloud storage:** upload the entire folder from the laptop. Wait for
  upload completion, then download all its files onto the PC. Keep it private;
  do not create a public sharing link.

Place the received folder at:

```text
$HOME/Documents/AmxxModding-PC-transfer
```

It must contain these seven files:

```text
history.bundle
research-cache.tar.gz
production-cache.tar.gz
original-artifacts.tar.gz
SOURCE_COMMIT.txt
START_HERE.md
SHA256SUMS
```

Use the file manager's upload/download/copy action. Do not paste the terminal
output into Qwen or upload only the checksum file. GitHub already holds the
committed project, but it does not hold these ignored caches or the original
external artifacts. Do not commit the archives into the project.

## 3. On the PC: verify and restore

You need Git, Python 3, tar, and sha256sum. Check they are available:

```bash
git --version
python3 --version
tar --version
sha256sum --version
```

On CachyOS, install any missing prerequisites (including GitHub CLI for later
pushes) through the package manager:

```bash
sudo pacman -S --needed git python tar coreutils github-cli
```

The following restore block creates a new project directory and stops if that
directory already exists. This avoids overwriting an existing PC project.

```bash
(
set -eu
transfer_dir="$HOME/Documents/AmxxModding-PC-transfer"
project_dir="$HOME/Documents/GitHub/AmxxModding"
originals_dir="$HOME/Documents/AmxxModding-original-artifacts"

cd "$transfer_dir"
sha256sum -c SHA256SUMS

if [ -e "$project_dir" ] || [ -e "$originals_dir" ]; then
  printf '%s\n' 'A destination already exists. Choose new empty destination paths.' >&2
  exit 1
fi

mkdir -p "$HOME/Documents/GitHub"
git clone --branch codex/pawn-foundation-checkpoint +  "$transfer_dir/history.bundle" "$project_dir"

cd "$project_dir"
test "$(git rev-parse HEAD)" = "$(cat "$transfer_dir/SOURCE_COMMIT.txt")"
tar -xzf "$transfer_dir/research-cache.tar.gz" -C "$project_dir"
tar -xzf "$transfer_dir/production-cache.tar.gz" -C "$project_dir"
mkdir -p "$originals_dir"
tar -xzf "$transfer_dir/original-artifacts.tar.gz" -C "$originals_dir"

git remote set-url origin https://github.com/drori200/AmxxModding.git
git status --short
git log -1 --oneline
printf '\nProject: %s\nOriginal artifacts: %s\n' "$project_dir" "$originals_dir"
)
```

If all commands succeed, the restored Git commit matches the laptop's export.
The short status should normally be empty. Changing the remote URL enables
future synchronization with GitHub; it does not upload anything or configure
authentication. No internet connection is needed for this bundle restore.

The original teaching artifacts are deliberately restored into a separate
folder. The historical manifest still records their laptop paths. Tell the
agent the new originals folder; do not edit old evidence to pretend those were
the paths used by the original execution.

## 4. Inspect validity on the PC

```bash
cd "$HOME/Documents/GitHub/AmxxModding"
python3 -B research/tools/pawn_gate.py
```

**FAIL and exit 1 are expected.** The PAWN gate already failed on the laptop.
It had 34 unresolved original profiles, five official-suite exceptions,
86 incomplete reviewed topic dispositions, unresolved PAWN prerequisites,
and no current independent advancement approval.

Additional missing-path or stale-evidence errors may occur on the PC. Many old
commands and raw-log paths contain `/home/crowg/Documents/GitHub/AmxxModding`.
A different username/path makes those historical paths unavailable; even at
the same path, changed libraries or tool binaries can require fresh execution.

Copied virtual environments, Node modules, compilers, and build products are
historical artifacts, not proof of PC compatibility. Keep the transfer folder
as an untouched backup before rebuilding. Let the agent follow section 7 of
LOCAL_MODEL_HANDOFF.md to rebuild/replay affected evidence when justified.
Preserve old reports; never rewrite their paths or hashes to manufacture a
passing gate. The copied cache includes the pinned original downloads, so
PAWN acquisition can reuse them if their hashes match.

Production dependency installation or downloading missing tools may still need
internet access. The computers need not be on the same network for either.

## 5. Connect Qwen to the restored folder

Use a coding-agent application configured to run the local Qwen model and give
it access to:

```text
$HOME/Documents/GitHub/AmxxModding
```

It needs file reading/search and, to continue implementation, controlled editing
and terminal tools. A model runner or chat window alone does not automatically
provide those tools. If you have only chat, attach the short starting prompt,
objective, and STATUS for discussion; executing the project still requires a
tool-capable application or manual terminal work.

Give Qwen this initial prompt, replacing YOUR_USERNAME:

```text
The project was transferred from my laptop to this PC.
Repository: /home/YOUR_USERNAME/Documents/GitHub/AmxxModding
Original teaching artifacts:
/home/YOUR_USERNAME/Documents/AmxxModding-original-artifacts

Read research/LOCAL_MODEL_START.md, research/OBJECTIVE.md, and
research/STATUS.md. Consult research/LOCAL_MODEL_HANDOFF.md by section.

First inspect the branch, worktree, restored cache, compiler configuration,
and current gate validity. Treat absolute paths in old evidence as
historical laptop paths. Report missing files and stale evidence accurately.
Preserve the original reports and transfer archives before any rebuild.

The PAWN gate currently fails. Keep AMXX research blocked.
The selected canonical compiler is official CompuPhase, using default
internal64 and explicit emitted cell widths with matching VMs.

Follow the handoff's reproduction and continuation procedures. Retrieve
specific files and report records instead of putting the whole reference
into context. Do not change expectations merely to obtain passing results.
Do not fabricate independent review.

After the environment audit, continue the next justified bounded task.
Checkpoint meaningful progress in STATUS.md and reviewed Git commits.
Push when authenticated and verify the remote commit.
```

## 6. Enable future GitHub checkpoints

GitHub can exchange commits between the laptop and PC while they are on different
networks and at different times. Authenticate on the PC using its own credentials;
do not copy the laptop's token or authentication files.

If GitHub CLI is installed, run:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh auth status --hostname github.com
git -C "$HOME/Documents/GitHub/AmxxModding" remote -v
```

Sign in as the account with repository write access. Ensure Git has your own
name/email configured before committing. If `gh` is missing, install GitHub CLI
through the PC's package manager first.
[GitHub CLI authentication](https://cli.github.com/manual/gh_auth_login)

Use one active working copy at a time initially. Before switching machines,
commit/push reviewed changes on the outgoing machine. On the incoming machine,
with a clean worktree, update the established branch using:

```bash
git pull --ff-only origin codex/pawn-foundation-checkpoint
```

If histories diverged, inspect and reconcile the changes; do not force-push.
Raw logs and caches remain outside Git, so transfer a fresh cache snapshot when
the other machine needs that exact evidence. A code pull does not transfer it.

## Scope and verification of this guide

The source branch/worktree, required archive folders, and original-artifact
manifest were inspected while preparing these instructions. Shell examples were
syntax-checked. The transfer and restoration are user actions described here;
they have not been performed on the PC by Codex, and Qwen has not been benchmarked
or installed as part of this guide.
