#!/usr/bin/env node
/*
Optimize screenshots for README/landing/listings.

- Reads docs/screenshots/manifest.json
- For each item.file (PNG), produces:
  - docs/screenshots/optimized/<id>.jpg (resized)
  - docs/screenshots/optimized/<id>.png (resized, if you prefer PNG)

Uses macOS `sips` (dependency-free).

Usage:
  node scripts/optimize_screenshots.mjs --width 1400 --format jpg
*/

import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const getArg = (name, def) => {
  const i = args.indexOf(name);
  if (i === -1) return def;
  const v = args[i + 1];
  if (!v || v.startsWith('--')) return def;
  return v;
};

const width = Number(getArg('--width', '1400'));
const format = String(getArg('--format', 'jpg')).toLowerCase();
const keepPng = args.includes('--keep-png');

if (!Number.isFinite(width) || width <= 0) {
  console.error(`Invalid --width: ${width}`);
  process.exit(2);
}
if (!['jpg', 'jpeg', 'png'].includes(format)) {
  console.error(`Invalid --format: ${format} (expected jpg|png)`);
  process.exit(2);
}

const repoRoot = process.cwd();
const manifestPath = path.join(repoRoot, 'docs', 'screenshots', 'manifest.json');
const shotsDir = path.dirname(manifestPath);
const outDir = path.join(shotsDir, 'optimized');
fs.mkdirSync(outDir, { recursive: true });

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const items = Array.isArray(manifest.items) ? manifest.items : [];

const run = (cmd, cmdArgs) => {
  execFileSync(cmd, cmdArgs, { stdio: 'inherit' });
};

const sipsExists = (() => {
  try {
    execFileSync('sips', ['--version'], { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
})();

if (!sipsExists) {
  console.error('Missing `sips` (macOS). This script currently requires macOS.');
  process.exit(2);
}

let ok = 0;
let skipped = 0;

for (const item of items) {
  const id = item?.id;
  const file = item?.file;
  if (!id || !file) continue;

  const inPath = path.join(shotsDir, file);
  if (!fs.existsSync(inPath)) {
    console.warn(`SKIP (missing): ${path.relative(repoRoot, inPath)}`);
    skipped++;
    continue;
  }

  const outExt = format === 'jpeg' ? 'jpg' : format;
  const outPath = path.join(outDir, `${id}.${outExt}`);

  // Resize + format conversion.
  // Note: sips writes in-place; we copy to a tmp path then convert.
  const tmpPath = path.join(outDir, `${id}.tmp.png`);
  fs.copyFileSync(inPath, tmpPath);

  // Resize first.
  run('sips', ['-Z', String(width), tmpPath]);

  if (outExt === 'png') {
    fs.renameSync(tmpPath, outPath);
  } else {
    run('sips', ['-s', 'format', 'jpeg', '-s', 'formatOptions', '80', tmpPath, '--out', outPath]);
    fs.rmSync(tmpPath);
  }

  if (keepPng && outExt !== 'png') {
    const outPng = path.join(outDir, `${id}.png`);
    const tmpPath2 = path.join(outDir, `${id}.tmp2.png`);
    fs.copyFileSync(inPath, tmpPath2);
    run('sips', ['-Z', String(width), tmpPath2]);
    fs.renameSync(tmpPath2, outPng);
  }

  ok++;
  console.log(`Wrote: ${path.relative(repoRoot, outPath)}`);
}

console.log(`\nDone. optimized=${ok}, skipped=${skipped}, outDir=${path.relative(repoRoot, outDir)}`);
