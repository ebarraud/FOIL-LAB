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

## Première collecte réellement enregistrée

Le fichier `seed_2024-2026_gleiten.json` contient **46 références candidates** (22 foils et 24 boards), relevées dans les index publics et datées entre août 2025 et octobre 2026. Certaines sont des traductions du même essai : elles ne doivent **pas** être traitées comme indépendantes. Ce lot n'est pas présenté comme exhaustif.

Le premier essai réseau du workflow a renvoyé `HTTPError` pour les deux catégories Gleiten.TV sur les IP GitHub Actions. L'index automatique a donc retourné **0 résultat**, bien que les pages soient accessibles via recherche web ; la liste de 46 références est un jeu de démarrage établi séparément. Le volet YouTube a été **ignoré faute de clé API configurée**. Aucun contenu parlé n'a été récupéré ni analysé.

Le filtre de date du script est glissant sur deux ans à compter de chaque exécution ; le fichier de démarrage conserve les dates fixes de cette campagne pour la traçabilité.

## Activation concrète de YouTube Data API (clé nécessaire)

1. Ouvrir [Google Cloud Console — projet](https://console.cloud.google.com/projectcreate) et créer (ou sélectionner) un projet Google Cloud.
2. [Activer YouTube Data API v3](https://console.cloud.google.com/apis/library/youtube.googleapis.com).
3. Ouvrir [Identifiants Google Cloud](https://console.cloud.google.com/apis/credentials), créer une **clé API** et la limiter à l'API YouTube Data v3. Pour ce job serveur GitHub Actions, **ne pas restreindre à un référent HTTP de navigateur** ; le service requiert une clé utilisable depuis le job, avec quota minimal et surveillance.
4. Ouvrir [GitHub → FOIL-LAB → Actions secrets](https://github.com/ebarraud/FOIL-LAB/settings/secrets/actions), choisir **New repository secret**, nom exactement `YOUTUBE_API_KEY`, coller sa valeur **dans GitHub**, jamais dans un fichier du dépôt ni dans la conversation.
5. Ouvrir [Actions → Discover Wingfoil Board and Foil Reviews](https://github.com/ebarraud/FOIL-LAB/actions/workflows/discover-wingfoil.yml), **Run workflow**, puis télécharger l'artefact `wingfoil-24-month-discovery`.

Le workflow est également planifié le lundi (07:10 UTC) ; il reste honnêtement inactif sur le volet YouTube tant que le secret manque. Le module n'obtient **pas** la transcription grâce à cette clé : l'API liste les vidéos et métadonnées publiques, mais n'ouvre pas l'accès aux sous-titres d'une chaîne tierce.

La découverte est volontairement limitée à une page de résultats par requête lors de chaque exécution hebdomadaire, pour préserver le quota et éviter une explosion du coût des recherches. La collecte reste non exhaustive et les résultats (titre, date, vidéo) doivent être filtrés et vérifiés avant attribution de conclusions techniques.
