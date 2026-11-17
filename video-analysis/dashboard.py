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
        analyses[review['video_id']]={'claims':len(review['claims']),'url':'video-analysis/reviews.html?video='+review['video_id'],'audio_verified':False}
    for r in source:
        vid=r['video_id']; a=analyses.get(vid)
        records[vid]={**records.get(vid,{}),'video_id':vid,'title':r['title'],'language':r.get('language'),'collection':r['status'],'segments':r.get('segment_count'),
          'keyword_candidates':r.get('candidate_count'), 'analysis':'interpreted' if a else 'queued' if r['status']=='timed_transcript_received' else 'awaiting_transcript',
          'claims':a['claims'] if a else 0,'evidence_url':a['url'] if a else None,
          'integration':'integrated' if vid in ('DMlWjjIcwss','NTOAhBM2Wms') else 'documented' if a else 'pending',
          'failure':(r.get('last_retry') or {}).get('http_status',r.get('failure_type')),
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
    integrations=load(root/'data/research/conditional_integrations.json',{}).get('integrations',[])
    integrated_ids={i['video_id'] for i in integrations}
    for video in videos:
        if video['video_id'] in integrated_ids:
            video['integration']='integrated'
            video['integration_reason']='Option conditionnelle intégrée au moteur, fiche constructeur contrôlée. Estimation de surface non mesurée; montage complet à confirmer.'
    for video in videos:
        review=review_by_id.get(video['video_id'],{})
        scope=review.get('scope','')
        video['review_kind']=('out_of_scope' if scope.startswith(('parawing','electric_assist','accessory_only','kite_only','wake_only','tow_only','wing_sail_only','prone_only')) else 'no_technical_speech' if scope.startswith('music_only') else 'limited_content' if scope.startswith(('intro_only','commercial_','design_description','unusable_','short_preview','range_description')) else 'technical_review') if video.get('analysis')=='interpreted' else None
        video['reading_scope']='scope_qualification' if scope.endswith('scope_qualification') else 'transcript_review' if review else None
        if video['reading_scope']=='scope_qualification':
            video['review_kind']='scope_qualification'
        if review.get('integration') in ('conditional_board_selection','conditional_selection'):
            video['integration']='integrated'
        elif review.get('integration') in ('conditional_caution','conditional_setup'):
            video['integration']='advice_integrated'
        elif review.get('integration')=='catalogue_documented':
            video['integration']='catalogue_documented'
    publishers=load(root/'data/research/video_publishers.json',{})
    for row in load(discovery,{}).get('videos',[]):
        vid=row.get('url','').split('v=')[-1].split('&')[0]
        if row.get('publisher'):
            publishers[vid]={'publisher':row['publisher'],'channel_id':row.get('channel_id')}
    for video in videos:
        metadata=publishers.get(video['video_id'],{})
        video['publisher']=metadata.get('publisher') or video.get('publisher')
        video['channel_id']=metadata.get('channel_id') or video.get('channel_id')
    for relation in load(root/'data/research/translation_links.json',{}).get('links',[]):
        video=next((v for v in videos if v['video_id']==relation['video_id']),None)
        if video and video.get('analysis')=='queued' and relation['related_source_id'] in analyses:
            video.update(analysis='related_version',review_kind='related_translation',related_source_id=relation['related_source_id'],integration='documented',integration_reason=relation['limit'],evidence_url='data/research/transcript_reviews.json',claims=0)
    qualifications=load(root/'data/research/discovery_qualification.json',{}).get('decisions',[])
    for decision in qualifications:
        video=next((v for v in videos if v['video_id']==decision['id']),None)
        if video:
            video['discovered_on']=decision.get('published_on') or video.get('discovered_on')
            video['metadata_screening']=decision['screening_status']
            video['screening_reasons']=decision['screening_reasons']
            if video['collection']=='new':
                video['analysis']='scope_review_required'
                video['integration_reason']='Qualification des métadonnées uniquement : '+', '.join(decision['screening_reasons'])
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
      'monitored_publishers':load(root/'data/research/monitored_publishers.json',{}).get('publishers',[]),
      'written_research':{'leads':len(load(root/'data/research/written_review_leads_latest.json',{}).get('articles',[])),'new_articles_read':len(load(root/'data/research/expanded_test_evidence.json',{}).get('reviews',[])),'evidence_url':'data/research/expanded_test_evidence.json'},
      'videos':videos,'improvements':[
       {'title':'Retard des 29 textes disponibles traité','detail':'26 lectures intégrales et trois qualifications ciblées explicitement signalées. 130 notes minutées, tailles réelles séparées des gammes et pratiques envisagées. Conseils MA Mk II 790/1190 et Enduro 700/900/1100 intégrés aux résultats, sans équivalence de surface inventée.','commit':'main'},
       {'title':'WAKA Glide : premier essai KiteWorld Shop intégré','detail':'Cinq volumes et dimensions fabricant ajoutés ; seule 77 L essayée à 76 kg. Sélection intermédiaire/avancée, avertissements sur nose, clapot latéral et assemblage.','video_id':'JbO6v-GSibQ','commit':'main'},
       {'title':'Catalogue élargi et essais écrits accessibles','detail':'Modèles sans notes désormais visibles, études vidéo et écrites consultables. F-ONE : générations historiques séparées des références TITAN 2. Recherche écrite élargie à plusieurs éditeurs.','commit':'main'},
       {'title':'Skybrid SLS 80 L : compromis de stabilité précisé','detail':'Essai à 83 kg : léger enfoncement au départ et moins de stabilité en roulis face à la 85 L 2025. Conseil visible, sans nouveau seuil de poids ni note inventée.','video_id':'vOvMPu4SbRo','commit':'main'},
       {'title':'Drifter 5 Pro Carbon : 60 L vérifiée et contextualisée','detail':'Ajout de la seule 60 L contrôlée chez KT : 165,1 × 55,88 cm. Essai avancé, sans conversion du ressenti en litres ni conseil débutant.','video_id':'khXSoXL7ccA','commit':'main'},
       {'title':'Super K 2 Carbon et Skybrid SLS 2026 : sélection de planches élargie','detail':'Dimensions constructeur vérifiées et générations séparées. Sélection à partir du niveau intermédiaire, avec volume et largeur adaptés; aucune note inventée.','commit':'main'},
       {'title':'One-Lock et Crest : conseils isolés par taille','detail':'1125 avec stab180 séparée des 725 et1525. Crest800/925 : conduite active et réception freinante signalées; les autres tailles ne récupèrent pas automatiquement ces conclusions.','commit':'main'},
       {'title':'Midlength Mk II X-Form : volumes vérifiés et sélection conditionnelle','detail':'Neuf volumes constructeur ajoutés. Réservée aux niveaux intermédiaires et avancés ; priorité facilité sans sinker implicite. Essais 55, 65 et 85 L contextualisés, sans note de performance inventée.','commit':'97cd8fc'},
       {'title':'Six essais : conseils par taille et montage','detail':'Enduro 2024, One-Lock 725 et 1525, MA MkII, UHA et Nomad : choix des tails, limites de glisse et contexte des tests. Conseils intégrés, sans modification arbitraire des notes.','commit':'97cd8fc'},
       {'title':'Glide 825 et Halo 670/800 : options conditionnelles','detail':'Glide pour glisse/allround à partir du niveau intermédiaire; Halo pour surf/saut avancé. Priorité facilité exclue. Fiches constructeur contrôlées, sans notes inventées ni plage de vent garantie.','commit':'main'},
       {'title':'Silk V2 : préserver la facilité','detail':'650 remplacée au minimum par 750 si priorité facilité ou niveau inférieur à 3. Précaution éditoriale, pas seuil mesuré.','video_id':'DMlWjjIcwss','commit':'fd8287a'},
       {'title':'Planche : éviter un sinker implicite','detail':'Priorité facilité : volume inférieur au poids écarté, sauf départ sinker explicite. Ne garantit pas la stabilité.','video_id':'NTOAhBM2Wms','commit':'ca659d2'},
       {'title':'Preuves consultables par taille','detail':'30 observations pilotes minutées dans le configurateur, limites et montages visibles.','commit':'549ef77'}]}
    dest=root/'data/research/progress.json';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return output

if __name__=='__main__':
    d=build();print('Dashboard:',len(d['videos']),'videos')
