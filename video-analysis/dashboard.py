"""Publish metadata-only progress and an automatic analysis queue."""
import json
from datetime import datetime, timezone
from pathlib import Path

def load(path, default):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default

def build(root=Path('.')):
    status=load(root/'research/BATCH_STATUS.json',{})
    batch=load(root/'video-index/batch-103.json',{})
    source=batch.get('results',status.get('results',[]))
    previous=load(root/'data/research/progress.json',{})
    records={r['video_id']:r for r in previous.get('videos',[])}
    analyses={}
    pilot=load(root/'data/research/pilot_3_video_tests_2026-11-15.json',{})
    for e in pilot.get('entries',[]):
        vid=e['video']['url'].split('v=')[-1].split('&')[0]
        claims=[c for c in e['claims'] if c['source_type']=='video_transcript']
        analyses[vid]={'claims':len(claims),'url':'video-analysis/evidence.html','audio_verified':False}
    board=load(root/'data/research/board_transcript_observations_2026-11-15.json',{})
    if board.get('claims'): analyses['NTOAhBM2Wms']={'claims':len(board['claims']),'url':'data/research/board_transcript_observations_2026-11-15.json','audio_verified':False}
    reviews=load(root/'data/research/transcript_reviews.json',{}).get('reviews',[])
    review_by_id={r['video_id']:r for r in reviews}
    for review in reviews:
        analyses[review['video_id']]={'claims':len(review['claims']),'url':'data/research/transcript_reviews.json','audio_verified':False}
    for r in source:
        vid=r['video_id']; a=analyses.get(vid)
        records[vid]={'video_id':vid,'title':r['title'],'language':r.get('language'),'collection':r['status'],'segments':r.get('segment_count'),
          'keyword_candidates':r.get('candidate_count'), 'analysis':'interpreted' if a else 'queued' if r['status']=='timed_transcript_received' else 'awaiting_transcript',
          'claims':a['claims'] if a else 0,'evidence_url':a['url'] if a else None,
          'integration':'integrated' if vid in ('DMlWjjIcwss','NTOAhBM2Wms') else 'documented' if a else 'pending',
          'failure':r.get('last_retry',{}).get('http_status',r.get('failure_type')),
          'integration_reason':review_by_id.get(vid,{}).get('integration_reason') or {
            'aiWA2W7hKos':'Vérification à effectuer par l’assistant : génération Glide 3.0 D/LAB, fiche catalogue du 825 et interfaces des montages H130/43 et H150/40 avant ajout au moteur. Aucun seuil de poids universel déduit des testeurs de 80–90 kg.',
            'zesN5IeyRQM':'Vérification à effectuer par l’assistant : génération Halo, fiches 670/800 et interfaces des fuselages 56/63. Les avis communs restent non départagés et les repères 80/90 kg ne sont pas des seuils mesurés.'
          }.get(vid)}
    # Merge newly discovered references without losing processed records.
    discovery=root/'video-index/youtube-details.json'
    if not discovery.exists(): discovery=root/'video-index/youtube.json'
    for row in load(discovery,{}).get('videos',[]):
        vid=row.get('url','').split('v=')[-1].split('&')[0]
        if len(vid)!=11:continue
        records.setdefault(vid,{'video_id':vid,'title':row['title'],'language':row.get('language'),'collection':'new','analysis':'needs_qualification','integration':'pending','claims':0,'discovered_on':row.get('published_on')})
    videos=list(records.values())
    publishers=load(root/'data/research/video_publishers.json',{})
    for row in load(discovery,{}).get('videos',[]):
        vid=row.get('url','').split('v=')[-1].split('&')[0]
        if row.get('publisher'):
            publishers[vid]={'publisher':row['publisher'],'channel_id':row.get('channel_id')}
    for video in videos:
        metadata=publishers.get(video['video_id'],{})
        video['publisher']=metadata.get('publisher') or video.get('publisher')
        video['channel_id']=metadata.get('channel_id') or video.get('channel_id')
    tasks=load(root/'data/research/analysis_activity.json',{}).get('tasks',[])
    now=datetime.now(timezone.utc)
    for video in videos:
        task=next((t for t in tasks if t.get('video_id')==video['video_id']),None)
        video['activity']=task
        if task and task.get('status')=='in_progress':
            try:
                active=datetime.fromisoformat(task['expires_at_utc'])>now
            except (ValueError,KeyError,TypeError):
                active=False
            if active:
                video['analysis_before_activity']=video['analysis']
                video['analysis']='in_progress'
    output={'updated_at_utc':datetime.now(timezone.utc).isoformat(),'collection_updated_at_utc':status.get('updated_at_utc'),
      'retry_not_before_utc':status.get('retry_not_before_utc'),'collection_state':status.get('retry_status'),
      'analysis_schedule':'Les passages sont repérés à chaque réception. L’interprétation technique est traitée par l’assistant lors des passages planifiés; une intégration exige une règle justifiée et testée.',
      'videos':videos,'improvements':[
       {'title':'Silk V2 : préserver la facilité','detail':'650 remplacée au minimum par 750 si priorité facilité ou niveau inférieur à 3. Précaution éditoriale, pas seuil mesuré.','video_id':'DMlWjjIcwss','commit':'fd8287a'},
       {'title':'Planche : éviter un sinker implicite','detail':'Priorité facilité : volume inférieur au poids écarté, sauf départ sinker explicite. Ne garantit pas la stabilité.','video_id':'NTOAhBM2Wms','commit':'ca659d2'},
       {'title':'Preuves consultables par taille','detail':'30 observations pilotes minutées dans le configurateur, limites et montages visibles.','commit':'549ef77'}]}
    dest=root/'data/research/progress.json';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output

if __name__=='__main__':
    d=build();print('Dashboard:',len(d['videos']),'videos')
