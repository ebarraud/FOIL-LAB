const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('index.html','utf8'), sandbox={};vm.createContext(sandbox);
vm.runInContext(source.slice(source.indexOf('const FOILS=['),source.indexOf('function compatibility(')),sandbox);
vm.runInContext(source.slice(source.indexOf('const KB_FOILS='),source.indexOf('let KB_RECORDS=')),sandbox);
const rows=sandbox.kbAllRecords();
const count=vm.runInContext('FOILS.reduce((n,f)=>n+f.sizes.length,0)+BOARDS.reduce((n,b)=>n+b.sizes.length,0)',sandbox);
assert.equal(rows.length,count,'No model may disappear because it lacks scores');
const drifter=rows.find(r=>r.name==='Drifter 5 Pro Carbon');assert.ok(drifter);assert.equal(drifter.entry.q,null);
assert.match(sandbox.kbMetrics(null),/Non noté/);
const extension=JSON.parse(fs.readFileSync('data/research/expanded_test_evidence.json','utf8'));
assert.equal(new Set(extension.catalogue_records.map(r=>r.key)).size,extension.catalogue_records.length);
assert.ok(extension.catalogue_records.every(r=>r.entry.q===null));
assert.ok(extension.catalogue_records.filter(r=>r.key.startsWith('manufacturer|')).every(r=>!r.tested),'Manufacturer-only records must never become tested');
assert.ok(extension.catalogue_records.find(r=>r.key.includes('ky1rk1QHya0')).tested,'Actual Sushi transcript evidence remains distinct from manufacturer-only TITAN2 entries');
assert.ok(extension.catalogue_records.some(r=>r.brand==='F-ONE'&&r.tested&&r.name.includes('2023')));
assert.ok(!rows.filter(r=>r.brand==='F-ONE'&&r.name==='SK8').some(r=>r.tested),'Old SK8 test must not mark V3 tested');
console.log('Catalogue completeness, no-score and generation isolation:',count,'embedded variants +',extension.catalogue_records.length,'new records');

const links=JSON.parse(fs.readFileSync("data/research/catalogue_evidence_links.json","utf8"));
for(const l of links.links)assert.ok(rows.some(r=>r.brand===l.brand&&r.name===l.model&&r.size===l.size),"Evidence target must exist");

assert.ok(rows.every(r=>r.entry.q===null),"Unvalidated legacy scores must not be rendered");
assert.ok(JSON.parse(fs.readFileSync("data/model_variants.json","utf8")).variants.every(v=>v.qualitative_scores===null));
vm.runInContext(source.slice(source.indexOf('function sourceInventoryRows('),source.indexOf('function renderSourceLibrary(')),sandbox);
const progress=JSON.parse(fs.readFileSync('data/research/progress.json','utf8'));
const leads=JSON.parse(fs.readFileSync('data/research/written_review_leads_latest.json','utf8'));
const written=JSON.parse(fs.readFileSync('data/research/written_test_evidence_2026.json','utf8'));
const inventory=sandbox.sourceInventoryRows(progress,leads,written,extension);
assert.equal(inventory.filter(r=>r.kind==='video').length,progress.videos.length,'Sources must show the full video inventory, not five examples');
assert.ok(inventory.some(r=>r.publisher==='KiteWorld Shop'));
assert.ok(inventory.some(r=>r.status==='Article repéré · lecture à faire'));
console.log('Complete source library:',inventory.length,'unique sources including',progress.videos.length,'videos');
const axisPng=extension.catalogue_records.filter(r=>r.brand==='AXIS'&&r.name.startsWith('PNG V2'));
assert.equal(axisPng.length,3);
for(const r of axisPng){assert.equal(r.size,r.manufacturer_geometry.true_area_cm2);assert.equal(r.width,r.manufacturer_geometry.span_cm);assert.notEqual(r.size,Number(r.name.split(' ').at(-1)),'AXIS model span must not become area');}
const axisReview=JSON.parse(fs.readFileSync('data/research/transcript_reviews.json','utf8')).reviews.find(r=>r.video_id==='iYxYwu15cuE');
assert.ok(axisReview.claims.some(c=>c.dimension==='tempo_1020_pratiques'&&c.statement_fr.includes('surf non essayé')));
console.log('AXIS span/area separation and Tempo practice limitations passed');
