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
