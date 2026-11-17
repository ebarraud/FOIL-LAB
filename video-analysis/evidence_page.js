'use strict';
const $=id=>document.getElementById(id);
let dossiers=[];
const make=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n};
function evidenceLink(url,text){const n=make('a',text);n.href=url;n.target='_blank';n.rel='noopener noreferrer';return n}
function evidenceTime(s){s=Math.floor(s);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
function renderDossier(){
 const e=dossiers.find(e=>e.id===$('model').value);$('records').replaceChildren();if(!e){$('records').append(make('p','Aucun dossier pour ces filtres. Effacez la recherche ou changez le type de source.','empty'));return}
 const box=make('section',undefined,'panel');box.append(make('h2',e.model),make('p',e.publisher||'Éditeur non renseigné','muted'),make('p',e.method||'Méthode : voir les limites','warning'));
 if(e.sizes.length)box.append(make('p','Tailles citées dans ce dossier : '+e.sizes.map(s=>s.value+' '+s.unit).join(' / '),'subtitle'));
 for(const [label,value] of [['Montage / langue',e.setup],['Décision',e.decision],['Empreinte de la source',e.hash]])if(value)box.append(make('p',label+' : '+value,'subtitle'));
 if(e.source)box.append(evidenceLink(e.source,'Ouvrir la source'));
 const notes=evidenceVisibleClaims(e,$('size').value,$('kind').value);box.append(make('p',notes.length+' note(s) pour cette sélection','subtitle'));
 for(const c of notes){const a=make('article',undefined,'claim');if(c.id)a.id=c.id;a.append(make('span',c.kind==='video'?'Transcription · audio non vérifié':'Source écrite','pill'));
  if(c.sizes.length)a.append(make('span',c.sizes.map(s=>s.value+' '+s.unit).join(' / '),'pill'));
  a.append(make('p',c.statement),make('p','Limites : '+(c.limits||'Voir la source.'),'subtitle'));
  if(c.scope)a.append(make('p',c.scope,'subtitle'));
  if(c.url)a.append(evidenceLink(c.url,Number.isFinite(c.start)&&Number.isFinite(c.end)?evidenceTime(c.start)+' → '+evidenceTime(c.end)+' · Passage source':'Lire la source'));box.append(a);
 }
 if(!notes.length)box.append(make('p','Aucune note pour ces filtres.','empty'));$('records').append(box);
}
function dossierSizes(){const e=dossiers.find(e=>e.id===$('model').value);$('size').replaceChildren();const all=make('option','Toutes les tailles du dossier');all.value='all';$('size').append(all);for(const s of e?.sizes||[]){const o=make('option',s.value+' '+s.unit);o.value=s.value+'|'+s.unit;$('size').append(o)}renderDossier()}
function dossierOptions(){const previous=$('model').value;const rows=evidenceVisibleEntries(dossiers,$('search').value,$('kind').value);$('model').replaceChildren();for(const e of rows){const o=make('option',e.model+' · '+(e.publisher||'éditeur à confirmer'));o.value=e.id;$('model').append(o)}if(rows.some(e=>e.id===previous))$('model').value=previous;$('matching').textContent=rows.length+' dossier(s) correspondant(s) sur '+dossiers.length;if(!rows.length)$('records').replaceChildren(make('p','Aucun dossier pour ces filtres. Effacez la recherche ou changez le type de source.','empty'));dossierSizes()}
async function loadEvidence(){
 const files={pilot:'pilot_3_video_tests_2026-11-15.json',transcripts:'transcript_reviews.json',board:'board_transcript_observations_2026-11-15.json',written:'written_test_evidence_2026.json',expanded:'expanded_test_evidence.json',progress:'progress.json',links:'catalogue_evidence_links.json'};
 const loaded={},errors=[];await Promise.all(Object.entries(files).map(async([key,name])=>{try{const r=await fetch('../data/research/'+name,{cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);loaded[key]=await r.json()}catch(e){errors.push(name+' : '+e.message)}}));
 dossiers=evidenceLibrary(loaded).sort((a,b)=>a.model.localeCompare(b.model,'fr'));
 $('models').textContent=dossiers.length;$('claims').textContent=dossiers.reduce((n,e)=>n+e.claims.length,0);$('transcripts').textContent=dossiers.filter(e=>e.kind==='video').length;
 $('loadStatus').textContent=errors.length?'Chargement partiel : '+errors.join(' ; '):'Tous les registres d’analyses disponibles sont chargés. Les simples liens de veille ne sont pas comptés comme essais.';
 $('search').addEventListener('input',dossierOptions);$('kind').addEventListener('change',dossierOptions);$('model').addEventListener('change',dossierSizes);$('size').addEventListener('change',renderDossier);dossierOptions();
 const vid=new URLSearchParams(location.search).get('video');if(vid){if(dossiers.some(e=>e.id==='video:'+vid)){$('model').value='video:'+vid;dossierSizes()}else $('loadStatus').textContent+=' Le dossier vidéo demandé n’est pas présent dans les registres chargés.'}
}
loadEvidence().catch(e=>{$('loadStatus').textContent='Preuves indisponibles : '+e.message});
