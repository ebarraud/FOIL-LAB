// Onglet « Wing et montage » : valeurs identiques au registre sourcé, bornes de poids, logique mât/fuselage/allongement.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const eq=(a,b,m)=>assert.equal(JSON.stringify(a),JSON.stringify(b),m); // tableaux issus du contexte vm
const source=fs.readFileSync('index.html','utf8');
const code=source.slice(source.indexOf('const FOILS=['),source.indexOf('function foilMarkup(')).replace('const FOILS=','globalThis.FOILS=').replace('const BOARDS=','globalThis.BOARDS=').replace(/^const \$=.*$/m,'');
const sb={};vm.createContext(sb);
vm.runInContext(code+';globalThis.T={WING_GUIDE,UNIT_2026,FOIL_GUIDE,EXPERT_SRC,expertWing,expertFoilCheck,expertMast,expertFuselage,expertAspect,setupMarkup,foilOptions}',sb);
const T=sb.T,reg=JSON.parse(fs.readFileSync('data/research/expert_setup_guides.json','utf8'));
const g=id=>reg.guides.find(x=>x.id===id);
// 1. Valeurs embarquées = registre public.
const w=g('surf_wing_size_2026'),pairs=o=>Object.values(o);
eq(T.WING_GUIDE.inland.map(r=>[r[1],r[2]]),pairs(w.inland_6_15_kn_m2));
eq(T.WING_GUIDE.coastal.map(r=>[r[1],r[2]]),pairs(w.coastal_12_20plus_kn_m2));
eq(T.UNIT_2026.map(r=>[...r]),g('duotone_unit_2026_wind_ranges').sizes_m2_wind_kn);
const f=g('surf_foil_size_2026');
eq(T.FOIL_GUIDE.light.rows.map(r=>[r[1],r[2]]),pairs(f.beginner_or_light_wind_8_15_kn_cm2));
eq(T.FOIL_GUIDE.experienced.rows.map(r=>[r[1],r[2]]),pairs(f.experienced_10_20_kn_cm2));
for(const s of Object.values(T.EXPERT_SRC))assert.match(s.url,/^https:\/\//);
// 2. Bornes : « moins de 60 » exclusif, « 60–75 » inclut 75, « 75–95 » inclut 95.
const p={w:83,l:2,wind:12,water:'flat',p:'all',pr:'balance',start:'knee',bt:'auto',b:'all',st:'normal',maxW:0,maxL:0,budget:'all',replace:'all',hardware:''};
const wing=o=>{const r=T.expertWing({...p,...o});return [r.min,r.max]};
eq(wing({w:59}),[4.5,5]);eq(wing({w:60}),[5,5.5]);eq(wing({w:75}),[5,5.5]);
eq(wing({w:76}),[5.5,6.5]);eq(wing({w:95}),[5.5,6.5]);eq(wing({w:96}),[6,7]);
eq(wing({wind:16}),[5,5.5]);
const foil=o=>{const r=T.expertFoilCheck({...p,...o},[]);return [r.min,r.max]};
eq(foil({w:69,l:0}),[1300,1500]);eq(foil({w:85,l:0}),[1500,1700]);eq(foil({w:86,l:3}),[1200,1500]);
// 3. Tailles constructeur listées = celles dont la plage publiée contient le vent.
eq(T.expertWing({...p,wind:12}).covering.map(c=>c.size),[4.5,5,5.5,6,6.5]);
assert.ok(T.expertWing({...p,wind:12}).covering.find(c=>c.size===4.5).low);
// 4. Mât, fuselage, allongement.
assert.equal(T.expertMast({...p,p:'speed'}).range,'90 cm');
assert.equal(T.expertMast({...p,water:'wave'}).range,'85–90 cm');
assert.equal(T.expertMast({...p,l:0}).range,'75 cm');
assert.equal(T.expertMast({...p,water:'chop'}).range,'82–85 cm');
assert.equal(T.expertMast(p).range,'75–85 cm');
assert.match(T.expertFuselage({...p,l:0}).advice,/65 cm/);
assert.match(T.expertFuselage({...p,l:3,p:'surf'}).advice,/court/);
assert.match(T.expertAspect({...p,l:0},[]).target,/bas/);
assert.match(T.expertAspect({...p,p:'glide'},[]).target,/élevé/);
// 5. Rendu : sources présentes, aucune note de performance.
const html=T.setupMarkup({...p,l:3,p:'light'},T.foilOptions({...p,l:3,p:'light'}));
for(const s of Object.values(T.EXPERT_SRC))assert.ok(html.includes(s.url),'source absente '+s.url);
assert.ok(!/\/5\b/.test(html));
assert.ok(source.includes('data-tab="setup"')&&source.includes('id="setupResults"'));
console.log('Expert wing/setup guides: registry parity, weight bands, mast/fuselage/aspect logic and sources OK');
