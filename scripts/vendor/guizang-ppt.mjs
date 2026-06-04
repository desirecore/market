#!/usr/bin/env node
/**
 * Vendor 更新器：把上游 op7418/guizang-ppt-skill 同步进官方市场的 skills/guizang-ppt/。
 *
 * 设计目标（“手动可更新”）：
 *   - 上游内容（references/ assets/ scripts/ LICENSE + SKILL.md 正文）是“被 vendored”的，可重复覆盖；
 *   - DesireCore 自己维护的元数据放在 skills/guizang-ppt/_desirecore/（frontmatter.yaml 覆盖层 + NOTICE.md），
 *     vendor 时不被上游覆盖；
 *   - 每次同步把上游 commit/版本写进 _desirecore/upstream.json，保证可追溯。
 *
 * 用法：
 *   node scripts/vendor/guizang-ppt.mjs --src /path/to/local/guizang-ppt-skill   # 复用本地 clone
 *   node scripts/vendor/guizang-ppt.mjs --ref v1.2.0                             # 联网 clone 指定 ref
 *   node scripts/vendor/guizang-ppt.mjs                                          # 联网 clone 默认分支
 *
 * 同步后仍需人工：核对 diff、必要时 bump _desirecore/frontmatter.yaml#version 与 metadata.updated_at、
 * 更新根 manifest.json，再 commit / push。
 */

import { execSync } from 'node:child_process'
import {
  existsSync,
  readFileSync,
  writeFileSync,
  rmSync,
  cpSync,
  mkdtempSync,
} from 'node:fs'
import { join, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { tmpdir } from 'node:os'

const SKILL_ID = 'guizang-ppt'
const UPSTREAM_URL = 'https://github.com/op7418/guizang-ppt-skill.git'
const DEFAULT_BRANCH = 'main'
// 从上游仓库 vendor 进来的顶层条目（会被每次同步覆盖刷新）
const VENDORED_ENTRIES = ['references', 'assets', 'scripts', 'LICENSE']

const __dir = dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = resolve(__dir, '..', '..') // scripts/vendor -> 仓库根
const SKILL_DIR = join(REPO_ROOT, 'skills', SKILL_ID)
const DESIRE_DIR = join(SKILL_DIR, '_desirecore')
const FRONTMATTER_FILE = join(DESIRE_DIR, 'frontmatter.yaml')

function parseArgs(argv) {
  const out = { src: null, ref: DEFAULT_BRANCH }
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--src') out.src = argv[++i]
    else if (argv[i] === '--ref') out.ref = argv[++i]
  }
  return out
}

function git(cmd, cwd) {
  return execSync(`git ${cmd}`, { cwd, encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim()
}

/** 取得上游源目录与 commit/ref；本地 --src 优先，否则浅克隆。返回 { srcDir, commit, ref, cleanup } */
function resolveSource(args) {
  if (args.src) {
    const srcDir = resolve(args.src)
    if (!existsSync(join(srcDir, 'SKILL.md'))) {
      throw new Error(`--src 指向的目录缺少 SKILL.md：${srcDir}`)
    }
    let commit = 'unknown'
    try {
      commit = git('rev-parse HEAD', srcDir)
    } catch {
      /* 非 git 目录则忽略 */
    }
    return { srcDir, commit, ref: args.ref, cleanup: () => {} }
  }
  const tmp = mkdtempSync(join(tmpdir(), 'guizang-vendor-'))
  console.log(`→ 克隆上游 ${UPSTREAM_URL} (ref=${args.ref}) ...`)
  execSync(`git clone --depth 1 --branch ${args.ref} ${UPSTREAM_URL} ${tmp}`, {
    stdio: ['pipe', 'pipe', 'pipe'],
  })
  const commit = git('rev-parse HEAD', tmp)
  return { srcDir: tmp, commit, ref: args.ref, cleanup: () => rmSync(tmp, { recursive: true, force: true }) }
}

/** 去掉上游 SKILL.md 的 frontmatter，返回正文 */
function stripFrontmatter(text) {
  const lines = text.split('\n')
  if (lines[0].trim() !== '---') return text.trim() + '\n'
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      return lines.slice(i + 1).join('\n').replace(/^\n+/, '')
    }
  }
  return text.trim() + '\n'
}

function main() {
  const args = parseArgs(process.argv.slice(2))

  if (!existsSync(FRONTMATTER_FILE)) {
    throw new Error(`缺少覆盖层 frontmatter：${FRONTMATTER_FILE}`)
  }
  const frontmatter = readFileSync(FRONTMATTER_FILE, 'utf-8').trimEnd()

  const { srcDir, commit, ref, cleanup } = resolveSource(args)
  try {
    // 1. 清理旧的 vendored 内容（保留 _desirecore/ 与 NOTICE.md 等维护态）
    for (const entry of [...VENDORED_ENTRIES, 'SKILL.md']) {
      rmSync(join(SKILL_DIR, entry), { recursive: true, force: true })
    }

    // 2. 复制上游 vendored 条目
    for (const entry of VENDORED_ENTRIES) {
      const from = join(srcDir, entry)
      if (existsSync(from)) {
        cpSync(from, join(SKILL_DIR, entry), { recursive: true })
      } else {
        console.warn(`  ⚠ 上游缺少 ${entry}，跳过`)
      }
    }

    // 3. 生成 SKILL.md = 覆盖层 frontmatter + 上游正文
    const upstreamSkill = readFileSync(join(srcDir, 'SKILL.md'), 'utf-8')
    const body = stripFrontmatter(upstreamSkill)
    writeFileSync(join(SKILL_DIR, 'SKILL.md'), `${frontmatter}\n\n${body}`)

    // 4. 写溯源信息
    const upstream = {
      skillId: SKILL_ID,
      repoUrl: UPSTREAM_URL,
      branch: DEFAULT_BRANCH,
      ref,
      commit,
      license: 'AGPL-3.0',
      author: '歸藏 (op7418)',
      vendoredAt: new Date().toISOString(),
    }
    writeFileSync(join(DESIRE_DIR, 'upstream.json'), `${JSON.stringify(upstream, null, 2)}\n`)

    console.log('✓ vendor 完成')
    console.log(`  upstream commit: ${commit}`)
    console.log(`  skill dir:       skills/${SKILL_ID}/`)
    console.log('  后续：核对 diff → 必要时 bump _desirecore/frontmatter.yaml#version 与根 manifest.json → commit')
  } finally {
    cleanup()
  }
}

main()
