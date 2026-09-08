import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile, chmod, access, rm } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import decompress from 'decompress';

const root = fileURLToPath(new URL('../', import.meta.url));
process.chdir(root);
const require = createRequire(import.meta.url);
const cli = require.resolve('amxxpack');
const config = JSON.parse(await readFile('.amxxpack.json', 'utf8'));

function amxxpack(...args) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    stdio: 'inherit', timeout: 120_000,
  });
  if (result.error) console.error(result.error.message);
  return result.status === 0;
}

async function download(url) {
  const response = await fetch(url, { signal: AbortSignal.timeout(60_000) });
  if (!response.ok) throw new Error(`Download failed (${response.status}): ${url}`);
  return response;
}

async function githubCompiler() {
  const platform = { linux: 'linux', win32: 'windows' }[process.platform];
  if (!platform) throw new Error('Compiler fallback supports Linux and Windows. Use Linux/WSL for this project.');
  const releases = await (await download('https://api.github.com/repos/alliedmodders/amxmodx/releases?per_page=100')).json();
  const release = releases.filter(r => !r.draft && r.tag_name.startsWith(`${config.compiler.version}.`))
    .sort((a, b) => b.tag_name.localeCompare(a.tag_name, undefined, { numeric: true }))[0];
  if (!release) throw new Error(`No official AMXX ${config.compiler.version} release found.`);
  const compilerDir = config.compiler.dir;
  await mkdir(compilerDir, { recursive: true });
  for (const addon of ['base', ...config.compiler.addons]) {
    const extension = platform === 'linux' ? 'tar.gz' : 'zip';
    const asset = release.assets.find(a => a.name.endsWith(`-${addon}-${platform}.${extension}`));
    if (!asset) throw new Error(`Missing ${addon}/${platform} archive in ${release.tag_name}.`);
    console.log(`Installing official compiler archive: ${asset.name}`);
    const buffer = Buffer.from(await (await download(asset.browser_download_url)).arrayBuffer());
    const prefix = 'addons/amxmodx/scripting/';
    await decompress(buffer, compilerDir, {
      filter: file => file.path.startsWith(prefix) && !file.path.endsWith('.sma'),
      map: file => ({ ...file, path: file.path.slice(prefix.length) }),
    });
  }
  await writeFile(path.join(compilerDir, 'SOURCE.json'), JSON.stringify({
    channel: config.compiler.version, release: release.tag_name, url: release.html_url,
  }, null, 2) + '\n');
}

try {
  if (!amxxpack('install', '--compiler')) {
    console.warn('AMXX download failed; trying official AlliedModders GitHub releases.');
    await githubCompiler();
  } else {
    // Do not retain provenance from an earlier fallback installation.
    await rm(path.join(config.compiler.dir, 'SOURCE.json'), { force: true });
  }
  if (!amxxpack('install', '--thirdparty')) throw new Error('Third-party installation failed. Rerun npm run setup.');
  const compiler = path.resolve(config.compiler.dir, process.platform === 'win32' ? 'amxxpc.exe' : 'amxxpc');
  await access(compiler);
  if (process.platform !== 'win32') await chmod(compiler, 0o755);
  await access('.thirdparty/reapi/addons/amxmodx/scripting/include/reapi.inc');
  await access('.thirdparty/amxx-modding-kit/api/custom-weapons/api_custom_weapons.sma');
  await access('.thirdparty/reapi-license/LICENSE');
  console.log('Setup complete. Run npm run build.');
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
