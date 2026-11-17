'use strict';
// Shared adapters: every reviewed source is kept; discovery leads are not reviews.
function evidenceLibrary(input){
 const out=[],publishers=new Map((input.progress?.videos||[]).map(v=>[v.video_id,v.publisher]));
 const videoUrl=id=>'https://www.youtube.com/watch?v='+id;
 const timedUrl=(id,start)=>videoUrl(id)+'&t='+Math.floor(start||0)+'s';
 const sizesFor=id=>{
  const sizes=[];
  for(const r of input.expanded?.catalogue_records||[])if(r.entry?.i?.endsWith('?video='+id))sizes.push({value:r.size,unit:r.type==='board'?'L':'cm²'});
  for(const r of input.links?.links||[])if(r.video_id===id)sizes.push({value:r.size,unit:r.size_unit||'cm²'});
  return [...new Map(sizes.map(s=>[s.value+'|'+s.unit,s])).values()];
 };
 for(const e of input.pilot?.entries||[])out.push({id:'pilot:'+e.id,model:e.model,publisher:publishers.get(e.video?.url?.split('v=')[1])||'Essai pilote',kind:'video',sizes:(e.tested_sizes_cm2||[]).map(value=>({value,unit:'cm²'})),method:'Transcription pilote consultée en entier ; audio non vérifié. Les sources écrites restent distinguées.',setup:e.transcript_setup_fr,source:e.video?.url,claims:e.claims.map(c=>({id:c.id,kind:c.source_type==='video_transcript'?'video':'written',statement:c.statement_fr,limits:c.limitations,start:c.start_s,end:c.end_s,url:c.source_url||e.written_source?.url,sizes:(c.sizes_cm2?.length?c.sizes_cm2:c.size_cm2?[c.size_cm2]:[]).map(value=>({value,unit:'cm²'})),scope:c.scope_basis_fr}))});
 for(const r of input.transcripts?.reviews||[])out.push({id:'video:'+r.video_id,model:r.model,publisher:r.publisher||publishers.get(r.video_id)||'Éditeur non renseigné',kind:'video',sizes:sizesFor(r.video_id),method:r.review_method,setup:r.language_note,decision:r.integration_reason,hash:r.transcript_sha256,source:videoUrl(r.video_id),claims:(r.claims||[]).map(c=>({id:c.id,kind:'video',statement:c.statement_fr,limits:c.limits,start:c.start_s,end:c.end_s,url:timedUrl(r.video_id,c.start_s),sizes:[],scope:'Taille / montage : lire le passage et ses limites ; aucune attribution automatique à toutes les tailles du dossier.'}))});
 const boards=new Map();
 for(const c of input.board?.claims||[]){const key=c.model;if(!boards.has(key))boards.set(key,[]);boards.get(key).push(c)}
 for(const [model,claims] of boards)out.push({id:'board:'+model,model,publisher:publishers.get('NTOAhBM2Wms')||'Essai de planche',kind:'video',sizes:[...new Set(claims.map(c=>c.size_l).filter(Boolean))].map(value=>({value,unit:'L'})),method:'Interprétation de transcription, audio non vérifié.',source:claims[0].source_url,hash:claims[0].transcript_sha256,claims:claims.map(c=>({id:c.id,kind:'video',statement:c.statement_fr,limits:c.limits,start:c.start_s,end:c.end_s,url:c.source_url,sizes:c.size_l?[{value:c.size_l,unit:'L'}]:[]}))});
 for(const r of input.written?.reviews||[])out.push({id:'written:'+r.id,model:r.brand+' '+r.model,publisher:r.source_author,kind:'written',sizes:(r.sizes_tested||[]).map(value=>({value,unit:(r.size_unit||'cm²').trim()})),method:'Essai écrit : paraphrases attribuées, pas une transcription vidéo.',setup:r.setup,source:r.source_url,claims:(r.claims||[]).map(c=>({kind:'written',statement:c.summary,limits:c.limits,url:r.source_url,sizes:c.size?[{value:c.size,unit:(r.size_unit||'cm²').trim()}]:[]}))});
 for(const r of input.expanded?.reviews||[])out.push({id:'expanded:'+r.id,model:r.brand+' '+r.model,publisher:r.publisher,kind:'written',sizes:r.size_cm2?[{value:r.size_cm2,unit:'cm²'}]:[],method:r.source_type==='publisher_overview_not_test'?'Présentation éditoriale lue ; pas un essai sur l’eau.':'Corps de l’essai écrit lu ; paraphrase courte attribuée.',setup:r.setup,source:r.source_url,hash:r.source_html_sha256,claims:[{kind:'written',statement:r.summary_fr,limits:r.limits,url:r.source_url,sizes:r.size_cm2?[{value:r.size_cm2,unit:'cm²'}]:[]}]});
 return out;
}
function evidenceVisibleEntries(entries,query,kind){const q=query.trim().toLocaleLowerCase('fr');return entries.filter(e=>(!q||(e.model+' '+e.publisher).toLocaleLowerCase('fr').includes(q))&&(kind==='all'||e.claims.some(c=>c.kind===kind)))}
function evidenceVisibleClaims(entry,size,kind){return entry.claims.filter(c=>(kind==='all'||c.kind===kind)&&(size==='all'||!c.sizes.length||c.sizes.some(s=>s.value+'|'+s.unit===size)))}
if(typeof module!=='undefined')module.exports={evidenceLibrary,evidenceVisibleEntries,evidenceVisibleClaims};
