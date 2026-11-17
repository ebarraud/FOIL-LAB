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
