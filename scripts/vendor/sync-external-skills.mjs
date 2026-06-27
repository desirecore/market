#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const sourcesPath = resolve(root, 'scripts/vendor/external-skills.json');
const lockPath = resolve(root, 'scripts/vendor/external-skills.lock.json');

async function readJson(path, fallback) {
  try {
    return JSON.parse(await readFile(path, 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') return fallback;
    throw error;
  }
}

function parseGitHubRepo(url) {
  const match = url.match(/^https:\/\/github\.com\/([^/]+)\/([^/.]+)(?:\.git)?$/);
  if (!match) return null;
  return { owner: match[1], repo: match[2] };
}

async function fetchJson(url) {
  const response = await fetch(url, {
    redirect: 'follow',
    headers: {
      accept: 'application/vnd.github+json',
      'user-agent': 'desirecore-market-sync'
    },
    signal: AbortSignal.timeout(15000)
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function getGitHead(url) {
  const repo = parseGitHubRepo(url);
  if (!repo) throw new Error('only GitHub HTTPS remotes are supported');

  const apiBase = `https://api.github.com/repos/${repo.owner}/${repo.repo}`;
  const metadata = await fetchJson(apiBase);
  const branchName = metadata.default_branch || 'main';
  const branch = await fetchJson(`${apiBase}/branches/${encodeURIComponent(branchName)}`);

  return {
    ref: branchName,
    revision: branch.commit?.sha || null
  };
}

async function getUrlDigest(url) {
  const response = await fetch(url, {
    redirect: 'follow',
    signal: AbortSignal.timeout(15000)
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText}`);
  }
  const buffer = Buffer.from(await response.arrayBuffer());
  return {
    revision: createHash('sha256').update(buffer).digest('hex'),
    size: buffer.length,
    contentType: response.headers.get('content-type') || null,
    lastModified: response.headers.get('last-modified') || null,
    etag: response.headers.get('etag') || null
  };
}

async function main() {
  const sources = await readJson(sourcesPath, []);
  const previous = await readJson(lockPath, { generatedAt: null, sources: {} });
  const next = {
    generatedAt: new Date().toISOString(),
    sources: {}
  };

  for (const source of sources) {
    const prior = previous.sources?.[source.id] || {};
    try {
      let info;
      if (source.kind === 'git') {
        info = await getGitHead(source.url);
      } else {
        info = await getUrlDigest(source.url);
      }

      next.sources[source.id] = {
        ...source,
        ...info,
        checkedAt: next.generatedAt,
        status: prior.revision && prior.revision !== info.revision ? 'changed' : 'current'
      };
    } catch (error) {
      next.sources[source.id] = {
        ...source,
        revision: prior.revision || null,
        checkedAt: next.generatedAt,
        status: 'check-failed',
        error: error.message
      };
    }
  }

  await writeFile(lockPath, `${JSON.stringify(next, null, 2)}\n`);

  const changed = Object.values(next.sources).filter((source) => source.status === 'changed');
  const failed = Object.values(next.sources).filter((source) => source.status === 'check-failed');

  console.log(`Checked ${sources.length} external skill sources.`);
  console.log(`Changed: ${changed.length}`);
  console.log(`Failed: ${failed.length}`);

  for (const source of changed) {
    console.log(`changed ${source.id}: ${source.revision}`);
  }
  for (const source of failed) {
    console.log(`failed ${source.id}: ${source.error}`);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
