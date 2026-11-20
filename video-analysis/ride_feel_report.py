"""Agrège le ressenti d'utilisation (data/research/ride_feel_annotations.json) par gamme.

Vidéos (annotations) et essais écrits (written_annotations). Pour chaque gamme et chaque critère de la grille : avis favorables / défavorables / nuancés,
nombre de sources distinctes (chaînes), dont indépendantes (ni revendeur, ni lien commercial déclaré),
et un statut :
  - « concordant »  : au moins 75 % des avis tranchés dans le même sens, exprimés par au moins 2 sources distinctes ;
  - « divergent »   : avis tranchés dans les deux sens, sans majorité de 75 % ;
  - « isolé »       : une seule source.
Écrit data/research/ride_feel_summary.json et affiche un rapport.
Usage : python video-analysis/ride_feel_report.py
"""
import json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'data/research'

# Chaînes identifiées comme magasins, écoles ou distributeurs (vendent le matériel testé).
# Les chaînes non identifiées sont classées « créateur » ; seuls les liens commerciaux déclarés dans les lectures sont détectés.
RETAILERS = {
    'Andy Biggs Watersports', 'KitePaddleSurf', 'Nature Kite', 'Sport al Centro', 'Liquid Blue Cabarete',
    'Viking Surfcenter', 'MACkiteboarding', 'KiteWorld Shop', 'bigwinds', 'Green Hat Kiteboarding',
    'Worthing Watersports', 'Flukes Kitesurfing', 'The SUP Company', 'The Foil Shop', 'Reactive Team',
}
MEDIA = {'Gleiten tv', 'Sup Passion // Foil Magazine', 'Tonic Mag', 'wingSURF world'}
COMMERCIAL = re.compile(r"ambassadeur|envoi de matériel|envoyé par|prêtée? par|code de remise|vendent ces|vendre ces|"
                        r"auteur vend|invite à acheter|magasin vendant|matériel envoyé", re.I)


def load(name):
    return json.loads((D / name).read_text(encoding='utf-8'))


def group_for(title, families):
    if len(families) == 1:
        return families[0]['family'], True
    if len(families) > 1:
        return None, True  # essai comparatif : non attribuable à une seule gamme
    t = re.split(r'\s*[·—(/]|\s\d', title)[0].strip()
    return 'hors moteur|' + t, False


