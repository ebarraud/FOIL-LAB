"""Rattache chaque lecture de transcription à une famille du moteur (index.html).

Produit data/research/review_family_map.json : video_id -> familles, tailles testées identifiées
dans l'intitulé de la lecture, et motif. Une lecture n'est rattachée qu'à la génération et à la
construction présentes au catalogue ; les autres restent non rattachées avec leur motif.
Usage : python video-analysis/build_review_family_map.py [--check]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
OUT = ROOT / 'data/research/review_family_map.json'

def families():
    block = HTML[HTML.index('const FOILS=['):HTML.index('const VERIFY')]
    fams = []
    for m in re.finditer(r"\{b:'([^']+)',n:'([^']+)',(?:kind:'(\w+)',)?[^\n]*?sizes:\[(\[[^\n]*?\]|[\d.,]*)\]", block):
        b, n, kind, sizes = m.groups()
        if kind:
            vals = [int(float(x)) for x in re.findall(r"\[(\d+(?:\.\d+)?),", sizes)]
        else:
            vals = [int(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", sizes)]
        fams.append({'brand': b, 'model': n, 'type': 'board' if kind else 'foil', 'sizes': vals})
    return fams

# (famille, motif requis, motifs exclus) — motifs testés sur l'intitulé en minuscules sans espaces superflus.
RULES = [
    ('AFS|Enduro', r'enduro', None),
    ('AFS|Silk V2', r'silk', None),
    ('AFS|Evo', r'\bafs evo|\bevo ?\d', None),
    ('AFS|Blackbird Mid Length Carbon', r'blackbird mid ?length', r'fiber|advanced'),
    ('Armstrong|MA Mk II', r'\bma ?mk ?ii|\bma mk2', r'sonar'),
    ('Armstrong|UHA', r'\buha', None),
    ('Armstrong|Midlength Mk II X-Form', r'midlength mk ?ii|x-form', None),
    ('Duotone|Crest D/LAB', r'crest', None),
    ('Duotone|Glide 3.0 D/LAB', r'glide ?3', None),
    ('Duotone|Skybrid SLS 2026', r'skybrid ?sls', r'^(?!.*2026).*(2027|2025)'),
    ('KT|Nomad', r'\bnomad\b(?! ?190)', None),
    ('KT|Super K 2 Carbon', r'super ?k ?(v ?)?2', None),
    ('KT|Drifter 5 Pro Carbon', r'drifter ?5', None),
    ('KT|Halo', r'\bhalo\b', None),
    ('Naish|Chimera 2026', r'chimera', r'^(?!.*2026).*2027'),
    ('Slingshot|One-Lock Glide', r'one-lock glide', None),
    ('F-ONE|Rocket Wing Midlength', r'rocket wing midlength', None),
    ('F-ONE|SK8', r'\bsk ?8\b', r'v ?2'),
    ('F-ONE|Eagle', r'\beagle\b', None),
    ('F-ONE|Seven Seas', r'seven seas', None),
    ('WAKA|Glide TravelFold', r'\bwaka\b', None),
    ('AXIS|Surge 890', r'\bsurge\b', None),
    ('Code|R Series 680R', r'680r', None),
    ('Cabrinha|Whippit', r'whippit', None),
    ('F-ONE|Gravity', r'\bgravity\b', None),
    ('Armstrong|CF V2', r'\bcf ?v2|\bcf ?(950|1200|1600|2050)\b', None),
    ('GA|Move', r'\bga ?move', None),
    ('KT|Atlas', r'\batlas\b', None),
    ('KT|Instinct', r'\binstinct\b', None),
    ('Duotone|Carve 3.0 D/LAB', r'carve ?3', r'sls'),
    ('North|Sonar SF', r'sonar ?sf|\bsf ?\d{3}', None),
    ('KT|Arc Pro Carbon', r'\bkt\b.*\barc\b|\barc ?\d', None),
]

def build():
    fams = {f"{f['brand']}|{f['model']}": f for f in families()}
    reviews = json.loads((ROOT / 'data/research/transcript_reviews.json').read_text(encoding='utf-8'))['reviews']
    out = {}
    for r in reviews:
        title = re.sub(r'\s+', ' ', r['model']).lower()
        spaced = re.sub(r'(?<=[a-z])(?=\d)', ' ', title)
        hits = []
        for key, pat, excl in RULES:
            if key not in fams:
                continue
            if re.search(pat, spaced) and not (excl and re.search(excl, spaced)):
                fam = fams[key]
                nums = {int(x) for x in re.findall(r'\d{2,4}', spaced)}
                for k in ('size_cm2', 'size_l'):
                    if r.get(k):
                        nums.add(int(r[k]))
                tested = sorted(n for n in nums if n in fam['sizes'])
                lo, hi = (20, 200) if fam['type'] == 'board' else (300, 2600)
                mentioned = sorted(n for n in nums if lo <= n <= hi)
                hits.append({'family': key, 'type': fam['type'], 'sizes_tested': tested, 'sizes_mentioned': mentioned})
        out[r['video_id']] = {
            'title': r['model'],
            'families': hits,
            'comparative': len(hits) > 1,
            'reason': None if hits else 'Modèle, génération ou construction absent du moteur.'
        }
    return {'schema_version': 1, 'generated_by': 'video-analysis/build_review_family_map.py', 'reviews': out}

if __name__ == '__main__':
    data = build()
    if '--check' in sys.argv:
        current = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else None
        sys.exit(0 if current == data else 1)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    mapped = sum(1 for v in data['reviews'].values() if v['families'])
    print(f"{mapped}/{len(data['reviews'])} lectures rattachées à une famille du moteur")
