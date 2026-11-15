# FOIL LAB EXPERT

## Transcriptions analysées — 15 novembre 2026

Les trois transcriptions AFS Silk V2, Duotone Glide 3.0 D/LAB 825 et KT Halo ont été récupérées sans clé ni crédit payant, puis consultées en entier. Le [rapport sourcé](research/ANALYSE_TRANSCRIPTIONS_2026-11-15.md) présente **30 synthèses minutées**, leurs tailles, montages et limites. Le [registre des preuves](video-analysis/evidence.html) les distingue des 10 observations écrites antérieures. Interprétations de transcription par assistant, sans vérification à l'écoute ni validation humaine ; aucune note ajoutée au catalogue.

Le pipeline conserve désormais **159 candidats sur 159**, contre 50 dans l'artefact initial, et permet une reprise hors ligne depuis un cache local optionnel. Les transcriptions intégrales ne sont pas versionnées.

Configurateur indépendant d'aide au choix de **foils et boards de wingfoil**.

## Objectif
Proposer une sélection restreinte (jusqu'à trois ailes avant et trois boards) adaptée au rider, en distinguant les spécifications constructeur, les essais indépendants, les retours des pratiquants et les extrapolations.

## Architecture cible
- `index.html` — application utilisable sur mobile
- `data/model_variants.json` — références, tailles, notes éditoriales et confiance
- `data/sources.json` — sources documentées
- `docs/METHODOLOGY.md` — méthode d'évaluation
- `research/CHANGELOG.md` — historique des découvertes

## État du dépôt
Structure initialisée le 14 novembre 2026. Le configurateur V5 et les 109 variantes JSON sont présents. La branche `feature/catalogue-json-mobile-v5` charge `data/model_variants.json` pour les fiches détaillées et les comparaisons, avec données intégrées de secours hors ligne. Les règles initiales de présélection par profil restent embarquées dans l’HTML ; leur externalisation est une étape ultérieure.

## Mise à jour des données
Modifier `data/model_variants.json` puis valider les quatre notes, la provenance et le niveau de confiance. En ligne, le configurateur recharge les fiches depuis le JSON au démarrage. Pour un usage via fichier HTML ouvert localement (`file://`), la lecture JSON peut être bloquée par le navigateur ; l'application utilise alors ses données intégrées.

## Publication
Le dépôt est privé. GitHub Pages peut nécessiter un plan éligible ou un dépôt public. Ne rendre le dépôt public que volontairement, après revue des données. Pour publier : Settings → Pages → Build and deployment → Deploy from a branch → main / (root). Le site publié est accessible publiquement, même pour certains dépôts privés éligibles.

## Précautions
Les notes de décollage, glisse, carving et contrôle sont ordinales et éditoriales (1–5), pas des mesures physiques. Les compatibilités de composants doivent être vérifiées par génération et constructeur.

La veille hebdomadaire documente les nouvelles données. Aucun contenu tiers ne doit être copié sans respecter sa licence.

## Parcours mobile (V5)
Le configurateur intégré dans `index.html` comporte trois étapes : profil, conditions de navigation, matériel/contraintes. Les recommandations restent calculées en direct par le moteur V4 ; sur mobile elles sont dévoilées à la dernière étape. Navigation clavier, cibles tactiles et préférence « mouvement réduit » prises en compte.

## Catalogue exporté
`data/model_variants.json` contient **72 variantes d'ailes avant et 37 variantes de boards**, extraites de la base embarquée V4. Il s'agit d'un **instantané de travail** : le moteur de recommandations consomme encore ses tableaux JavaScript intégrés ; il n'y a donc pas encore de synchronisation automatique entre JSON et HTML. Les preuves et notes restent à auditer référence par référence.

## Mise en ligne
Pour exposer l'application publiquement, il faut configurer un hébergement statique (par exemple GitHub Pages avec les règles d'accès adaptées au dépôt privé). Le dépôt GitHub seul n'est pas une URL publique d'application.
