// AMXXPack's asset glob skips extensionless files such as LICENSE.
import { copyFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

process.chdir(fileURLToPath(new URL('../', import.meta.url)));
const output = 'dist/addons/amxmodx';
for (const [source, destination] of [
  ['.thirdparty/amxx-modding-kit/LICENSE', 'licenses/amxx-modding-kit/LICENSE'],
  ['.thirdparty/amxx-modding-kit/CREDITS.md', 'licenses/amxx-modding-kit/CREDITS.md'],
  ['node_modules/amxxpack/LICENSE', 'licenses/amxxpack/LICENSE'],
  ['.thirdparty/reapi-license/LICENSE', 'licenses/reapi/LICENSE'],
  ['README.md', 'README.md'],
  ['.amxxpack.json', 'build-config.json'],
]) {
  const target = path.join(output, destination);
  await mkdir(path.dirname(target), { recursive: true });
  await copyFile(source, target);
}
