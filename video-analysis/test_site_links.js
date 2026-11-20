const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const pages=['index.html','progress.html','video-analysis/evidence.html','video-analysis/reviews.html','video-analysis/review.html'];
let checked=0;
for(const page of pages){const html=fs.readFileSync(page,'utf8');for(const m of html.matchAll(/\b(?:href|src)=["']([^"']+)["']/g)){
 const url=m[1];if(/^(?:https?:|mailto:|data:|#)/.test(url)||/[${}]/.test(url))continue;
 const target=decodeURIComponent(url.split(/[?#]/)[0]);if(!target)continue;
 assert.ok(fs.existsSync(path.resolve(path.dirname(page),target)),page+' points to missing '+url);checked++;
}}
const evidence=fs.readFileSync('video-analysis/evidence.html','utf8');assert.ok(evidence.includes('evidence_library.js')&&evidence.includes('evidence_page.js'));
assert.ok(!fs.readFileSync('video-analysis/review.html','utf8').includes('preuves techniques des 3 essais'));
const centralDoc='docs/FONCTIONNEMENT_ARCHITECTURE_ACCES.md';
const readme=fs.readFileSync('README.md','utf8'),documentation=fs.readFileSync(centralDoc,'utf8');
assert.ok(readme.includes(centralDoc),'README must expose the central operating documentation');
for(const required of ['## 1. Objectif','## 8. Stockage','## 9. Accès et permissions','YOUTUBE_APU','TRANSCRIPT_API_KEY','.transcript-cache/','data/research/progress.json','GitHub Pages']){
 assert.ok(documentation.includes(required),'Central documentation missing '+required);
}
for(const match of documentation.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)){
 const target=match[1];if(/^(?:https?:|#)/.test(target))continue;
 assert.ok(fs.existsSync(path.resolve(path.dirname(centralDoc),target)),centralDoc+' points to missing '+target);
}
console.log('Local links and script assets:',checked,'links across',pages.length,'pages');
// Exercise the import form against the actual registry, including fetch failure.
const vm=require('node:vm');
const form=fs.readFileSync('video-analysis/review.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
async function checkForm(fail){
 const nodes={};const get=id=>nodes[id]||(nodes[id]={value:'',textContent:'',options:[],listeners:{},addEventListener(k,f){this.listeners[k]=f},replaceChildren(...v){this.options=v},add(v){this.options.push(v)}});
 const progress=JSON.parse(fs.readFileSync('data/research/progress.json','utf8'));
 vm.runInNewContext(form,{document:{getElementById:get},Option:function(text,value){this.text=text;this.value=value},fetch:async()=>({ok:!fail,json:async()=>progress}),URL,setTimeout});
 await new Promise(resolve=>setImmediate(resolve));
 if(fail){assert.match(get('preset-status').textContent,/indisponible/);return}
 const ids=new Set(progress.videos.map(v=>v.video_id).filter(Boolean));
 assert.equal(get('preset').options.length,ids.size+1);
 const axis=progress.videos.find(v=>/axis/i.test(v.title));assert.ok(axis);
 get('preset').value=axis.video_id;get('preset').listeners.change();
 assert.equal(get('title').value,axis.title);assert.ok(get('video').value.includes(axis.video_id));
 assert.ok(get('preset').options.some(v=>/kiteworld/i.test(v.text)));
}
Promise.resolve().then(()=>checkForm(false)).then(()=>checkForm(true)).then(()=>console.log('Import form: complete registry, AXIS, KiteWorld Shop and explicit failure verified')).catch(e=>{console.error(e);process.exitCode=1});
// Avis vidéo sur les cartes : rendu échappé, lien minuté, mention « sans effet sur le classement ».
{
 const src=fs.readFileSync('index.html','utf8');
 const blk=src.slice(src.indexOf('let REVIEW_INDEX='),src.indexOf('function foilMarkup('));
 const ctx={};require('node:vm').createContext(ctx);require('node:vm').runInContext(blk.replace('let REVIEW_INDEX=','globalThis.REVIEW_INDEX=')+';globalThis.T={buildReviewIndex,reviewsMarkup}',ctx);
 ctx.REVIEW_INDEX=ctx.T.buildReviewIndex({reviews:{abc:{title:'Test <b>',families:[{family:'X|Y',sizes_tested:[900],sizes_mentioned:[900]}]}}},[{video_id:'abc',claims:[{start_s:75,statement_fr:'Bon <script>',limits:'L'}]}]);
 const h=ctx.T.reviewsMarkup('X|Y',900,'cm²');
 assert.ok(h.includes('&lt;script&gt;')&&!h.includes('<script>'),'texte non échappé');
 assert.ok(h.includes('t=75s')&&h.includes('1:15')&&h.includes('ta taille testée')&&/ni la taille ni le classement/.test(h));
 assert.match(ctx.T.reviewsMarkup('Z|Z',1,'L'),/aucun essai relu/);
 console.log('Video review cards: escaping, timestamp links and scope notice');
}
// Ressenti agrégé sur les cartes : seulement concordants et avis partagés, sources nommées et échappées.
{
 const src=fs.readFileSync('index.html','utf8');
 const vm=require('node:vm');const ctx={};vm.createContext(ctx);
 vm.runInContext(src.slice(src.indexOf('const esc='),src.indexOf('function mmss('))+src.slice(src.indexOf('let FEEL_INDEX='),src.indexOf('function foilMarkup(')).replace('let FEEL_INDEX=','globalThis.FEEL_INDEX=')+';globalThis.T={feelMarkup}',ctx);
 ctx.FEEL_INDEX={'X|Y':{sources:3,criteria:{TOL:{statut:'concordant',sens:'-',sources_majoritaires:2,sources_majoritaires_independantes:1,favorable:0,defavorable:2},MAN:{statut:'divergent',favorable:1,defavorable:1},GLI:{statut:'isolé'}},
  evidence:{TOL:[{pol:'-',source:'A <x>'},{pol:'-',source:'B'}]}}};
 const h=ctx.T.feelMarkup('X|Y');
 assert.ok(h.includes('Peu tolérante')&&h.includes('2 sources concordantes')&&h.includes('dont 1 sans lien commercial déclaré'));
 assert.ok(h.includes('A &lt;x&gt;')&&!h.includes('<x>'),'source non échappée');
 assert.ok(h.includes('Avis partagés')&&h.includes('maniabilité (1 favorable, 1 défavorable)')&&!h.includes('glisse'));
 assert.equal(ctx.T.feelMarkup('Z|Z'),'');
 console.log('Ride feel cards: concordant/divergent only, escaped sources, scope notice');
}
