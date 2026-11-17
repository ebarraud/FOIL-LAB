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

const families=source.slice(source.indexOf('const FOILS=['),source.indexOf('const BOARDS=[')).replace('const FOILS=','globalThis.FOILS=');
vm.runInContext(families,sandbox);
sandbox.foilTarget=()=>825;
const glide={...profile,b:'Duotone',p:'glide',pr:'perf',l:2};
assert.ok(sandbox.foilOptions(glide).some(o=>o.f.n==='Glide 3.0 D/LAB'&&o.size===825));
assert.ok(!sandbox.foilOptions({...glide,pr:'easy'}).some(o=>o.f.n==='Glide 3.0 D/LAB'));
sandbox.foilTarget=()=>800;
const halo={...profile,b:'KT',p:'jump',pr:'perf',l:3};
assert.ok(sandbox.foilOptions(halo).some(o=>o.f.n==='Halo'&&o.size===800));
assert.ok(!sandbox.foilOptions({...halo,l:1}).some(o=>o.f.n==='Halo'));
assert.ok(!sandbox.foilOptions({...halo,p:'light'}).some(o=>o.f.n==='Halo'));
console.log('Glide and Halo conditional recommendation checks passed');

sandbox.foilTarget=()=>825;assert.match(sandbox.foilOptions(glide).find(o=>o.f.n==='Glide 3.0 D/LAB').evidence.setup,/H130/);assert.match(sandbox.foilOptions({...glide,p:'all'}).find(o=>o.f.n==='Glide 3.0 D/LAB').evidence.setup,/PX145/);

assert.match(sandbox.transcriptSuitability({b:'Duotone',n:'Crest D/LAB'},1050,profile).caution,/H185 est seulement envisagé/);

assert.match(sandbox.transcriptSuitability({b:'Slingshot',n:'One-Lock Glide'},1525,profile).setup,/Turbo 180/);
assert.match(sandbox.transcriptSuitability({b:'KT',n:'Nomad'},700,profile).setup,/155/);
assert.match(sandbox.transcriptSuitability({b:'KT',n:'Nomad'},1160,profile).setup,/190/);
assert.match(sandbox.transcriptSuitability({b:'KT',n:'Nomad'},830,profile).setup,/pas isolés/);
assert.match(sandbox.transcriptSuitability({b:'Armstrong',n:'UHA'},870,profile).caution,/pas un racefoil/);

const boardFamilies=source.slice(source.indexOf('const BOARDS=['),source.indexOf('const VERIFY=')).replace('const BOARDS=','globalThis.BOARDS=');
vm.runInContext(boardFamilies,sandbox);
vm.runInContext(source.slice(source.indexOf('function boardTarget('),source.indexOf('function foilMarkup(')),sandbox);
const ml=sandbox.BOARDS.find(b=>b.n==='Midlength Mk II X-Form');
assert.ok(ml);assert.equal(ml.sizes.find(a=>a[0]===55)[1],162.56);
const allBoardFamilies=sandbox.BOARDS;
sandbox.BOARDS=[ml];
const bp={w:85,l:2,wind:18,st:'normal',start:'auto',bt:'midi',p:'all',pr:'easy',water:'flat'};
assert.ok(sandbox.boardOptions(bp).length>0);
assert.ok(sandbox.boardOptions(bp).every(b=>b.v>=85));
assert.equal(sandbox.boardOptions({...bp,l:0}).length,0);
assert.equal(sandbox.boardOptions({...bp,maxL:150}).length,0);
console.log('MkII board catalogue and profile checks passed');

// Verify that advice cannot leak from a tested size to untested sizes.
assert.match(sandbox.transcriptSuitability({b:'Slingshot',n:'One-Lock Glide'},1125,profile).setup,/180/);
assert.equal(sandbox.transcriptSuitability({b:'Slingshot',n:'One-Lock Glide'},925,profile).setup,undefined);
assert.match(sandbox.transcriptSuitability({b:'Duotone',n:'Crest D/LAB'},800,profile).caution,/réception très freinante/);
sandbox.BOARDS=allBoardFamilies;
for(const name of ['Super K 2 Carbon','Skybrid SLS 2026']){
 const family=sandbox.BOARDS.find(b=>b.n===name); assert.ok(family);
 sandbox.BOARDS=[family]; assert.equal(sandbox.boardOptions({...bp,l:0}).length,0);
 const options=sandbox.boardOptions(bp); assert.ok(options.length>0);
 assert.ok(options.every(o=>o.v>=bp.w));
 sandbox.BOARDS=allBoardFamilies;
}
assert.equal(sandbox.BOARDS.find(b=>b.n==='Super K 2 Carbon').sizes.find(a=>a[0]===90)[1],187.96);
assert.equal(sandbox.BOARDS.find(b=>b.n==='Skybrid SLS 2026').sizes.find(a=>a[0]===80)[2],53.34);
console.log('Generation, size isolation, and new board safety checks passed');
const drifter=sandbox.BOARDS.find(b=>b.n==='Drifter 5 Pro Carbon');
assert.ok(drifter);assert.deepEqual(Array.from(drifter.sizes[0]),[60,165.1,55.88]);
sandbox.BOARDS=[drifter];
assert.equal(sandbox.boardOptions({...bp,l:0}).length,0);
assert.equal(sandbox.boardOptions({...bp,w:85,pr:'easy'}).length,0);
assert.ok(sandbox.boardOptions({...bp,w:55,l:3,bt:'compact',start:'sinker',pr:'normal'}).length>0);
sandbox.BOARDS=allBoardFamilies;
console.log('Drifter 5 tested-volume and beginner exclusion checks passed');
vm.runInContext(source.slice(source.indexOf('const FOILS=['),source.indexOf('const BOARDS=[')).replace('const FOILS=','globalThis.FOILS='),sandbox);
const code=sandbox.FOILS.find(f=>f.b==='Code');assert.ok(code);sandbox.FOILS=[code];
const cp={...profile,l:3,b:'Code',p:'glide',pr:'perf'};
assert.equal(sandbox.foilOptions({...cp,l:2}).length,0);
assert.equal(sandbox.foilOptions({...cp,pr:'easy'}).length,0);
assert.equal(sandbox.foilOptions({...cp,p:'jump'}).length,0);
assert.ok(sandbox.foilOptions(cp).length>0);
assert.match(sandbox.foilOptions(cp)[0].evidence.url,/l2HmFjc7eiI/);
assert.match(code.risk,/Sauts exclus/);
const waka=sandbox.BOARDS.find(b=>b.b==='WAKA');assert.ok(waka);sandbox.BOARDS=[waka];
assert.equal(sandbox.boardOptions({...bp,l:0}).length,0);
assert.ok(sandbox.boardOptions({...bp,w:76,pr:'easy'}).every(o=>o.v>=76));
assert.equal(waka.sizes.find(a=>a[0]===77)[2],50);
console.log('KiteWorld Shop integrations: WAKA sizing, Code 680R skill/jump exclusions and source links passed');
