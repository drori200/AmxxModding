import assert from 'node:assert/strict';
import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

process.chdir(fileURLToPath(new URL('../', import.meta.url)));
const kit = '.thirdparty/amxx-modding-kit';
const output = 'dist/addons/amxmodx';

async function files(dir, extension) {
  const result = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const name = path.join(dir, entry.name);
    if (entry.isDirectory()) result.push(...await files(name, extension));
    else if (entry.name.endsWith(extension)) result.push(name);
  }
  return result;
}

try {
  const localScripts = (await readdir('.')).filter(name => name.endsWith('.sma'));
  assert(localScripts.length > 0, 'No root plugin sources found; include the existing sources in your checkout.');
  const kitScripts = (await Promise.all(['api', 'entities', 'weapons', 'player-effects']
    .map(dir => files(`${kit}/${dir}`, '.sma')))).flat();
  assert.equal(kitScripts.length, 24, 'Expected the 24 plugins in the pinned modding kit. Review dependency updates.');
  const sources = [...localScripts, ...kitScripts];
  const expected = sources.map(source => path.basename(source, '.sma') + '.amxx');
  assert.equal(new Set(expected).size, expected.length, 'Plugin output name collision.');
  const binaries = await files(`${output}/plugins`, '.amxx');
  assert.deepEqual(binaries.map(file => path.relative(`${output}/plugins`, file)).sort(), expected.sort(),
    'Missing or unexpected plugins in dist (test plugins and stale outputs must not ship).');
  for (const binary of binaries) assert((await stat(binary)).size > 0, `Empty plugin: ${binary}`);
  const packagedScripts = await files(`${output}/scripting`, '.sma');
  assert.deepEqual(packagedScripts.map(file => path.basename(file)).sort(), sources.map(file => path.basename(file)).sort());
  for (const source of sources) {
    assert.deepEqual(await readFile(`${output}/scripting/${path.basename(source)}`), await readFile(source), `Source copy mismatch: ${source}`);
  }

  const ini = await readFile(`${output}/configs/plugins-modding-kit.ini`, 'utf8');
  const plugins = ini.split(/\r?\n/).map(line => line.split(';')[0].trim()).filter(Boolean);
  assert.deepEqual([...plugins].sort(), kitScripts.map(file => path.basename(file, '.sma') + '.amxx').sort());
  for (const source of kitScripts) {
    const plugin = path.basename(source, '.sma') + '.amxx';
    const text = await readFile(source, 'utf8');
    for (const [, dependency] of text.matchAll(/^\s*#(?:try)?include\s+<(api_[^>]+)>/gm)) {
      const provider = `${dependency}.amxx`;
      if (plugins.includes(provider)) assert(plugins.indexOf(provider) < plugins.indexOf(plugin), `${provider} must load before ${plugin}`);
    }
  }
  // Later include inputs intentionally replace the old standard headers for packaging.
  const expectedIncludes = new Map();
  for (const dir of ['include', '.compiler/include', kit, '.thirdparty/reapi/addons/amxmodx/scripting/include']) {
    for (const file of await files(dir, '.inc')) expectedIncludes.set(path.basename(file), file);
  }
  for (const [name, file] of expectedIncludes) {
    assert.deepEqual(await readFile(`${output}/scripting/include/${name}`), await readFile(file), `Include copy mismatch: ${name}`);
  }
  for (const name of ['amxx-modding-kit', 'amxxpack', 'reapi']) {
    assert((await stat(`${output}/licenses/${name}/LICENSE`)).size > 0, `Missing ${name} license`);
  }
  console.log(`Verified ${localScripts.length} existing plugins + ${kitScripts.length} kit plugins, ${expectedIncludes.size} includes, sources, licenses, and load order.`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
