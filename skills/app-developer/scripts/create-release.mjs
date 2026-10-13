/** 教学清单生成器：读取显式inputs，固定原始字节；不是平台自动build/install器。 */
import { createHash } from 'node:crypto'
import { lstatSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve, join } from 'node:path'

if (!process.argv[2]) throw new Error('example_directory_required')
const directory = resolve(process.argv[2])
const input = JSON.parse(readFileSync(join(directory, 'release-inputs.json'), 'utf8'))
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
const canonical = value => Array.isArray(value) ? value.map(canonical) : value && typeof value === 'object'
  ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value
const files = input.files.map(file => {
  if (typeof file.path !== 'string' || /[\\\x00-\x1f?#:]/.test(file.path) || file.path.startsWith('/') ||
    file.path.split('/').some(part => !part || part === '.' || part === '..') || file.path === 'app-release.json') throw new Error('invalid_payload_path')
  const parts = file.path.split('/')
  for (let i = 1; i <= parts.length; i++) if (lstatSync(join(directory, ...parts.slice(0, i))).isSymbolicLink()) throw new Error('payload_link_rejected')
  const bytes = readFileSync(join(directory, file.path))
  return { path: file.path, role: file.role, sha256: hash(bytes), size: bytes.length }
}).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0)
if (new Set(files.map(file => file.path)).size !== files.length) throw new Error('duplicate_payload_path')
if (!files.some(file => file.path === 'application.json' && file.role === 'definition') ||
  !files.some(file => file.path === '说明.md') ||
  (input.dataContractPath && !files.some(file => file.path === input.dataContractPath && file.role === 'data-contract'))) throw new Error('missing_declared_payload')
const definition = JSON.parse(readFileSync(join(directory, 'application.json'), 'utf8'))
const manifest = { schemaVersion: 1, canonicalization: 'app-release-c14n-v1', definition, delivery: input.delivery, files,
  source: { kind: 'worktree', sha256: hash(JSON.stringify(canonical(files))) }, supportedPlatforms: input.supportedPlatforms,
  minimumClientVersion: '10.0.180', requiredCapabilities: input.requiredCapabilities,
  ...(input.dataContractPath ? { dataContract: JSON.parse(readFileSync(join(directory, input.dataContractPath), 'utf8')) } : {}),
  ...(input.bridgeCapabilities ? { bridgeCapabilities: input.bridgeCapabilities } : {}),
  instructionsPath: '说明.md' }
manifest.releaseDigest = hash(JSON.stringify(canonical(manifest)))
writeFileSync(join(directory, 'app-release.json'), JSON.stringify(manifest, null, 2) + '\n')
console.log(JSON.stringify({ appId: definition.id, version: definition.version, releaseDigest: manifest.releaseDigest, files: files.length }))
