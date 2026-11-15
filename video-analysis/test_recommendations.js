const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('index.html','utf8');
const start=source.indexOf('function transcriptSuitability('), end=source.indexOf('function boardTarget(');
const sandbox={};vm.createContext(sandbox);vm.runInContext(source.slice(start,end),sandbox);
const f={b:'AFS',n:'Silk V2'};
assert.equal(sandbox.transcriptSuitability(f,650,{pr:'easy',l:4}).minimumSize,750);
assert.equal(sandbox.transcriptSuitability(f,650,{pr:'perf',l:2}).minimumSize,750);
assert.equal(sandbox.transcriptSuitability(f,650,{pr:'perf',l:3}).minimumSize,null);
assert.equal(sandbox.transcriptSuitability({b:'KT',n:'Nomad'},650,{pr:'easy',l:1}).minimumSize,null);
assert.match(sandbox.transcriptSuitability(f,950,{pr:'easy',l:3}).caution,/surf foil/);
// Exercise the actual ranking function with controlled family sizing.
Object.assign(sandbox,{FOILS:[{...f,range:[2,3,4],sizes:[650,750,950],lift:1,tags:['surf'],quote:'test',risk:'test'}],foilTarget:()=>650});
const profile={l:3,b:'all',p:'surf',w:62,wind:18,pr:'easy',water:'flat',budget:'all'};
assert.equal(sandbox.foilOptions(profile)[0].size,750);
assert.equal(sandbox.foilOptions({...profile,pr:'perf'})[0].size,650);
console.log('Transcript recommendation checks passed');

const boardStart=source.indexOf('function boardEvidenceAllows('),boardEnd=source.indexOf('function boardOptions(');
vm.runInContext(source.slice(boardStart,boardEnd),sandbox);
assert.equal(sandbox.boardEvidenceAllows(78,{w:85,pr:'easy',start:'auto'}),false);
assert.equal(sandbox.boardEvidenceAllows(85,{w:85,pr:'easy',start:'auto'}),true);
assert.equal(sandbox.boardEvidenceAllows(78,{w:85,pr:'perf',start:'auto'}),true);
assert.equal(sandbox.boardEvidenceAllows(78,{w:85,pr:'easy',start:'sinker'}),true);
console.log('Board ease and explicit sinker checks passed');
