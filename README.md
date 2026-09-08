# AmxxModding

Build the existing Counter-Strike 1.6 plugins and the complete
[AMXX Modding Kit](https://github.com/Hedgefog/amxx-modding-kit) with
[AMXXPack](https://github.com/Hedgefog/node-amxxpack). The kit provides 20 APIs
and four bundled entities, weapons, and effects. It does not automatically
create a new gameplay mode.

## Requirements and setup

- Node.js 22 or newer, with npm on `PATH` (`nvm install && nvm use` if using nvm).
- Linux is the tested build platform; on Windows, WSL with Ubuntu is recommended.
- On Ubuntu/Debian, install the 32-bit compiler runtime:

  ```sh
  sudo apt-get update
  sudo apt-get install lib32stdc++6 lib32z1
  ```

From the project directory:

```sh
npm ci
npm run setup
npm run build
```

`setup` installs an AMXX 1.10 compiler and Counter-Strike headers into
`.compiler/`, and downloads the kit and ReAPI into `.thirdparty/`. If the AMXX
download site is unavailable, it downloads the newest AMXX 1.10 release from
the official AlliedModders GitHub repository instead. The fallback records
the selected release in `.compiler/SOURCE.json`. A fresh setup may obtain a
newer compiler within the 1.10 channel. Setup needs internet access.

If npm is missing but Node is installed, activate your nvm installation or
install Node with npm. If `amxxpc` exists but cannot execute, check the 32-bit
runtime packages above and `ldd .compiler/amxxpc`.

## Development commands

| Command | Result |
| --- | --- |
| `npm run setup` | Download compiler and configured third-party dependencies |
| `npm run build` | Clean and rebuild the complete distribution, then verify it |
| `npm run watch` | Build and watch sources/includes, recompiling dependents |
| `npm run compile -- plugins/stock_plugins/admin.sma` | Compile one existing plugin |
| `npm run compile -- api_custom_weapons.sma` | Compile one kit plugin |
| `npm run verify` | Check the previously built package and kit load order |

Put your own `.sma` files under `plugins/` and organize stock or custom plugins
in subdirectories such as `plugins/stock_plugins/`. The build discovers `.sma`
files recursively below `plugins/`; keep plugin filenames unique because the
packaged output is flat. Put your custom `.inc` files in
`include/`. Kit headers are available directly, for example
`#include <api_custom_entities>`. Preserve their native and forward interfaces;
the corresponding API plugin must run on the server before its consumers.

The existing source layout, includes, compiler, and `compile.sh` are preserved.
The legacy script still uses the old root compiler and builds only root plugins.
The npm workflow uses the isolated compiler's standard headers ahead of the old
local headers. Packaged standard headers also come from the isolated compiler.
Avoid giving custom headers the same names as standard AMXX headers.

Production inputs are plugins under `plugins/`, the kit's `api/`, `entities/`,
`weapons/`, and `player-effects/` sources, their includes, and project `assets/`.
AMXX/ReAPI tests, `testsuite/`, downloaded compiler samples, and generated source
copies are excluded. Kit sources remain downloaded dependencies; put maintained
project changes in your own root plugins. Stop watch mode before a full build,
rerunning setup, or updating dependencies.

## Build output and server installation

`dist/addons/amxmodx/` contains compiled plugins, matching sources and includes,
`configs/plugins-modding-kit.ini`, license notices, this guide, and the build
configuration. It is an add-on package for an existing server, not a complete
AMXX/server installation. The standard plugins retain their original names.

1. Prepare CS 1.6 with AMXX 1.10 (base and Counter-Strike packages), Metamod,
   compatible [ReHLDS](https://github.com/rehlds/ReHLDS) and
   [ReGameDLL_CS](https://github.com/rehlds/ReGameDLL_CS), and
   [ReAPI 5.29.0.358](https://github.com/rehlds/ReAPI/releases/tag/5.29.0.358).
   Follow the engine/module projects' installation requirements.
2. Install the ReAPI module for your server OS from
   `.thirdparty/reapi/addons/amxmodx/modules/` into the server's matching module
   directory, or use the official release. ReAPI binaries are not copied into
   `dist/`; its headers are included for development.
3. Ensure the AMXX `engine`, `fakemeta`, `hamsandwich`, `cstrike`, and `csx` modules
   are available. ReAPI and standard AMXX modules normally autoload from plugin
   requirements; confirm this using `amxx modules`. JSON support is part of AMXX
   1.10. Orpheu is not used by this build.
4. Install the generated files under the server's `cstrike/` directory after
   backing up existing files. The root stock plugin binaries replace files of
   the same names if copied; keep your existing `plugins.ini` and stock settings.
5. AMXX loads `configs/plugins-*.ini` files in addition to `plugins.ini`. Install
   `plugins-modding-kit.ini` once; do not duplicate its entries in `plugins.ini`.
   It enables all 24 kit plugins, with API providers before bundled consumers.
   Put your custom consumers below the kit entries in this same file to make
   their load order explicit.

Keep a complete stock CS/Half-Life game installation, including resources found
through the `valve/` fallback. In particular, the supplied plugins precache:

- Assets API: `sprites/bubble.spr` and `sound/common/null.wav` (defaults).
- Camera API: `models/rpgrocket.mdl`.
- Entity Selection API: `sprites/laserbeam.spr`.
- Custom Weapons API: `sprites/bubble.spr` and `sound/weapons/scock1.wav`.
- Fire entity: `sprites/bexplo.spr`, `sprites/cexplo.spr`,
  `sprites/black_smoke1.spr` through `black_smoke4.spr`, and
  `sound/ambience/burning1.wav` through `burning3.wav`.

These game resources are not redistributed here. Resources registered by your
own entities, weapons, cosmetics, or music must also exist and be precached.
The throwable plugin provides a base weapon class; it does not give players a
new weapon automatically. The rounds API uses CS rounds unless a consumer
explicitly enables its custom round manager.

## Verification

The build verifier checks all plugins under `plugins/` plus all 24 kit plugins, nonempty
binaries, exact source/include copies, third-party licenses, and provider order.
Unexpected binaries (including stale or test plugins) fail verification.
GitHub Actions runs setup, compilation, and package verification on Ubuntu with
Node 22 and publishes the `amxx-modding-cstrike` artifact.

On a development server, start a standard map and run:

```text
meta list
amxx modules
amxx plugins
changelevel de_dust2
```

Confirm that ReAPI and required modules load, all 24 kit plugins report `running`,
and no missing natives, missing resources, or runtime errors appear in the
server console or `addons/amxmodx/logs/`, including after the map change. Join
the server and confirm normal CS round progression. Compilation and packaging
checks do not establish runtime compatibility; a live server is required for
this smoke test.

## Dependencies and updates

| Dependency | Selection |
| --- | --- |
| AMXXPack | npm `amxxpack` **1.5.3**, locked by `package-lock.json` |
| AMXX compiler | **1.10** channel, base + cstrike |
| Modding Kit | commit `1a29ced127e3e93c5f0cdcae22651a782c5c55c0` |
| ReAPI | **5.29.0.358** release and matching license |

Change third-party URLs in `.amxxpack.json` deliberately. Remove the affected
generated dependency directory before running setup to avoid retaining removed
upstream files. Recheck plugin names, kit plugin count and load order, includes,
server requirements, and the smoke test when updating the kit. Change the npm
version with `npm install --save-dev --save-exact amxxpack@VERSION`, retaining
the updated lockfile. Do not use a floating branch archive for the kit.

AMXXPack 1.5.3 depends on `decompress` 4.2.1, which currently has npm audit
advisories for archive extraction and no patched release in that package line.
This integration retains the requested AMXXPack version and downloads archives
only from the specified upstream projects. Do not configure untrusted archive
URLs. A compatible `minimatch` override fixes the separately reported glob
matching advisories. Review `npm audit` when updating dependencies.

The upstream AMXXPack and Modding Kit MIT licenses and kit credits, and ReAPI's
license, are included in the distribution's `licenses/` directory. Existing
AMXX source license headers remain intact. Downloaded dependencies, `dist/`,
`.compiler/`, and `.amxx` files are ignored by Git; commit the existing project
sources and the new configuration, tooling, documentation, and lockfile.