def build():
    ann = load('ride_feel_annotations.json')
    reviews = {r['video_id']: r for r in load('transcript_reviews.json')['reviews']}
    fmap = load('review_family_map.json')['reviews']
    pub = {v['video_id']: (v.get('publisher') or '?') for v in load('progress.json')['videos']}

    commercial_review = {
        vid: bool(COMMERCIAL.search(' '.join(c.get('statement_fr', '') for c in (r.get('claims') or []))))
        for vid, r in reviews.items()
    }

    groups = collections.defaultdict(lambda: {'in_engine': False, 'videos': set(), 'sources': set(),
                                              'criteria': collections.defaultdict(list)})
    unattributed = 0
    for a in ann['annotations']:
        vid = a['video_id']
        g, in_engine = group_for(reviews[vid]['model'], fmap.get(vid, {}).get('families', []))
        if g is None:
            unattributed += 1
            continue
        source = pub.get(vid, '?')
        kind = 'revendeur' if source in RETAILERS else ('média' if source in MEDIA else 'créateur')
        independent = kind != 'revendeur' and not commercial_review.get(vid)
        G = groups[g]
        G['in_engine'] = in_engine
        G['videos'].add(vid)
        G['sources'].add(source)
        for c in a['criteria']:
            G['criteria'][c['c']].append({'pol': c['pol'], 'int': c['int'], 'source': source,
                                          'independent': independent, 'video_id': vid,
                                          'start_s': a.get('start_s'), 'compared_to': a.get('compared_to')})

    for w in ann.get('written_annotations', []):
        G = groups[w['family']]
        G['in_engine'] = True
        G['videos'].add(w['source_url'])
        G['sources'].add(w['publisher'])
        independent = w['publisher_kind'] != 'revendeur'
        for c in w['criteria']:
            G['criteria'][c['c']].append({'pol': c['pol'], 'int': c['int'], 'source': w['publisher'],
                                          'independent': independent, 'video_id': None, 'url': w['source_url'],
                                          'start_s': None, 'compared_to': w.get('compared_to')})

    summary = {}
    for g, G in groups.items():
        crits = {}
        for code, ops in G['criteria'].items():
            pos = [o for o in ops if o['pol'] == '+']
            neg = [o for o in ops if o['pol'] == '-']
            nua = [o for o in ops if o['pol'] == '~']
            srcs = {o['source'] for o in ops}
            indep = {o['source'] for o in ops if o['independent']}
            decided = len(pos) + len(neg)
            share = max(len(pos), len(neg)) / decided if decided else 0
            major = pos if len(pos) >= len(neg) else neg
            major_srcs = {o['source'] for o in major}
            if len(srcs) < 2:
                status = 'isolé'
            elif decided and share >= 0.75 and len(major_srcs) >= 2:
                status = 'concordant'
            elif pos and neg:
                status = 'divergent'
            else:
                status = 'nuancé'
            crits[code] = {
                'favorable': len(pos), 'defavorable': len(neg), 'nuance': len(nua),
                'sources': len(srcs), 'sources_independantes': len(indep), 'statut': status,
                'sources_majoritaires': len(major_srcs) if decided else 0,
                'sources_majoritaires_independantes': len({o['source'] for o in major if o['independent']}) if decided else 0,
                'sens': ('+' if len(pos) > len(neg) else '-' if len(neg) > len(pos) else '~') if decided else '~',
                'avec_comparaison': sum(1 for o in ops if o['compared_to']),
            }
        summary[g] = {'in_engine': G['in_engine'], 'videos': len(G['videos']), 'sources': len(G['sources']),
                      'criteria': crits,
                      'evidence': {code: [{k: o[k] for k in ('pol', 'source', 'independent', 'video_id', 'start_s', 'compared_to') if o.get(k) is not None}
                                          | ({'url': o['url']} if o.get('url') else {})
                                          for o in ops] for code, ops in G['criteria'].items()}}
    return ann, summary, unattributed


def main():
    ann, summary, unattributed = build()
    total_claims = sum(len(r.get('claims') or []) for r in load('transcript_reviews.json')['reviews'])
    n_ann = len(ann['annotations'])
    n_crit = sum(len(a['criteria']) for a in ann['annotations'])
    with_cmp = sum(1 for a in ann['annotations'] if a.get('compared_to'))
    freq = collections.Counter(c['c'] for a in ann['annotations'] for c in a['criteria'])
    status = collections.Counter(c['statut'] for s in summary.values() for c in s['criteria'].values())
    concordant = {g: [k for k, c in s['criteria'].items() if c['statut'] == 'concordant'] for g, s in summary.items()}
    engine = {g: s for g, s in summary.items() if s['in_engine']}
    out = {
        'as_of': ann['as_of'],
        'totals': {'observations': total_claims, 'observations_ressenti': n_ann, 'mentions_critere': n_crit,
                   'avec_comparaison': with_cmp, 'non_attribuables_comparatifs': unattributed,
                   'gammes': len(summary), 'gammes_moteur': len(engine),
                   'criteres_par_statut': dict(status), 'frequence_criteres': dict(freq)},
        'families': summary,
    }
    (D / 'ride_feel_summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps(out['totals'], ensure_ascii=False, indent=1))
    print('\nGammes du moteur :')
    for g, s in sorted(engine.items(), key=lambda kv: -kv[1]['sources']):
        cc = ', '.join(f"{k}{s['criteria'][k]['sens']}({s['criteria'][k]['sources']})" for k in concordant[g]) or '—'
        print(f"  {g:38s} vidéos {s['videos']:2d} · sources {s['sources']:2d} · concordants : {cc}")
    print('\nHors moteur, au moins un critère concordant :')
    for g, s in sorted(summary.items(), key=lambda kv: -kv[1]['sources']):
        if not s['in_engine'] and concordant[g]:
            print(f"  {g:38s} sources {s['sources']} · " + ', '.join(f"{k}{s['criteria'][k]['sens']}" for k in concordant[g]))


if __name__ == '__main__':
    main()
