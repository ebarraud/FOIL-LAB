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
assert.ok(extension.catalogue_records.filter(r=>r.name.includes('TITAN 2')).every(r=>!r.tested));
assert.ok(extension.catalogue_records.some(r=>r.brand==='F-ONE'&&r.tested&&r.name.includes('2023')));
assert.ok(!rows.filter(r=>r.brand==='F-ONE'&&r.name==='SK8').some(r=>r.tested),'Old SK8 test must not mark V3 tested');
console.log('Catalogue completeness, no-score and generation isolation:',count,'embedded variants +',extension.catalogue_records.length,'new records');

const links=JSON.parse(fs.readFileSync("data/research/catalogue_evidence_links.json","utf8"));
for(const l of links.links)assert.ok(rows.some(r=>r.brand===l.brand&&r.name===l.model&&r.size===l.size),"Evidence target must exist");

assert.ok(rows.every(r=>r.entry.q===null),"Unvalidated legacy scores must not be rendered");
assert.ok(JSON.parse(fs.readFileSync("data/model_variants.json","utf8")).variants.every(v=>v.qualitative_scores===null));
