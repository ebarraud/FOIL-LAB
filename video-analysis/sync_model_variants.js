#!/usr/bin/env node
// Synchronise data/model_variants.json avec les familles et tailles embarquées dans index.html.
// - conserve à l'identique les variantes déjà présentes (métadonnées auditées) ;
// - ajoute les tailles du moteur absentes du JSON à partir des seules données embarquées ;
// - signale les variantes JSON orphelines (absentes du moteur) sans les supprimer ;
// - n'attribue jamais de note : qualitative_scores reste null.
// Usage : node video-analysis/sync_model_variants.js [--check]
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const jsonPath = path.join(root, 'data/model_variants.json');

function slice(startMarker, endMarker) {
  const a = html.indexOf(startMarker), b = html.indexOf(endMarker, a);
  if (a < 0 || b < 0) throw new Error('Marqueur introuvable : ' + startMarker);
  return html.slice(a, b);
}
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(
  slice('const FOILS=[', 'const fmt=')
    .replace('const FOILS=', 'globalThis.FOILS=')
    .replace('const BOARDS=', 'globalThis.BOARDS=')
    .replace('const VERIFY=', 'globalThis.VERIFY='),
  sandbox);
vm.runInContext(
  slice('const KB_FOILS={', 'const KB_LABELS=')
    .replace('const KB_FOILS=', 'globalThis.KB_FOILS=')
    .replace('const KB_BOARDS=', 'globalThis.KB_BOARDS='),
  sandbox);
const { FOILS, BOARDS, VERIFY, KB_FOILS, KB_BOARDS } = sandbox;

function engineVariants() {
  const out = [];
  for (const f of FOILS) {
    const k = f.b + '|' + f.n, e = KB_FOILS[k] || {}, v = VERIFY[k] || {};
    for (const size of f.sizes) out.push({
      id: `foil:${f.b}:${f.n}:${size}`, type: 'foil', brand: f.b, model: f.n, size_cm2: size,
      year: e.year || 'Génération à vérifier dans la source',
      qualitative_scores: null,
      confidence: e.confidence === 'med' ? 'med' : e.confidence === 'high' ? 'high' : 'low',
      independently_tested_exact_size: Array.isArray(e.tested) && e.tested.includes(size),
      sources: [e.f || f.src, e.i, v.test].filter(Boolean).filter((u, i, a) => a.indexOf(u) === i),
      note: e.reason || f.about || f.quote || 'Documentation disponible',
      sync_origin: 'engine_embedded_metadata',
      score_status: 'not_assigned_no_validated_rubric'
    });
  }
  for (const b of BOARDS) {
    const k = b.b + '|' + b.n, e = KB_BOARDS[k] || {}, v = VERIFY[k] || {};
    for (const [volume, length, width] of b.sizes) out.push({
      id: `board:${b.b}:${b.n}:${volume}`, type: 'board', brand: b.b, model: b.n, volume_l: volume,
      length_cm: Number.isFinite(length) ? length : null, width_cm: Number.isFinite(width) ? width : null,
      year: e.year || 'Génération à vérifier dans la source',
      qualitative_scores: null,
      confidence: e.confidence === 'med' ? 'med' : e.confidence === 'high' ? 'high' : 'low',
      independently_tested_exact_size: Array.isArray(e.tested) && e.tested.includes(volume),
      sources: [e.f || b.src, e.i, v.test].filter(Boolean).filter((u, i, a) => a.indexOf(u) === i),
      note: e.reason || b.about || b.quote || 'Documentation disponible',
      sync_origin: 'engine_embedded_metadata',
      score_status: 'not_assigned_no_validated_rubric'
    });
  }
  return out;
}

const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
const engine = engineVariants();
const engineIds = new Set(engine.map(v => v.id));
const existing = new Map(data.variants.map(v => [v.id, v]));
const missing = engine.filter(v => !existing.has(v.id));
const orphans = data.variants.filter(v => !engineIds.has(v.id)).map(v => v.id);

if (process.argv.includes('--check')) {
  console.log(JSON.stringify({ engine: engine.length, json: data.variants.length, missing: missing.map(v => v.id), orphans }, null, 1));
  process.exit(missing.length || orphans.length ? 1 : 0);
}
// Ordre du moteur, variantes existantes conservées telles quelles.
const merged = engine.map(v => existing.get(v.id) || v).concat(data.variants.filter(v => !engineIds.has(v.id)));
data.variants = merged;
data.as_of = new Date().toISOString().slice(0, 10);
data.generated_from = 'index.html (FOILS, BOARDS, KB_FOILS, KB_BOARDS, VERIFY) via video-analysis/sync_model_variants.js';
fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2) + '\n');
console.log(`model_variants.json : ${merged.length} variantes (${missing.length} ajoutées, ${orphans.length} orphelines conservées).`);
