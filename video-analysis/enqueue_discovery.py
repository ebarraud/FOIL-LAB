"""Qualify new references using titles only and enqueue eligible metadata once."""
import html,json,re
from pathlib import Path
from qualify import assess,BOARD,FOIL

# Explicit title checks: metadata eligibility only, never technical evidence.
TITLE_CHECKS={
    'qvvLnJBdlC0':('board','Le titre italien annonce une recension de planche wingfoil Indiana Super Fly CML ; « Recensione » signifie revue.'),
    'kOnOMWTcOmI':('board','Le titre annonce un essai de longue durée Skybrid SLS en wingfoil et Foil Drive ; conserver les deux usages séparés lors de la lecture.')
}

def main():
    root=Path('.')
    progress=json.loads((root/'data/research/progress.json').read_text(encoding='utf-8'))
    batch_path=root/'video-index/batch-103.json'
    batch=json.loads(batch_path.read_text(encoding='utf-8'))
    known={r['video_id'] for r in batch['results']}
    previous_path=root/'data/research/discovery_qualification.json'
    previous={d['id']:d for d in json.loads(previous_path.read_text(encoding='utf-8')).get('decisions',[])} if previous_path.exists() else {}
    previous_ids=set(previous)
    decisions=[]
    for row in progress['videos']:
        if row['collection']!='new' and row['video_id'] not in previous_ids:continue
        title=html.unescape(row['title'])
        category='board' if BOARD.search(title) else 'foil' if FOIL.search(title) else 'other'
        item=assess(dict(id=row['video_id'],title=title,category=category,url='https://www.youtube.com/watch?v='+row['video_id'],published_on=row.get('discovered_on') or previous.get(row['video_id'],{}).get('published_on'),publisher=row.get('publisher')))
        extra=[]
        if re.search(r'\b(?:foil.?assist|foil.?drive|e-?foil|leash|scoot|kite.?foil|dock.?start|pump.?foil)\b',title,re.I):extra.append('assist_accessory_or_other_discipline_scope_review')
        if re.search(r'traduit|translat|version fran',title,re.I):extra.append('declared_translation_link_before_collecting_again')
        if re.search(r'parawing|pocket rocket',title,re.I) and category not in ('board','foil'):extra.append('parawing_equipment_not_board_or_front_foil')
        if category=='board' and re.search(r'\bwing\b|wingfoil',title,re.I):
            item['screening_reasons']=[x for x in item['screening_reasons'] if x!='other_foil_discipline_not_wingfoil_confirmed']
        if re.search(r'front wing review',title,re.I):
            item['screening_reasons']=[x for x in item['screening_reasons'] if x!='non_test_or_tutorial_signal']
        item['screening_reasons']+=extra
        if row['video_id'] in TITLE_CHECKS:
            item['category'],item['title_scope_check_fr']=TITLE_CHECKS[row['video_id']]
            item['screening_reasons']=[]
        item['screening_status']='needs_manual_scope_review' if item['screening_reasons'] else 'priority_metadata_candidate'
        item['category_basis']='inferred_from_title_only_not_content_verified'
        eligible=item['screening_status']=='priority_metadata_candidate'
        item['queue_decision']='queued_for_free_collection' if eligible else 'scope_review_required'
        decisions.append(item)
        if eligible and row['video_id'] not in known:
            batch['results'].append(dict(video_id=row['video_id'],title=title,status='awaiting_transcript',requested_language='auto',failure_type=None))
            known.add(row['video_id'])
    batch['inventory_count']=len(batch['results'])
    batch['processed']=sum(r['status']!='awaiting_transcript' for r in batch['results'])
    batch_path.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    dest=root/'data/research/discovery_qualification.json'
    dest.write_text(json.dumps(dict(method='Title/date/publisher metadata screening only; no video or transcript analyzed by this screening.',decisions=decisions),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('New references:',len(decisions),'queued:',sum(d['queue_decision']=='queued_for_free_collection' for d in decisions))
if __name__=='__main__':main()
