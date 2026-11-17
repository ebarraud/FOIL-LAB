"""Apply explicit metadata decisions without claiming transcript analysis."""
import json
from datetime import datetime,timezone
from pathlib import Path

def apply(root=Path('.')):
    public=root/'data/research'
    progress=json.loads((public/'progress.json').read_text(encoding='utf8'))
    batch_path=root/'video-index/batch-103.json'
    batch=json.loads(batch_path.read_text(encoding='utf8'))
    excluded={
      'qkxFEAlF1p0':'Titre consacré à Duotone Foil Assist, assistance électrique.',
      'sM6P0gvhHHc':'Titre consacré au Foil Scoot et à une méthode d’apprentissage assistée.',
      'Ax6TYpS3F3c':'Titre consacré à Foil Dash, assistance électrique.',
      '2s2VL-JOLLs':'Titre consacré à un leash rétractable.',
      'fi6nIkY35SU':'Titre consacré à un mât intégré Foil Drive.',
      'QsVsnwS5yR4':'Titre consacré à la wing textile XPS, pas à une aile avant immergée.',
      'PZzXYbquiss':'Titre consacré à un support de caméra Flymount.',
      'ppnjPsBSaog':'Titre consacré à des adaptateurs de propulsion Foil Drive.',
      'beK4X-VVH_A':'Extrait renvoyant à une revue de mât Foil Drive, hors sélection non motorisée.',
      'kpgETqovr_U':'Titre consacré à des racks de bateau pour wake/surf.',
      'Bf8esuL_pa4':'Titre consacré à une parawing textile, hors catalogue foils/planches.',
      'nno-iK7N6wo':'Teaser annonçant une revue complète ultérieure, pas un essai complet identifié.'}
    related={'Mj2Z9gHKAYs':'xrEGIa5cgdQ','A34IZza2TEQ':'viZUrrOCL6E','WCiwij40Qr0':'lrW4o4H05tI','6vRUH8WteCk':'_W2HhY4gySA'}
    previous_path=public/'reference_decisions.json'
    previous=json.loads(previous_path.read_text(encoding='utf8')) if previous_path.exists() else {'decisions':[]}
    decisions={r['video_id']:r for r in previous['decisions']}
    known={r['video_id'] for r in batch['results']}
    for v in progress['videos']:
        vid=v['video_id']
        if v['analysis'] not in ('scope_review_required','needs_qualification'):continue
        row={'video_id':vid,'title':v['title'],'checked_on':'2026-11-17','method':'Qualification manuelle des métadonnées conservées : titre, éditeur, modèle et correspondances. Aucun visionnage ou examen du texte revendiqué.','content_verified':False,'transcript_analyzed':False}
        if vid in excluded:
            row.update(decision='excluded_metadata',reason=excluded[vid]+' Écarté du moteur wingfoil non motorisé sur métadonnées uniquement ; réévaluable si une source de contenu révèle un essai pertinent.')
        elif vid in related:
            row.update(decision='related_reference',related_source_id=related[vid],reason='Traduction déclarée dans le titre, même éditeur et modèle que la source liée. Pas un essai indépendant ; traduction non validée sémantiquement, texte non collecté à nouveau.')
        else:
            row.update(decision='collect',reason='Référence retenue pour collecte et vérification du contenu. Le titre ne suffit pas à établir les tailles essayées, l’indépendance ou une performance.')
            if vid not in known:
                batch['results'].append({'video_id':vid,'title':v['title'],'status':'awaiting_transcript','language':None,'collection_priority':100 if vid=='-htD7qNM7_k' else 10,'qualification_reason':row['reason']})
                known.add(vid)
        decisions[vid]=row
    previous.update(updated_at_utc=datetime.now(timezone.utc).isoformat(),decisions=list(decisions.values()))
    previous_path.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    batch['inventory_count']=len(batch['results'])
    batch_path.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return previous

if __name__=='__main__':
    from collections import Counter
    print(dict(Counter(r['decision'] for r in apply()['decisions'])))
