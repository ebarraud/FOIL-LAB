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
const ma790=sandbox.transcriptSuitability({b:'Armstrong',n:'MA Mk II'},790,{p:'surf'});
assert.match(ma790.url,/m9spmeFy0J4/);
assert.match(ma790.caution,/aucune équivalence/);
assert.ok(!sandbox.transcriptSuitability({b:'Armstrong',n:'MA Mk II'},990,{p:'surf'}).url.includes('m9spmeFy0J4'),'790/1190 review must not overwrite 990 evidence');
assert.match(sandbox.transcriptSuitability({b:'AFS',n:'Enduro'},700,{}).reason,/moins de marge/);
assert.match(sandbox.transcriptSuitability({b:'AFS',n:'Enduro'},1100,{}).reason,/relance/);
assert.ok(!sandbox.transcriptSuitability({b:'AFS',n:'Enduro'},1300,{}).url.includes('8Mf-D-pKrZ8'),'Untested 1300 must not inherit the new same-session comparison');
console.log('Backlog integration: MA and Enduro exact-size evidence isolation passed');
sandbox.foilTarget=()=>835;
vm.runInContext(source.slice(source.indexOf('const FOILS=['),source.indexOf('const BOARDS=[')).replace('const FOILS=','globalThis.FOILS='),sandbox);
const axisProfile={...profile,b:'AXIS',p:'surf',pr:'perf',l:3};
const surgeOptions=sandbox.foilOptions(axisProfile);assert.ok(surgeOptions.some(o=>o.f.n==='Surge 890'&&o.size===835));
assert.ok(!sandbox.foilOptions({...axisProfile,l:1}).some(o=>o.f.n==='Surge 890'));
assert.ok(!sandbox.foilOptions({...axisProfile,pr:'easy'}).some(o=>o.f.n==='Surge 890'));
assert.ok(!sandbox.foilOptions({...axisProfile,p:'jump'}).some(o=>o.f.n==='Surge 890'));
assert.match(surgeOptions.find(o=>o.f.n==='Surge 890').evidence.url,/-htD7qNM7_k/);
console.log('Surge 890 uses real 835cm2, skill/ease exclusions and its own evidence');

// Repères AFS : le programme « vent léger » choisi doit agrandir la cible Enduro / Silk V2 comme la cible générique.
{
 const sb={};vm.createContext(sb);
 vm.runInContext(source.slice(source.indexOf('const FOILS=['),source.indexOf('function boardTarget(')).replace('const FOILS=','globalThis.FOILS=').replace('const BOARDS=','globalThis.BOARDS=').replace(/^const \$=.*$/m,''),sb);
 const base={w:83,l:2,wind:12,water:'flat',p:'all',pr:'balance',start:'knee',bt:'auto',b:'AFS',st:'normal',maxW:0,maxL:0,budget:'all',replace:'all',hardware:''};
 const enduro=x=>sb.foilOptions(x).find(o=>o.f.n==='Enduro');
 assert.equal(enduro(base).size,1100);
 assert.ok(enduro({...base,p:'light'}).size>enduro(base).size,'Enduro: le programme vent léger doit relever la taille');
 assert.equal(enduro({...base,p:'surf'}).size,1000);
 console.log('AFS reference sizing keeps the light-wind program factor');
}

// Corrections issues du balayage de 8 100 profils (19/11/2026).
{
 const sb={};vm.createContext(sb);
 vm.runInContext(source.slice(source.indexOf('const FOILS=['),source.indexOf('function boardTarget(')).replace('const FOILS=','globalThis.FOILS=').replace('const BOARDS=','globalThis.BOARDS=').replace(/^const \$=.*$/m,''),sb);
 const base={w:85,l:2,wind:12,water:'flat',p:'all',pr:'balance',start:'knee',bt:'auto',b:'all',st:'normal',maxW:0,maxL:0,budget:'all',replace:'all',hardware:''};
 // 1. Silk V2 : le repère AFS 750 @ 75 kg vaut pour le profil carving seulement.
 const silk=x=>sb.foilOptions({...x,b:'AFS'}).find(o=>o.f.n==='Silk V2');
 assert.ok(!silk(base)||silk(base).size>850,'Silk V2 freeride ne doit pas reprendre le repère carving');
 assert.equal(silk({...base,p:'surf'}).size,850);
 // 2. Une famille dotée d'un repère constructeur ne passe plus en tête par un écart nul à sa propre cible.
 const first=sb.foilOptions(base)[0];
 assert.ok(!(first.f.n==='Silk V2'&&first.size===850),'classement biaisé par la cible propre à la famille');
 // 3. Freeride : les familles spécialisées (sans étiquette « all ») passent derrière les polyvalentes.
 for(const l of [3,4])for(const w of [65,75,85])assert.ok(sb.foilOptions({...base,l,w})[0].f.tags.includes('all'),`freeride L${l} ${w} kg : 1re aile spécialisée`);
 // 4. Débutant + programme non adapté : le moteur ne renvoie rien, l'interface bascule sur le freeride avec explication.
 assert.equal(sb.foilOptions({...base,l:0,p:'surf'}).length,0);
 assert.ok(sb.foilOptions({...base,l:0,p:'all'}).length>0);
 assert.ok(source.includes('Programme adapté à ton niveau'));
 console.log('Sweep fixes: Silk carving scope, fair ranking, freeride specialists, beginner program fallback');
}

// Calibrage sourcé de la surface (SURF Magazin, AFS Evo) et nouvelles familles débutant.
{
 const sb={};vm.createContext(sb);
 vm.runInContext(source.slice(source.indexOf('const FOILS=['),source.indexOf('function boardTarget(')).replace('const FOILS=','globalThis.FOILS=').replace('const BOARDS=','globalThis.BOARDS=').replace(/^const \$=.*$/m,''),sb);
 const b={w:75,l:4,wind:12,water:'flat',p:'all',pr:'balance',start:'knee',bt:'auto',b:'all',st:'normal',maxW:0,maxL:0,budget:'all',replace:'all',hardware:''};
 assert.ok(sb.foilTarget(b)>=1000,'freeride ≤ 15 nds : plancher SURF expérimenté');
 assert.ok(sb.foilTarget({...b,wind:18})<1000,'au-delà de 15 nds, le niveau garde son effet');
 assert.ok(sb.foilTarget({...b,p:'surf'})<1000,'surf : pas de plancher');
 assert.equal(sb.foilTarget({...b,w:83,l:3,p:'light'}),1500);
 assert.ok(sb.foilTarget({...b,w:84,l:0,pr:'easy'})<=1700,'débutant : plafond SURF');
 const evo=x=>sb.foilOptions({...x,b:'AFS'}).find(o=>o.f.n==='Evo');
 assert.equal(evo({...b,l:0,w:80,wind:12}).size,1650);
 assert.equal(evo({...b,l:0,w:80,wind:22}).size,1450);
 for(const n of ['Gravity','CF V2'])assert.ok(sb.FOILS.some(f=>f.n===n&&f.range[0]===0),n+' accessible au niveau 0');
 assert.ok(sb.foilOptions({...b,l:0,w:95}).length>=2,'au moins deux familles proposées à un débutant lourd');
 console.log('Sourced sizing floor/ceiling, AFS Evo strong wind and beginner families');
}
