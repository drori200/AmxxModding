# PAWN-first project: complete continuation handoff

Prepared on 2026-09-10 for a local Qwen coding agent, from the repository and
retained evidence. The starting revision for this write-up was
`0c7a8792f9aaaf59dde4f66ab914db189a5a4623` on
`codex/pawn-foundation-checkpoint`, in
[drori200/AmxxModding](https://github.com/drori200/AmxxModding).

This is a project handoff, not a claim of completed research, a raw transcript of
every conversation, or the final research report. File paths below are relative
to the repository root unless explicitly absolute. The existing workspace is
`/home/crowg/Documents/GitHub/AmxxModding`.

Read [LOCAL_MODEL_START.md](LOCAL_MODEL_START.md) first for a small initial
context. Use this document as a reference by section:

1. [Objective and authority](#1-objective-and-authority)
2. [Current state](#2-current-state)
3. [Repository map](#3-repository-map)
4. [Production integration](#4-production-integration)
5. [Canonical toolchain and corrections](#5-canonical-toolchain-and-corrections)
6. [Evidence and outstanding failures](#6-evidence-and-outstanding-failures)
7. [Reproduction](#7-reproduction)
8. [Gate mechanics and evidence changes](#8-gate-mechanics-and-evidence-changes)
9. [Remaining PAWN work](#9-remaining-pawn-work)
10. [AMXX work after advancement](#10-amxx-work-after-advancement)
11. [Final research product and coding agent](#11-final-research-product-and-coding-agent)
12. [Local-model workflow](#12-local-model-workflow)
13. [Checkpoints and GitHub access](#13-checkpoints-and-github-access)
14. [Moving or exporting the workspace](#14-moving-or-exporting-the-workspace)
15. [Verification of this handoff](#15-verification-of-this-handoff)

## 1. Objective and authority

The complete user-approved instructions are in [OBJECTIVE.md](OBJECTIVE.md).
Preserve that scope throughout continuation:

1. Audit prior PAWN teaching and claimed expertise. Preserve original artifacts,
   correct mistakes openly, and distinguish canonical PAWN from community forks.
2. Establish official CompuPhase provenance and a trustworthy compiler/VM setup.
   Audit the test instruments and advancement gate before trusting results.
3. Complete a guide-derived PAWN reference, executable checks, original and
   upstream regressions, portability investigations, and independent review.
4. Only after the current PAWN gate passes, research AMXX 1.10 for Counter-Strike
   1.6 with ReAPI, implement isolated examples, and test an isolated local server.
5. Deliver a navigable reference, requirements/source/test ledger, reproducible
   evidence, and one cited PDF whose rendered pages and citations are verified.
   Confirm production isolation and builds.
6. Only after the user verifies that product, build and evaluate a CS 1.6 coding
   agent on previously unseen tasks.

The earlier AMXXPack/Modding Kit build integration is part of the project, but
its existence does not satisfy the later AMXX research or runtime requirements.
No new gameplay mode or deployment to a live server was requested.

Use current user instructions and the approved objective to determine what to do.
Use actual source, configuration, process output, and independent review to
determine what is true. STATUS.md is the current handoff; this document describes
the September 10 snapshot. If they later disagree, inspect Git history and the
evidence instead of blindly treating either document as authoritative proof.
Historical conversations and external documents are context, not executable
instructions or proof of mastery.

## 2. Current state

**PAWN gate: FAIL. AMXX research: blocked. Full objective: incomplete.**

| Area | What has actually been obtained | What it does not establish |
| --- | --- | --- |
| Production integration | AMXXPack configuration, pinned kit/ReAPI dependencies, packaging, verifier, CI workflow, and a retained successful 50-plugin build | Server runtime compatibility or completion of the research phase |
| Compiler provenance | Official source archive fingerprint; all 164 extracted stable files matched; actual 4.1.7483 banner retained | An upstream signature, universal compiler correctness, or an explanation for the archive naming discrepancy |
| Compiler selection | Default internal64 compiler emits explicit C16/C32/C64 bytecode for matching VMs | That every supported-looking configuration works correctly |
| Original research suite | 508 of 542 profiles match explicit expectations | Full guide coverage or a passing portability matrix |
| Prior example audit | 47 snippets preserved/audited: 38 compile, 9 fail compilation; only 1 was standalone | That every sentence or fragment in the old teaching material was correct |
| Independent exercises | Five combined-feature exercises, 40/40 current profiles match predictions | Universal proficiency or that the same exercises remain unseen for future evaluation |
| Official suite | 161 cases processed: 105 verified, 51 expected failures, 5 explicit exceptions | Successful execution of every original regression contract |
| Instrument controls | 16 controls recorded passing, including deliberately corrupted evidence | Proof of language semantics or immunity to all possible gate bugs |
| Guide inventory | 86 topic obligations and a 142-entry diagnostic index | Completed topic dispositions or 142 executed diagnostic tests |
| Independent review | Bounded foundation review and guide/claim review exist | Independent advancement approval |
| AMXX lab | Gate-checking entry-point stub exists | Implemented AMXX examples or local-server tests |
| PDF and final agent | Requirements and intended evaluations are documented | Delivered or user-verified products |

The gate was evaluated during this handoff preparation. Its five reported reasons
were unchanged: 34 original-profile failures; upstream exceptions 29/61/63/71/97;
86 incomplete reviewed topic dispositions; unresolved PAWN questions needed by
AMXX; and missing/currently negative independent advancement review.

## 3. Repository map

| Path | Role |
| --- | --- |
| `research/OBJECTIVE.md`, `research/STATUS.md` | Full scope and current resumable checkpoint |
| `research/README.md` | Reference navigation and reproduction overview |
| `research/pawn/toolchains.md`, `setup-audit.md`, `errata.md` | Provenance, setup corrections, and corrections to prior teaching |
| `research/pawn/coverage-inventory.json` | L01–L60 language topics and I01–I26 implementer topics, source sections, available cases, remaining obligations |
| `research/pawn/coverage-evidence.json` | Topic dispositions; currently an empty items list plus unresolved prerequisite questions |
| `research/pawn/claims.json` | Existing claim/source/test index; partial, not the completed final ledger |
| `research/pawn/review-findings.md`, `advancement-review.json` | Independent findings and the current changes-required advancement record |
| `research/pawn/cases.json`, `cases/*.p`, `include/lab.inc` | Original test definitions, explicit expectations, source programs, test natives |
| `research/pawn/host/labrun.c`, `host/contracts.h` | Custom C test host and native/host contract checks |
| `research/pawn/defects/*.p` | Bounded defect fixtures and deliberately failing examples |
| `research/pawn/prior/` | Original-artifact manifest, exact old snippet text/wrappers, independent exercises/predictions, historical reports |
| `research/pawn/upstream-expectations.json` | 161 official cases, original REXX locations/oracles, adaptations, exceptions |
| `research/tools/toolchains.py` | Download verification, acquisition, isolated compiler/VM/host builds, locks, file fingerprints |
| `research/tools/pawn_lab.py` | Original profile matrix, bounded execution, raw evidence validation |
| `research/tools/pawn_examples.py` | Prior snippet audit and independent exercise replay |
| `research/tools/upstream_pawn.py` | Official REXX-suite adapter and its explicit compiler/runtime oracles |
| `research/tools/pawn_compiler_config.py` | Controlled compiler-internal-width comparison |
| `research/tools/pawn_defects.py` | Separate diagnostic VM experiment and defect observations |
| `research/tools/test_pawn_audit.py`, `pawn_gate.py` | Instrument controls and advancement enforcement |
| `research/tools/amxx_lab.py` | AMXX entry stub; validates PAWN before doing anything else |
| `research/evidence/*.json` | Versioned manifests, reports, historical observations, reviews |
| `.cache/research/` | Ignored downloads, source trees, builds, raw process logs, bytecode, diagnostic variants |
| `package.json`, `package-lock.json`, `.amxxpack.json` | Production npm workflow and build/dependency configuration |
| `tools/setup.mjs`, `package.mjs`, `verify-build.mjs` | Production acquisition, packaging, and distribution validation |
| `plugins/`, `include/`, `assets/` | Maintained production source, local headers, packaged assets/configuration |
| `.compiler/`, `.thirdparty/`, `dist/` | Ignored production compiler, dependencies, distribution |
| `compile.sh` | Preserved legacy root-level compile workflow |
| `.github/workflows/build.yml` | Ubuntu production build and downloadable artifact workflow |

Some shorthand entries in this table share the directory shown in the first
entry of their row. Keep raw evidence outside the retrieval index by default;
search individual logs when investigating a particular result.

## 4. Production integration

The original request integrated
[AMXXPack](https://github.com/Hedgefog/node-amxxpack) and the complete
[AMXX Modding Kit](https://github.com/Hedgefog/amxx-modding-kit).
The current implementation has:

- Private npm package; Node >=22; `.nvmrc` selects 22.
- Exact `amxxpack@1.5.3` and `decompress@4.2.1` dependencies with lockfile;
  a `minimatch@3.1.5` override.
- AMXX 1.10 base plus Counter-Strike compiler/includes in `.compiler/`.
- Kit commit `1a29ced127e3e93c5f0cdcae22651a782c5c55c0`.
- ReAPI release `5.29.0.358`, including matching development headers and license.
- Production discovery of `plugins/**/*.sma` and kit `api/**/*.sma`,
  `entities/*.sma`, `weapons/*.sma`, and `player-effects/*.sma`.
- Flat packaged plugin names, dependent rebuilds, compiler-standard include
  precedence, kit API/utility includes, sources, and upstream license notices.
- `assets/addons/amxmodx/configs/plugins-modding-kit.ini` with 24 kit entries,
  API providers before bundled consumers.
- Clean full builds, package verification, and CI on Ubuntu 24.04 with Node 22
  and the 32-bit libraries `lib32stdc++6` and `lib32z1`.

The current layout supersedes the original root-plugin discovery proposal:
stock plugins are now in `plugins/stock_plugins/`. Preserve that user-owned
organization. Putting a new source in the repository root does not include it
in the current npm production build. An older README sentence referring to
maintained “root plugins” should not override `.amxxpack.json`.

The AMXX download endpoint previously returned HTTP 403. Setup now falls back to
the official AlliedModders GitHub releases and records that selected release in
`.compiler/SOURCE.json`. This remains a moving **1.10 channel**, not an exact
compiler-release pin; fresh setup may choose a newer 1.10 build. Do not confuse
this with the separately hash-pinned CompuPhase research toolchain.

The successful retained production check is
`research/evidence/production-isolation.json`, observed 2026-09-09, using Node
22.23.2: **26 project plugins + 24 kit plugins = 50**, production verifier exit 0,
research inputs excluded. It explicitly says runtime verification is false.
In the restricted sandbox the 32-bit AMXX compiler was killed with SIGSYS (-31).
AMXXPack reported success incorrectly, but the package verifier detected the
missing outputs; the authorized unrestricted build then succeeded.

Read the root README for installation, module prerequisites, resource paths,
license information, and dependency updates. ReAPI module binaries and game
resources are not included in the add-on distribution. Required runtime pieces
include CS 1.6, AMXX base/cstrike, Metamod, compatible ReHLDS/ReGameDLL_CS, ReAPI,
and standard engine/fakemeta/hamsandwich/cstrike/csx modules.

Build/watch/single-plugin commands exist. This handoff rechecked their definitions,
not a new watch or single-plugin execution. If durable proof of source/include
watch rebuilds cannot be located, perform and retain those checks as part of the
remaining final production validation. A workflow file alone does not prove that
the latest GitHub Actions run succeeded.

## 5. Canonical toolchain and corrections

### Official source identities

[sources.json](evidence/sources.json) is the authoritative five-download manifest.
It records exact URLs, local cache paths, access dates, and SHA-256 fingerprints.

| Artifact | Version identity | SHA-256 |
| --- | --- | --- |
| Stable source | CompuPhase `pawn-4.1.7487.zip`; internal revision/banner 4.1.7483, metadata date 2025-08-20 | `05cf630baef59912a9ffaf2745652187038d8d5be1a3aab870d13ea0bd31c7bc` |
| Development source | Official Codeberg commit `79620fcfff474c622fdb11d78027598235b8f11f` | `d0c5b372c7e277f65b07909f24f0dd3c28bba82f4e7fc47031c2eb1cb9f6f030` |
| Language Guide | August 2025 PDF at commit `73b9ae62319c213936f179345addf1fc9ac728f1` | `398bac8b1e9d07aeec39af263862179bb5e1507a69bef773293958bebd052e79` |
| Implementer's Guide | Same documentation edition/commit | `aeb323fed8fd6ebe197e86e78afe273a464a3b8e753902e184682763d43aea20` |
| Official regression sources | CompuPhase `pawntest.zip` | `096a1bf093f5d9d9d1ddc021cb77f22f655f6611c096839fef909c939a97e82d` |

A fresh HTTPS stable download on September 10 matched the pinned archive; all
164 extracted stable files matched. Evidence:
`pawn-compiler-origin-recheck.json`, `pawn-official-provenance.json`, and
`toolchains.json` under `research/evidence/`. This is origin and integrity
evidence, not an upstream cryptographic signature. The reason for the advertised
7487 versus actual 7483 discrepancy remains unknown.

The guides are contemporary documentation rather than proof that every printed
example agrees with the compiler. For these PDFs, printed page +4 is the one-based
PDF page. Preserve edition and page-number convention in citations.

### Four widths/properties that must stay separate

| Property | Selected setup |
| --- | --- |
| Host architecture | Linux x86-64 |
| Compiler-internal maximum cell arithmetic | 64 bits, matching upstream `compiler/sc.h` default |
| Emitted bytecode cell width | Explicit `-C16`, `-C32`, or `-C64` |
| VM cell width | Match the emitted bytecode |

The canonical compiler path is `.cache/research/build64/pawncc` for **all**
selected output widths. `build32/pawncc` and `build16/pawncc` remain preserved
internal-width experiments. They are not the selected baseline compiler.
Baseline execution uses `build32/labrun` or `build32/pawnrun`.

The first setup narrowed compiler internals alongside the VM. Controlled tests
later showed that a C32 boundary fixture at d2/O3 aborted with internal32 but
compiled and executed its nine checks correctly with default internal64.
That old abort is therefore not a defect demonstrated against the default
canonical compiler. The 12-record comparison retains both successful and failing
configurations. Pre-correction reports are preserved as
`pawn-pre-default-compiler-*.json`.

### Build and VM choices

The retained manifest identifies GCC 16.2.1 and CMake 4.4.3. Provisioning explicitly
uses GNU C99 because the archive's `constexpr` identifier conflicts with the newer
default C language mode. This is a build-mode choice, not an upstream-source patch.

The portable C interpreter and custom test host use matching cell definitions.
The minimal host has no JIT, optional libraries, dynamic module loading, or code
relocation. Its `check`, `identity`, and `native_error` functions are research
instruments, not PAWN language primitives or AMXX APIs. The official suite uses
canonical `pawnrun` with separately fingerprinted optional modules.

`HAVE_CURSES_H=0` produces capturable stream output. The non-curses amxString
build needs upstream `linux/getch.c` linked explicitly because upstream CMake
omits it in that configuration. Source remains unchanged; the command/hash is
recorded. Dyncall is unavailable, so foreign-call support has not been established.

The separate official development snapshot failed in `compiler/sc1.c:dostate`
because `name` is undeclared. Setup records this failure without substituting
that compiler for stable or claiming an execution comparison.

### Earlier teaching and lab mistakes

The previous task used the community `pawn-lang/compiler` fork at
`134ad7a836c581546665340aedb59efd4636e269`, with SA:MP-oriented documentation and
3.10.10 build metadata. Its results are not canonical 4.1 results. Four original
slide/build artifacts remain preserved in the earlier workspace and are identified
by `research/pawn/prior/original-artifacts.json`. Their hashes were checked again
for this handoff. The 47 extracted snippets and wrappers are retained in Git.

No durable custom canonical execution corpus was found in the inspected old
workspace. This is a statement about preserved evidence, not proof that no
transient execution ever happened.

Corrections retained in `errata.md` and executable fixtures include:

- Signed division floors; a nonzero remainder has the divisor's sign. The four
  `(a,b) -> (a/b,a%b)` examples are `(7,3)->(2,1)`,
  `(-7,3)->(-3,2)`, `(7,-3)->(-3,-2)`, `(-7,-3)->(2,-1)`.
  The C16 failure still limits the execution evidence for that width.
- Assertions do not replace release-safe checks. Reject negative and too-large
  indexes before dereferencing; a caller-supplied count still has its own validity
  precondition.
- Operator parameter tags do not declare the return tag. The arithmetic example
  requires an explicit tagged operator result. A tag cast does not itself perform
  a numeric conversion.
- In this canonical version, square-bracket initializers describe cell arrays;
  braces describe packed characters. Double quotes produce packed strings.
  Consult the actual source fixtures for unpacked-literal syntax.
- The guide leaves argument evaluation order undefined; reverse stack order in
  a calling convention does not create a language sequencing guarantee.
- Old `enum` record/`N char` examples and `state:` as a tag are not accepted as
  written by this canonical compiler. Some replacement coverage remains pending.

The lab itself had mistakes: `@entry` was an ordinary public function rather
than canonical `entry()` state behavior; a constant-group fixture needed
`const Mode:`; `sizeof` was incorrectly applied to a constant. These were fixed
as fixture errors. A whole-string symbolic-field assignment remains a preserved
guide/compiler disagreement; the positive fixture uses explicit character stores.

Instrument corrections reject compiler crashes after an expected diagnostic,
differentiate VM initialization/registration from execution errors, guard host
pointers after failed allocation helpers, select the explicit empty compiler
configuration, reject altered source trees without overwriting them, preserve
unique run logs, check raw evidence instead of summary flags, retain CRLF where
required, and coordinate setup/tests with locks. Read `setup-audit.md` for the
evidence links and exact scope; these fixes do not certify every possible harness
behavior.

## 6. Evidence and outstanding failures

### Original matrix

The current `research/evidence/pawn-original-results.json` contains 542 unique
profiles and 508 matches. Profiles mean source × selected width × debug mode ×
optimization, after explicitly excluding unsafe or inapplicable combinations.

| Emitted cells | Matching profiles | Failing profiles | Selected settings |
| --- | --- | --- | --- |
| C16 | 49/58 | 9 | d0/O0, d2/O0, d2/O1 |
| C32 | 364/364 | 0 | d0/d1/d2 crossed with O0/O1/O2/O3 |
| C64 | 95/120 | 25 | d0/d2 crossed with O0/O1/O3 |

`-d0` is unchecked/release behavior, `-d1` retains checking without symbolic
metadata, and `-d2` supplies checking and symbolic metadata. Native C build
optimization and PAWN bytecode optimization are separate configurations.

The nine C16 failures are three profiles each of signed arithmetic, packed
strings, and evaluation. C64 has six string failures and nineteen O3 failures
across release-safe indexing, aliasing, functions, evaluation, storage, control
flow, states, boundaries, assertions, and checked division errors. The exact
34 identities are listed in `research/evidence/pawn-gate.json`.

The current signed-arithmetic C16/d2/O0 record compiles successfully but runs:

```text
lab: bits=16 checks=0 failures=0 result=0 error=11 sleeps=0
phase: init=0 register=0 exec_entered=1 stage=exec
```

The host exits 2. Zero assertion failures here is **not success**: zero checks
executed, and execution ended with error 11. The expected arithmetic checks have
not been demonstrated in that profile.

### Official regression adapter

`pawntest.zip` supplies 39 original files and 161 REXX-described cases.
`upstream-expectations.json` preserves original case/source locations, compiler
arguments, required and forbidden diagnostics, runtime text, and explicit
exceptions. Each run copies original sources into its own case workspace and
fingerprints source, compiler, headers, libraries, logs, and bytecode.

The selected gate baseline is C32, checked d2, no global optimization override,
and the adapter's default optimization 2, respecting individual case arguments.
Additional adapter profiles are available, but their availability does not mean
they were all validated or replace the selected gate baseline.

| Outcome | Count | Interpretation |
| --- | --- | --- |
| verified | 105 | Recorded selected-profile observations match the adapter's explicit oracle |
| expected_failure | 51 | Deliberate negative cases match their expectations; these are not 51 unexplained regressions |
| documented_oracle_drift | 2 | Cases 29 and 61 differ explicitly from the original oracle |
| unsupported_harness | 3 | Cases 63, 71, and 97 cannot satisfy the original contract in this setup |

The five exceptions need independent, bounded advancement dispositions:

- **29:** The old oracle permits warning 203 only. Stable 4.1.7483 also emits
  recursion warning 237 for the fixture. The adapter records the exact alternate
  diagnostics and required runtime text; it does not silently call that the
  original oracle passing.
- **61:** The old fixed-point fixture expects 31.018 for 3.142 cubed. The retained
  explanation traces current rounding to 31.019. This is optional fixed-point
  library behavior and documented oracle drift; its reviewed disposition remains due.
- **63 and 97:** Original leak claims require FORTIFY compiler instrumentation.
  Seeing an expected diagnostic or successful compile without leak instrumentation
  cannot establish leak absence.
- **71:** Original caret escape/control-character configuration is unavailable
  in canonical 4.1. The rejection is retained. Rewriting the source to backslashes
  would test a different condition, not satisfy that original regression.

The old internal32 crash in official case 100 disappeared with the default
internal64 compiler; the case now produces its expected diagnostic.

### Bounded VM experiments

`pawn_defects.py` builds explicitly separate diagnostic VMs from a copy of
official `amx.c`. It changes five cell-instruction stores, in FILL, SWAP_PRI,
SWAP_ALT, CONST, and CONST_S, from fixed 32-bit stores to cell-width stores.
Do not replace every `_W32`: other uses can intentionally describe 32-bit data.

Retained observations in `pawn-defect-probes.json`:

| Probe | Unmodified interpreter/compiler | Separate diagnostic VM |
| --- | --- | --- |
| cell16_fill | One of three checks fails | Three checks pass |
| cell16_swap | One check fails | That check passes |
| cell64_fill | Both checks lose high bits | Both checks pass |
| cell64_store at O1 | Passes | Passes; this probe does not demonstrate a failure |
| optimizer32_shift at O3 | Passes with default compiler | No repaired-VM conclusion |
| optimizer64_expression at O3 | Compiler aborts in `sc7.c:stgopt` | No executable comparison possible |

These show bounded effects of the diagnostic changes. They do not explain all
34 matrix failures, validate a replacement VM, fix the compiler, or authorize a
production patch. Preserve non-triggering probes as limits on the hypothesis.

### Reviews and coverage

`pawn-foundation-checkpoint-review.json` records an independent, read-only
review of compiler selection and shared-lock advancement validation. The reviewer
found no consequential flaw in that bounded scope and checked 12 comparison
records. A warning about the comparison's historical input snapshot led to a
refreshed comparison. That review did not approve advancement.

The guide inventory covers lexical rules, declarations, cells and constants,
operators/tags, arrays/strings, functions/arguments, control flow, preprocessing,
states, diagnostics, bytecode, memory, debugging, and the host/native boundary.
Read each item's subtopics and remaining obligations. A topic with a mapped
fixture is still incomplete until the specific coverage and limitations are
adequately explained and independently reviewed.

## 7. Reproduction

Run commands from the repository root. Inspect the worktree before any command
that updates manifests. Stop watch/setup conflicts first; do not delete user work
to make a rebuild simpler.

### Existing intact workspace

```sh
git status --short
git branch --show-current
git log -3 --oneline
python3 -B research/tools/pawn_gate.py
```

The last command evaluates current evidence and exits **1** while the gate fails;
without `--record`, it does not replace the retained gate JSON. It still uses
the cooperative toolchain lock. A lock file's existence is not evidence that a
process is running.

For provenance verification:

```sh
python3 -B research/tools/toolchains.py --verify-only
```

Despite its name, this command writes `pawn-official-provenance.json`; it does
not rebuild tools. The content can affect gate fingerprints. Inspect the resulting
diff and do not describe it as completely read-only. For a Python caller,
`toolchains.verify_sources()` returns the verification observations directly.

### Fresh checkout or missing cache

Prerequisites are Python 3, a C compiler, Make, CMake, and network access for
pinned downloads. Reproduction is currently Linux-specific, including POSIX
resource limits and `fcntl` locking. Use the same pinned CMake when seeking the
closest match to retained builds:

```sh
python3 -m venv .cache/research/python
.cache/research/python/bin/pip install cmake==4.4.3
PATH="$PWD/.cache/research/python/bin:$PATH" python3 -B research/tools/toolchains.py --current
python3 -B research/tools/toolchains.py --verify-only
```

The temporary PATH prefix makes the isolated CMake win over another system
installation. Setup downloads the five pinned inputs, verifies them, builds
stable tools and matching hosts, and separately attempts the development source.
A recorded development build failure is an expected historical observation,
not permission to patch official sources or a reason to discard the stable build.
Changed compiler/CMake versions can produce different binary hashes; record the
new environment and rerun affected evidence instead of copying old fingerprints.

If only the custom host changes, use `toolchains.py --hosts-only` after reviewing
the change. It rebuilds hosts and updates the toolchain manifest without replacing
compiler/module binaries. Dependent execution evidence must then be refreshed.

### Research suites

Run each command separately, inspect its exit code and report, and retain failures.
Do not put this whole sequence behind a shell policy that stops at the first
expected failing suite and then assume later suites ran.

```sh
python3 -B research/tools/test_pawn_audit.py
python3 -B research/tools/pawn_compiler_config.py
python3 -B research/tools/pawn_lab.py
python3 -B research/tools/pawn_examples.py
python3 -B research/tools/pawn_defects.py
python3 -B research/tools/upstream_pawn.py --source .cache/research/toolchains/pawntest --compiler .cache/research/build64/pawncc --runner .cache/research/build32/pawnrun --include .cache/research/toolchains/pawn-stable/include --output research/evidence/pawn-upstream-results.json
python3 -B research/tools/pawn_gate.py --record
```

| Command | Main retained output and interpretation |
| --- | --- |
| test_pawn_audit.py | `pawn-audit-controls.json`; last retained run: 16 controls, zero failures/errors |
| pawn_compiler_config.py | `pawn-compiler-config-comparison.json`; 12 controlled observations, including intentional failures |
| pawn_lab.py | `pawn-original-results.json`; currently exits 1 for the 34 unmatched profiles |
| pawn_examples.py | `pawn-examples-results.json`; prior audit plus 40 independently predicted exercise profiles |
| pawn_defects.py | `pawn-defect-probes.json`; records observations, not a proficiency verdict |
| upstream_pawn.py | `pawn-upstream-results.json`; inspect all categories and exceptions, not just process success |
| pawn_gate.py --record | Replaces `pawn-gate.json` with current PASS/FAIL and exact blockers; currently exit 1 |

Outputs in that table are under `research/evidence/`. The primary harnesses use
unique run directories in the cache while updating their selected latest report.
Before deliberately replacing evidence, preserve the preceding report through Git
or a labeled historical copy when its history matters.

For the next focused investigation:

```sh
python3 -B research/tools/pawn_lab.py --case signed_arithmetic
```

This runs that case's selected widths/profiles, not only C16. The focused report
is `.cache/research/runs/original/results.json`, with an additional unique run
copy. It does **not** replace the authoritative full-suite report.

For a focused official exception, the adapter supports `--cases 29` (or a
comma-separated selection). Keep all the canonical compiler/runner/include
arguments above and use a different `--output` in the ignored cache. A focused
report cannot substitute for the required 161-case baseline.

The original harness uses a five-second CPU limit, eight-second wall timeout,
512 MiB address-space limit, two-MiB file limit, and disabled core dumps. Inspect
the actual adapter settings before extending a probe; its limits are separate.
Unchecked invalid-memory cases must remain outside ordinary correctness runs.
The custom host is not a security sandbox for arbitrary untrusted bytecode.

### Production commands

```sh
npm ci
npm run setup
npm run build
npm run verify
npm run compile -- plugins/stock_plugins/admin.sma
npm run compile -- api_custom_weapons.sma
npm run watch
```

Use watch as a separate interactive process; stop it before setup or a full build.
The prebuild step removes generated `dist/`; do not keep maintained work there.
The kit filename compile example depends on setup having downloaded the kit.
Production setup/build is separate from PAWN research.

On the original machine, Node 22.23.2 was available at `/usr/bin/node`, while npm
was previously found under the user's nvm v24.14.0 installation. Start a fresh
login shell and inspect `command -v node`, `node --version`, and
`command -v npm`; do not assume an old absolute npm path is still appropriate.
Use the Node/npm pair selected for the project.

## 8. Gate mechanics and evidence changes

The gate checks official archives/source trees, compiler selection/build flags,
binary/header/module identity, host source freshness, selected matrix identities,
commands, raw logs and bytecode, expected observations, example predictions,
official-suite coverage, instrument controls, topic dispositions, unresolved
prerequisites, and independent review fingerprints. It recomputes results rather
than trusting stored summary PASS values.

All primary harnesses supply `research/pawn/empty.cfg` with `-T`. An ambient
`pawn.cfg` must not contaminate a supposedly identical profile. Shared locks
cover tests and advancement checks; setup holds the exclusive lock. Those locks
coordinate cooperating tools, not arbitrary external writers.

Two kinds of freshness matter:

- Executable-input snapshots bind sources, headers, tools, host code, manifests,
  and relevant Python files. A relevant change requires new affected executions.
  The current snapshot is deliberately broad, so changing another research Python
  module can invalidate more evidence than expected.
- Advancement fingerprints also include PAWN reference/review material and
  selected evidence JSON. A documentation or review change may invalidate
  approval without changing the previously executed language program.

The three top-level handoff/navigation Markdown files do not replace the PAWN
evidence, and are outside the present gate's selected PAWN-document input tree.
Do not exploit that implementation detail to hide consequential semantic changes;
put such changes into the reference and relevant ledger/tests.

`amxx_lab.py` calls `require_current_pass()` before discovery, downloading,
compilation, or server work. The guard reevaluates the current gate and compares
its inputs to a recorded PASS. Even after an eventual valid PASS, the current
AMXX entry only reports that implementation is pending: it is still a stub.

**A remaining implementation obligation:** the current gate unconditionally
rejects unmatched original profiles and official exception categories. It has
no completed mechanism for reviewed defect dispositions to satisfy advancement.
The objective allows bounded defects/limitations with adequate evidence, but
adding a prose note or a topic row does not currently clear those failures.
After causal investigation and independent review, implement narrowly scoped
disposition handling if justified. Bind it to exact cases, configurations,
evidence hashes, predicted observations, and review. Add rejection controls for
stale, overbroad, duplicate, or unreviewed dispositions. Never introduce a
blanket “ignore failures” switch.

Topic disposition rows currently require an ID, a recognized status
(`verified`, `bounded_limitation`, or `inapplicable`), rationale, evidence
entries with path/hash, and an independent-review field. These structural checks
are not proof that a rationale or review is adequate. The reviewer must check
the actual topic obligations and cited evidence.

Likewise, filling `advancement-review.json` with `approve` is not review.
A real independent reviewer must examine the final inputs and bind the decision
to `input_hashes_without_review()`. Relevant changes afterward invalidate it.
The gate does not certify unspecified behavior, performance on other hardware,
or complete expertise outside the recorded scope.

## 9. Remaining PAWN work

Work in this order unless new evidence establishes a more consequential setup
fault that must be corrected first.

### A. Explain the C16 signed-arithmetic failure

1. Read `cases/signed_arithmetic.p`, its entry in `cases.json`, and the three
   C16 records in the current original report. Inspect the recorded compiler,
   bytecode, and runtime paths/hashes before deciding a rerun is needed.
2. Separate compile-time folding from execution: the fixture contains both
   literal expressions and values routed through the `identity` native.
   Inspect the matching VM's error definition and the first executed operations.
3. Check whether local array initialization, stack operations, or value loading
   corrupts an operand before division. This is an investigation hypothesis,
   not an established explanation for error 11.
4. Minimize the source while retaining the symptom. Hold compiler, emitted
   width, configuration, and bytecode constant when comparing VMs.
5. Use a separately named diagnostic VM/trace. If the existing five-store repair
   changes the result, isolate which instruction/store matters; a passing
   modified interpreter alone does not prove the cause.
6. Retain a source/bytecode-level causal trace or a precisely bounded unresolved
   reproducer, with successful controls at another width where applicable.
7. Obtain independent scrutiny of the causal claim before recording a defect
   disposition or moving on with an assumed explanation.

Acceptance: reproducible symptom, explicit expected behavior and source basis,
exact configuration, bounded cause or remaining uncertainty, raw evidence, and
a clear statement of what the result does and does not imply.

### B. Bound the other portability failures

Group by observed symptom, not by a guessed common cause. Investigate C16 packed
strings/evaluation and C64 packed strings/O3 separately. Check runtime opcodes
against emitted bytecode; distinguish invalid code generation, interpreter
execution errors, test bugs, and unsupported configurations. Keep compiler
assertions distinct from VM failures. Preserve default compiler internals.

Acceptance: every current failing profile is connected to a reviewed explanation
or an explicitly unresolved bounded reproducer; every eventual advancement
disposition has evidence, applicability, and limitations. Do not replace the
official baseline VM merely to produce a green matrix.

### C. Resolve the official-suite exceptions

Review the exact old oracle and current implementation for 29 and 61. For 63
and 97, determine whether an appropriate FORTIFY compiler build can be reproduced;
if not, state exactly which leak claim remains untested and whether that prevents
advancement. Do not use `--fortify` as a bare assertion of instrumentation.
For 71, independently verify removal of the old configuration and bound
inapplicability to this compiler/version.

Acceptance: each exception has an independent disposition and either its original
contract is exercised or the limitation/inapplicability is justified without
claiming the unperformed test passed. Any new gate policy must preserve these
distinctions and reject broader accidental exemptions.

### D. Close all 86 guide obligations

Select one topic or a tightly related group. Read the pinned guide sections,
associated implementation and available cases. Identify which subtopics lack
an executable check, explanation, diagnostic example, or host contract test.
Create focused examples with predictions before running them. Label complete
programs, wrapped fragments, and intentionally failing examples.

Develop the missing lexical/declaration/tag/macro/state material and host/native
address, lifetime, argument, memory, and debugging contracts. Distinguish language
rules from optional library behavior and implementation limitations. Complete
corrected replacements still missing from the prior-material audit.

Add truthful reviewed dispositions to `coverage-evidence.json` and extend the
claim/source/test ledger. An inapplicable status requires a source-backed scope
reason; it cannot be used to shrink the requested learning scope.

Acceptance: every inventory ID has adequate evidence for every listed obligation,
or a reviewed bounded limitation that satisfies the approved scope. The
`unresolved_questions_required_by_amxx` list becomes empty only when those
questions have actually been resolved sufficiently for the next phase.

### E. Final PAWN review and advancement

Freeze the intended input set for review. Rerun affected suites and controls,
verify exact coverage and raw evidence, and obtain a separately reasoned review.
Use new combined-feature exercises for genuinely unseen evaluation; the five
existing exercises are already known continuation material.

Have the reviewer examine consequential claims, setup, failure dispositions,
remaining scope limits, and prerequisite closure. Resolve disagreements through
sources and experiments. Record approval only after review, bind it to current
inputs, then record/evaluate the gate and test that stale or failing records still
block AMXX. A genuine passing gate is prerequisite to section 10, not the final
completion of the whole project.

## 10. AMXX work after advancement

This section is an implementation plan, not a description of completed AMXX
research. Keep the gate check before downloads/discovery/execution in the AMXX
research entry point. The already-authorized production build remains separate.

### Compatibility bridge and API coverage

Record the actual AMXX compiler binary/version, source provenance, includes,
module versions, and target engine/GameDLL. Compare canonical PAWN and AMXX
syntax, tags, strings/arrays, preprocessing, diagnostics, and runtime contracts
using small paired examples. A canonical example must not be copied into AMXX
and assumed compatible; the two toolchains are deliberately distinct.

Inventory public APIs from versioned headers, official documentation, and
implementation sources. Cover lifecycle and load ordering; natives and forwards;
commands and menus; tasks and callbacks; entities and hooks; resources and
precaching; containers and ownership; persistence; database callbacks; and module
boundaries. Record the exact include/native/forward and version for every recipe.

For each consequential contract, implement a minimal isolated plugin and an
observable test:

| Contract | Required observations |
| --- | --- |
| Handles and allocations | Creation, ownership transfer if any, failure handling, release, and cleanup on unload/map change |
| Players | Disconnect/reconnect, reused client slot, delayed task/callback associated with the original player |
| Entities | Removal and index reuse, validity at hook/callback time, safe access to required state |
| Timing and hooks | Lifecycle order, pre/post behavior, return-value effects, reentrancy where relevant |
| Resources | Required file present/absent, legal precache phase, map transition, actionable failure reporting |
| Persistence/SQL | Normal completion, failed connection/query, delayed callback, unloaded/reloaded context |
| Module boundary | Missing module/native, provider/consumer order, compatible engine/GameDLL versions |

### Required integration studies

Use AMXXPack, the complete Modding Kit, and ReAPI as mandatory case studies.
Study what the build tool packages versus what server providers supply; kit API
load order and resource ownership; native/forward integration; and ReAPI hooks
and engine prerequisites.

Survey Orpheu, CSDM, Zombie Plague, and additional relevant utilities using their
original repositories, releases, documentation, issue activity, and compatibility
evidence. Label historical influence separately from current suitability. Do not
equate stars, old tutorials, or a familiar name with current maintenance.

Identify distinct integration patterns and implement representative lab examples
for those patterns. The survey should justify the pattern set rather than
arbitrarily treating one example per project as adequate coverage. Version-pin
dependencies and record licensing/resource requirements. Research examples must
remain outside production discovery.

### Isolated local server

Previously located resources, to revalidate before use:

- `/home/crowg/.local/share/Steam/steamapps/common/Half-Life/`, including
  `cstrike/`, `valve/`, `hlds_run`, and `hlds_linux`.
- `/home/crowg/.steam/steamcmd/steamcmd.sh`.

Availability is not a tested server installation. Prepare a separate server tree
with compatible components; preserve the existing game installation, production
plugins, and configuration. Avoid hard links for files the lab may modify.
Record the server's files, version manifest, launch command, map, test plugins,
module configuration, console output, and AMXX error logs.

Begin with:

```text
meta list
amxx modules
amxx plugins
changelevel de_dust2
```

Confirm required modules/providers load and plugins report running; inspect logs
for missing natives/resources and runtime errors before and after the map change.
Join/rejoin when player contracts require it. Test normal CS round progression
and the specific integration behaviors, not merely server startup.

The root README lists supplied resources such as `sprites/bubble.spr`,
`sound/common/null.wav`, `models/rpgrocket.mdl`, `sprites/laserbeam.spr`,
`sound/weapons/scock1.wav`, explosion/smoke sprites, and burning sounds.
Verify availability through the CS/valve resource paths. These game assets are
not redistributed in the project.

Acceptance: a reproducible isolated installation and retained successful/expected
failure observations for loading, lifecycle, ownership, resources, integrations,
and map changes. If some runtime capability is unavailable, identify exactly
what remains unverified; compilation cannot replace that evidence.

## 11. Final research product and coding agent

Complete the navigable reference with explanations, corrected executable examples,
compatibility tables, API coverage, recipes, and unresolved limitations. Expand
the existing ledger into one authoritative requirements-to-source-to-test record.
Avoid competing spreadsheets/JSON files that disagree about completion.

Each consequential claim should identify: scope/version, source and location,
test/profile, expected result, observed evidence, hashes, review, and limitation.
Retain deliberately failing examples as such. Make every complete teaching example
compilable/executable through a documented command, and mark fragments explicitly.

Generate **one cited PDF report** from the validated material. Check that its
citations support the associated claims, preserve page/edition conventions, and
resolve to the intended sources. Render and inspect every page for clipped code,
unreadable tables, missing glyphs, broken layout, and incorrect page references.
No final PDF has been produced or visually verified yet.

Recheck production packaging after research changes. Require an exact expected
plugin set, current sources/includes/licenses, provider order, and no research,
test, or generated-source contamination across repeated builds. Retain focused
compile and source/include watch tests if their earlier proof is absent. Report
runtime validation separately from compilation and package verification.

Then present the research product for **user verification**. Do not infer approval
from silence, a passing gate, or the user's request to export this handoff.

After that approval, build the final coding agent grounded in the reference,
retrieval and tool workflows. An existing
`.github/agents/amxx-pawn-engineer.agent.md` file is not evidence that this final,
validated agent deliverable has been completed.

Evaluate the agent on new tasks covering canonical/AMXX dialect distinctions,
plugin correctness, version compatibility, player/entity lifetime, resource
ownership, hooks/callbacks, debugging, and calibrated uncertainty. Preserve task
prompts, expected acceptance criteria, patches, compile/runtime results, and
failure analysis. Keep test tasks separate from training/reference examples.
Measure demonstrated capability; do not promise equivalence to a larger hosted
model or universal perfection.

## 12. Local-model workflow

The user's proposed machine is CachyOS, Intel i9-10900F, 16 GB system RAM, and an
AMD RX 6700 XT. The prior recommendation was Qwen3.5-9B Q4_K_M through a current
llama.cpp Vulkan backend, with Q5_K_M as a later comparison and an initial 8,192
token context/one active request. This was a candidate recommendation, **not a
local installation, speed benchmark, or PAWN-accuracy result**.
Model/runtime references: [Qwen model card](https://huggingface.co/Qwen/Qwen3.5-9B),
[GGUF files](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/tree/main),
[llama.cpp Vulkan build guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).
Recheck runtime support before installing; keep it outside production directories.

Use the local model through an application that can read/search files, propose
edits, and run controlled commands. Merely opening a GGUF model does not give it
repository access, terminal tools, persistent task state, or independent review.
This handoff is retrieved context, not a weight update or a fine-tuning dataset.

For a small context window:

1. Load LOCAL_MODEL_START.md, the current STATUS.md, and the objective.
2. Retrieve the one handoff section needed for the selected task.
3. Retrieve the specific source, expectation, and report record, not an entire
   multi-megabyte report or all raw logs.
4. Keep a small working note distinguishing established facts, hypotheses, work
   in progress, and next steps. Checkpoint it before context eviction.
5. Re-read the authoritative files after resumption instead of trusting a
   model-generated summary when hashes, commands, or results matter.

A useful record inspection, run from the project root:

```sh
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("research/evidence/pawn-original-results.json").read_text())
for record in report["records"]:
    if record["name"] == "signed_arithmetic-C16-d2-O0":
        print(json.dumps(record, indent=2))
PY
```

Before accepting local-model edits, inspect the diff and run the relevant
compiler/VM or server checks. Evaluate a few new PAWN tasks first, including one
where the correct answer is to identify missing evidence. Generic coding
benchmarks do not establish reliable PAWN syntax, native contracts, or gate policy.

The existing independent exercises may be used as familiar smoke tests but cannot
be counted as unseen after reading this repository. Independent review must come
from a human or a separately tasked reviewer. A second response from the same
context is not automatically independent evidence. If review resources are
unavailable, retain the open requirement.

## 13. Checkpoints and GitHub access

The user authorized checkpoint commits and pushes. Use the established branch
`codex/pawn-foundation-checkpoint`; do not silently move work onto master.
Inspect task-owned versus unrelated changes and never force-push.

At session start, after substantial work, and before expensive work, check any
available account usage. At 80% of an applicable allowance, finish the bounded
work unit and checkpoint before another substantial task. At 90%, prioritize
the checkpoint and preserve capacity for the handoff. Do not buy credits or
redeem resets automatically.

During preparation of this handoff, the Codex account tool reported 100% used
in the five-hour window and 16% in the weekly window, with an available credit
balance. This requested documentation handoff was handled as a checkpoint task;
no new language matrix, model benchmark, or server study was started. Historical
reset timestamps are not proof that capacity has since been restored.

A local model normally has a different resource constraint: finite context,
GPU/system memory, and execution time rather than this Codex account allowance.
Retain milestone/context checkpoints and verify local capacity. Do not copy
stale Codex percentages into a claim about Qwen's capacity.

Every STATUS.md checkpoint must retain the full objective by summary and link,
current milestone, verified changes/evidence, gate failures, versions/configurations,
reproduction commands, live handles/pending reviews, the next action and acceptance
criteria, and available usage information.

Checkpoint sequence, with staged files adjusted to the task:

```sh
git status --short
git diff --check
git diff
git add research/STATUS.md PATHS_YOU_REVIEWED
git diff --cached --check
git diff --cached
git commit -m "Describe the concrete completed checkpoint"
git push origin codex/pawn-foundation-checkpoint
git rev-parse HEAD
git ls-remote --exit-code origin refs/heads/codex/pawn-foundation-checkpoint
```

`PATHS_YOU_REVIEWED` is a placeholder, not a real filename. Inspect the staged
diff before the commit. Compare the two final hashes; a successful local commit
or dry-run push is not proof of actual publication.

GitHub CLI authentication as `drori200` was verified from fresh login shells,
and actual pushes were successful. The remote branch was verified at checkpoint
`0c7a8792f9aaaf59dde4f66ab914db189a5a4623`, which includes the earlier research
checkpoint `b45b6a484da59218ee84f44fc06ead62d58ae8e5`.
Those are historical anchors; inspect the current remote tip after this handoff.

Under the Codex sandbox, `gh` executes but API network calls fail; the same
authentication and repository calls succeed with approved execution outside
that sandbox. The sandbox's “invalid token” report did not establish a bad login.
Use the application's normal approval mechanism when that environment requires
it; never disable or evade the sandbox. A separate local terminal may have a
different policy and should be checked directly.

The connected GitHub integration previously rejected writes with HTTP 403
`Resource not accessible by integration`. Working CLI credentials do not imply
that connector permission changed. Never export auth files or token values.

At the prior checkpoint no compiler/VM research process was running, the
foundation review had completed, and an old pending-init inventory-review handle
was interrupted. These are historical observations. Poll real handles or inspect
current processes before restarting work; a timeout or a leftover lock file is
not proof that a task finished.

## 14. Moving or exporting the workspace

The versioned reference uses ordinary Markdown, JSON, PAWN/C sources, and Python/
JavaScript tools. These are the local model's working inputs. Keep an offline
backup of the cache for raw evidence and historical binaries, but retrieve
specific text from it rather than indexing executable files.

The earlier export inspection measured approximately 6.8 MB for `research/`
and 838 MB for `.cache/research/`; these are snapshot sizes, not requirements.
GitHub contains the versioned reports but not the ignored raw-cache files.

After committing the desired checkpoint, create backups with:

```sh
export_dir="$HOME/Documents/AmxxModding-local-export"
mkdir -p "$export_dir"
git bundle create "$export_dir/history.bundle" --all
git bundle verify "$export_dir/history.bundle"
git archive --format=tar.gz --output="$export_dir/project.tar.gz" HEAD
tar -czf "$export_dir/research-cache.tar.gz" .cache/research
```

Run from the repository root. Git bundle/archive do not include uncommitted or
untracked files. Inspect and separately preserve user-owned work before exporting.
The commands above are instructions; this handoff task did not create those
backup archives. Production `.compiler/`, `.thirdparty/`, `node_modules/`,
and `dist/` are also ignored; regenerate them with the production workflow, or
preserve a separately labeled environment backup if exact old artifacts matter.

For a complete original-teaching archive, also preserve the four files listed
in `research/pawn/prior/original-artifacts.json`, currently under:

```text
/home/crowg/Documents/Codex/2026-09-07/explore-x20/
  .pptx-build/pawn-course/build-detailed-course.mjs
  .pptx-build/pawn-course/build-pawn-course.mjs
  output/pawn-zero-to-hero-course.pptx
  output/pawn-zero-to-hero-detailed-course.pptx
```

The project retains the extracted snippets and original file hashes, not complete
copies of those four original files. The current example harness uses the saved
snippet corpus, so replaying snippets is different from independently repeating
the original extraction from slide artifacts. Preserve both when moving machines.

The referenced old Codex task ID is `01a07d33-0d5d-7033-9263-724ae01687fc`.
A task link/ID is not a transcript. Export any desired conversation/attachments
separately and label them historical; this handoff does not claim to contain every
chat message. Avoid copying the whole Codex profile, which may contain unrelated
private data or credentials.

To restore history in a new location, clone the bundle with
`git clone --branch codex/pawn-foundation-checkpoint /path/to/history.bundle /path/to/AmxxModding`,
then extract the cache archive at the restored repository root. Replace the
placeholder paths. Unpack `project.tar.gz` instead if a source snapshot without
Git history is sufficient.

Many recorded commands and log paths are absolute. A different directory,
compiler, library environment, or rebuilt binary can make historical evidence
stale. Python virtual environments and cached executables are also host-specific.
Keep old reports for provenance, rebuild/replay affected work for the new
environment, and obtain current validation/review. Do not rewrite old paths and
hashes to pretend old evidence was produced by a new execution.

## 15. Verification of this handoff

This write-up was checked against the current objective, STATUS/README files,
production configuration/scripts, PAWN harness and gate source, source/toolchain
manifests, original/upstream/example/control/defect reports, independent review
records, and the original-artifact manifest.

During preparation, the gate was evaluated without replacing its recorded JSON;
it still reported the five expected blockers. Counts were independently derived
from original-profile records and compared with the retained summaries. All four
original teaching/build artifact hashes still matched their manifest.

Document checks found 43 valid local links and 11 shell examples with valid Bash
syntax across the two handoff files, README, and STATUS. Matrix/upstream counts
and all five pinned download fingerprints match the inspected reports. These checks
do not constitute a fresh full language suite, production build, local-model
benchmark, server test, independent advancement approval, or PDF review.

On continuation, preserve this distinction: what the previous evidence recorded,
what a new run actually observed, what remains a hypothesis, and what the user
still requires. Update STATUS.md after meaningful progress and keep the full
objective intact.
