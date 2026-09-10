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

Run the versioned export script from a terminal on the laptop:

```bash
cd /home/crowg/Documents/GitHub/AmxxModding
bash tools/export-for-qwen.sh
```

It creates a new timestamped folder under `~/Documents/` and prints its full
path. It refuses to overwrite an existing export. To select a different new
folder, pass its path as the script's only argument.

The console and `export.log` show the repository, branch, commit, disk space,
required input paths, sizes, each archive stage, and the exact shell-quoted
arguments sent to Git and tar. A failure reports the stage, exit status, shell
line/command, and log location. It does not dump credentials or environment
variables. The large research archive prints periodic GNU tar write checkpoints;
compression can still take time between progress lines.

Success requires all six payload checksums to report `OK`, followed by a
`[SUCCESS]` message and an `EXPORT_COMPLETE.txt` file. If anything fails, retain
`export.log` and rerun into a new folder after addressing the error. Do not use
an incomplete folder for the PC restore.

### Correction to the first version of this guide

The earlier inline commands incorrectly contained literal `+` arguments in
three places: original-artifact tar, checksum generation, and Git clone. This
caused `tar: +: Cannot stat` despite successful bundle verification. These were
errors in the saved guide, not missing user files. Bash syntax checking alone
did not catch them because `+` is a syntactically valid filename argument.
The exporter now uses a checked-in script and a Bash array for artifact paths;
the restore command below is one complete line. Copy shell commands from the
file view, not a Git diff containing added-line markers.

The laptop's research cache was about 838 MB before compression when inspected.
The production folders were much smaller. Allow a few GB of free space for
archives, restoration, and future test runs; exact sizes will change.

The earlier `project.tar.gz` export is optional here. Cloning `history.bundle`
restores the committed files and their history, including both Qwen handoff
documents. A bundle supports offline cloning; it cannot itself receive pushes.
[Git bundle documentation](https://git-scm.com/docs/git-bundle)

## 2. Carry the export to the PC

Choose either route:

- **USB:** copy the entire timestamped export folder printed by the script to a USB drive,
  safely eject it, then copy it onto the PC.
- **Personal cloud storage:** upload the entire folder from the laptop. Wait for
  upload completion, then download all its files onto the PC. Keep it private;
  do not create a public sharing link.

On the PC, rename the received timestamped folder to `AmxxModding-PC-transfer`
and place it at:

```text
$HOME/Documents/AmxxModding-PC-transfer
```

It must contain these nine files:

```text
history.bundle
research-cache.tar.gz
production-cache.tar.gz
original-artifacts.tar.gz
SOURCE_COMMIT.txt
START_HERE.md
SHA256SUMS
export.log
EXPORT_COMPLETE.txt
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
test -f EXPORT_COMPLETE.txt
sha256sum -c SHA256SUMS

if [ -e "$project_dir" ] || [ -e "$originals_dir" ]; then
  printf '%s\n' 'A destination already exists. Choose new empty destination paths.' >&2
  exit 1
fi

mkdir -p "$HOME/Documents/GitHub"
git clone --branch codex/pawn-foundation-checkpoint "$transfer_dir/history.bundle" "$project_dir"

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
manifest were inspected while preparing these instructions. The first version
was only syntax-checked, which missed valid but unintended `+` arguments.
The replacement script has passed a functional fixture export with spaces in
paths, six checksum checks, exact tar-member checks, and offline Git clone/commit
verification. Negative checks confirmed that existing output, missing artifacts,
and a dirty checkout fail without a completion marker or discarded user changes.
The actual destination PC has not been accessed, and Qwen has not been benchmarked
or installed as part of this guide.
