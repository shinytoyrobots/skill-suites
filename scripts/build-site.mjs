#!/usr/bin/env node
// Builds the static site into dist/ from skills/ and site-src/. No dependencies.
//   node scripts/build-site.mjs            build (SITE_BASE defaults to /skill-suites/)
//   node scripts/build-site.mjs --check    build, then verify every internal link resolves
//   node scripts/build-site.mjs --serve    build, then serve dist/ under SITE_BASE on :8080
import { readFileSync, writeFileSync, readdirSync, existsSync, rmSync, mkdirSync, cpSync, statSync } from 'node:fs';
import { join, dirname, resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';
import { createHash } from 'node:crypto';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SKILLS = join(ROOT, 'skills');
const SRC = join(ROOT, 'site-src');
const DIST = join(ROOT, 'dist');
const REPO = 'shinytoyrobots/skill-suites';
const GH = `https://github.com/${REPO}`;

let BASE = process.env.SITE_BASE || '/skill-suites/';
if (!BASE.startsWith('/')) BASE = '/' + BASE;
if (!BASE.endsWith('/')) BASE += '/';
const url = (p = '') => BASE + p.replace(/^\/+/, '');

// Cache-bust the stylesheet: an older site at the same URL may still be in browser caches.
const CSS_V = createHash('sha256').update(readFileSync(join(SRC, 'assets', 'site.css'))).digest('hex').slice(0, 10);
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// ---- minimal front matter / yaml (top-level scalars, one nested `metadata:` map) ----
function parseYaml(text) {
  const out = {};
  let nested = null;
  for (const line of text.split('\n')) {
    if (!line.trim() || line.trim().startsWith('#')) continue;
    const m = line.match(/^(\s*)([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!m) continue;
    const [, indent, key, raw] = m;
    const val = raw.replace(/^["']|["']$/g, '');
    if (indent.length === 0) {
      if (raw === '') { out[key] = out[key] ?? {}; nested = key; } else { out[key] = val; nested = null; }
    } else if (nested && typeof out[nested] === 'object') out[nested][key] = val;
  }
  return out;
}
function splitFrontMatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  return m ? { fm: parseYaml(m[1]), body: m[2] } : { fm: {}, body: text };
}

// ---- minimal markdown: paragraphs, [links](url), `code` ----
function inline(s) {
  const codes = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
  s = esc(s).replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2">$1</a>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(codes[i])}</code>`);
}
const paragraphs = (md) => md.trim().split(/\n\s*\n/).map((p) => `<p>${inline(p.replace(/\n/g, ' '))}</p>`).join('\n');

function sections(body) {
  const out = {};
  let cur = null;
  for (const line of body.split('\n')) {
    const h = line.match(/^##\s+(.*)$/);
    if (h) { cur = h[1].trim(); out[cur] = ''; } else if (cur) out[cur] += line + '\n';
  }
  return out;
}

// ---- load ----
// Clean first: a failed build must never leave a stale page behind.
rmSync(DIST, { recursive: true, force: true });
const errors = [];
const suites = [];
const dirs = (p) => readdirSync(p, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort();
for (const suiteDir of dirs(SKILLS)) {
  const base = join(SKILLS, suiteDir);
  if (!existsSync(join(base, 'skills'))) continue;
  const meta = existsSync(join(base, 'suite.yaml')) ? parseYaml(readFileSync(join(base, 'suite.yaml'), 'utf8')) : {};
  const suite = { id: suiteDir, meta, skills: [] };
  for (const skillDir of dirs(join(base, 'skills'))) {
    const file = join(base, 'skills', skillDir, 'SKILL.md');
    if (!existsSync(file)) continue;
    const { fm } = splitFrontMatter(readFileSync(file, 'utf8'));
    if (fm.name !== skillDir) errors.push(`${suiteDir}/${skillDir}: frontmatter name "${fm.name}" does not match directory`);
    if (fm.metadata?.suite !== suiteDir) errors.push(`${suiteDir}/${skillDir}: metadata.suite "${fm.metadata?.suite}" does not match suite directory`);
    if (!fm.description) errors.push(`${suiteDir}/${skillDir}: missing description`);
    suite.skills.push({ name: skillDir, suite: suiteDir, description: fm.description || '', path: `skills/${suiteDir}/skills/${skillDir}/SKILL.md` });
  }
  suites.push(suite);
}
const all = suites.flatMap((s) => s.skills);
const contentDir = join(SRC, 'content');
const contentFiles = existsSync(contentDir) ? readdirSync(contentDir).filter((f) => f.endsWith('.md')) : [];
for (const f of contentFiles) if (!all.some((s) => `${s.name}.md` === f)) errors.push(`content/${f}: orphan, no skill with that name`);
for (const s of all) {
  const f = join(contentDir, `${s.name}.md`);
  if (!existsSync(f)) { errors.push(`${s.name}: missing site-src/content/${s.name}.md`); continue; }
  const raw = readFileSync(f, 'utf8');
  if (raw.includes('[VERIFY')) errors.push(`${s.name}: content has an unresolved [VERIFY] marker`);
  const { fm, body } = splitFrontMatter(raw);
  const sec = sections(body);
  if (typeof fm.tagline !== 'string' || !fm.tagline.trim()) errors.push(`${s.name}: missing tagline`);
  if (!sec['What it does']?.trim()) errors.push(`${s.name}: missing "What it does" section`);
  if (sec['Where it came from'] !== undefined) errors.push(`${s.name}: "Where it came from" belongs in site-src/suites/${s.suite}.md, not the skill file`);
  Object.assign(s, { tagline: fm.tagline, what: sec['What it does'] });
}
// Provenance lives at the suite level.
const suiteContentDir = join(SRC, 'suites');
const suiteFiles = existsSync(suiteContentDir) ? readdirSync(suiteContentDir).filter((f) => f.endsWith('.md')) : [];
for (const f of suiteFiles) if (!suites.some((x) => `${x.id}.md` === f)) errors.push(`suites/${f}: orphan, no suite with that name`);
for (const x of suites) {
  const f = join(suiteContentDir, `${x.id}.md`);
  if (!existsSync(f)) { errors.push(`${x.id}: missing site-src/suites/${x.id}.md`); continue; }
  const raw = readFileSync(f, 'utf8');
  if (raw.includes('[VERIFY')) errors.push(`${x.id}: suite content has an unresolved [VERIFY] marker`);
  const origin = sections(splitFrontMatter(raw).body)['Where it came from'];
  if (!origin?.trim()) errors.push(`${x.id}: suite content missing "Where it came from" section`);
  x.origin = origin;
}
if (errors.length) {
  console.error(`Build failed with ${errors.length} error(s):\n` + errors.map((e) => `  - ${e}`).join('\n'));
  process.exit(1);
}

// ---- templates ----
const FONTS = 'https://fonts.googleapis.com/css2?family=Golos+Text:wght@400&family=Roboto+Mono:wght@500;700&display=swap';
function page({ title, desc, current, body }) {
  const nav = [['Home', url(), 'home'], ['Skills', url('#skills'), 'skills'], ['GitHub', GH, 'gh']]
    .map(([t, h, k]) => `<a href="${esc(h)}"${k === current ? ' aria-current="page"' : ''}>${t}</a>`).join('');
  return `<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="icon" href="${url('assets/favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS}">
<link rel="stylesheet" href="${url('assets/site.css')}?v=${CSS_V}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap"><a class="brand" href="${url()}">skill-suites</a><nav aria-label="Primary">${nav}</nav></div></header>
<main id="main"><div class="wrap">
${body}
</div></main>
<footer class="site"><div class="wrap">Apache-2.0. <a href="${GH}">Source on GitHub</a>.</div></footer>
</body>
</html>
`;
}
const installSkill = (names) => `npx skills add ${REPO} ${names.map((n) => `--skill ${n}`).join(' ')}`;
const installPlugin = (suite) => `claude plugin marketplace add ${REPO}\nclaude plugin install ${suite.meta.name || 'skill-suites-' + suite.id}@skill-suites`;
const ghBlob = (p) => `${GH}/blob/main/${p}`;

function home() {
  const groups = suites.map((s) => `
<section aria-labelledby="suite-${esc(s.id)}">
<p class="overline">Suite</p>
<h2 id="suite-${esc(s.id)}"><a href="${url(`suites/${s.id}/`)}">${esc(s.meta.displayName || s.id)}</a></h2>
<p class="suite-desc">${esc(s.meta.description || '')}</p>
<ul class="catalogue">
${s.skills.map((k) => `<li><a class="name" href="${url(`skills/${k.name}/`)}">${esc(k.name)}</a><a class="src" href="${esc(ghBlob(k.path))}">GitHub</a><p class="tag">${esc(k.tagline)}</p></li>`).join('\n')}
</ul>
</section>`).join('\n');
  const body = `<h1>Skills that work together, and install one at a time</h1>
<p class="lede">${all.length} Agent Skills in ${suites.length} suites. Each skill is a self-contained directory in the <a href="https://agentskills.io">Agent Skills</a> format.</p>
<h2 id="skills">Skills</h2>
${groups}
<h2 id="install">Install</h2>
<p>Install any skill on its own with any Agent Skills host:</p>
<pre><code>npx skills add ${REPO} --list
${esc(installSkill([all[0].name]))}</code></pre>
<p>Or install a suite as a plugin:</p>
<pre><code>${esc(suites.map(installPlugin).join('\n\n'))}</code></pre>`;
  return page({ title: 'skill-suites: Agent Skills that work together', desc: `${all.length} Agent Skills in ${suites.length} suites, each installable on its own.`, current: 'home', body });
}

function suitePage(x) {
  const name = esc(x.meta.displayName || x.id);
  const body = `<p class="overline">Suite</p>
<h1>${name}</h1>
<p class="lede">${esc(x.meta.description || '')}</p>
<h2>Where it came from</h2>
${paragraphs(x.origin)}
<h2>Skills</h2>
<ul class="catalogue">
${x.skills.map((k) => `<li><a class="name" href="${url(`skills/${k.name}/`)}">${esc(k.name)}</a><a class="src" href="${esc(ghBlob(k.path))}">GitHub</a><p class="tag">${esc(k.tagline)}</p></li>`).join('\n')}
</ul>
<h2>Install</h2>
<pre><code>${esc(installPlugin(x))}</code></pre>
<p><a href="${esc(`${GH}/tree/main/skills/${x.id}`)}">View the ${name} suite on GitHub</a></p>`;
  return page({ title: `${x.meta.displayName || x.id} suite | skill-suites`, desc: x.meta.description || '', current: null, body });
}

function skillPage(s, i, siblings) {
  const prev = siblings[i - 1], next = siblings[i + 1];
  const suite = suites.find((x) => x.id === s.suite);
  const body = `<p class="overline"><a href="${url(`suites/${s.suite}/`)}">${esc(suite.meta.displayName || s.suite)} suite</a></p>
<h1>${esc(s.name)}</h1>
<p class="lede">${esc(s.tagline)}</p>
<h2>What it does</h2>
${paragraphs(s.what)}
<p>Where it came from: see the <a href="${url(`suites/${s.suite}/`)}">${esc(suite.meta.displayName || s.suite)} suite</a>.</p>
<h2>Trigger text</h2>
<p>The description the skill's <code>SKILL.md</code> gives a host, verbatim:</p>
<blockquote class="trigger"><p>${esc(s.description)}</p></blockquote>
<h2>Install</h2>
<pre><code>${esc(installSkill([s.name]))}</code></pre>
<p>Or get the whole suite: <code>${esc(suite.meta.name || 'skill-suites-' + s.suite)}</code>.</p>
<p><a href="${esc(ghBlob(s.path))}">View ${esc(s.name)} on GitHub</a></p>
<nav class="pn" aria-label="Skills in this suite">
<span>${prev ? `<a href="${url(`skills/${prev.name}/`)}">&larr; ${esc(prev.name)}</a>` : ''}</span>
<span>${next ? `<a href="${url(`skills/${next.name}/`)}">${esc(next.name)} &rarr;</a>` : ''}</span>
</nav>`;
  return page({ title: `${s.name} | skill-suites`, desc: s.tagline, current: null, body });
}

// ---- write ----
mkdirSync(DIST, { recursive: true });
cpSync(join(SRC, 'assets'), join(DIST, 'assets'), { recursive: true });
writeFileSync(join(DIST, '.nojekyll'), '');
writeFileSync(join(DIST, 'index.html'), home());
for (const suite of suites) {
  mkdirSync(join(DIST, 'suites', suite.id), { recursive: true });
  writeFileSync(join(DIST, 'suites', suite.id, 'index.html'), suitePage(suite));
  suite.skills.forEach((s, i, arr) => {
    const dir = join(DIST, 'skills', s.name);
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, 'index.html'), skillPage(s, i, arr));
  });
}
console.log(`Built ${all.length} skill pages, suite pages and the home page into dist/ (base ${BASE}).`);

// ---- check: every internal href/src resolves under BASE ----
function walk(d) { return readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(d, e.name)) : [join(d, e.name)])); }
function resolveUrl(u) {
  const p = u.split('#')[0].split('?')[0];
  const rel = p.slice(BASE.length);
  const f = resolve(DIST, rel);
  if (f !== DIST && !f.startsWith(DIST + sep)) return null;
  if (existsSync(f) && statSync(f).isDirectory()) return existsSync(join(f, 'index.html')) ? join(f, 'index.html') : null;
  return existsSync(f) ? f : null;
}
function check() {
  const bad = [];
  let n = 0;
  for (const f of walk(DIST).filter((x) => x.endsWith('.html'))) {
    const html = readFileSync(f, 'utf8');
    for (const [, , u] of html.matchAll(/\b(href|src)="([^"]*)"/g)) {
      if (/^(https?:)?\/\//.test(u) || u.startsWith('mailto:')) continue;
      n++;
      if (u.startsWith('#')) { if (!html.includes(`id="${u.slice(1)}"`)) bad.push(`${f.replace(DIST, 'dist')}: "${u}" fragment missing`); continue; }
      if (!u.startsWith(BASE)) { bad.push(`${f.replace(DIST, 'dist')}: "${u}" is not under ${BASE}`); continue; }
      const target = resolveUrl(u);
      if (!target) { bad.push(`${f.replace(DIST, 'dist')}: "${u}" does not resolve`); continue; }
      const frag = u.split('#')[1];
      if (frag && target.endsWith('.html') && !readFileSync(target, 'utf8').includes(`id="${frag}"`)) bad.push(`${f.replace(DIST, 'dist')}: "${u}" fragment missing`);
    }
  }
  if (bad.length) { console.error(`Link check failed:\n` + bad.map((b) => `  - ${b}`).join('\n')); process.exit(1); }
  console.log(`Link check passed: ${n} internal references resolve.`);
}

if (process.argv.includes('--check')) check();

if (process.argv.includes('--serve')) {
  const types = { '.html': 'text/html', '.css': 'text/css', '.svg': 'image/svg+xml' };
  createServer((req, res) => {
    let u;
    try { u = decodeURIComponent(req.url.split('?')[0]); } catch { res.writeHead(400); return res.end('bad request'); }
    const f = u.startsWith(BASE) ? resolveUrl(u) : null;
    if (!f) { res.writeHead(404); return res.end('not found'); }
    res.writeHead(200, { 'content-type': types[extname(f)] || 'application/octet-stream' });
    res.end(readFileSync(f));
  }).listen(8080, '127.0.0.1', () => console.log(`Serving dist/ at http://localhost:8080${BASE}`));
}
