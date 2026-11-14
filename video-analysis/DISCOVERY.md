# Inventaire vidéo Wingfoil — 24 derniers mois

Période fixe de cette première campagne : **14/11/2024 → 14/11/2026 inclus**. Seuls les **essais de foils et de boards utilisés en wingfoil** entrent dans ce périmètre. Les vidéos de wing (voiles), parawing seulement, kitefoil seulement, tutoriels généraux et publicités sont exclues.

## Découverte automatisée

`discover.py` explore les pages de listes **Gleiten.TV Wingfoil → Foil** et **Wingfoil → Wingboard** en suivant leur pagination, puis ajoute éventuellement les vidéos YouTube identifiées à l'aide de l'API officielle Google. Les vidéos sur plusieurs plateformes sont des références candidates : une traduction anglaise du même essai allemand n'est pas comptée comme un test indépendant.

```bash
python video-analysis/discover.py --sources gleiten --max-pages 12 --output video-index/gleiten.json
```

### Recherche YouTube

La recherche publique exhaustive par date sur YouTube nécessite une source de découverte : ici l'**API YouTube Data v3**. Pour activer le volet YouTube, créer un projet Google Cloud, activer l'API et enregistrer une clé limitée au service en secret GitHub Actions nommé `YOUTUBE_API_KEY` (ne jamais la mettre en dur dans le dépôt). Les requêtes comprennent français, anglais, allemand, médias et noms de chaînes ; les résultats sont filtrés par date de publication et type d'essai.

```bash
export YOUTUBE_API_KEY="clé récupérée dans Google Cloud"
python video-analysis/discover.py --sources youtube --youtube-pages 2 --output video-index/youtube.json
```

**Sans clé**, le volet YouTube est marqué `missing_api_key_no_yt_search_performed`, jamais comme une recherche réussie. Une recherche YouTube ne peut pas garantir de recenser absolument toutes les vidéos, notamment celles non indexées.

### Traçabilité

- `published_on` d'après l'API YouTube : date de publication issue de la source.
- `published_on` extrait à proximité d'un lien Gleiten.TV : candidat **à confirmer** car la structure HTML peut varier.
- Une date absente ou imprécise ne doit pas être traitée comme située avec certitude dans les 24 mois.
- `source_status` n'implique aucun visionnage.
- Les champs `transcript_status=not_obtained` et `fully_watched=false` sont conservés jusqu'à analyse effective.

Les fichiers de sortie sont archivés en tant qu'artefacts GitHub Actions, pas injectés automatiquement dans les recommandations. Les transcriptions autorisées pourront ensuite être analysées dans `review.html` ou `analyze.py`, validées et rattachées au bon millésime/à la bonne taille.

## Sources

- https://gleiten.tv/foil/test/wingfoil/foil/alle/
- https://gleiten.tv/foil/test/wingfoil/wingboard/alle/
- https://developers.google.com/youtube/v3/docs/search/list
